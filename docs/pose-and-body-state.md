# Pose and coarse body state

The CV service uses MediaPipe Pose as the selected CPU-capable estimator. Its output is normalized to named, 0–1 image-coordinate landmarks. Raw frame arrays are discarded; only an aggregate body-state observation is persisted.

Person detection is deliberately first: no-person clips return before pose inference. For positive clips, sampled-frame states are aggregated only when at least 60% of usable frames agree (configurable with `minimum_frame_agreement`); otherwise the result is `unknown`.

The initial rules are configurable and conservative: visible landmark confidence must be at least 0.55; a wide body bounding box (width/height ≥1.15) suggests `floor_level`; ankle-to-hip separation relative to torso distinguishes standing and sitting. These are starting hypotheses, not clinical thresholds. `floor_level` never means a fall.

Expand fixtures with front/side/occluded standing; chair/sofa/bed/wheelchair sitting; supine/side/prone/floor sitting; and kneeling, tying shoes, deep bends, crawling, occlusion, and upper-body-only views as unknown. Validate precision and false floor-level labels across diverse camera heights before building fall detection.
