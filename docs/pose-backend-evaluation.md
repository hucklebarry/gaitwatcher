# Pose backend and pose-light diagnostic evaluation

The worker exposes two local, pretrained CPU pose backends behind the same owned normalized landmark contract: the existing MediaPipe BlazePose Lite (`model_complexity=0`) and YOLOv8n-pose. The selected backend is request-scoped through `poseBackend` (`mediapipe` default, or `yolo`), but each is initialized at most once per worker process. Initialization is reported in debug output and excluded from per-media pose timing.

YOLOv8n-pose was selected as the single alternate because it returns the COCO shoulder, hip, knee, and ankle keypoints needed by the existing adapter. It uses the upstream pretrained `yolov8n-pose.pt` artifact (6,832,633 bytes in the benchmark container). Ultralytics distributes its package under AGPL-3.0 unless a commercial enterprise license is obtained; this local research evaluation must be reviewed before any proprietary deployment.

The diagnostic-only `safetyPrimitive` does not alter `bodyState`, write records, send notifications, or infer falls. It uses confident shoulders and hips only, where available. The current person gate does not expose a real person bounding box, so box aspect ratio/centroid measurements have not been claimed or evaluated; that is a separate prerequisite for box-based diagnostics.

The URFD subset consists only of 12 still frames labelled for floor-level evaluation from one low/oblique camera view. It is useful for availability evidence, not for validating temporal primitives, upright posture, sitting posture, or a camera-placement matrix. Add consented staged clips below `fixtures/viewpoint/` as described in `viewpoint-validation.md` before making placement claims.
