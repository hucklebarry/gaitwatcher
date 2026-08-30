from pose import Landmark,PoseResult,classify_frame,aggregate,normalize_landmarks
from safety_primitives import classify_upper_body,aggregate_safety
def pose(state):
    y={"standing":(.2,.5,.9),"sitting":(.3,.6,.68),"floor_level":(.45,.5,.55)}[state];w=.8 if state=="floor_level" else .2
    p={n:Landmark(.5+(-w/2 if n.startswith("left") else w/2),v,.95) for n,v in {"leftShoulder":y[0],"rightShoulder":y[0],"leftHip":y[1],"rightHip":y[1],"leftKnee":(y[1]+y[2])/2,"rightKnee":(y[1]+y[2])/2,"leftAnkle":y[2],"rightAnkle":y[2]}.items()};return PoseResult(p,.9)
def test_normalizes_owned_landmarks(): assert normalize_landmarks(pose("standing").landmarks)["leftHip"]["x"] >= 0
def test_missing_pose_unknown(): assert classify_frame(None)[0]=="unknown"
def test_body_states():
    assert classify_frame(pose("standing"))[0]=="standing"
    assert classify_frame(pose("sitting"))[0]=="sitting"
    assert classify_frame(pose("floor_level"))[0]=="floor_level"
def test_contradictory_aggregation_unknown(): assert aggregate([("standing",.9),("sitting",.9)],2,{"minimum_frame_agreement":.75})[0]=="unknown"
def test_upper_body_diagnostic_needs_confident_torso():
 assert classify_upper_body(None)[0]=="unknown"
def test_drop_candidate_is_diagnostic_and_requires_a_torso_time_series():
 first=pose("standing")
 moved={**first.landmarks,"leftShoulder":Landmark(.4,.55,.95),"rightShoulder":Landmark(.6,.55,.95),"leftHip":Landmark(.4,.85,.95),"rightHip":Landmark(.6,.85,.95)}
 assert aggregate_safety([first,PoseResult(moved,.9)])["primitive"]=="rapid_vertical_drop_candidate"
