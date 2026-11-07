# workstation-tailscale-connectivity Delta Specification

## MODIFIED Requirements

### Requirement: Single-authority Tailscale Cask installation and shell wrapper CLI

`iosteam-mac-mini` (`100.70.16.83`) SHALL manage Tailscale via the `tailscale-app` Cask (`/usr/local/bin/tailscale` wrapper), and `macbook-pro-m5` (`100.106.143.78`) SHALL run standalone `tailscaled-on-macOS` (`/Library/LaunchDaemons/sh.brew.tailscale.plist`) with socket-aware CLI wrappers that never symlink directly to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`.

#### Scenario: CLI invocation resolves via the bundle-preserving shell wrapper
- **WHEN** an operator or automation script invokes `tailscale version` or `tailscale status` from `PATH` on `iosteam-mac-mini` or `macbook-pro-m5`
- **THEN** on `iosteam-mac-mini`, `command -v tailscale` SHALL resolve to `/usr/local/bin/tailscale` executing `/Applications/Tailscale.app/Contents/MacOS/Tailscale "$@"` so `Bundle.main.bundleIdentifier` resolves to `io.tailscale.ipn.macsys` without raising a `BundleIdentifiers.swift` fatal error
- **AND** on `macbook-pro-m5`, `command -v tailscale` SHALL resolve to `/opt/homebrew/bin/tailscale` or `/usr/local/bin/tailscale` targeting `/opt/homebrew/opt/tailscale/bin/tailscale --socket=/var/run/tailscaled.socket`
- **AND** neither workstation SHALL have a symlink pointing directly to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`

#### Scenario: Symlinked CLI invocation outside app bundle is rejected as a defect
- **WHEN** `/opt/homebrew/bin/tailscale` or `/usr/local/bin/tailscale` exists as a symlink whose target resolves to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`
- **THEN** `setup-macbook-omniroute-client.sh --check` SHALL report a CLI wrapper defect and exit non-zero

### Requirement: Active Tailscale Network Extension tunnel, MagicDNS, and Tailscale Serve routing

The workstations (`iosteam-mac-mini` `100.70.16.83` and `macbook-pro-m5` `100.106.143.78`) SHALL maintain `BackendState: "Running"` with active `utun` addressing, MagicDNS resolution for `tailc6b508.ts.net`, Tailscale Serve HTTPS proxying, and L4 TCP forwarding for OmniRoute (`:20128`, `:20129`, `:20132` on `iosteam-mac-mini`) and AgentMemory mesh traffic (`:3111` on both nodes).

#### Scenario: Post-upgrade tunnel and MagicDNS verification
- **WHEN** Tailscale is upgraded or restarted on `iosteam-mac-mini`
- **THEN** `tailscale status --json` SHALL report `BackendState: "Running"` and `Self.Online: true` with zero health warnings (`Health: []`)
- **AND** the host `utun` interface SHALL carry `100.70.16.83` (`fd7a:115c:a1e0::a938:1053`)
- **AND** `scutil --dns` SHALL register `100.100.100.100` (`fd7a:115c:a1e0::53`) as the scoped resolver for `tailc6b508.ts.net`

#### Scenario: Tailscale Serve HTTPS proxy remains active
- **WHEN** `tailscale serve status --json` is queried on `iosteam-mac-mini`
- **THEN** `https://iosteam-mac-mini.tailc6b508.ts.net` (port `443`, tailnet-only) SHALL proxy `/` to `http://127.0.0.1:20128`
- **AND** the upstream loopback health endpoint `http://127.0.0.1:20128/api/monitoring/health` SHALL return HTTP `200`

#### Scenario: Tailscale Serve exposes raw L4 TCP port 3111 for AgentMemory mesh traffic
- **WHEN** `tailscale serve status --json` is inspected on `iosteam-mac-mini` or `macbook-pro-m5` (`macbook-pro-ca-l-1`)
- **THEN** TCP port `3111` SHALL be actively mapped to `127.0.0.1:3111` under the tailnet-only listener table (`tcp://100.70.16.83:3111` and `tcp://100.106.143.78:3111`)
- **AND** remote tailnet peers SHALL be able to establish TCP connections to `:3111` without physical LAN interfaces exposing the port

### Requirement: Five-port Tailscale Serve HTTPS and L4 raw TCP forwarding for OmniRoute and Hermes WebUI

The workstation (`iosteam-mac-mini`, `100.70.16.83`) SHALL expose raw L4 TCP forwarders in Tailscale Serve on ports `20128` (`127.0.0.1:20128`), `20129` (`127.0.0.1:20129`), `20132` (`127.0.0.1:20132`), and `3111` (`127.0.0.1:3111`) alongside its tailnet-only HTTPS reverse proxies on ports `443` (`http://127.0.0.1:20128`) and `8443` (`http://127.0.0.1:8787`), while preserving strict Docker loopback bindings (`127.0.0.1:20128-20129` and `127.0.0.1:20132`).

#### Scenario: Concurrent L4 raw TCP forwarders and HTTPS proxies remain active
- **WHEN** `tailscale serve status --json` is queried on `iosteam-mac-mini`
- **THEN** `.TCP` SHALL contain active port entries for `"20128"` (`TCPForward: "127.0.0.1:20128"`), `"20129"` (`TCPForward: "127.0.0.1:20129"`), `"20132"` (`TCPForward: "127.0.0.1:20132"`), `"3111"` (`TCPForward: "127.0.0.1:3111"`), `"443"` (`HTTPS: true`), and `"8443"` (`HTTPS: true`)
- **AND** `.Web` SHALL map `iosteam-mac-mini.tailc6b508.ts.net:443` `/` to `http://127.0.0.1:20128` and `iosteam-mac-mini.tailc6b508.ts.net:8443` `/` to `http://127.0.0.1:8787`
- **AND** `docker ps --filter name=omniroute` SHALL continue binding ports `20128`, `20129`, and `20132` exclusively to `127.0.0.1`

#### Scenario: Direct IPv4 L4 TCP inference bypasses userspace HTTPS HTTP/2 head-of-line blocking
- **WHEN** a Tailnet client sends requests to `http://100.70.16.83:20128/v1/models`, `http://100.70.16.83:20128/v1/chat/completions`, `http://100.70.16.83:20128/v1/responses`, `http://100.70.16.83:20128/v1/messages`, and `http://100.70.16.83:20129/v1/chat/completions`
- **THEN** each endpoint SHALL respond with HTTP `200` over L4 TCP forwarding without invoking Tailscale Serve's `:443` userspace TLS handshake or HTTP/2 stream multiplexer
- **AND** `ws://100.70.16.83:20132` SHALL accept TCP socket connections for OmniRoute LiveWS telemetry

### Requirement: Idempotent macbook-pro-m5 remote OmniRoute client provisioning and verification

The workspace SHALL provide an idempotent provisioning script (`~/Developer/scripts/setup-macbook-omniroute-client.sh`) with `--check` and `--apply` modes to configure `macbook-pro-m5` (`100.106.143.78`, `/Users/vinhlk`) to route coding-agent CLIs and shell launchers to `iosteam-mac-mini` OmniRoute over direct Tailscale IPv4 L4 TCP (`http://100.70.16.83:20128/v1` and `:20129`).

#### Scenario: Read-only audit mode reports Tailscale and OmniRoute client convergence
- **WHEN** `~/Developer/scripts/setup-macbook-omniroute-client.sh --check` is executed locally on `iosteam-mac-mini` or on `macbook-pro-m5`
- **THEN** the script SHALL verify that `command -v tailscale` resolves to an executable that is never a raw symlink to `/Applications/Tailscale.app/Contents/MacOS/Tailscale`, `BackendState == "Running"`, `Self.Online == true`, `KeyExpiry == null`, `RandomizeClientPort == true`, `Self.Relay` is in `("hkg", "tok")`, and `tailscale ping --until-direct=false -c 3 100.70.16.83` reachability without modifying any files
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

Both workstations (`iosteam-mac-mini` `100.70.16.83` and `macbook-pro-m5` `100.106.143.78`) SHALL enforce SSH keepalive timeouts across Tailnet addresses and audit background peer WebSocket dialers (`100.106.143.78:6768` and legacy `100.101.64.56:6768`) so CGNAT roam or sleep transitions do not leave dead TCP sockets or continuous `SYN_SENT` loops saturating `magicsock` DERP send queues.

#### Scenario: SSH keepalive bounds stale cross-node TCP sessions across CGNAT roam transitions
- **WHEN** `~/.ssh/config` is configured for Tailnet hosts (`100.70.16.83`, `iosteam-mac-mini*`, `100.106.143.78`, `100.101.64.56`, `macbook-pro*`)
- **THEN** `ServerAliveInterval 15`, `ServerAliveCountMax 3`, and `TCPKeepAlive yes` SHALL be active so unreachable remote SSH sessions terminate within 45 seconds rather than remaining `ESTABLISHED` across multi-hour sleep cycles

#### Scenario: Offline peer WebSocket dialer audit prevents magicsock DERP send-queue saturation
- **WHEN** `macbook-pro-m5` (`100.106.143.78`) is offline or `ws://100.106.143.78:6768` is unreachable from `iosteam-mac-mini`
- **THEN** `setup-macbook-omniroute-client.sh --check` SHALL detect repeated `SYN_SENT` / `open-conn-track: timeout opening (TCP ... => 100.106.143.78:6768)` activity and stale `:22` sockets so `--apply` can clear stale sessions and prevent `magicsock_send_derp_dropped` queue overflow

## ADDED Requirements

### Requirement: Zero-configuration Tailscale Split DNS and surgical /32 subnet routing from macbook-pro-m5

The workstation mesh SHALL allow `iosteam-mac-mini` (`100.70.16.83`, `AcceptDNS: true`, `RouteAll: true`) and authorized mobile/desktop peers to resolve internal SHB domains (`shb.com.vn`, `shbho.shb.vn`, `shb.vn` via `10.4.82.20`, `10.4.82.21`, `10.4.82.23`) and reach approved internal `/32` SHB endpoints advertised by `macbook-pro-m5` (`macbook-pro-ca-l-1`, `100.106.143.78`) over userspace `gVisor netstack` without local `/etc/hosts` or static route overrides on peer nodes.

#### Scenario: Zero-configuration internal host DNS resolution and HTTPS reachability from iosteam-mac-mini
- **WHEN** `macbook-pro-m5` (`100.106.143.78`) has an active corporate Ethernet attachment (`en7`/`en8`) and advertises its `/32` DNS and internal host routes (`10.4.82.20/32`, `10.4.82.21/32`, `10.4.82.23/32`, `172.16.3.10/32`, `172.16.3.11/32`, `10.4.88.24/32`, `10.4.88.33/32`, `10.4.88.142/32`, `10.4.98.189/32`, `10.4.98.201/32`, `10.4.99.37/32`, `10.4.99.40/32`)
- **THEN** `tailscale dns query gitlab-nhs.shb.com.vn A` on `iosteam-mac-mini` SHALL return `172.16.3.10` via internal resolvers `10.4.82.20`, `10.4.82.21`, and `10.4.82.23`
- **AND** `route -n get 172.16.3.10` on `iosteam-mac-mini` SHALL route via the Tailscale `utun` interface
- **AND** `curl -skI https://gitlab-nhs.shb.com.vn` on `iosteam-mac-mini` SHALL succeed with an HTTP `200` or `302` response while `sysctl net.inet.ip.forwarding` on `macbook-pro-m5` remains `0`
