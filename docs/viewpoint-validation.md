# Pose and viewpoint validation

Use `fixtures/viewpoint/<placement>/<label>/` with `standing`, `walking`, `chair_sitting`, `sofa_sitting`, `floor_lying`, `floor_sitting`, and `kneeling_or_bending`. Current body-state mapping is standing/walking → `standing`; chair/sofa → `sitting`; floor lying/sitting → `floor_level`; kneeling/bending → `unknown`.

The pose `safetyPrimitive` debug field is diagnostic only: `upright`, `low_horizontal`, `rapid_vertical_drop_candidate`, `persistent_low_state`, or `unknown`. It is never persisted or alerting. Separate person-box diagnostics are now available as `upright_box`, `horizontal_box`, `rapid_downward_motion_candidate`, and `persistent_low_position`; see [person-box temporal diagnostics](person-box-temporal.md). Neither set is a fall label. The pose primitives use only reliable upper-body landmarks. Multi-frame primitives cannot be assessed from URFD stills.

`rapid_vertical_drop_candidate` is emitted only when an initially upright, confident shoulder/hip torso moves downward by at least 0.25 normalized image heights across a sampled clip. `persistent_low_state` requires at least three samples and `low_horizontal` in at least 75% of them. These are intentionally conservative debug signals, not fall labels. No threshold was selected against URFD.

Benchmark one placement at a time by pointing the existing runner at its mapped body-state fixture directory, for example `BENCHMARK_ROOT=fixtures/viewpoint/mid_height_front npm run benchmark`; use `POSE_BACKEND=yolo` to select the alternate backend. Empty placement directories are intentional placeholders, and must not be interpreted as validation evidence.

Record short consented, staged clips at each placement before drawing deployment conclusions. Labeling should capture viewpoint and posture but must not turn floor-level states into falls.
