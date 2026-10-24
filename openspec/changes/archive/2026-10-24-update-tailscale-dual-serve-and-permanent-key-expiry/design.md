# Design: Update Tailscale Dual-Port Serve Routing, Permanent Key Expiry, and Double-NAT Relay Policy

## Context

See `proposal.md` — Why. Following the `1.104.2` Tailscale Cask reconciliation (`2026-10-24-reconcile-tailscale-cask-cli-and-key-renewal`), we audited all optional operational follow-ups across Tailscale Serve port allocations, node key expiry state, and NAT/peer-relay topology.

## Goals / Non-Goals

- **Goals**:
  - Serve both OmniRoute (`127.0.0.1:20128`) and Hermes WebUI (`127.0.0.1:8787`) over tailnet-only HTTPS without port collision.
  - Verify permanent key expiry disablement (`KeyExpiry: null` / `Never`) for `iosteam-mac-mini`.
  - Prevent peer-relay blackholing under double NAT (`192.168.10.78 -> 192.168.10.1 -> 192.168.1.1 -> 1.54.174.244`).
- **Non-Goals**:
  - Editing `scripts/workstation-daily-update.sh` (owned by active change `persist-agent-tcc-provenance-and-auto-upgrade`).

## Decisions

1. **Assign Hermes WebUI to Tailscale Serve HTTPS port `8443` while preserving OmniRoute on `443`**:
   - Running `tailscale serve --bg --https=8443 http://127.0.0.1:8787` adds a second TLS-terminated listener on `iosteam-mac-mini.tailc6b508.ts.net:8443` while keeping `iosteam-mac-mini.tailc6b508.ts.net:443` mapped to `http://127.0.0.1:20128`.
2. **Verify permanent key expiry disablement on `iosteam-mac-mini`**:
   - Both `tailscale debug netmap` (`SelfNode.KeyExpiry: null`) and the refreshed `Tailscale.app` device detail view (`Key expiry: Never`) confirm that key expiry is disabled on the rotated key (`nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108`), matching the other permanent macOS nodes (`macbook-pro-ca-l-1` and `les-mac-mini`).
3. **Do not enable `tailscale.com/cap/relay` ACL grant while double-NAT UDP `41642` is unforwarded**:
   - `iosteam-mac-mini` sits behind two NAT layers (`192.168.10.1` running `nginx/1.12.2` and `192.168.1.1` running `Boa/0.94.13` FPT GPON ONT) with `Probe: {PCP:false PMP:false UPnP:false}`.
   - Per Tailscale Peer Relay documentation (`https://tailscale.com/kb/1591/peer-relays`), granting `tailscale.com/cap/relay` when the relay's external UDP port (`1.54.174.244:41642`) is blocked by upstream NAT causes peers to attempt relay allocation before falling back to DERP. Keeping the local `udp4:41642`/`udp6:41642` listener ready while leaving the ACL capability ungranted avoids failed relay handshakes; LAN peers (`iphone-15-pro-max` at `192.168.10.67:41641`) already achieve direct UDP (`8ms` ping), and remote symmetric-NAT peers (`macbook-pro-ca-l-1` at `27.67.149.107`) route via `DERP(sin)` (`105ms`).

## Transaction & Verification Boundaries

- Verified via `tailscale serve status --json`, `tailscale debug netmap`, `tailscale ping`, and `Tailscale.app` AX inspection, then closed the `Tailscale.app` window to leave the desktop clean.
