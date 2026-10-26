# workstation-tailscale-connectivity Specification Delta

## ADDED Requirements

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
