"""Small explainable within-clip IoU association, not identity or cross-room tracking."""
from dataclasses import dataclass
from person_detector import BoundingBox,DetectionFrame,PersonDetection
def iou(a:BoundingBox,b:BoundingBox):
 x=max(a.x,b.x);y=max(a.y,b.y);r=min(a.x+a.width,b.x+b.width);bottom=min(a.y+a.height,b.y+b.height);inter=max(0,r-x)*max(0,bottom-y);union=a.width*a.height+b.width*b.height-inter;return inter/union if union else 0
@dataclass(frozen=True)
class TrackPoint: track_id:int;frame_index:int;timestamp_s:float;detection:PersonDetection
def associate(frames:list[DetectionFrame],minimum_iou=.05,max_missing_frames=1):
 next_id=1;active={};points=[]
 # `frame.index` is a source-frame index and may jump when sampling. Association
 # limits therefore use sampled-frame order, not the raw index difference.
 for sample_order,frame in enumerate(frames):
  candidates=[]
  for tid,(detection,last_order) in active.items():
   if sample_order-last_order<=max_missing_frames+1:
    for n,current in enumerate(frame.detections):candidates.append((iou(detection.bounding_box,current.bounding_box),tid,n))
  matched_tracks=set();matched_detections=set()
  for score,tid,n in sorted(candidates,reverse=True):
   if score<minimum_iou or tid in matched_tracks or n in matched_detections:continue
   matched_tracks.add(tid);matched_detections.add(n);active[tid]=(frame.detections[n],sample_order);points.append(TrackPoint(tid,frame.index,frame.timestamp_s,frame.detections[n]))
  for n,detection in enumerate(frame.detections):
   if n not in matched_detections:active[next_id]=(detection,sample_order);points.append(TrackPoint(next_id,frame.index,frame.timestamp_s,detection));next_id+=1
  active={tid:value for tid,value in active.items() if sample_order-value[1]<=max_missing_frames+1}
 return points
