"""GaitWatcher-owned pose contract and conservative, explainable body-state rules."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import time
import os
BODY_STATES=("standing","sitting","floor_level","unknown")
DEFAULT_THRESHOLDS={"minimum_landmark_visibility":.55,"minimum_pose_confidence":.55,"floor_width_height_ratio":1.15,"standing_ankle_hip_ratio":.80,"sitting_ankle_hip_ratio":.35,"minimum_frame_agreement":.60,"minimum_valid_pose_fraction":.30}
REQUIRED=("leftShoulder","rightShoulder","leftHip","rightHip","leftKnee","rightKnee","leftAnkle","rightAnkle")
GROUPS={"shoulders":("leftShoulder","rightShoulder"),"hips":("leftHip","rightHip"),"knees":("leftKnee","rightKnee"),"ankles":("leftAnkle","rightAnkle")}
@dataclass(frozen=True)
class Landmark: x:float;y:float;visibility:float
@dataclass(frozen=True)
class PoseResult: landmarks:dict[str,Landmark];confidence:float
@dataclass(frozen=True)
class PoseRun: samples:list[PoseResult];frames_decoded:int;frames_sampled:int;no_pose_frames:int;decode_ms:int;error:str|None=None
class PoseEstimator(Protocol):
 def estimate_samples(self,media_path:str,sample_fps:float)->PoseRun: ...
def normalize_landmarks(points:dict[str,Landmark])->dict[str,dict[str,float]]:return {n:{"x":p.x,"y":p.y,"visibility":p.visibility} for n,p in points.items()}
class MediaPipePoseEstimator:
 """One BlazePose Lite model per worker process—not per clip or frame."""
 def __init__(self):
  started=time.perf_counter();import mediapipe as mp;self._mp=mp
  self._ids={"leftShoulder":mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,"rightShoulder":mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER,"leftHip":mp.solutions.pose.PoseLandmark.LEFT_HIP,"rightHip":mp.solutions.pose.PoseLandmark.RIGHT_HIP,"leftKnee":mp.solutions.pose.PoseLandmark.LEFT_KNEE,"rightKnee":mp.solutions.pose.PoseLandmark.RIGHT_KNEE,"leftAnkle":mp.solutions.pose.PoseLandmark.LEFT_ANKLE,"rightAnkle":mp.solutions.pose.PoseLandmark.RIGHT_ANKLE,"nose":mp.solutions.pose.PoseLandmark.NOSE}
  self._model=mp.solutions.pose.Pose(static_image_mode=False,model_complexity=0,min_detection_confidence=.5,min_tracking_confidence=.5);self.initialization_ms=int((time.perf_counter()-started)*1000)
 def _infer(self,image):
  import cv2
  r=self._model.process(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
  if not r.pose_landmarks:return None
  p=r.pose_landmarks.landmark;pts={n:Landmark(p[i].x,p[i].y,p[i].visibility) for n,i in self._ids.items()};return PoseResult(pts,min(v.visibility for v in pts.values()))
 def estimate_samples(self,path:str,sample_fps:float)->PoseRun:
  import cv2
  started=time.perf_counter();samples=[];decoded=sampled=no_pose=0
  try:
   # VideoCapture is not reliable for still images in all OpenCV builds; decode them directly.
   if Path(path).suffix.lower() in {".png",".jpg",".jpeg",".webp"}:
    img=cv2.imread(path);decoded=1
    if img is None:return PoseRun([],decoded,0,0,int((time.perf_counter()-started)*1000),"image_decode_failed")
    sampled=1;r=self._infer(img)
    if r:samples.append(r)
    else:no_pose=1
   else:
    cap=cv2.VideoCapture(path);fps=cap.get(cv2.CAP_PROP_FPS) or 30;stride=max(1,round(fps/max(sample_fps,.1)));frame=0
    while True:
     ok,img=cap.read()
     if not ok:break
     decoded+=1
     if frame%stride==0:
      sampled+=1;r=self._infer(img)
      if r:samples.append(r)
      else:no_pose+=1
     frame+=1
    cap.release()
   return PoseRun(samples,decoded,sampled,no_pose,int((time.perf_counter()-started)*1000))
  except Exception as exc:return PoseRun(samples,decoded,sampled,no_pose,int((time.perf_counter()-started)*1000),type(exc).__name__)
class YoloPoseEstimator:
 """YOLOv8n-pose adapter; COCO keypoint confidences become owned landmark visibility."""
 def __init__(self):
  started=time.perf_counter();from ultralytics import YOLO
  model_path=os.getenv("YOLO_POSE_MODEL","yolov8n-pose.pt")
  self._model=YOLO(model_path);self.initialization_ms=int((time.perf_counter()-started)*1000);self.model_name="YOLOv8n-pose";self.model_artifact_bytes=Path(model_path).stat().st_size if Path(model_path).exists() else None
 def _infer(self,image):
  r=self._model(image,verbose=False,device="cpu")[0]
  if r.keypoints is None or len(r.keypoints)==0:return None
  person=int(r.boxes.conf.argmax().item()) if r.boxes is not None else 0;xyn=r.keypoints.xyn[person].tolist();conf=r.keypoints.conf[person].tolist() if r.keypoints.conf is not None else [0.0]*len(xyn)
  ids={"nose":0,"leftShoulder":5,"rightShoulder":6,"leftHip":11,"rightHip":12,"leftKnee":13,"rightKnee":14,"leftAnkle":15,"rightAnkle":16};pts={n:Landmark(float(xyn[i][0]),float(xyn[i][1]),float(conf[i])) for n,i in ids.items()};return PoseResult(pts,sum(p.visibility for p in pts.values())/len(pts))
 def estimate_samples(self,path:str,sample_fps:float)->PoseRun:
  import cv2
  started=time.perf_counter();samples=[];decoded=sampled=no_pose=0
  try:
   if Path(path).suffix.lower() in {".png",".jpg",".jpeg",".webp"}:
    img=cv2.imread(path);decoded=1
    if img is None:return PoseRun([],1,0,0,int((time.perf_counter()-started)*1000),"image_decode_failed")
    sampled=1;r=self._infer(img);samples.extend([r] if r else []);no_pose=0 if r else 1
   else:
    cap=cv2.VideoCapture(path);fps=cap.get(cv2.CAP_PROP_FPS) or 30;stride=max(1,round(fps/max(sample_fps,.1)));frame=0
    while True:
     ok,img=cap.read()
     if not ok:break
     decoded+=1
     if frame%stride==0:
      sampled+=1;r=self._infer(img);samples.extend([r] if r else []);no_pose+=0 if r else 1
     frame+=1
    cap.release()
   return PoseRun(samples,decoded,sampled,no_pose,int((time.perf_counter()-started)*1000))
  except Exception as exc:return PoseRun(samples,decoded,sampled,no_pose,int((time.perf_counter()-started)*1000),type(exc).__name__)
def create_pose_estimator(name):
 if name=="mediapipe":return MediaPipePoseEstimator()
 if name=="yolo":return YoloPoseEstimator()
 raise ValueError(f"unsupported pose backend: {name}")
def _mean(p,names,axis):return sum(getattr(p[n],axis) for n in names)/len(names)
def classify_frame(pose:PoseResult|None,t:dict[str,float]|None=None):
 t={**DEFAULT_THRESHOLDS,**(t or {})}
 if not pose:return "unknown",0,{"reasonCode":"no_pose_returned"}
 missing=[n for n in REQUIRED if n not in pose.landmarks]
 if missing:return "unknown",0,{"reasonCode":"insufficient_required_landmarks","missing":",".join(missing)}
 low=[n for n in REQUIRED if pose.landmarks[n].visibility<t["minimum_landmark_visibility"]]
 if pose.confidence<t["minimum_pose_confidence"] or low:return "unknown",0,{"reasonCode":"landmark_visibility_or_confidence_below_threshold","lowVisibility":",".join(low)}
 p=pose.landmarks;torso=max(_mean(p,GROUPS["hips"],"y")-_mean(p,GROUPS["shoulders"],"y"),.001);leg=max(_mean(p,GROUPS["ankles"],"y")-_mean(p,GROUPS["hips"],"y"),0);xs=[x.x for x in p.values()];ys=[x.y for x in p.values()];ratio=(max(xs)-min(xs))/max(max(ys)-min(ys),.001);leg_ratio=leg/torso;e={"bboxWidthHeightRatio":ratio,"ankleHipOverTorso":leg_ratio}
 if ratio>=t["floor_width_height_ratio"]:return "floor_level",min(.95,pose.confidence*ratio/t["floor_width_height_ratio"]),e
 if leg_ratio>=t["standing_ankle_hip_ratio"]:return "standing",pose.confidence,e
 if leg_ratio<=t["sitting_ankle_hip_ratio"]:return "sitting",pose.confidence,e
 return "unknown",0,{**e,"reasonCode":"geometric_body_state_evidence_insufficient"}
def aggregate(frames,sampled_frames,t=None):
 t={**DEFAULT_THRESHOLDS,**(t or {})};valid=[x for x in frames if x[0]!="unknown"]
 if not valid:return "unknown",0,"no_frame_reached_body_state_geometry"
 if len(valid)/max(sampled_frames,1)<t["minimum_valid_pose_fraction"]:return "unknown",0,"aggregation_valid_pose_fraction_insufficient"
 winner=max(BODY_STATES[:-1],key=lambda s:sum(state==s for state,_ in valid));scores=[c for state,c in valid if state==winner];agreement=len(scores)/len(valid)
 return (winner,agreement*sum(scores)/len(scores),"accepted") if agreement>=t["minimum_frame_agreement"] else ("unknown",0,"aggregation_temporal_disagreement")
def group_visibility(samples):
 out={}
 for group,names in GROUPS.items():
  values=[sample.landmarks[n].visibility for sample in samples for n in names if n in sample.landmarks]
  out[group]={"usable":len(values)==len(samples)*len(names) and all(v>=DEFAULT_THRESHOLDS["minimum_landmark_visibility"] for v in values),"averageVisibility":sum(values)/len(values) if values else None,"minVisibility":min(values) if values else None}
 return out
