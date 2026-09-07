from person_detector import BoundingBox,PersonDetection,DetectionFrame
from tracking import iou,associate
from box_primitives import features,diagnostics

def d(x,y,w,h,c=.9):return PersonDetection(BoundingBox(x,y,w,h),c)
def frames(*groups):return [DetectionFrame(n,float(n),list(group)) for n,group in enumerate(groups)]
def test_normalized_box_and_multiple_detections():
 result=associate(frames([d(.1,.1,.2,.5),d(.6,.2,.2,.4)]));assert len(result)==2;assert result[0].detection.bounding_box.x==.1
def test_iou_association_and_track_loss():
 kept=associate(frames([d(.1,.1,.2,.5)],[d(.12,.12,.2,.5)]));assert {p.track_id for p in kept}=={1};lost=associate(frames([d(.1,.1,.2,.5)],[],[],[d(.1,.1,.2,.5)]));assert len({p.track_id for p in lost})==2
def test_features_and_rapid_downward_diagnostic():
 points=associate(frames([d(.2,.1,.2,.6)],[d(.2,.45,.5,.35)]));last=features(points[-1],points[0]);assert last["deltaCenterY"]>.1;assert "rapid_downward_motion_candidate" in diagnostics(points)[0]["primitives"]
def test_persistent_low_and_pose_independence():
 points=associate(frames([d(.2,.5,.5,.3)],[d(.2,.55,.5,.3)],[d(.2,.6,.5,.3)]));assert "persistent_low_position" in diagnostics(points)[0]["primitives"]
