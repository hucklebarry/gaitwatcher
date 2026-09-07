# Prompt 2.3 person-box and temporal diagnostics

The worker now begins each sampled frame with YOLOv8n COCO person detection. Its adapter returns only GaitWatcher-owned normalized `PersonDetection` values (`boundingBox.x/y/width/height`, confidence), supports multiple people, and uses IoU association only within one clip. Track identifiers are neither residents nor cross-room identities.

Box diagnostics are camera-relative: `upright_box`, `horizontal_box`, `rapid_downward_motion_candidate`, and `persistent_low_position`. They are debug-only evidence. They do not imply a fall, emergency, physical velocity, or distance, and do not create an Observation or alert. Pose is invoked only after at least one person is detected, and `invokePose:false` permits box-only evaluation.

`personDetectionMs` includes detector inference plus frame decoding in the current single-pass detector adapter; association and feature calculation are included in `totalProcessingMs` and are too small to resolve in current integer-millisecond reporting. `personFrames`, `detectionsPerFrame`, and `poseCallsAvoided` expose cascade availability. Once a clip contains any person, the current pose adapter samples the whole clip; selective pose invocation for only person-positive frames remains a future efficiency refinement.

The detector is upstream YOLOv8n, downloaded by Ultralytics as `yolov8n.pt`. The same AGPL-3.0/commercial-license review noted for YOLO pose applies. Thresholds are deliberately configuration constants in `box_primitives.py`, not universal camera facts: aspect >= 1.15 is horizontal, center-y >= .65 is low, and a single-track center-y change >= .15 is a rapid-downward candidate.

Use `POST /detect` with `sampleFps`, `invokePose`, and `debug:true` to inspect `personRun.frames`, `tracks`, and `boxDiagnostics`. The IoU association threshold is 0.05 to tolerate ordinary detector box jitter and posture-driven shape change; it is not identity-safe in crowds. Benchmark clips should include viewpoint and a manually reviewed scenario label; the current URFD archive has a legal RGB frame sequence but does not itself establish complete fall or lookalike ground truth.

Prompt 2.4 uses `fixtures/temporal/manifest.json` as the reviewable corpus annotation and `npm run benchmark:temporal` for 1, 2, and 5 FPS runs. Tracker continuity is explicitly `maintained`, `track_lost_or_reassigned`, or `not_applicable`; a gap or reassignment is never treated as motion evidence.
