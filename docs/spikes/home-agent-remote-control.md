# Home Agent remote-control proof

## Purpose and boundary

This development proof connects a remote browser to the Home Agent by way of a tiny Cloud control service. It does not expose the camera, RTSP, ONVIF, or camera credentials to the internet. `apps/remote-control` is the Cloud deployment unit; `apps/home-agent` is the Pi deployment unit. They share only hardware-agnostic interaction contracts through `packages/shared`.

```text
remote browser → test-control service → outbound Home Agent WebSocket → Reolink E1 Pro speaker
```

The control service accepts fixed message IDs and can store short caregiver browser recordings in private object storage. The Home Agent owns the local Reolink credentials, resolves fixture IDs locally, and downloads a short-lived signed URL for a custom recording only at playback time. It is deliberately beside—not inside—the existing perception/CV pipeline. Both belong in the future Home Agent deployment boundary and will eventually share household/device identity, but neither changes the current observation pipeline.

## What is proven locally

- Reolink E1 Pro local speaker control through the ONVIF/RTSP backchannel.
- `PCMU/8000` prerecorded speech playback.
- RTSP microphone capture and practical duplex with acoustic echo/bleed present.
- A Home Agent can receive a fixed command over an outbound WebSocket and invoke the local adapter.
- A local end-to-end `lunch_reminder` command reached `completed` after the Home Agent performed playback. Remote/cellular browser testing is still manual validation.

## Catalog

Only these development fixtures may be requested:

| Message ID | Audio fixture |
| --- | --- |
| `audio_test` | `fixtures/audio/audio-test.mp3` |
| `lunch_reminder` | `fixtures/audio/lunch-reminder.mp3` |
| `walk_reminder` | `fixtures/audio/walk-reminder.mp3` |
| `family_checkin` | `fixtures/audio/family-checkin.mp3` |

No remote request can provide a filesystem path or arbitrary speech.

## Custom caregiver recordings

The Cloud page can record a short voice message with browser `MediaRecorder`, name it, save it, play it, and delete it. Saved audio lives only in private S3-compatible object storage; the browser has a short signed upload URL and the Pi has a separate short signed download URL. Cloud does not know any Reolink protocol or camera credential. The Pi writes the downloaded audio to a temporary file solely for the existing adapter/FFmpeg playback path and removes it after playback.

This path is intended for reminder playback, not live caregiver talk or AI conversation. Delete blocks new playback requests; the Home Agent intentionally has no persistent custom-audio cache.

## Start the local proof

Set one long random development token for browser command requests. Camera credentials remain only in the Home Agent's local `.env`; the prototype does not authenticate the outbound agent WebSocket separately.

```bash
export REMOTE_CONTROL_TOKEN='long-random-development-token'
export HOME_AGENT_ID=dev-home-agent
export HOME_AGENT_DEVICE_ID=living-room-reolink

# Terminal 1: test-control service (the only service later made publicly reachable)
npm run dev:remote-control

# Terminal 2: Home Agent, on the E1 Pro's LAN
HOME_AGENT_CLOUD_URL=ws://127.0.0.1:3100 npm run dev:home-agent
```

Open `http://127.0.0.1:3100/`, enter the control token, then press **Lunch Reminder**. Status transitions mean:

`requested` → the test-control service accepted the catalogued command.

`agent_received` → the connected Home Agent accepted it for the configured device.

`camera_playback_started` → it resolved the local stream and began its outbound playback call.

`completed` / `failed` → the Home Agent reported the outcome. The returned command and status endpoint preserve the complete timestamped state history, so short-lived intermediate transitions are not lost to browser polling. HTTP acceptance by itself is not success.

## Phone/cellular demonstration without camera port forwarding

Run the control service on any reachable development host, then use an HTTPS tunnel for **port 3100 only** (for example a temporary Cloudflare Tunnel or ngrok tunnel). Set `HOME_AGENT_CLOUD_URL` to that tunnel's `wss://…` address before starting the Home Agent. Open the tunnel's `https://…` URL on a phone using cellular, enter the token, and press **Lunch Reminder**. The camera remains LAN-only; do not forward its RTSP or ONVIF ports.

Confirm that the E1 Pro audibly plays the lunch phrase and that the browser reaches `completed`.

## Temporary security shortcuts

This is not production authentication or authorization:

- one shared development token protects browser command requests only; the agent WebSocket is unauthenticated in this prototype;
- browser token entry is not persisted, but a tunnel URL must still be treated as sensitive;
- command status is in memory and is lost on restart;
- fixed development agent/device IDs are documented rather than managed in a database;
- no TLS is provided for localhost; use an HTTPS/WSS tunnel for an internet demonstration.

The next milestone after the physical remote demonstration is a narrow Home Agent interaction boundary with durable device mapping and proper authentication/authorization—not TTS, STT, or live conversation. Echo suppression must be evaluated before enabling live talk, not before prerecorded reminders.
