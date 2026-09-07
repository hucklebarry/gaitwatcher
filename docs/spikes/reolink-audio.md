# Reolink E1 Pro outbound-audio spike

## Scope

This is a manual, opt-in hardware experiment. It does not add a Reolink provider, alter camera-event ingestion, or make any product claim about interaction support.

The exact target hardware is:

- Reolink E1 Pro
- hardware `IPC_NT1NA45MP`
- firmware `v3.1.0.4417_2412122130`
- local RTSP and ONVIF enabled

The question is whether an arbitrary local audio file can reach this camera's built-in speaker over the local network.

## Mechanism selected

The harness uses [`rtsp-backchannel` 0.3.1](https://github.com/GagaKor/rtsp-backchannel), a TypeScript ONVIF/RTSP-backchannel client. GaitWatcher does not construct RTSP requests, RTP packets, or codecs itself. The library:

1. queries ONVIF device/media services for profiles and audio-output evidence;
2. resolves an RTSP stream URI through ONVIF;
3. sends `Require: www.onvif.org/ver20/backchannel`, finds an SDP `a=sendonly` audio track, and opens the RTSP session; and
4. uses FFmpeg to decode/resample the input before sending the library-selected RTP codec at real-time pace.

That is the ONVIF backchannel flow: `DESCRIBE` with the backchannel requirement, a `sendonly` audio media section, `SETUP`, then `PLAY`. See the [ONVIF Audio Backchannel Client Test Specification](https://www.onvif.org/wp-content/uploads/2019/07/ONVIF_Audio_Backchannel_Client_Test_Specification_19.06.pdf).

Reolink documents AAC as its ordinary RTSP audio format but says its RTSP two-way-audio path supports G.711. The harness deliberately negotiates rather than assuming either codec. [Reolink format documentation](https://support.reolink.com/articles/900000638523-What-s-the-Format-of-the-RTSP-Video-Audio-that-Reolink-Cameras-Use/)

`rtsp-backchannel` is a focused third-party library and not independent evidence that this camera supports the standard. A failure must therefore be recorded as either camera capability evidence or a library/protocol limitation, not proof that the Reolink app's proprietary talk feature is unavailable.

## Run

FFmpeg must be available on `PATH`. It is used for conversion only; it is not an RTSP-backchannel implementation.

```bash
export REOLINK_HOST='camera-lan-address'
export REOLINK_USERNAME='camera-user'
read -rs REOLINK_PASSWORD
export REOLINK_PASSWORD
npm run reolink:audio-test
```

Without `REOLINK_AUDIO_FILE`, the script creates a one-second 880 Hz WAV tone in a temporary directory, plays it once, and deletes it. To test arbitrary prerecorded audio instead:

```bash
REOLINK_AUDIO_FILE=/absolute/path/to/gaitwatcher-audio-test.wav npm run reolink:audio-test
```

Optional controls:

- `REOLINK_ONVIF_PORT` — defaults to `8000`.
- `REOLINK_TIMEOUT_MS` — per-request ONVIF timeout; defaults to `8000`.
- `REOLINK_AUDIO_VOLUME` — linear conversion gain from `0` through `1`; defaults to `0.05`.
- `REOLINK_AUDIO_CODEC` — `auto` (default), `pcma`, `pcmu`, `g726-16`, `g726-24`, `g726-32`, `g726-40`, or `aac`. Leave at `auto` unless diagnosing a camera-advertised codec.
- `REOLINK_AUDIO_VERBOSE=1` — prints the non-secret ONVIF capability report.

Never put credentials in a committed file or in an RTSP URL. `.env` is ignored; `.env.example` intentionally contains blank values only.

## Audio conversion

The input may be a normal audio file supported by FFmpeg. The client transcodes it to the codec and clock rate in the camera's `sendonly` SDP track. For a G.711 selection, this is 8 kHz mono PCMA or PCMU; G.726 and AAC follow their SDP-negotiated RTP configuration. The test tone is only a fixture source—not the wire format.

## Diagnostics and interpretation

The command reports capability discovery, audio-output profile evidence, RTSP backchannel negotiation, selected codec, conversion, RTP packet count, and elapsed time. It redacts the configured password from reported errors.

Interpret results narrowly:

| Observation | Meaning |
| --- | --- |
| `AudioOutputConfiguration` is reported | ONVIF profile evidence only; not proof of a usable backchannel. |
| `no sendonly backchannel audio track` | Standards-based ONVIF/RTSP talkback was not exposed to this client. The Reolink app may still use a different mechanism. |
| A codec/session is negotiated and RTP packets are sent | Standards-based invocation reached the outbound media session; manually verify speaker audibility. |
| Speaker emits the file/tone | Arbitrary local speaker output works through the tested standards-based path. |

## Results

Status: **not yet run against the physical camera from this repository.** The harness was type-checked and its missing-configuration guard was exercised; physical speaker output is intentionally not part of CI. Record the observed speaker result, negotiated codec, elapsed time, and any dropout/reliability notes here after a manual run.

## Next narrow experiment

If a tone is audible, repeat with a short spoken WAV and measure start-to-audible latency several times. If the standard backchannel is absent or fails, capture the script's redacted failure category and compare its ONVIF profile/SDP evidence with a mature client such as GStreamer's ONVIF-backchannel support before considering any Reolink-specific protocol work.
