"""Camera-relative box features and diagnostics. They never make a fall decision."""
from tracking import TrackPoint
def features(point:TrackPoint,previous:TrackPoint|None=None):
 b=point.detection.bounding_box;out={"aspectRatio":b.width/max(b.height,.001),"centerX":b.x+b.width/2,"centerY":b.y+b.height/2,"top":b.y,"bottom":b.y+b.height,"width":b.width,"height":b.height,"area":b.width*b.height,"bottomDistance":1-(b.y+b.height)}
 if previous:
  p=features(previous);dt=max(point.timestamp_s-previous.timestamp_s,.001)
  out.update({"deltaCenterY":out["centerY"]-p["centerY"],"deltaHeight":out["height"]-p["height"],"deltaWidth":out["width"]-p["width"],"deltaAspectRatio":out["aspectRatio"]-p["aspectRatio"],"deltaArea":out["area"]-p["area"],"verticalVelocityProxy":(out["centerY"]-p["centerY"])/dt})
 return out
def diagnostics(points:list[TrackPoint],config=None):
 c={"horizontalAspectRatio":1.15,"lowCenterY":.65,"rapidDownDeltaY":.15,"persistentSamples":3,"persistentFraction":.75,**(config or {})};by={}
 for p in points:by.setdefault(p.track_id,[]).append(p)
 out=[]
 for track_id,track in by.items():
  values=[features(p,track[n-1] if n else None) for n,p in enumerate(track)];last=values[-1];primitives=[]
  if last["aspectRatio"]>=c["horizontalAspectRatio"]:primitives.append("horizontal_box")
  else:primitives.append("upright_box")
  if any(v.get("deltaCenterY",0)>=c["rapidDownDeltaY"] for v in values[1:]):primitives.append("rapid_downward_motion_candidate")
  low=[v["centerY"]>=c["lowCenterY"] for v in values]
  tail=low[-c["persistentSamples"]:]
  if len(tail)>=c["persistentSamples"] and sum(tail)/len(tail)>=c["persistentFraction"]:primitives.append("persistent_low_position")
  out.append({"trackId":track_id,"frames":len(track),"features":last,"primitives":primitives})
 return out
