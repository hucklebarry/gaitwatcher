# CV and perception findings

This document preserves the experimental conclusions behind the current perception strategy. It complements detailed method notes; it is not a claim of clinical validation.

## Current components

The CV worker has real YOLOv8n person detection; normalized, GaitWatcher-owned person bounding boxes; within-clip IoU tracking; pose adapters that normalize landmarks; MediaPipe BlazePose Lite as the CPU-oriented default; YOLOv8n-pose as an experimental alternate; conservative body-state aggregation; and debug-only temporal box and pose primitives. Raw media is temporary processing input; the application persists semantic evidence and measurements instead.

Tracking IDs are short-lived association IDs, not resident identity or cross-room identity. Person and pose model availability should not be mistaken for activity or fall accuracy.

## URFD pose result

On 12 low/oblique URFD floor-level frames, MediaPipe returned a pose on 4/12. Lower-body visibility was extremely weak, floor-level recall was 0%, and all or essentially all classifications were `unknown`. An initial approximately 332 ms measurement was partly bad model lifecycle: initializing BlazePose once per process brought pose/decode time to roughly 31–40 ms/frame in that environment.

YOLOv8n-pose returned poses on approximately 7/12, but did not materially improve floor-level classification and was materially slower, roughly 169 ms/frame in that benchmark. Therefore, do not switch the default to YOLO pose merely because it returns more poses. Both YOLO assets also require license review before proprietary deployment; see [pose backends](pose-backend-evaluation.md).

## Temporal person-box work

Real YOLOv8n person detection, bounding boxes, and short-term tracking were added. A staged URFD sequence produced some potentially useful camera-relative primitives: `upright_box`, `horizontal_box`, `rapid_downward_motion_candidate`, and `persistent_low_position`. These are diagnostic/debug evidence only; they do not create a fall observation, alert, or velocity measurement.

The HMDB51 exploratory corpus showed weak track continuity in heterogeneous movie/web footage. Raising sample rate improved detections and pose availability but did not solve track continuity. The available temporal primitives were not sufficiently discriminative for fall-like classification. HMDB is a stress test, not representative household deployment data; its preparation and manual-review limits are in [external temporal corpus assessment](external-temporal-corpus-assessment.md).

## Decision and prerequisites

**`floor_level != fall`**. Fall-like event detection is intentionally deferred until representative residential footage, stronger contextual tracking, and routine/location context are available. The evidence does not support another round of threshold tuning.

Relevant limitations are:

- Arbitrary consumer-camera viewpoints materially affect pose quality; full lower-body pose cannot be assumed.
- Low/oblique floor-level footage remains difficult for MediaPipe and YOLO pose.
- Public fall/action datasets do not supply the household lookalikes and false-positive evidence needed for deployment.
- Tracking continuity remains weak outside controlled clips, and higher FPS adds compute without resolving it.
- Actual inference must fuse detection, tracking, box geometry, temporal motion, pose where available, room context, and the resident’s routine baseline.

Before revisiting, collect consented representative residential clips—including intentional lying, kneeling, bending, floor activity, partial exits, pets, displays, occlusion, and multiple people—and validate at qualified camera placements. See [viewpoint validation](viewpoint-validation.md) and [data guidance](../data/README.md).
