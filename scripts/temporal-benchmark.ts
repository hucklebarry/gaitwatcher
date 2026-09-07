import {readFile,writeFile} from "node:fs/promises";
const api=process.env.CV_WORKER_URL??"http://localhost:8000";
const rates=(process.env.SAMPLE_RATES??"1,2,5").split(",").map(Number);
const manifest=process.env.TEMPORAL_MANIFEST??"fixtures/temporal/manifest.json";
const corpus=JSON.parse(await readFile(manifest,"utf8"));
const runs:any[]=[];
for(const clip of corpus.clips)for(const sampleFps of rates){
 const response=await fetch(`${api}/detect`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({mediaPath:clip.path,sampleFps,debug:true,invokePose:true})});
 const result:any=await response.json(),person=result.debug?.personRun,pose=result.debug?.poseRun,boxes=person?.boxDiagnostics??[];
 const primitives=[...new Set(boxes.flatMap((x:any)=>x.primitives))];const trackLengths=Object.values((person?.tracks??[]).reduce((a:any,x:any)=>{a[x.trackId]=(a[x.trackId]??0)+1;return a},{}));
 const continuity=trackLengths.length===1&&trackLengths[0]===result.personFrames?"maintained":result.personFrames===0?"not_applicable":"track_lost_or_reassigned";
 const failureReasons=[person?.error,continuity==="track_lost_or_reassigned"?"TRACK_LOST_OR_REASSIGNED":undefined,result.personFrames===0?"NO_PERSON_DETECTIONS":undefined].filter(Boolean);
 runs.push({id:clip.id,activity:clip.activity,kind:clip.kind,viewpoint:clip.viewpoint,sampleFps,expectations:clip.expectations,personDetected:result.personDetected,personPositiveFrames:result.personFrames,framesAnalyzed:result.framesAnalyzed,detectionsPerFrame:result.detectionsPerFrame,trackContinuity:continuity,trackLengths,primitives,poseReturned:pose?.poseReturned??0,poseAvailability:result.framesAnalyzed?(pose?.poseReturned??0)/result.framesAnalyzed:0,bodyState:result.bodyState,poseCallRate:result.framesAnalyzed?result.framesSentToPoseModel/result.framesAnalyzed:0,failureReasons,personDetectionMs:result.personDetectionMs,poseInferenceMs:result.poseInferenceMs,totalProcessingMs:result.totalProcessingMs});
}
const byRate=Object.fromEntries(rates.map(rate=>[rate,{runs:runs.filter(r=>r.sampleFps===rate),averageTotalMs:runs.filter(r=>r.sampleFps===rate).reduce((n,r)=>n+r.totalProcessingMs,0)/corpus.clips.length}]));
const report={manifest,corpus:{clips:corpus.clips.length,byKind:corpus.clips.reduce((a:any,x:any)=>(a[x.kind]=(a[x.kind]??0)+1,a),{}),annotationRules:corpus.annotationRules},runs,byRate,note:"Descriptive primitive evaluation only; no fall score or alert is produced."};
if(process.env.BENCHMARK_OUTPUT)await writeFile(process.env.BENCHMARK_OUTPUT,JSON.stringify(report,null,2)+"\n");
else console.log(JSON.stringify(report,null,2));
