# Architecture

```mermaid
flowchart TD
 P[Camera Provider] --> A[Event API]
 A -->|synchronous validation + 202| Q[Queue]
 Q --> W[Processing Worker]
 W --> C[CV Worker]
 C --> D[(Observation DB)]
 D --> U[Caregiver API/UI]
```

Only validation, authorization and enqueueing are synchronous. The worker is at-least-once and Observation has a unique event ID, making duplicate delivery safe. Providers expose capabilities through the domain package; downstream code only sees `CameraProvider`.
