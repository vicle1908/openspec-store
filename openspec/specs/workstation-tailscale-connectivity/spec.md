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

### Requirement: Dual-port Tailscale Serve HTTPS proxying for OmniRoute and Hermes WebUI

The workstation SHALL expose both OmniRoute (`http://127.0.0.1:20128`) and Hermes WebUI (`http://127.0.0.1:8787`) concurrently over tailnet-only HTTPS via Tailscale Serve on ports `443` and `8443` respectively.

#### Scenario: Concurrent HTTPS serve routes on ports 443 and 8443
- **WHEN** `tailscale serve status --json` is inspected
- **THEN** TCP port `443` (`HTTPS: true`) SHALL map `iosteam-mac-mini.tailc6b508.ts.net:443` `/` to `http://127.0.0.1:20128`
- **AND** TCP port `8443` (`HTTPS: true`) SHALL map `iosteam-mac-mini.tailc6b508.ts.net:8443` `/` to `http://127.0.0.1:8787`
- **AND** both loopback backends (`http://127.0.0.1:20128/api/monitoring/health` and `http://127.0.0.1:8787/health`) SHALL return HTTP `200`

### Requirement: Permanent node key expiry disablement and double-NAT peer-relay gating

The workstation node (`iosteam-mac-mini`) SHALL maintain disabled key expiry (`KeyExpiry: null` / `Never`) on its rotated node key and SHALL withhold tailnet-wide `tailscale.com/cap/relay` ACL grants while upstream double-NAT gateways lack external `UDP 41642` port forwarding.

#### Scenario: Permanent key expiry disablement is active
- **WHEN** `tailscale debug netmap` and `tailscale status --json` are queried for `SelfNode` / `Self`
- **THEN** `Self.PublicKey` SHALL be `nodekey:875e7cbbafcdf9d9498cc1c1728f5bb4e196c81e6a3889a5cf7b4c059119a108`
- **AND** `KeyExpiry` SHALL evaluate to `null` (omitted, corresponding to `Key expiry: Never` in the Tailscale client UI)

#### Scenario: Peer relay avoids blackholing under unforwarded double NAT
- **WHEN** `tailscale debug portmap` reports `{PCP:false PMP:false UPnP:false}` behind double-NAT gateways (`192.168.10.1` and `192.168.1.1`) without inbound `UDP 41642` port forwarding
- **THEN** `iosteam-mac-mini` SHALL keep local `RelayServerPort: 41642` bound on `udp4:41642` and `udp6:41642` while `tailscale debug peer-relay-servers` remains empty (`[]`) so remote symmetric-NAT peers route cleanly through `DERP(hkg)` without timeout penalties
- **AND** LAN peers (`iphone-15-pro-max` on `192.168.10.67` ephemeral UDP port) SHALL connect directly over UDP (`<10ms` RTT)

### Requirement: Randomized WireGuard client port and DERP 20 regional convergence

The workstation SHALL avoid static UDP `:41641` LAN source-port collisions by enabling WireGuard client port randomization (`RandomizeClientPort: true` via the `randomize-client-port` node attribute) and rebinding `magicsock`, and the tailnet policy SHALL suppress `DERP 3` (`sin`) in `derpMap` so Hanoi nodes converge on `DERP 20` (`hkg`) while preserving `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`.

#### Scenario: Client port randomization eliminates LAN 41641 source-port collision after rebind
- **WHEN** the `randomize-client-port` node attribute is applied in the tailnet policy and the tunnel is rebound and checked via `tailscale netcheck`
- **THEN** `tailscale debug control-knobs` SHALL report `"RandomizeClientPort": true`
- **AND** `SelfNode.Endpoints` in `tailscale debug netmap` SHALL bind an ephemeral local UDP port (`!= 41641`) that maps to a non-1024 external STUN port on `1.54.174.244` without colliding with other LAN Tailscale devices (`iphone-15-pro-max`)

#### Scenario: DERP 3 suppression converges Hanoi peers on DERP 20 while preserving peer-relay prefs
- **WHEN** `"derpMap": {"Regions": {"3": null}}` is configured in the tailnet policy and `tailscale debug netmap` and `tailscale debug prefs` are inspected
- **THEN** `DERPMap.Regions` in `tailscale debug netmap` SHALL omit region `3` (`sin`), `Self.Relay` in `tailscale status --json` SHALL be `"hkg"`, and online Hanoi peers (`Peers[].HomeDERP`) SHALL report `20`
- **AND** `tailscale debug prefs` SHALL preserve `RelayServerPort: 41642` and `RelayServerStaticEndpoints: ["1.54.174.244:41642"]`

### Requirement: Five-port Tailscale Serve HTTPS and L4 raw TCP forwarding for OmniRoute and Hermes WebUI

The workstation (`iosteam-mac-mini`, `100.70.16.83`) SHALL expose raw L4 TCP forwarders in Tailscale Serve on ports `20128` (`127.0.0.1:20128`), `20129` (`127.0.0.1:20129`), and `20132` (`127.0.0.1:20132`) alongside its tailnet-only HTTPS reverse proxies on ports `443` (`http://127.0.0.1:20128`) and `8443` (`http://127.0.0.1:8787`), while preserving strict Docker loopback bindings (`127.0.0.1:20128-20129` and `127.0.0.1:20132`).

#### Scenario: Concurrent L4 raw TCP forwarders and HTTPS proxies remain active
- **WHEN** `tailscale serve status --json` is queried on `iosteam-mac-mini`
- **THEN** `.TCP` SHALL contain active port entries for `"20128"` (`TCPForward: "127.0.0.1:20128"`), `"20129"` (`TCPForward: "127.0.0.1:20129"`), `"20132"` (`TCPForward: "127.0.0.1:20132"`), `"443"` (`HTTPS: true`), and `"8443"` (`HTTPS: true`)
- **AND** `.Web` SHALL map `iosteam-mac-mini.tailc6b508.ts.net:443` `/` to `http://127.0.0.1:20128` and `iosteam-mac-mini.tailc6b508.ts.net:8443` `/` to `http://127.0.0.1:8787`
- **AND** `docker ps --filter name=omniroute` SHALL continue binding ports `20128`, `20129`, and `20132` exclusively to `127.0.0.1`

#### Scenario: Direct IPv4 L4 TCP inference bypasses userspace HTTPS HTTP/2 head-of-line blocking
- **WHEN** a Tailnet client sends requests to `http://100.70.16.83:20128/v1/models`, `http://100.70.16.83:20128/v1/chat/completions`, `http://100.70.16.83:20128/v1/responses`, `http://100.70.16.83:20128/v1/messages`, and `http://100.70.16.83:20129/v1/chat/completions`
- **THEN** each endpoint SHALL respond with HTTP `200` over L4 TCP forwarding without invoking Tailscale Serve's `:443` userspace TLS handshake or HTTP/2 stream multiplexer
- **AND** `ws://100.70.16.83:20132` SHALL accept TCP socket connections for OmniRoute LiveWS telemetry

### Requirement: Idempotent macbook-pro-m5 remote OmniRoute client provisioning and verification

The workspace SHALL provide an idempotent provisioning script (`~/Developer/scripts/setup-macbook-omniroute-client.sh`) with `--check` and `--apply` modes to configure `macbook-pro-m5` (`100.101.64.56`, `/Users/vinhlk`) to route coding-agent CLIs and shell launchers to `iosteam-mac-mini` OmniRoute over direct Tailscale IPv4 L4 TCP (`http://100.70.16.83:20128/v1` and `:20129`).

#### Scenario: Read-only audit mode reports Tailscale and OmniRoute client convergence
- **WHEN** `~/Developer/scripts/setup-macbook-omniroute-client.sh --check` is executed locally or over SSH (`ssh vinhlk@100.101.64.56 'bash -s -- --check' < ~/Developer/scripts/setup-macbook-omniroute-client.sh`)
- **THEN** the script SHALL verify that `command -v tailscale` resolves to a regular shell wrapper file (`! -L`, never a raw symlink to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`), `BackendState == "Running"`, `Self.Online == true`, `KeyExpiry == null`, `RandomizeClientPort == true`, `Self.Relay == "hkg"`, and `tailscale ping --until-direct=false -c 3 100.70.16.83` reachability without modifying any files
- **AND** the script SHALL audit OmniRoute endpoint reachability (`http://100.70.16.83:20128/v1/models`, `:20129`, `:20132`) and installed coding-agent CLI configurations, exiting `0` when all checks pass or non-zero when drift is detected

#### Scenario: Apply mode configures direct IPv4 L4 TCP OmniRoute endpoints with mode-0600 backups
- **WHEN** `~/Developer/scripts/setup-macbook-omniroute-client.sh --apply` is executed on `macbook-pro-m5`
- **THEN** before mutating any configuration file, the script SHALL write a mode-`0600` backup under `~/.omniroute/backups/` (preserving any existing `.bak` file from an earlier run) and merge new entries into `sha256-manifest.json` without overwriting previously recorded hashes
- **AND** the script SHALL rewrite only `(localhost|127\.0\.0\.1):(20128|20129)` to `100.70.16.83:\2` across coding-agent CLI configs, `~/.zshrc` (`omniroute` and `cockpit`), and `~/.claude/profiles/{omniroute-pm,cockpit}.json` (`env.ANTHROPIC_BASE_URL`), leaving `shopapikey` (`https://api.phanmemvip.shop`), local Cockpit (`:51006`), and local MCP Router (`:3282`) untouched
- **AND** Goose (`OPENAI_BASE_PATH: chat/completions`) and Grok (`api_backend = "chat_completions"`) SHALL preserve their Chat Completions wire transport exceptions

#### Scenario: Shared mac-mini-1 credential indirection unifies cross-Mac semantic cache and hybrid memory
- **WHEN** `macbook-pro-m5` coding agents authenticate to `http://100.70.16.83:20128` or `:20129`
- **THEN** authentication SHALL resolve `OMNIROUTE_API_KEY` (`mac-mini-1`, owner ID `6a72d8ab-88db-4d49-973b-864c6cbdace5`) from `~/.zshenv` (mode `0600`) or `~/.claude/helpers/omniroute-key.sh` without embedding literal API keys in plain-text agent config files where environment indirection is supported
- **AND** requests from `macbook-pro-m5` SHALL share the unified `6a72d8ab-88db-4d49-973b-864c6cbdace5` owner partition for Layer-2 Redis Semantic Cache and Qdrant + SQLite FTS5 BM25 Hybrid Memory

### Requirement: Cross-node SSH keepalive and background peer dialer DERP queue hygiene

Both workstations (`iosteam-mac-mini` `100.70.16.83` and `macbook-pro-m5` `100.101.64.56`) SHALL enforce SSH keepalive timeouts across Tailnet addresses and audit background peer WebSocket dialers (`100.101.64.56:6768`) so CGNAT roam or sleep transitions do not leave dead TCP sockets or continuous `SYN_SENT` loops saturating `magicsock` DERP send queues.

#### Scenario: SSH keepalive bounds stale cross-node TCP sessions across CGNAT roam transitions
- **WHEN** `~/.ssh/config` is configured for Tailnet hosts (`100.70.16.83`, `iosteam-mac-mini*`, `100.101.64.56`, `macbook-pro*`)
- **THEN** `ServerAliveInterval 15`, `ServerAliveCountMax 3`, and `TCPKeepAlive yes` SHALL be active so unreachable remote SSH sessions terminate within 45 seconds rather than remaining `ESTABLISHED` across multi-hour sleep cycles

#### Scenario: Offline peer WebSocket dialer audit prevents magicsock DERP send-queue saturation
- **WHEN** `macbook-pro-m5` (`100.101.64.56`) is offline or `ws://100.101.64.56:6768` is unreachable from `iosteam-mac-mini`
- **THEN** `setup-macbook-omniroute-client.sh --check` SHALL detect repeated `SYN_SENT` / `open-conn-track: timeout opening (TCP ... => 100.101.64.56:6768)` activity and stale `100.101.64.56:22` sockets so `--apply` can clear stale sessions and prevent `magicsock_send_derp_dropped` queue overflow
