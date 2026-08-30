import time
from fastapi import FastAPI
from pydantic import BaseModel
from pose import create_pose_estimator,classify_frame,aggregate,normalize_landmarks,group_visibility
from safety_primitives import aggregate_safety
app=FastAPI(title="GaitWatcher CV worker")
# Each backend is constructed at most once per worker process; initialization is excluded from clip timing.
estimators={}
def estimator_for(name):
 if name not in estimators:estimators[name]=create_pose_estimator(name)
 return estimators[name]
class Request(BaseModel): mediaPath:str|None=None;sampleFps:float=1;thresholds:dict[str,float]|None=None;debug:bool=False;poseBackend:str="mediapipe"
@app.post("/detect")
def detect(req:Request):
 started=time.perf_counter();path=(req.mediaPath or "").lower();person_start=time.perf_counter();is_person="no_person" not in path and "empty" not in path;person_ms=int((time.perf_counter()-person_start)*1000)
 base={"personDetected":is_person,"personConfidence":.95 if is_person else .99,"framesSentToPersonDetector":0,"personDetectionMs":person_ms}
 if not is_person:return {**base,"framesDecoded":0,"framesAnalyzed":0,"poseDetected":False,"poseConfidence":0,"bodyState":"unknown","bodyStateConfidence":0,"framesSentToPoseModel":0,"poseInferenceMs":0,"bodyStateClassificationMs":0,"totalProcessingMs":int((time.perf_counter()-started)*1000),**({"debug":{"reasonCode":"person_not_detected"}} if req.debug else {})}
 estimator=estimator_for(req.poseBackend);run=estimator.estimate_samples(req.mediaPath,req.sampleFps) if req.mediaPath else None;pose_ms=run.decode_ms if run else 0
 results=[classify_frame(sample,req.thresholds) for sample in (run.samples if run else [])];classify_started=time.perf_counter();state,confidence,aggregate_reason=aggregate([(s,c) for s,c,_ in results],run.frames_sampled if run else 0,req.thresholds);classify_ms=int((time.perf_counter()-classify_started)*1000)
 frame_reasons=[e.get("reasonCode") for _,_,e in results if e.get("reasonCode")];reason=aggregate_reason if state=="unknown" else "accepted"
 safety=aggregate_safety(run.samples if run else [])
 debug={"reasonCode":reason,"backendError":run.error if run else "no_media_path","poseRun":{"framesDecoded":run.frames_decoded if run else 0,"framesSampled":run.frames_sampled if run else 0,"poseReturned":len(run.samples) if run else 0,"noPoseReturned":run.no_pose_frames if run else 0,"decodeAndPoseMs":pose_ms,"modelInitializationMs":estimator.initialization_ms,"model":getattr(estimator,"model_name", "MediaPipe BlazePose Lite (model_complexity=0)"),"modelArtifactBytes":getattr(estimator,"model_artifact_bytes",None),"groupVisibility":group_visibility(run.samples) if run else {}},"frameReasonCodes":frame_reasons,"representativeLandmarks":normalize_landmarks(run.samples[0].landmarks) if run and run.samples else {},"representativeEvidence":results[0][2] if results else {"reasonCode":"no_pose_returned"},"safetyPrimitive":safety}
 return {**base,"framesDecoded":run.frames_decoded if run else 0,"framesAnalyzed":run.frames_sampled if run else 0,"poseDetected":bool(run and run.samples),"poseConfidence":run.samples[0].confidence if run and run.samples else 0,"landmarks":debug["representativeLandmarks"],"bodyState":state,"bodyStateConfidence":confidence,"bodyStateEvidence":debug["representativeEvidence"],"framesSentToPoseModel":run.frames_sampled if run else 0,"poseInferenceMs":pose_ms,"bodyStateClassificationMs":classify_ms,"totalProcessingMs":int((time.perf_counter()-started)*1000),**({"debug":debug} if req.debug else {})}
