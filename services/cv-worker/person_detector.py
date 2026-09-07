"""Owned, CPU-only person detection contract; no vendor result leaves this module."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os,time

@dataclass(frozen=True)
class BoundingBox: x:float;y:float;width:float;height:float
@dataclass(frozen=True)
class PersonDetection: bounding_box:BoundingBox;confidence:float
@dataclass(frozen=True)
class DetectionFrame: index:int;timestamp_s:float;detections:list[PersonDetection]
@dataclass(frozen=True)
class DetectionRun: frames:list[DetectionFrame];frames_decoded:int;frames_sampled:int;inference_ms:int;error:str|None=None

class YoloPersonDetector:
 """YOLOv8n COCO person detector, instantiated once per worker process."""
 def __init__(self):
  started=time.perf_counter();from ultralytics import YOLO
  self.model_path=os.getenv("YOLO_PERSON_MODEL","yolov8n.pt");self._model=YOLO(self.model_path)
  self.initialization_ms=int((time.perf_counter()-started)*1000);self.model_name="YOLOv8n (COCO person class)";self.model_artifact_bytes=Path(self.model_path).stat().st_size if Path(self.model_path).exists() else None
 def infer(self,image):
  result=self._model(image,verbose=False,device="cpu")[0];h,w=image.shape[:2];out=[]
  if result.boxes is None:return out
  for box,confidence,klass in zip(result.boxes.xyxy.tolist(),result.boxes.conf.tolist(),result.boxes.cls.tolist()):
   if int(klass)!=0:continue
   x1,y1,x2,y2=box;x=max(0,min(1,x1/w));y=max(0,min(1,y1/h));right=max(x,min(1,x2/w));bottom=max(y,min(1,y2/h))
   out.append(PersonDetection(BoundingBox(x,y,right-x,bottom-y),float(confidence)))
  return out
 def detect_samples(self,path:str,sample_fps:float)->DetectionRun:
  import cv2
  started=time.perf_counter();frames=[];decoded=sampled=0
  try:
   if Path(path).suffix.lower() in {".png",".jpg",".jpeg",".webp"}:
    image=cv2.imread(path);decoded=1
    if image is None:return DetectionRun([],decoded,0,0,"image_decode_failed")
    sampled=1;frames.append(DetectionFrame(0,0,self.infer(image)))
   else:
    cap=cv2.VideoCapture(path);fps=cap.get(cv2.CAP_PROP_FPS) or 30;stride=max(1,round(fps/max(sample_fps,.1)));index=0
    while True:
     ok,image=cap.read()
     if not ok:break
     decoded+=1
     if index%stride==0:sampled+=1;frames.append(DetectionFrame(index,index/fps,self.infer(image)))
     index+=1
    cap.release()
   return DetectionRun(frames,decoded,sampled,int((time.perf_counter()-started)*1000))
  except Exception as exc:return DetectionRun(frames,decoded,sampled,int((time.perf_counter()-started)*1000),type(exc).__name__)
