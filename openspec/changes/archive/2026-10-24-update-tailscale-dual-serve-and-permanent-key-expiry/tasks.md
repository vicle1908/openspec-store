# Tasks: Update Tailscale Dual-Port Serve Routing, Permanent Key Expiry, and Double-NAT Relay Policy

## 1. Research & Topology Evaluation

- [x] 1.1 Audit Tailscale Peer Relay documentation (`kb/1591/peer-relays`), `tailscale debug netmap`, `tailscale debug peer-relay-servers`, `tailscale debug metrics`, and double-NAT gateway headers (`192.168.10.1` and `192.168.1.1`)
- [x] 1.2 Verify `Self.KeyExpiry: null` (`Key expiry: Never` in Tailscale GUI) across `iosteam-mac-mini`, `macbook-pro-ca-l-1`, and `les-mac-mini`, and close the `Tailscale.app` GUI window after inspection

## 2. Dual-Port Tailscale Serve Configuration

- [x] 2.1 Configure `tailscale serve --bg --https=8443 http://127.0.0.1:8787` to expose Hermes WebUI on `:8443` alongside OmniRoute on `:443` (`http://127.0.0.1:20128`)
- [x] 2.2 Verify `tailscale serve status --json` reports both `:443` (`http://127.0.0.1:20128`) and `:8443` (`http://127.0.0.1:8787`) active and verify direct (`iphone-15-pro-max`, `8ms`) and DERP (`macbook-pro-ca-l-1`, `105ms`) peer connectivity

## 3. Specification Validation & Archive

- [x] 3.1 Record live verification evidence in `evidence.md` and validate `update-tailscale-dual-serve-and-permanent-key-expiry` strictly via `openspec validate update-tailscale-dual-serve-and-permanent-key-expiry --strict --json --store openspec-store`
