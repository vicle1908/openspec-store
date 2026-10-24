# Design: Reconcile Tailscale Cask CLI Wrapper, Connection State, and Node Key Renewal

## Context

See `proposal.md` — Why. On macOS arm64 (`darwin 27.0.0`), Tailscale is installed via the `tailscale-app` Homebrew Cask (`1.104.2`), which deploys `/Applications/Tailscale.app` (`io.tailscale.ipn.macsys`), the Network Extension (`io.tailscale.ipn.macsys.network-extension`), and `/usr/local/bin/tailscale`.

Three operational failure modes were observed after the `1.104.1 -> 1.104.2` upgrade:
1. **Swift Bundle Identifier Crash via Symlinked CLI**:
   - `/Applications/Tailscale.app/Contents/MacOS/Tailscale` validates `Bundle.main.bundleIdentifier` against its internal registry (`Tailscale/BundleIdentifiers.swift:49`).
   - When invoked via a symlink at `/opt/homebrew/bin/tailscale`, macOS `CFBundleGetMainBundle()` resolves the bundle directory from the symlink's parent directory (`/opt/homebrew/bin`), where no `Info.plist` exists, causing `Bundle.main.bundleIdentifier` to evaluate to `nil` and crashing the process with `Fatal error: The current bundleIdentifier is unknown to the registry`.
   - Tailscale's PKG `postinstall` script (`InstallTailscaleCLI.scpt`) specifically avoids symlinks by installing `/usr/local/bin/tailscale` as a `#!/bin/sh` wrapper script that executes `/Applications/Tailscale.app/Contents/MacOS/Tailscale "$@"`.
2. **Post-Upgrade Stopped Network Extension**:
   - After `Tailscale-1.104.2-macos.pkg` replaced the system extension and the previous `1.104.1` extension was terminated, `io.tailscale.ipn.macsys.network-extension` (`1.104.2`) initialized with `BackendState: "Stopped"` (`WantRunning: false`).
3. **Imminent Node Key Expiry & Reauthentication Side Effects**:
   - Node `iosteam-mac-mini` (`nxbJehfDo421CNTRL`, created `2026-04-28T06:42:19Z`) had `Self.KeyExpiry: "2026-10-25T06:42:19Z"` (~22 hours remaining).
   - Running `chrome-devtools-mcp` had spawned a secondary `/Applications/Google Chrome.app` process (`PID 26975`) with `--user-data-dir=/Users/androidteam/.cache/chrome-devtools-mcp/chrome-profile`, which intercepted macOS `NSWorkspace` URL opens instead of the operator's authenticated Chrome instance (`PID 476`, `victory1908@gmail.com`).
   - Additionally, Tailscale reauthentication resets `RelayServerPort` and `RelayServerStaticEndpoints` in `ipn.Prefs` to `null` unless re-applied via `tailscale set`.

## Goals / Non-Goals

- **Goals**:
  - Guarantee `tailscale` CLI invocations on `PATH` use `/usr/local/bin/tailscale` without bundle-identifier crashes.
  - Restore and verify `BackendState: "Running"`, MagicDNS, peer connectivity, and Tailscale Serve (`https://iosteam-mac-mini.tailc6b508.ts.net` → `127.0.0.1:20128`).
  - Rotate the node key using the operator's `victory1908@gmail.com` Chrome profile and preserve `RelayServerPort=41642` and `RelayServerStaticEndpoints=["1.54.174.244:41642"]`.
- **Non-Goals**:
  - Editing `scripts/workstation-daily-update.sh` while active change `persist-agent-tcc-provenance-and-auto-upgrade` holds write ownership of that script.

## Decisions

1. **Use `/usr/local/bin/tailscale` shell wrapper as sole CLI entry point**:
   - Remove `/opt/homebrew/bin/tailscale` symlink rather than replacing it with a second custom wrapper in `/opt/homebrew/bin`. This keeps `/opt/homebrew/bin` clean for `brew doctor` and aligns with the `tailscale-app` cask `uninstall` stanza, which manages `/usr/local/bin/tailscale`.
2. **Terminate isolated `chrome-devtools-mcp` Chrome (`PID 26975`) before interactive OAuth**:
   - Ensuring only the operator's primary Chrome process (`PID 476`) is running guarantees macOS LaunchServices dispatches the Tailscale `AuthURL` (`https://login.tailscale.com/a/...`) into the signed-in `victory1908@gmail.com` profile.
3. **Explicitly re-apply `tailscale set` peer-relay settings post-reauth**:
   - After interactive reauthentication rotates `Self.PublicKey` and extends `Self.KeyExpiry` to `2027-04-22T08:37:52Z`, run `tailscale set --relay-server-port=41642 --relay-server-static-endpoints="1.54.174.244:41642"` and verify via `tailscale debug prefs`.

## Transaction & Verification Boundaries

- All host state mutations (`rm -f /opt/homebrew/bin/tailscale`, `tailscale up`, interactive key renewal, `tailscale set`) are idempotent and verified against live daemon state (`tailscale status --json`, `tailscale debug prefs`, `tailscale serve status --json`, `scutil --dns`).
