# Tasks: verify-hermes-webui-iphone-access

## 1. Tailscale connectivity (completed in setup change)

- [x] 1.1 iPhone connected to victory1908 tailnet
- [x] 1.2 Tailscale ping confirms iPhone reachable via DERP relay

## 2. Server-side infrastructure (completed in setup change)

- [x] 2.1 Hermes WebUI running on 127.0.0.1:8787 under launchd
- [x] 2.2 Tailscale Serve configured at https://iosteam-mac-mini.tailc6b508.ts.net
- [x] 2.3 Password authentication active and verified

## 3. Device-side acceptance (completed)

- [x] 3.1 Open iPhone Safari, visit https://iosteam-mac-mini.tailc6b508.ts.net/health
- [x] 3.2 Confirm JSON response contains "status":"ok"
- [x] 3.3 Open Hermex, enter server URL and password
- [x] 3.4 Send authenticated test message, confirm response received
