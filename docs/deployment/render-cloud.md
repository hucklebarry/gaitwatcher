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

Set only these environment variables on Render:

```text
REMOTE_CONTROL_TOKEN=<long-random-development-token>
NODE_ENV=production
```

Render supplies `PORT`; the Cloud binds to it automatically. Its public endpoints are:

- `/` — caregiver web page
- `/health` — lightweight health check and connected-agent count
- `/agent?agentId=<id>` — Home Agent WebSocket endpoint
- `/commands` and `/commands/:id` — browser command/status API

The web page carries no camera credentials. It accepts only fixed message IDs from the shared contract and displays current agent availability plus the timestamped delivery lifecycle.

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

Set the Pi's `HOME_AGENT_CLOUD_URL` to that computer's LAN address, for example `ws://192.168.1.20:3100`, then start the Pi Home Agent. Open the web page, enter the development token, confirm **Home Agent: online**, and press **Lunch Reminder**. Confirm the lifecycle ends at `completed` and the E1 Pro audibly plays the message.

## Cellular proof

After Render deployment, put the iPhone on cellular, open the Render HTTPS URL, enter the development token, and press **Lunch Reminder**. The browser should show `Requested`, `Agent received`, `Playback started`, and `Completed`; the Pi stays outbound-only and the E1 Pro plays the fixture locally.

## Prototype limits

`REMOTE_CONTROL_TOKEN` is development-only shared browser protection. Agent WebSockets are unauthenticated in this simplified prototype, command state is in memory, agent/device IDs are fixed development values, and Render restarts lose history. Production caregiver auth, agent provisioning, authorization, and durable command persistence are deliberately deferred.
