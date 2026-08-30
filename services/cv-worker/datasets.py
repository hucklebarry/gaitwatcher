"""Small benchmark-only adapters; they never train or alter the pose model."""
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True)
class EvaluationSample: media_path:Path; expected_label:str; dataset_name:str; sequence_id:str
class UrfdAdapter:
    """URFD convention: sequences under fall-* or activities-of-daily-living-* directories."""
    def __init__(self,root:Path):self.root=root
    def samples(self):
        if not self.root.exists():return []
        out=[]
        for path in self.root.rglob("*"):
            if path.suffix.lower() not in {".avi",".mp4",".mts"}:continue
            name=str(path.parent).lower();label="floor_level" if "fall" in name else "unknown"
            out.append(EvaluationSample(path,label,"urfd",path.parent.name))
        return out
