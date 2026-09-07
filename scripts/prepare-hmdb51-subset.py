"""Create a small, frozen HMDB51 evaluation manifest; never train or tune on it."""
from __future__ import annotations
import json
from pathlib import Path

root=Path("data/external/hmdb51/prepared")
classes={
 "sit":("sit_down_or_sitting","non_fall_lookalike",{"rapid_downward_motion_candidate":"viewpoint_dependent","horizontal_box":"not_expected","persistent_low_position":"not_expected"}),
 "stand":("stand_up_or_standing","non_fall_lookalike",{"rapid_downward_motion_candidate":"not_expected","horizontal_box":"not_expected","persistent_low_position":"not_expected"}),
 "walk":("walking","non_fall_lookalike",{"rapid_downward_motion_candidate":"not_expected","horizontal_box":"not_expected","persistent_low_position":"not_expected"}),
 "fall_floor":("staged_fall_reference","fall_like",{"rapid_downward_motion_candidate":"expected","horizontal_box":"viewpoint_dependent","persistent_low_position":"viewpoint_dependent"}),
}
clips=[]
for label,(activity,kind,expectations) in classes.items():
 files=sorted((root/label).rglob("*.avi"));selected=[files[round(i*(len(files)-1)/7)] for i in range(8)]
 for path in selected:
  clips.append({"id":f"hmdb51_{label}_{path.stem}","path":str(path),"dataset":"HMDB51","originalSequence":path.name,"source":"https://huggingface.co/datasets/Serrelab/hmdb51","licenseRestriction":"CC-BY-4.0; evaluation/reference only, not shipped with product","activity":activity,"kind":kind,"viewpoint":"unknown","annotationConfidence":"class_label_only","manual_reviewed":False,"expectations":expectations})
out=root/"temporal-manifest.json";out.write_text(json.dumps({"annotationRules":"Frozen baseline. Dataset class labels define coarse selection only; each clip requires visual review before semantic claims.","clips":clips},indent=2)+"\n")
print(f"wrote {len(clips)} clips to {out}")
