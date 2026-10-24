# Proposal: Reconcile Tailscale Cask CLI Wrapper, Connection State, and Node Key Renewal

## Why

After upgrading the `tailscale-app` Homebrew Cask to `1.104.2`, the workstation's Tailscale Network Extension restarted in `BackendState: "Stopped"`, a manual symlink at `/opt/homebrew/bin/tailscale` shadowed `/usr/local/bin/tailscale` and crashed with `Tailscale/BundleIdentifiers.swift:49: Fatal error: The current bundleIdentifier is unknown to the registry`, and the node key (`iosteam-mac-mini`) was within 22 hours of its 180-day expiration (`2026-10-25T06:42:19Z`). Reconciling the CLI wrapper, bringing the tunnel and Tailscale Serve online, renewing the node key for 180 days (`2027-04-22T08:37:52Z`), and restoring custom peer-relay preferences (`RelayServerPort=41642`, `RelayServerStaticEndpoints=["1.54.174.244:41642"]`) ensures uninterrupted tailnet connectivity and governance.

## What Changes

- **Canonical CLI Wrapper Enforcement (`/usr/local/bin/tailscale`)**:
  - Remove the broken `/opt/homebrew/bin/tailscale` symlink pointing to `/Applications/Tailscale.app/Contents/MacOS/Tailscale` (which strips `Bundle.main.bundleIdentifier` when invoked outside `.app/Contents/MacOS/`).
  - Resolve `tailscale` on `PATH` exclusively through the PKG-installed `/usr/local/bin/tailscale` shell wrapper (`#!/bin/sh` invoking `/Applications/Tailscale.app/Contents/MacOS/Tailscale "$@"`), matching the single `tailscale-app` Homebrew Cask (`1.104.2`) authority.
- **Daemon & Tailscale Serve Connection Recovery**:
  - Transition the `io.tailscale.ipn.macsys.network-extension` (`1.104.2`) daemon from `BackendState: "Stopped"` to `BackendState: "Running"` via `tailscale up`.
  - Verify `utun2` IPv4/IPv6 assignment (`100.70.16.83`, `fd7a:115c:a1e0::a938:1053`), MagicDNS resolution (`tailc6b508.ts.net` via `100.100.100.100`), peer reachability, and Tailscale Serve HTTPS proxying (`https://iosteam-mac-mini.tailc6b508.ts.net` → `http://127.0.0.1:20128`).
- **Node Key Rotation & Peer-Relay Preference Persistence**:
  - Renew the node key via Tailscale's interactive reauthentication flow (`POST /localapi/v0/login-interactive` / `Tailscale Settings → Accounts → Renew…`) using the operator's `victory1908@gmail.com` Chrome profile after terminating the isolated `chrome-devtools-mcp` Chrome process (`PID 26975`) that was intercepting URL opens.
  - Re-apply `tailscale set --relay-server-port=41642 --relay-server-static-endpoints="1.54.174.244:41642"` after reauthentication to preserve custom peer-relay preferences in `ipn.Prefs`.

## Non-Goals

- Modifying `workstation-daily-update.sh` or `portable-workstation-toolchain` (currently owned by active change `persist-agent-tcc-provenance-and-auto-upgrade`).
- Installing or re-enabling the duplicate open-source `tailscale` Homebrew formula (`/opt/homebrew/opt/tailscale`), which conflicts with the `tailscale-app` GUI Cask and System Extension.
- Altering upstream router/ISP NAT hardware configuration outside the macOS host.

## Capabilities

### New Capabilities
- `workstation-tailscale-connectivity`: Defines the workstation Tailscale Cask (`tailscale-app`) CLI wrapper contract, active `BackendState: "Running"` and Tailscale Serve invariants, node key renewal lifecycle, and `ipn.Prefs` peer-relay preference preservation.

### Modified Capabilities
- None.

## Impact

- **Ownership Boundary**: Host macOS Tailscale installation (`/Applications/Tailscale.app`, `/usr/local/bin/tailscale`), Network Extension (`io.tailscale.ipn.macsys.network-extension`), and central governance documentation in `/Users/androidteam/Developer/platform/openspec-store`.
