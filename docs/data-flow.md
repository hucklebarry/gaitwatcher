# Data flow and privacy

An event is normalized to a provider-neutral `CameraEvent`, queued, and its media is retrieved only for processing. The worker records semantic observations plus measurements, not raw video. Production adapters must download to ephemeral storage, count bytes, and delete files in a `finally` block; fixture retention is development-only. URLs and secrets are redacted from worker errors.
