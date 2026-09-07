# External temporal corpus assessment — frozen Prompt 2.4 baseline

This assessment is for evaluation only. No external data is used for training, fine-tuning, threshold selection, or shipment with the product.

## Candidates assessed

| Candidate | Official/authorized source | Useful labels/media | Access and terms | Size | Decision |
| --- | --- | --- | --- | --- | --- |
| HMDB51 | Serre Lab’s official Hugging Face organization | `sit`, `stand`, `walk`, and `fall_floor`; selected clips require individual review | Public, ungated Serre Lab release under CC-BY-4.0. Dataset is evaluation/reference material only and is not shipped with the product. | 2.0 GB original archive; 4.14 GB repository including stabilized variant | Downloaded: only `hmdb51_org.rar`; extracted only the four selected class archives. |
| SPHERE House scripted dataset v2.0 | University of Bristol DOI | Excellent residential labels: walking, bent, kneel, lie, sit, squat, stand, and posture transitions | CC-BY data release, but public records are RGB-D tracking/annotation CSVs rather than shareable RGB clips. | Long sessions, CSV-centric | Not downloaded for this video benchmark: it cannot exercise the current RGB detector/tracker pipeline. It is a strong future source if a compatible authorized visual release becomes available. |
| UCF101 | University of Central Florida / CRCV | `BodyWeightSquats`, `Lunges`, and `WalkingWithDog` are only loose proxies; not household ADLs | Official archive is reachable, but no explicit commercial license is published on the download page. It is sourced from YouTube, so product reuse requires separate rights analysis. | 6,932,971,618 bytes (6.46 GiB) for whole archive | Not downloaded: oversized all-or-nothing archive, insufficiently targeted, and no clear product-use permission. No mirrors or selective unofficial downloaders used. |

## Corpus rule

External media may be added only under `data/external/<dataset>/raw` and `prepared`; it remains Git-ignored. Each prepared clip must enter `fixtures/temporal/manifest.json` with original file name, source, license/restriction, activity, viewpoint if known, annotation confidence, and manual-review state. A class name alone is not a primitive label.

## Current result

The public Serre Lab HMDB51 release supplied a 32-clip deterministic subset: eight clips each from `sit`, `stand`, `walk`, and `fall_floor`. The raw archive, selected class archives, videos, and generated manifest are all under `data/external/hmdb51/`. `scripts/prepare-hmdb51-subset.py` regenerates `prepared/temporal-manifest.json`; run `TEMPORAL_MANIFEST=data/external/hmdb51/prepared/temporal-manifest.json npm run benchmark:temporal` for the frozen 1/2/5 FPS evaluation.

Every HMDB entry deliberately has `manual_reviewed: false` and `annotationConfidence: class_label_only`. The action class is a coarse selection hint, not primitive ground truth. Visual review must exclude clips with irrelevant action, camera motion, multiple people, or unusable visibility before any quantitative fall-like-versus-lookalike claim is made.

## Manual next steps

1. Visually review the prepared HMDB51 subset and set `manual_reviewed: true` only for usable clips, with clip-specific annotations.
2. Ask SPHERE maintainers whether any authorized RGB or RGB-D video release exists beyond the published tracking CSVs.
3. Add consented household clips annotated with the existing manifest contract for quick sitting, intentional lying, kneeling/bending, floor activity, partial exits, TV/person, posters, and pets.
