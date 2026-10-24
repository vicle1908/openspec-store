# Design: Optimize Tailscale Client Port Randomization and Hanoi DERP 20 Convergence

## Context

See `proposal.md` — Why. Deep-dive inspection of `iosteam-mac-mini` (`100.70.16.83`, `192.168.10.78`) and `macbook-pro-ca-l-1` (`100.101.64.56`, `27.67.149.107`) established:
1. **LAN `:41641 -> :1024` NAT Port Collision & Startup Rebind Behavior**:
   - With `"RandomizeClientPort": false` in `tailscale debug control-knobs`, both `iphone-15-pro-max` (`192.168.10.67:41641`) and `iosteam-mac-mini` (`192.168.10.78:41641`) bind static UDP port `41641`.
   - `iphone-15-pro-max` claims `1.54.174.244:41641` on the outer NAT table first, causing the router to rewrite `iosteam-mac-mini` to fallback privileged port `1.54.174.244:1024`.
   - Per `tailscale/tailscale` (`wgengine/magicsock` and Issue #18328), `RandomizeClientPort` selects a random ephemeral port (`:0`) when `magicsock` initializes or rebinds its socket, and `SelfNode.Endpoints` updates after a fresh STUN check (`tailscale down && tailscale up && tailscale netcheck`).
2. **Hanoi `DERP 20` (`hkg`) vs `DERP 3` (`sin`) Split-Home Flapping**:
   - Both `iosteam-mac-mini` (FPT Hanoi) and `macbook-pro-ca-l-1` (Viettel Hanoi) have `~25 ms` RTT to `DERP 20` (`hkg`) versus `~79.5 ms` to `DERP 3` (`sin`).
   - Suppressing region `3` in the tailnet policy (`"derpMap": {"Regions": {"3": null}}`) ensures both Hanoi nodes consistently home on `DERP 20` (`hkg`) without cross-region DERP flapping.
3. **Preserving Canonical Peer-Relay Preferences & Vendor CLI Wrapper**:
   - `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]` remain configured in `ipn.Prefs` in alignment with `openspec/specs/workstation-tailscale-connectivity/spec.md`.
   - `/usr/local/bin/tailscale` is left as written by `Tailscale-<ver>-macos.pkg`'s `postinstall` script to prevent spec drift across upgrades.

## Goals / Non-Goals

- **Goals**:
  - Enable `RandomizeClientPort: true` via tailnet `nodeAttrs` (`"randomize-client-port"`) and rebind `magicsock` (`tailscale down && tailscale up && tailscale netcheck`) so `iosteam-mac-mini` binds a non-colliding ephemeral WireGuard UDP port.
  - Configure `"derpMap": {"Regions": {"3": null}}` in the tailnet policy so Hanoi nodes converge on `DERP 20` (`hkg`).
  - Keep `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]` intact in `ipn.Prefs`.
- **Non-Goals**:
  - Editing `/usr/local/bin/tailscale` to add `exec`.
  - Clearing `RelayServerPort: 41642` or `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`.
  - Modifying `scripts/workstation-daily-update.sh`.

## Decisions

1. **Add `"randomize-client-port"` in `nodeAttrs` and `"derpMap": {"Regions": {"3": null}}` in the Tailscale Policy File**:
   - Sets `"RandomizeClientPort": true` in `tailscale debug control-knobs` and removes `DERP 3` (`sin`) from the tailnet DERP map so Hanoi nodes stay pinned to `DERP 20` (`hkg`).
2. **Cycle/Rebind `magicsock` and Run `tailscale netcheck`**:
   - Forces `magicsock` to drop static port `41641`, bind an ephemeral high UDP port, and publish the updated STUN endpoint to `SelfNode.Endpoints`, while verifying `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]` remain set.

## Transaction & Verification Boundaries

- Policy updates in the Tailscale Admin Console (`https://login.tailscale.com/admin/acls/file`) and local tunnel rebind (`tailscale down && tailscale up && tailscale netcheck`) are verified via `tailscale debug control-knobs`, `tailscale debug netmap`, and `tailscale debug prefs`.
