# Phase 1A: presence episode aggregation

Fall-like inference remains **experimental/deferred**: public-video tracking is unreliable, pose is viewpoint-sensitive, and household lookalikes remain insufficiently characterized. This phase uses only real person detection, without pose, to produce room-level semantic presence.

The API worker consumes provider media, calls the CV worker with `invokePose:false`, and records a compact `presence_evidence`, `no_person_evidence`, or `unknown_presence_evidence` observation. A positive event merges into the latest same-device episode when it is within `PRESENCE_MAX_GAP_MS` (default five minutes); otherwise a new episode starts. Episodes are candidates until two positive events confirm them; daily aggregates exclude unconfirmed candidates. Production persistence retains compact per-event evidence for auditability and one merged `PresenceEpisode`, never raw frames or model objects.

`CameraDevice.room` is the provider-independent logical location. No room names are hardcoded in CV. Episodes record room, start/end, confidence, positive/negative sample counts, maximum detection count, and whether multiple people were seen. They mean **a person was observed**, not that a particular resident was identified.

`GET /v1/households/:householdId/presence-daily?day=YYYY-MM-DD` exposes episode count, presence milliseconds by room, and first/last observed activity. It deliberately does not infer cross-camera transitions or a personal baseline.
