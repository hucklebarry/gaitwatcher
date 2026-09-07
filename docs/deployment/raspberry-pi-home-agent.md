# Raspberry Pi Home Agent runbook

This deploys the existing Node-based Home Agent on a Raspberry Pi 3 running Raspberry Pi OS Lite 64-bit. It does not deploy the CV worker: YOLO/MediaPipe workload migration is deliberately out of scope.

## Portability audit

| Area | Finding |
| --- | --- |
| Node | `rtsp-backchannel` requires Node.js 22 or newer. Use Node 22 on ARM64. |
| npm modules | `rtsp-backchannel`, `ws`, and their dependencies are JavaScript; no native addon or Mac binary is used by the Home Agent. |
| FFmpeg | Required on `PATH` by `rtsp-backchannel` to transcode WAV input. Raspberry Pi OS provides it through `apt`. |
| Filesystem | Home Agent reads four committed `fixtures/audio/*.mp3` messages (about 36 KB total); audio-spike temporary files use Node's portable temp directory. |
| macOS commands | `say` was only used once on the Mac to create committed development fixtures. It is not invoked by the Home Agent or Pi setup. |
| CPU/RAM | No Pi measurement has been taken. The Home Agent is light while idle; playback adds one short FFmpeg transcode plus RTSP session. Measure before treating this as a capacity claim. |

## Install Raspberry Pi OS and prerequisites

Use [Raspberry Pi Imager](https://www.raspberrypi.com/documentation/computers/getting-started.html) to write **Raspberry Pi OS Lite (64-bit)**. In Imager customization, set a unique hostname, Wi-Fi (if used), a non-default user, locale/timezone, and SSH public-key access. Boot, find the address from the router, then SSH in.

```bash
ssh <pi-user>@<pi-address>
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y ca-certificates curl ffmpeg git

# Node.js 22 is required by rtsp-backchannel.
curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/nodesource_setup.sh
sudo -E bash /tmp/nodesource_setup.sh
sudo apt install -y nodejs
node --version # must be v22 or newer
ffmpeg -version
```

The NodeSource Node 22 Debian installation sequence is documented in its [distribution instructions](https://github.com/nodesource/distributions/blob/master/DEV_README.md). Raspberry Pi officially recommends Lite for headless installations and supports configuring SSH during imaging. [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html)

## Install GaitWatcher and configure the Home Agent

```bash
sudo adduser --system --group --home /var/lib/gaitwatcher gaitwatcher
sudo mkdir -p /opt/gaitwatcher /etc/gaitwatcher /var/lib/gaitwatcher
sudo chown -R "$USER":gaitwatcher /opt/gaitwatcher /var/lib/gaitwatcher
git clone <your-gaitwatcher-repository-url> /opt/gaitwatcher
cd /opt/gaitwatcher
# Installs only the Home Agent workspace plus interaction/shared dependencies.
# It does not install Cloud/Fastify/browser dependencies or perception packages.
npm ci --workspace @gaitwatcher/home-agent --include=dev

sudo install -m 600 -o root -g gaitwatcher /dev/null /etc/gaitwatcher/home-agent.env
sudoedit /etc/gaitwatcher/home-agent.env
```

Put only these values in `/etc/gaitwatcher/home-agent.env` (use real values; do not commit this file):

```dotenv
REOLINK_HOST=
REOLINK_USERNAME=
REOLINK_PASSWORD=
HOME_AGENT_ID=dev-home-agent
HOME_AGENT_DEVICE_ID=living-room-reolink
HOME_AGENT_CLOUD_URL=wss://<your-test-control-service-host>
# Optional; defaults to 5000.
HOME_AGENT_RECONNECT_MS=5000
```

## Manual validation before systemd

Run this on the Pi, on the same LAN as the E1 Pro. It must succeed before continuing:

```bash
cd /opt/gaitwatcher
set -a; source /etc/gaitwatcher/home-agent.env; set +a
npm run reolink:audio-test
```

Confirm the E1 Pro emits the generated tone. Then start the existing Home Agent manually:

```bash
set -a; source /etc/gaitwatcher/home-agent.env; set +a
npm run start --workspace @gaitwatcher/home-agent
```

From the remote-control browser, press **Lunch Reminder** and confirm speaker playback plus `completed`. No camera port, ONVIF endpoint, RTSP URL, or router port forwarding is needed; the Pi makes an outbound WSS connection.

## Unattended systemd service

```bash
cd /opt/gaitwatcher
sudo install -m 644 deploy/systemd/gaitwatcher-home-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gaitwatcher-home-agent

sudo systemctl status gaitwatcher-home-agent
sudo journalctl -u gaitwatcher-home-agent -f
sudo systemctl restart gaitwatcher-home-agent
sudo systemctl stop gaitwatcher-home-agent
sudo systemctl disable --now gaitwatcher-home-agent
sudo rm /etc/systemd/system/gaitwatcher-home-agent.service
sudo systemctl daemon-reload
```

## Reboot and reconnect validation

Manual validation is still required on the physical Pi:

1. Confirm a remote **Lunch Reminder** reaches `completed`.
2. Run `sudo reboot`; do not SSH in or start anything manually.
3. Wait for Wi-Fi/network and systemd startup, then trigger the reminder again.
4. Temporarily disconnect the Pi from its network or stop the test-control service, then restore it.
5. Confirm journal logs show `retrying` followed by `connected`, and the next reminder completes.

Record idle and active usage during this test:

```bash
systemctl show gaitwatcher-home-agent -p MainPID --value | xargs -r ps -o pid,%cpu,rss,cmd -p
sudo journalctl -u gaitwatcher-home-agent --since '10 minutes ago'
```

The Pi is expected to be suitable for this narrow interaction workload if the tests are stable; do not claim a CPU/RAM result until the commands above are measured on the target hardware.
