# Proposal: Optimize Tailscale Client Port Randomization and Hanoi DERP 20 Convergence

## Why

Live `magicsock` and NAT telemetry between `iosteam-mac-mini` (`100.70.16.83`, FPT Hanoi) and `macbook-pro-ca-l-1` (`100.101.64.56`, Viettel Hanoi) revealed two tailnet policy issues: (1) static UDP source port `41641` on `iosteam-mac-mini` collides on the LAN NAT table with `iphone-15-pro-max` (`192.168.10.67:41641`), forcing the router to rewrite `iosteam-mac-mini`'s external WireGuard endpoint to privileged port `1.54.174.244:1024`; and (2) Hanoi nodes intermittently split-home between `DERP 20` (`hkg`, `25 ms`) and `DERP 3` (`sin`, `79.5 ms`), adding cross-region relay latency when direct connections or peer-relay handshakes are negotiating.

## What Changes

- **Enable WireGuard Client Port Randomization (`randomize-client-port`) with Socket Rebind**:
  - Add `"randomize-client-port"` to `nodeAttrs` (targeting `autogroup:member`) in the tailnet policy file (`https://login.tailscale.com/admin/acls/file`), then cycle/rebind Tailscale and run `tailscale netcheck` so `tailscale debug control-knobs` sets `"RandomizeClientPort": true` and `magicsock` binds a unique high ephemeral UDP port instead of colliding on static port `41641` (`-> :1024`).
- **Pin Hanoi Nodes to DERP 20 (`hkg`) by Suppressing DERP 3 (`sin`) in `derpMap`**:
  - Configure `"derpMap": {"Regions": {"3": null}}` at the top level of the tailnet policy file so both Hanoi nodes (`iosteam-mac-mini` and `macbook-pro-ca-l-1`) converge on `DERP 20` (`hkg`, `25 ms`) without `DERP 3` (`sin`) split-home flapping.
- **Preserve Canonical Peer-Relay Preferences (`RelayServerPort: 41642`, `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`)**:
  - Keep `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]` intact in `ipn.Prefs`, aligned with `openspec/specs/workstation-tailscale-connectivity/spec.md`.

## Non-Goals

- Modifying `/usr/local/bin/tailscale` to add `exec`: `Tailscale-<ver>-macos.pkg`'s `postinstall` script overwrites `/usr/local/bin/tailscale` without `exec` on every `tailscale-app` Cask upgrade, so leaving the vendor-generated wrapper unmodified avoids spec drift.
- Clearing or disabling `RelayServerPort: 41642` or `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`.
- Modifying `scripts/workstation-daily-update.sh` or `config/script-provenance-manifest.tsv`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `workstation-tailscale-connectivity`: Adds the requirement for `RandomizeClientPort: true` (`randomize-client-port` node attribute with socket rebind) to prevent LAN `:41641 -> :1024` NAT port collisions and `derpMap` region `3` (`sin`) suppression so Hanoi nodes converge on `DERP 20` (`hkg`), while preserving `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`.

## Impact

- **Ownership Boundary**: Tailscale tailnet policy (`nodeAttrs` and `derpMap`), local host `magicsock` socket binding and `ipn.Prefs`, `openspec/specs/workstation-tailscale-connectivity/spec.md` in `/Users/androidteam/Developer/platform/openspec-store`, and `wiki/entities/tailscale.md` in `/Users/androidteam/Developer/wiki`.
