# Proposal

## Why

Live telemetry and unified log inspection across `iosteam-mac-mini` (`100.70.16.83`, `/Users/androidteam`) and the remote `macbook-pro-m5` workstation (`macbook-pro-ca-l-1.tailc6b508.ts.net`, `100.101.64.56`, `/Users/vinhlk`) identified four compounding bottlenecks that cause OmniRoute requests from `macbook-pro-m5` to stall, drop, or fail when operating over remote networks:

1. **Docker Loopback Isolation vs. Missing L4 TCP Forwarders**: On `iosteam-mac-mini`, OmniRoute (`v3.8.52`) binds strictly to loopback (`127.0.0.1:20128` dashboard/inference, `127.0.0.1:20129` API bridge, and `127.0.0.1:20132` LiveWS) to avoid exposing unauthenticated inference routes on the physical LAN. Previously, `workstation-tailscale-connectivity` only configured Tailscale Serve for HTTPS on `:443` (`http://127.0.0.1:20128`) and `:8443` (`http://127.0.0.1:8787`), causing any coding CLI or SDK on `macbook-pro-m5` targeting standard ports (`http://100.70.16.83:20128`, `:20129`, `:20132`) to fail with `Connection Refused` and raw IP HTTPS requests (`https://100.70.16.83`) to fail TLS SNI verification (`SSL alert number 35`).
2. **HTTPS (`:443`) HTTP/2 Multiplexing Head-of-Line Blocking & TLS Resets over Symmetric CGNAT / `DERP(hkg)`**: When `macbook-pro-m5` connects from cellular/MiFi or Symmetric CGNAT networks (such as `116.106.97.208` / `192.168.8.172`), direct UDP hole-punching against `iosteam-mac-mini`'s non-UPnP router (`192.168.10.1` -> `1.54.174.244`) cannot complete, forcing 100% of traffic through `DERP(hkg)` (`derp-20`). Routing AI coding agents through `https://iosteam-mac-mini.tailc6b508.ts.net` (`:443`) stacks TLS 1.3 and HTTP/2 multiplexing inside Go userspace `httputil.ReverseProxy` on top of TCP-over-DERP. Under CGNAT packet loss or port rotation, `io.tailscale.ipn.macsys.network-extension` logs `http2: received GOAWAY`, `http: TLS handshake error ... read tcp 100.70.16.83:443: connection reset by peer`, and `http: proxy error: context canceled`, stalling all multiplexed streams simultaneously.
3. **MagicDNS IPv6 (`AAAA`) Resolution Delays on IPv4-Only Remote Links**: MagicDNS (`100.100.100.100`) returns both `100.70.16.83` (`A`) and `fd7a:115c:a1e0::a938:1053` (`AAAA`) for `iosteam-mac-mini.tailc6b508.ts.net`. Clients on `macbook-pro-m5` without happy-eyeballs fallback or with dual-stack DNS preference can stall attempting IPv6 socket connections before falling back to IPv4, whereas targeting the literal Tailscale IPv4 L4 TCP forwarder (`http://100.70.16.83:20128` / `http://100.70.16.83:20129`) resolves in `0ms` and responds in `26–35ms`.
4. **Background `100.101.64.56:6768` SYN-Flooding & Stale SSH Tunnels Saturating the `magicsock` DERP Queue**: On `iosteam-mac-mini`, `Orca.app` (`~/Library/Application Support/orca/orca-environments.json` paired to `ws://100.101.64.56:6768`) dials `100.101.64.56:6768` every 5 seconds while `macbook-pro-m5` is asleep or Orca is closed, and unconfigured SSH keepalives leave dead `100.70.16.83 -> 100.101.64.56:22` sockets open for 12+ hours. This continuous packet injection triggers `open-conn-track` timeouts every 5s, fires `13,347` `CallMeMaybe` disco probes, and overflows the per-peer DERP send queue (`magicsock_send_derp_dropped: 28,793`).

## What Changes

- **Formalize 5-Port Tailscale Serve Topology (Dual HTTPS + 3 L4 Raw TCP Forwarders) on `iosteam-mac-mini`**:
  - Extend `workstation-tailscale-connectivity` so `iosteam-mac-mini` (`100.70.16.83`) maintains five concurrent tailnet-only `tailscale serve` listeners while keeping Docker containers bound strictly to `127.0.0.1`:
    1. `tcp://100.70.16.83:20128` -> `127.0.0.1:20128` (L4 raw TCP forwarder for OmniRoute OpenAI `/v1/responses`, `/v1/chat/completions`, `/v1/models`, and dashboard HTTP/1.1)
    2. `tcp://100.70.16.83:20129` -> `127.0.0.1:20129` (L4 raw TCP forwarder for OmniRoute dedicated API bridge `/v1/messages` and `/v1/chat/completions`)
    3. `tcp://100.70.16.83:20132` -> `127.0.0.1:20132` (L4 raw TCP forwarder for OmniRoute LiveWS WebSocket telemetry)
    4. `https://iosteam-mac-mini.tailc6b508.ts.net:443` -> `http://127.0.0.1:20128` (HTTPS reverse proxy for browser dashboard access)
    5. `https://iosteam-mac-mini.tailc6b508.ts.net:8443` -> `http://127.0.0.1:8787` (HTTPS reverse proxy for Hermes WebUI)
- **Provide Idempotent Cross-Mac OmniRoute Client Provisioning & Verification Script (`~/Developer/scripts/setup-macbook-omniroute-client.sh`)**:
  - Create `~/Developer/scripts/setup-macbook-omniroute-client.sh` supporting `--check` (read-only audit) and `--apply` (atomic backup + convergence) modes for `macbook-pro-m5` (`macbook-pro-ca-l-1.tailc6b508.ts.net`, `100.101.64.56`, `/Users/vinhlk`):
    - **Tailscale Client & DERP Verification**: Verifies that `command -v tailscale` resolves to a non-symlink bundle-preserving shell wrapper (`! -L`, accepting `/usr/local/bin/tailscale` or `/opt/homebrew/bin/tailscale` `exec` wrapper), `BackendState: "Running"`, `KeyExpiry: null`, `RandomizeClientPort: true`, `Self.Relay: "hkg"`, and DERP relay reachability (`tailscale ping --until-direct=false -c 3 100.70.16.83`).
    - **Direct IPv4 L4 TCP Endpoint Standardization (`http://100.70.16.83:20128` / `:20129`)**: Configures `macbook-pro-m5` environment variables (`OMNIROUTE_BASE_URL="http://100.70.16.83:20128"`, `COPILOT_PROVIDER_BASE_URL="http://100.70.16.83:20128/v1"`), Claude Code zsh launchers (`omniroute` and `cockpit` in `~/.zshrc` plus `"ANTHROPIC_BASE_URL"` in `~/.claude/profiles/omniroute-pm.json` and `~/.claude/profiles/cockpit.json`, while leaving `shopapikey` on `https://api.phanmemvip.shop`), and installed coding-agent CLI configurations (`~/.omp/agent/models.yml`, `~/.pi/agent/models.json`, `~/.prime/agent/models.json`, `~/.config/opencode/opencode.json`, `~/.config/kilo/kilo.jsonc`, `~/.config/goose/config.yaml` + `custom_omniroute.json`, `~/.codex/config.toml`, `~/.config/muse/settings.json`, `~/.qwen/settings.json`, `~/.kimi-code/config.toml`, `~/.grok/config.toml`, `~/.factory/settings.json`) by matching only `(localhost|127\.0\.0\.1):(20128|20129)` so local `:51006` (Cockpit) and `:3282` (MCP Router) entries remain untouched (with mode-`0600` pre-mutation backups in `~/.omniroute/backups/`), while preserving the shared `mac-mini-1` `OMNIROUTE_API_KEY` (`id: 6a72d8ab-88db-4d49-973b-864c6cbdace5`).
    - **Cross-Node SSH Keepalive & Peer Queue Hygiene**: Configures SSH keepalive guards (`ServerAliveInterval 15`, `ServerAliveCountMax 3`, `TCPKeepAlive yes`) for `100.70.16.83` and `100.101.64.56` so CGNAT roam/sleep transitions close stale TCP sockets within 45s instead of hanging 12+ hours, and provides a clean diagnostic/remediation check for background `100.101.64.56:6768` (`Orca`) `SYN_SENT` loops that saturate `magicsock` DERP queues.
- **Update Curated LLM Wiki & Managed Skills**:
  - Update `~/Developer/wiki/entities/tailscale.md` and `~/Developer/wiki/entities/omniroute.md` to document the 5-port Tailscale Serve topology (`443`/`8443` HTTPS + `20128`/`20129`/`20132` L4 TCP) and the `macbook-pro-m5` remote client routing architecture.

## Capabilities

### New Capabilities
<!-- None; extends existing workstation-tailscale-connectivity capability -->

### Modified Capabilities
- `workstation-tailscale-connectivity`: Extend Tailscale Serve routing requirements to include raw L4 TCP forwarders (`20128`, `20129`, `20132`) alongside dual HTTPS (`443`, `8443`), and add requirements for remote `macbook-pro-m5` (`100.101.64.56`) direct IPv4 L4 TCP OmniRoute client routing (`http://100.70.16.83:20128/v1` and `:20129`) and cross-node DERP send-queue / SSH keepalive hygiene.

## Impact

- **OpenSpec Store (`~/Developer/platform/openspec-store`)**:
  - `openspec/specs/workstation-tailscale-connectivity/spec.md` (via delta spec in this change).
- **Workstation Scripts (`~/Developer/scripts/`)**:
  - `~/Developer/scripts/setup-macbook-omniroute-client.sh`: Idempotent `--check` / `--apply` cross-Mac client setup and verification script for `macbook-pro-m5` (`100.101.64.56`) connecting to `iosteam-mac-mini` (`100.70.16.83`).
- **Host & Remote Workstation Surfaces (`iosteam-mac-mini` `100.70.16.83` & `macbook-pro-m5` `100.101.64.56`)**:
  - `iosteam-mac-mini`: Tailscale Serve 5-port listener table (`443`, `8443`, `20128`, `20129`, `20132`), SSH client keepalives, and `Orca` remote peer connection hygiene.
  - `macbook-pro-m5`: Coding-agent CLI and shell launcher endpoints (`http://100.70.16.83:20128/v1` and `http://100.70.16.83:20129`) backed by `OMNIROUTE_API_KEY` (`mac-mini-1`) with mode-`0600` backups.
- **Curated Knowledge Base (`~/Developer/wiki/`)**:
  - `~/Developer/wiki/entities/tailscale.md` and `~/Developer/wiki/entities/omniroute.md`.
