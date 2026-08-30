"""Prepare a small, evaluation-only URFD still-image subset from official annotations."""
from __future__ import annotations
import csv, shutil, zipfile
from pathlib import Path
root=Path("data/external/urfd"); archive=root/"fall-01-cam0-rgb.zip"; labels=root/"urfall-cam0-falls.csv"; out=root/"benchmark/floor_level"
out.mkdir(parents=True,exist_ok=True); selected=[]
with labels.open() as f:
    for row in csv.reader(f):
        if row[0]=="fall-01" and row[2]=="1": selected.append(int(row[1]))
# Evenly sample no more than 12 independent ground-pose frames; transitions (0) and non-ground (-1) never enter.
stride=max(1,len(selected)//12); selected=selected[::stride][:12]
with zipfile.ZipFile(archive) as z:
    for frame in selected:
        name=f"fall-01-cam0-rgb/fall-01-cam0-rgb-{frame:03d}.png"; target=out/Path(name).name
        with z.open(name) as src, target.open("wb") as dst: shutil.copyfileobj(src,dst)
print(f"prepared {len(selected)} URFD floor_level frames in {out}")
