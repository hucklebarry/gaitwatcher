# Local temporal validation clips

Place consented, staged clips in scenario folders, optionally beneath a viewpoint folder: `mid_height_front/<scenario>/clip.mp4`, `high_corner/<scenario>/clip.mp4`, `room_corner/<scenario>/clip.mp4`, or `low_or_tabletop/<scenario>/clip.mp4`.

Required scenarios before any event-level classifier is considered: `walking`, `sitting_down`, `lying_intentionally`, `bending_or_kneeling`, `rapid_sitting`, `staged_fall`, `leaving_frame`, `no_person_or_camera_motion`, plus lookalikes such as `sofa_lying`, `tying_shoe`, `picking_object`, and `floor_sitting`. Record the placement, sampling rate, and a manual truth table for detector presence, track continuity, box geometry, rapid-downward, persistent-low, and pose availability. Media files remain ignored; this README is the fixture contract.
