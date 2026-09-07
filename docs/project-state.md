# Project state and roadmap

This is the canonical project checkpoint for GaitWatcher. Read it with the [architecture](architecture.md) and [CV/perception findings](cv-perception-findings.md) before beginning a new capability.

## Product direction

GaitWatcher is an aging-in-place caregiver intelligence platform: commodity smart-home hardware supplies observations about routine; those observations become useful caregiver information and, later, resident interaction. The product should favor:

```text
provider media → temporary processing → semantic observations → discard temporary media
```

It is not a permanent raw-video archive, medical diagnostic product, definitive fall detector, or replacement for emergency services. Do not represent Parkinson’s detection, dementia diagnosis, or medical emergency response as current capabilities.

## Status

| Area | Status | Notes |
| --- | --- | --- |
| Provider-neutral camera abstraction | Active / working | `CameraProvider`, mock provider, and capability metadata exist. |
| Ring monitoring provider | Working boundary / integration gated | Official credentials, permissions, and media access remain required. |
| Event, queue, and worker pipeline | Active / working | Idempotent event-to-observation path with PostgreSQL persistence. |
| Real person detection | Working / experimental accuracy | YOLOv8n-based, normalized GaitWatcher-owned boxes. |
| Short-term tracking | Working / needs residential validation | IoU association is within one clip only; never identity tracking. |
| Pose abstraction | Active / working | GaitWatcher-owned normalized landmarks behind backend adapters. |
| MediaPipe BlazePose Lite | Experimental default | CPU-oriented and materially viewpoint-sensitive. |
| YOLOv8n-pose | Experimental / not default | More poses in one test, but slower without material floor-level benefit. |
| Coarse body-state evidence | Experimental | `standing`, `sitting`, `floor_level`, `unknown`; not a fall classifier. |
| Fall-like inference | Deferred | See the explicit decision below. |
| Presence and room activity | Next core product work | Presence episodes are implemented; routine baseline and deviations follow. |
| Interactive audio | Current hardware spike | Audio Spike 1 is the next immediate milestone. |
| Gait/mobility trends | Future / qualified camera only | Enable only where lower-body viewpoint geometry is sufficient. |
| Robot/mobile hardware | Future / evidence-dependent | Consider only if fixed sensors leave important gaps. |

## What has been completed

The foundation includes camera-provider abstraction; mock and Ring provider boundaries; event ingestion; queue/worker processing; PostgreSQL semantic `Observation` persistence; tests; load testing; CV benchmarking; and cost-estimation tooling.

The perception work includes real person detection, normalized person bounding boxes, short-term IoU tracking, pose-provider abstraction, MediaPipe BlazePose Lite, experimental YOLOv8n-pose, normalized landmarks, conservative body-state classification, temporal aggregation, debug/failure telemetry, box features and temporal diagnostics, URFD support, HMDB51 exploratory support, benchmark tooling, and Git-ignored external dataset storage. Detailed evidence is preserved in [CV/perception findings](cv-perception-findings.md), [pose/body state](pose-and-body-state.md), [pose backends](pose-backend-evaluation.md), [person-box temporal diagnostics](person-box-temporal.md), and [external temporal corpus assessment](external-temporal-corpus-assessment.md).

## Deliberate fall-inference decision

**`floor_level != fall`**.

Fall-like event inference is experimental and deferred, not abandoned. Do not restart threshold tuning. Existing evidence shows arbitrary camera viewpoints materially affect pose quality; both pose backends struggle on low/oblique floor-level footage; temporal boxes are not discriminative on available public data; tracking continuity is weak in heterogeneous footage; and representative household false-positive/lookalike media is still missing.

Any later fall-like inference should combine person detection, short-term tracking, box geometry, temporal motion, pose when available, room context, and a personal routine baseline. Revisit it only with representative residential data, stronger contextual tracking, and routine/location context.

## Active roadmap

1. **Semantic presence and room activity.** Person observed in kitchen, presence episodes, movement/no-movement evidence, room transitions when supported.
2. **Personal routine baseline.** Usual wake period, first kitchen visit, activity by hour, and nighttime movement—primarily compared against the resident’s own history.
3. **Deviations and caregiver summaries.** Structured findings such as “no kitchen activity by the usual breakfast window” or materially lower activity. LLMs may summarize structured events; they do not perform per-frame perception.
4. **Richer activities.** Walking episodes, prolonged inactivity, probable meals, and extended room stays.
5. **Qualified-camera gait/mobility.** Only cameras with sufficient lower-body geometry participate.
6. **Revisit fall-like event inference.** Only after the prerequisite evidence and context above.

In parallel, validate interaction hardware for reminders, talk-through, check-ins, and eventual context-driven prompts. This is a capability track within the same product, not a replacement for semantic intelligence.

## Shared device and interaction seam

The current schema already prevents a second audio project from inventing separate identities: `CameraDevice` belongs to a `Household`, has a provider ID and logical `room`, stores capability metadata, and is referenced by events and presence episodes. Residents, caregivers, observations, metrics, and provider configuration remain shared.

The domain capability metadata already has a small provider-owned representation for video, inbound/outbound audio, full-duplex talk, PTZ, streaming, and event clips. No new interaction-provider interface is added in this checkpoint: actual Reolink model, firmware, local reachability, protocol, codec, and talk semantics remain unverified. Once Audio Spike 1 produces that evidence, introduce the narrow interaction service/provider boundary described in [architecture](architecture.md), connected to this existing device identity and room—not a separate database or `/audio-project`.

## Hardware strategy

- **Ring:** primary installed-base/distribution candidate for passive monitoring; keep it replaceable and do not assume unrestricted outbound speaker control.
- **Reolink/open IP cameras:** current physical development/reference platform for richer local video/audio and possible programmable two-way communication. A physical Reolink camera is available, but its exact capability must be verified.
- **Alexa/Echo/speakers:** possible future reminder/interaction integration, not current implementation scope.
- **Robot:** deferred and contingent on evidence that fixed sensors leave unresolved needs.

## Next immediate task: Audio Spike 1

Determine whether GaitWatcher can programmatically send arbitrary audio through the physical Reolink camera speaker. Answer: local reachability; exact model/firmware; official and local interfaces; arbitrary-audio support; required outbound codec/container; full-duplex versus push-to-talk; cloud/app dependency; and measured end-to-end latency.

The narrow implementation target is:

```text
local test audio or generated speech → GaitWatcher test harness → Reolink speaker
```

Do not add LLM conversation, speech recognition, reminder scheduling, or caregiver UI during this spike.
