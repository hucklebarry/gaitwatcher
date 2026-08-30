"""Diagnostic-only torso safety primitives. They are not falls and never create alerts."""
from pose import Landmark,PoseResult
UPPER=("leftShoulder","rightShoulder","leftHip","rightHip")
def classify_upper_body(pose:PoseResult|None,min_visibility=.55):
 if not pose or any(n not in pose.landmarks or pose.landmarks[n].visibility<min_visibility for n in UPPER):return "unknown",{"reasonCode":"upper_body_unavailable"}
 p=pose.landmarks;sy=(p["leftShoulder"].y+p["rightShoulder"].y)/2;hy=(p["leftHip"].y+p["rightHip"].y)/2;ys=[p[n].y for n in UPPER];xs=[p[n].x for n in UPPER];height=max(max(ys)-min(ys),.001);width=max(xs)-min(xs);center=(sy+hy)/2;e={"upperBodyWidthHeight":width/height,"upperBodyCenterY":center,"shoulderHipVerticalDelta":hy-sy}
 # Conservative: horizontal envelope plus low-in-frame evidence, never called a fall.
 if width/height>=1.5 and center>=.55:return "low_horizontal",e
 if hy-sy>=.12:return "upright",e
 return "unknown",{**e,"reasonCode":"upper_body_geometry_inconclusive"}
def aggregate_safety(samples):
 classified=[classify_upper_body(s) for s in samples];states=[state for state,_ in classified]
 low=states.count("low_horizontal")
 # A substantial down-frame torso shift from an initially upright torso is
 # diagnostic only. It deliberately does not infer a fall or produce an alert.
 centers=[e["upperBodyCenterY"] for state,e in classified if state!="unknown" and "upperBodyCenterY" in e]
 if len(centers)>=2 and states[0]=="upright" and centers[-1]-centers[0]>=.25:return {"primitive":"rapid_vertical_drop_candidate","frameStates":states,"torsoCenterDeltaY":centers[-1]-centers[0]}
 if len(samples)>=3 and low/len(samples)>=.75:return {"primitive":"persistent_low_state","frameStates":states}
 return {"primitive":states[0] if len(states)==1 else "unknown","frameStates":states}
