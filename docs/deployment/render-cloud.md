# Render Cloud deployment (prototype)

`apps/remote-control` is the prototype GaitWatcher Cloud deployable. It serves the caregiver web page, command/status APIs, and the Home Agent WebSocket endpoint. It has no Reolink package dependency, no camera credentials, no FFmpeg invocation, and no local-device access.

## Render dashboard setup

Create one **Web Service** from this monorepo:

| Setting | Value |
| --- | --- |
| Root directory | repository root |
| Runtime | Node |
| Node version | 22 or newer |
| Build command | `npm ci --workspace @gaitwatcher/cloud --include=dev` |
| Start command | `npm run start --workspace @gaitwatcher/cloud` |
| Health check path | `/health` |

Set these environment variables on Render:

```text
REMOTE_CONTROL_TOKEN=<long-random-development-token>
NODE_ENV=production
AUDIO_STORAGE_ENDPOINT=https://<cloudflare-account-id>.r2.cloudflarestorage.com
AUDIO_STORAGE_REGION=auto
AUDIO_STORAGE_BUCKET=gaitwatcher-audio
AUDIO_STORAGE_ACCESS_KEY_ID=<R2-S3-access-key-id>
AUDIO_STORAGE_SECRET_ACCESS_KEY=<R2-S3-secret-access-key>
```

Render supplies `PORT`; the Cloud binds to it automatically. Its public endpoints are:

- `/` — caregiver web page
- `/health` — lightweight health check and connected-agent count
- `/agent?agentId=<id>` — Home Agent WebSocket endpoint
- `/commands` and `/commands/:id` — browser command/status API
- `/audio-assets` — authenticated custom-recording list/upload-finalize/delete API

The web page carries no camera credentials. It supports both committed quick-message fixtures and short browser-recorded voice messages, and displays current agent availability plus the timestamped delivery lifecycle.

## Private voice-message storage (Cloudflare R2)

Create a private R2 bucket, for example `gaitwatcher-audio`; do **not** enable public-bucket access. Create an R2 S3 API token limited to that bucket with object read/write permission, then place its endpoint and credentials in the Render variables above. Those credentials belong only on Render, never in the browser or on the Pi.

The browser receives a five-minute signed `PUT` URL for each recording. Configure bucket CORS to allow the Render service origin (for example `https://<your-render-service>.onrender.com`), method `PUT`, and header `content-type`:

```json
[
  {"AllowedOrigins":["https://<your-render-service>.onrender.com"],"AllowedMethods":["PUT"],"AllowedHeaders":["content-type"],"MaxAgeSeconds":300}
]
```

The Pi receives a separate five-minute signed `GET` URL only when a caregiver presses Play. It downloads the recording into a temporary directory, plays it through the existing Reolink adapter, then deletes the temporary file. No custom audio is committed to Git or permanently cached on the Pi.

Recordings are limited to 60 seconds and 10 MB. Their metadata is stored beside the object in the same private bucket, so recordings survive Cloud deploys/restarts. Delete removes the audio object and marks its metadata deleted; it cannot be selected for later playback. In-progress uploads that never finalize are not listed or playable.

## Connect the Pi

Put Render's HTTPS hostname in the Pi Home Agent environment as WSS, then restart its service or manual process:

```dotenv
HOME_AGENT_CLOUD_URL=wss://<your-render-service>.onrender.com
HOME_AGENT_ID=dev-home-agent
HOME_AGENT_DEVICE_ID=living-room-reolink
```

Do not set `REOLINK_*` values on Render. Do not expose Pi, camera, RTSP, or ONVIF ports. The Pi connects outward to Render.

## Local integration before Render

Start Cloud on a development computer:

```bash
REMOTE_CONTROL_TOKEN='development-token' npm run dev:remote-control
```

Set the Pi's `HOME_AGENT_CLOUD_URL` to that computer's LAN address, for example `ws://192.168.1.20:3100`, then start the Pi Home Agent. Open the web page, enter the development token, confirm **Home Agent: online**, and press **Lunch Reminder**. Confirm the lifecycle ends at `completed` and the E1 Pro audibly plays the message. To test custom audio locally, configure a private S3-compatible bucket and the `AUDIO_STORAGE_*` variables too.

## Cellular proof

After Render deployment, put the iPhone on cellular, open the Render HTTPS URL, enter the development token, and press **Lunch Reminder**. The browser should show `Requested`, `Agent received`, `Playback started`, and `Completed`; the Pi stays outbound-only and the E1 Pro plays the fixture locally.

## Prototype limits

`REMOTE_CONTROL_TOKEN` is development-only shared browser protection. Agent WebSockets are unauthenticated in this simplified prototype, command state is in memory, agent/device IDs are fixed development values, and Render restarts lose command history. Recording assets themselves are durable private object-storage objects, but they are not yet per-household/user authorized. Production caregiver auth, agent provisioning, authorization, and durable command persistence are deliberately deferred.
