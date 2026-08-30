from pathlib import Path
from datasets import UrfdAdapter
def test_missing_dataset_is_empty(tmp_path): assert UrfdAdapter(tmp_path/"missing").samples()==[]
def test_urfd_mapping(tmp_path):
    f=tmp_path/"fall-01"/"a.avi";f.parent.mkdir();f.touch();assert UrfdAdapter(tmp_path).samples()[0].expected_label=="floor_level"
