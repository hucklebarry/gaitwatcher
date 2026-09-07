# GaitWatcher

GaitWatcher is an aging-in-place caregiver intelligence platform. It uses commodity smart-home devices to turn temporary media and device events into privacy-conscious semantic observations, then (over time) into routine-aware caregiver information and resident interaction. It is a wellness/informational product direction, not a diagnostic system or emergency-service replacement.

## Run

1. `cp .env.example .env` (the local Docker database is exposed on port `5433` to avoid host PostgreSQL collisions)
2. `docker compose up --build`
3. In another terminal, create schema/demo records: `npm run db:generate && npm run db:migrate && npm run seed`
4. Start the web UI: `npm run dev:web`, then set `localStorage.householdId = "demo-household"` and `localStorage.userId` to the seed command’s printed value.

POST `/v1/events` with `{ "provider":"mock", "providerEventId":"person-demo", "deviceId":"mock-front", "occurredAt":"2026-08-16T14:43:12Z" }`. The duplicate-safe response is immediate (202); the timeline requires `x-user-id` and household scoping.

## Commands

`npm run test` · `npm run load-test` · `npm run benchmark` · `npm run benchmark:temporal` · `npm run cost-estimate` · `npm run reolink:audio-test` · `npm run reolink:audio-duplex-test`

For the downloaded, non-commercial URFD evaluation subset: `python3 scripts/prepare-urfd-subset.py` then `BENCHMARK_ROOT=data/external/urfd/benchmark npm run benchmark`. See `data/README.md` for licensing and the intentionally narrow label mapping.

The CV worker has real local YOLO person detection and an offline mock-provider fixture path. Fixture behavior and public benchmark results do not establish deployment accuracy. Ring remains credential-gated; see [Ring integration](docs/ring-integration.md).

## Architecture and project context

The active path is `provider → event/media pipeline → perception → semantic domain/persistence → future routine intelligence → caregiver and interaction experiences`. The same household-scoped device and room model will support both observation and future interaction; audio is not a separate project.

- [Architecture](docs/architecture.md) explains the system boundaries and shared device seam.
- [Project state and roadmap](docs/project-state.md) is the canonical status, strategy, and next-work document.
- [CV and fall-like evaluation findings](docs/cv-perception-findings.md) preserves the benchmark decisions and limitations.
- [Data and privacy flow](docs/data-flow.md), [validation](docs/validation.md), and [external dataset guidance](data/README.md) cover supporting operational detail.
- [Reolink outbound-audio spike](docs/spikes/reolink-audio.md) documents the opt-in local hardware experiment.
- [Pi Home Agent deployment](docs/deployment/raspberry-pi-home-agent.md) and [Render Cloud deployment](docs/deployment/render-cloud.md) document the separate prototype deployables.

The body-state contract is `standing` / `sitting` / `floor_level` / `unknown`. **`floor_level != fall`**; fall-like inference is intentionally deferred.
