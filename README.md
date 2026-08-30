# GaitWatcher MVP

Provider-neutral elder-care monitoring vertical slice: `mock event → queue → CV → observation → caregiver timeline`.

## Run

1. `cp .env.example .env` (the local Docker database is exposed on port `5433` to avoid host PostgreSQL collisions)
2. `docker compose up --build`
3. In another terminal, create schema/demo records: `npm run db:generate && npm run db:migrate && npm run seed`
4. Start the web UI: `npm run dev:web`, then set `localStorage.householdId = "demo-household"` and `localStorage.userId` to the seed command’s printed value.

POST `/v1/events` with `{ "provider":"mock", "providerEventId":"person-demo", "deviceId":"mock-front", "occurredAt":"2026-08-16T14:43:12Z" }`. The duplicate-safe response is immediate (202); the timeline requires `x-user-id` and household scoping.

## Commands

`npm run test` · `npm run load-test` · `npm run benchmark` · `npm run cost-estimate`

For the downloaded, non-commercial URFD evaluation subset: `python3 scripts/prepare-urfd-subset.py` then `BENCHMARK_ROOT=data/external/urfd/benchmark npm run benchmark`. See `data/README.md` for licensing and the intentionally narrow label mapping.

The current CV container uses deterministic fixture-label detection for a fully offline mock path. Install and use an approved lightweight YOLO runtime in that service before treating results as CV accuracy. Ring remains credential-gated; see `docs/ring-integration.md`.

Pose/body-state is documented in `docs/pose-and-body-state.md`. The implementation uses a conservative `standing` / `sitting` / `floor_level` / `unknown` contract; `floor_level` is not a fall label.
