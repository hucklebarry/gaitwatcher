import time
from fastapi import FastAPI
from pydantic import BaseModel
from pose import create_pose_estimator,classify_frame,aggregate,normalize_landmarks,group_visibility
from safety_primitives import aggregate_safety
from person_detector import YoloPersonDetector
from tracking import associate
from box_primitives import diagnostics

app=FastAPI(title="GaitWatcher CV worker")
estimators={};person_detector=None
def estimator_for(name):
 if name not in estimators:estimators[name]=create_pose_estimator(name)
 return estimators[name]
def detector_for():
 global person_detector
 if person_detector is None:person_detector=YoloPersonDetector()
 return person_detector
class Request(BaseModel): mediaPath:str|None=None;sampleFps:float=1;thresholds:dict[str,float]|None=None;debug:bool=False;poseBackend:str="mediapipe";invokePose:bool=True
@app.post("/detect")
def detect(req:Request):
 started=time.perf_counter()
 if not req.mediaPath:return {"personDetected":False,"personConfidence":0,"framesDecoded":0,"framesAnalyzed":0,"framesSentToPersonDetector":0,"framesSentToPoseModel":0,"personDetectionMs":0,"poseInferenceMs":0,"bodyStateClassificationMs":0,"totalProcessingMs":0,"poseDetected":False,"poseConfidence":0,"bodyState":"unknown","bodyStateConfidence":0}
 detector=detector_for();detected=detector.detect_samples(req.mediaPath,req.sampleFps);frames_with_people=sum(bool(f.detections) for f in detected.frames);all_detections=[d for f in detected.frames for d in f.detections];tracks=associate(detected.frames);box=diagnostics(tracks)
 base={"personDetected":bool(all_detections),"personConfidence":max((d.confidence for d in all_detections),default=0),"framesDecoded":detected.frames_decoded,"framesAnalyzed":detected.frames_sampled,"framesSentToPersonDetector":detected.frames_sampled,"personDetectionMs":detected.inference_ms,"personFrames":frames_with_people,"poseCallsAvoided":detected.frames_sampled if not all_detections else 0,"detectionsPerFrame":[len(f.detections) for f in detected.frames]}
 person_debug={"model":detector.model_name,"modelInitializationMs":detector.initialization_ms,"modelArtifactBytes":detector.model_artifact_bytes,"error":detected.error,"frames":[{"index":f.index,"timestampS":f.timestamp_s,"detections":[{"boundingBox":d.bounding_box.__dict__,"confidence":d.confidence} for d in f.detections]} for f in detected.frames],"tracks":[{"trackId":p.track_id,"frameIndex":p.frame_index,"timestampS":p.timestamp_s,"boundingBox":p.detection.bounding_box.__dict__} for p in tracks],"boxDiagnostics":box}
 if not all_detections or not req.invokePose:return {**base,"poseDetected":False,"poseConfidence":0,"bodyState":"unknown","bodyStateConfidence":0,"framesSentToPoseModel":0,"poseInferenceMs":0,"bodyStateClassificationMs":0,"totalProcessingMs":int((time.perf_counter()-started)*1000),**({"debug":{"reasonCode":"person_not_detected" if not all_detections else "pose_not_requested","personRun":person_debug}} if req.debug else {})}
 estimator=estimator_for(req.poseBackend);run=estimator.estimate_samples(req.mediaPath,req.sampleFps);pose_ms=run.decode_ms;results=[classify_frame(sample,req.thresholds) for sample in run.samples];classify_started=time.perf_counter();state,confidence,aggregate_reason=aggregate([(s,c) for s,c,_ in results],run.frames_sampled,req.thresholds);classify_ms=int((time.perf_counter()-classify_started)*1000)
 frame_reasons=[e.get("reasonCode") for _,_,e in results if e.get("reasonCode")];reason=aggregate_reason if state=="unknown" else "accepted";safety=aggregate_safety(run.samples)
 debug={"reasonCode":reason,"personRun":person_debug,"poseRun":{"framesDecoded":run.frames_decoded,"framesSampled":run.frames_sampled,"poseReturned":len(run.samples),"noPoseReturned":run.no_pose_frames,"decodeAndPoseMs":pose_ms,"modelInitializationMs":estimator.initialization_ms,"model":getattr(estimator,"model_name","MediaPipe BlazePose Lite (model_complexity=0)"),"modelArtifactBytes":getattr(estimator,"model_artifact_bytes",None),"groupVisibility":group_visibility(run.samples)},"frameReasonCodes":frame_reasons,"representativeLandmarks":normalize_landmarks(run.samples[0].landmarks) if run.samples else {},"representativeEvidence":results[0][2] if results else {"reasonCode":"no_pose_returned"},"safetyPrimitive":safety}
 return {**base,"poseDetected":bool(run.samples),"poseConfidence":run.samples[0].confidence if run.samples else 0,"landmarks":debug["representativeLandmarks"],"bodyState":state,"bodyStateConfidence":confidence,"bodyStateEvidence":debug["representativeEvidence"],"framesSentToPoseModel":run.frames_sampled,"poseInferenceMs":pose_ms,"bodyStateClassificationMs":classify_ms,"totalProcessingMs":int((time.perf_counter()-started)*1000),**({"debug":debug} if req.debug else {})}
