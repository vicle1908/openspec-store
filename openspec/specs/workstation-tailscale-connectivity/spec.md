# workstation-tailscale-connectivity Specification

## Purpose
Defines the workstation Tailscale Cask (`tailscale-app`) CLI wrapper contract (`/usr/local/bin/tailscale`), active Network Extension tunnel (`BackendState: "Running"`), MagicDNS and Tailscale Serve routing invariants, node key renewal lifecycle, and `ipn.Prefs` peer-relay preference preservation on macOS.

## Requirements

### Requirement: Single-authority Tailscale Cask installation and shell wrapper CLI

The workstation SHALL manage Tailscale exclusively through the `tailscale-app` Homebrew Cask (`/Applications/Tailscale.app`) and expose the `tailscale` CLI on `PATH` through the PKG-managed `/usr/local/bin/tailscale` shell wrapper script rather than a symlink outside `.app/Contents/MacOS/`.

#### Scenario: CLI invocation resolves via the bundle-preserving shell wrapper
- **WHEN** an operator or automation script invokes `tailscale version` or `tailscale status` from `PATH`
- **THEN** `command -v tailscale` SHALL resolve to `/usr/local/bin/tailscale`
- **AND** `/usr/local/bin/tailscale` SHALL execute `/Applications/Tailscale.app/Contents/MacOS/Tailscale "$@"` so `Bundle.main.bundleIdentifier` resolves to `io.tailscale.ipn.macsys` without raising a `BundleIdentifiers.swift` fatal error
- **AND** no symlink at `/opt/homebrew/bin/tailscale` or duplicate Homebrew `tailscale` formula installation SHALL shadow `/usr/local/bin/tailscale`

#### Scenario: Symlinked CLI invocation outside app bundle is rejected as a defect
- **WHEN** `/opt/homebrew/bin/tailscale` exists as a symlink to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`
- **THEN** remediation SHALL remove `/opt/homebrew/bin/tailscale` so `PATH` resolution falls through to `/usr/local/bin/tailscale`

### Requirement: Active Tailscale Network Extension tunnel, MagicDNS, and Tailscale Serve routing

The workstation's Tailscale Network Extension (`io.tailscale.ipn.macsys.network-extension`) SHALL maintain `BackendState: "Running"` with active `utun` IPv4/IPv6 addressing, MagicDNS resolution for `tailc6b508.ts.net`, and Tailscale Serve HTTPS proxying to configured loopback services.

#### Scenario: Post-upgrade tunnel and MagicDNS verification
- **WHEN** `tailscale-app` is upgraded or restarted on macOS
- **THEN** `tailscale status --json` SHALL report `BackendState: "Running"` and `Self.Online: true` with zero health warnings (`Health: []`)
- **AND** the host `utun` interface SHALL carry `100.70.16.83` (`fd7a:115c:a1e0::a938:1053`)
- **AND** `scutil --dns` SHALL register `100.100.100.100` (`fd7a:115c:a1e0::53`) as the scoped resolver for `tailc6b508.ts.net`

#### Scenario: Tailscale Serve HTTPS proxy remains active
- **WHEN** `tailscale serve status --json` is queried
- **THEN** `https://iosteam-mac-mini.tailc6b508.ts.net` (port `443`, tailnet-only) SHALL proxy `/` to `http://127.0.0.1:20128`
- **AND** the upstream loopback health endpoint `http://127.0.0.1:20128/api/monitoring/health` SHALL return HTTP `200`

### Requirement: Node key renewal and custom peer-relay preference preservation

When the workstation's Tailscale node key approaches expiration or is rotated via interactive reauthentication, the node key SHALL be renewed using the operator's authenticated browser profile and custom `tailscale set` peer-relay preferences SHALL be preserved in `ipn.Prefs`.

#### Scenario: Interactive key renewal via authenticated Chrome profile
- **WHEN** `Self.KeyExpiry` is within the renewal window and interactive reauthentication is triggered
- **THEN** no isolated automation Chrome instance (`--user-data-dir=.../chrome-devtools-mcp/chrome-profile`) SHALL intercept the macOS OAuth URL open ahead of the operator's authenticated `victory1908@gmail.com` Chrome session
- **AND** completing reauthentication SHALL rotate `Self.PublicKey` and extend `Self.KeyExpiry` by the 180-day tailnet policy window

#### Scenario: Peer-relay preferences are preserved after reauthentication
- **WHEN** interactive reauthentication completes and resets transient preference fields
- **THEN** `tailscale set --relay-server-port=41642 --relay-server-static-endpoints="1.54.174.244:41642"` SHALL be applied
- **AND** `tailscale debug prefs` SHALL report `WantRunning: true`, `RouteAll: true`, `CorpDNS: true`, `RelayServerPort: 41642`, `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`, and `AutoUpdate: {"Check": true, "Apply": true}`
