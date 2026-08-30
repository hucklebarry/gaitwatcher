# External evaluation datasets

External media is benchmark-only; GaitWatcher does not train or fine-tune models. `data/external/` is Git-ignored.

## UR Fall Detection Dataset (URFD)

- Official project/source: University of Rzeszów fall-detection dataset; obtain through its published project page or authorized mirror.
- Expected path: `data/external/urfd/`.
- Contents: staged fall and activities-of-daily-living video/sensor sequences.
- Mapping: directories named `fall-*` map to `floor_level`; ADL sequences map to `unknown` because they do not reliably distinguish standing versus sitting.
- Restrictions: CC BY-NC-SA 4.0; permitted here only for local non-commercial evaluation/research. Commercial use requires contacting the authors.
- Downloaded automatically: **yes**, on 2026-08-30, from the official University of Rzeszów link: one RGB archive (`fall-01-cam0-rgb.zip`, 55 MB) plus the official `urfall-cam0-falls.csv` annotations (228 KB).
- Preparation: `python3 scripts/prepare-urfd-subset.py` extracts up to 12 individually annotated ground-pose stills to `data/external/urfd/benchmark/floor_level/`. Only CSV label `1` is mapped to `floor_level`; `0` (transition) and `-1` (not lying) are excluded. This is not a fall benchmark and provides no standing/sitting labels.
- Run: `BENCHMARK_ROOT=data/external/urfd/benchmark npm run benchmark`.

UP-Fall, Le2i, and CASIA-B are not adapters yet. Their access and licensing vary; CASIA-B commonly requires registration. Do not bypass those controls. These datasets feature staged or research-subject events and are not representative evidence for elderly real-world falls.

## Other candidates assessed on 2026-08-30

### UP-Fall

The original UP-Fall publication describes a public 812 GB consolidated dataset (and a 171 GB feature dataset), recorded with 17 healthy young adults. The official project URL cited by the paper is no longer a practical automated download path in this environment, and the complete dataset is far beyond the scope of this local evaluation. It was not downloaded. A third-party Zenodo collection lists a 3.2 GB derivative; that is not treated as an official UP-Fall distribution here.

### Le2i / ImVia Fall Detection Dataset

The original CNRS/ImVia source is the appropriate authority, but its current access/licensing terms were not available as a clear authorized automated download. A Kaggle mirror lists an unknown license and a 17.44 GB payload, so it was not used. The 9.1 GB Zenodo derivative is likewise not substituted for official authorization. Obtain the original source and written terms manually before adding an adapter.
