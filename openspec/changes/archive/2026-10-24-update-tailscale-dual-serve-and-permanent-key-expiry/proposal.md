# Proposal: Update Tailscale Dual-Port Serve Routing, Permanent Key Expiry, and Double-NAT Relay Policy

## Why

Following initial Tailscale `1.104.2` connection recovery and key rotation, three follow-up items required evaluation and execution: (1) Tailscale Serve on port `443` (`http://127.0.0.1:20128`, OmniRoute) had displaced the Hermes WebUI HTTPS proxy (`http://127.0.0.1:8787`), (2) `iosteam-mac-mini`'s node key expiry was permanently disabled (`KeyExpiry: null` / `Never`), and (3) Tailscale Peer Relay (`RelayServerPort=41642`, `RelayServerStaticEndpoints=["1.54.174.244:41642"]`) sits behind a double-NAT topology (`192.168.10.1` → `192.168.1.1`) without UPnP/NAT-PMP, requiring `tailscale.com/cap/relay` ACL grants to remain gated until upstream UDP `41642` port forwarding is in place.

## What Changes

- **Dual-Port Tailscale Serve HTTPS Routing (`:443` & `:8443`)**:
  - Keep `https://iosteam-mac-mini.tailc6b508.ts.net` (`:443`, tailnet-only) proxying `/` to `http://127.0.0.1:20128` (OmniRoute AI Gateway).
  - Configure `tailscale serve --bg --https=8443 http://127.0.0.1:8787` so `https://iosteam-mac-mini.tailc6b508.ts.net:8443` (`:8443`, tailnet-only) simultaneously proxies `/` to `http://127.0.0.1:8787` (Hermes WebUI).
- **Permanent Node Key Expiry Disablement Verification**:
  - Verify `Self.KeyExpiry: null` (`SelfNode.KeyExpiry: null` in `tailscale debug netmap` and `Key expiry: Never` in the Tailscale macOS GUI) alongside the rotated node key (`nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108`).
- **Double-NAT Peer-Relay ACL Policy Gating**:
  - Document and verify that `iosteam-mac-mini` listens on `udp4:41642` / `udp6:41642` (`RelayServerPort=41642`), while tailnet-wide `tailscale.com/cap/relay` ACL grants remain intentionally withheld while double-NAT routers (`192.168.10.1` and `192.168.1.1`, `Probe: {PCP:false PMP:false UPnP:false}`) lack external `UDP 41642` port forwarding, preventing blackholed relay allocation attempts from remote symmetric-NAT peers.

## Non-Goals

- Modifying `scripts/workstation-daily-update.sh` or `config/script-provenance-manifest.tsv` (owned by active change `persist-agent-tcc-provenance-and-auto-upgrade`).
- Modifying router firmware settings on `192.168.10.1` (`nginx/1.12.2`) or `192.168.1.1` (`Boa/0.94.13` FPT GPON ONT).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `workstation-tailscale-connectivity`: Adds requirements for dual-port Tailscale Serve routing (`:443` OmniRoute and `:8443` Hermes WebUI), permanent key expiry disablement (`KeyExpiry: null` / `Never`), and double-NAT peer-relay ACL gating.

## Impact

- **Ownership Boundary**: Host Tailscale Serve configuration (`tailscale serve status --json`), node key metadata, and `openspec/specs/workstation-tailscale-connectivity/spec.md` in `/Users/androidteam/Developer/platform/openspec-store`.
