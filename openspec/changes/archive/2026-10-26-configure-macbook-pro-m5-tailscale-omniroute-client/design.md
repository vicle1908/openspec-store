# Design

## Context

`iosteam-mac-mini` (`100.70.16.83`, `/Users/androidteam`) hosts the canonical OmniRoute (`v3.8.52`) gateway stack (`omniroute`, `omniroute-qdrant`, `omniroute-redis`) on Docker loopback ports `127.0.0.1:20128` (dashboard + OpenAI/Anthropic inference), `127.0.0.1:20129` (dedicated API bridge), and `127.0.0.1:20132` (`LiveWS` telemetry). The remote developer laptop `macbook-pro-m5` (`macbook-pro-ca-l-1.tailc6b508.ts.net`, `100.101.64.56`, `/Users/vinhlk`) consumes this gateway over Tailscale.

Live diagnostics on `2026-10-26` revealed why `macbook-pro-m5` experienced intermittent slowness, stream drops, and connection refusals:
1. `macbook-pro-m5` frequently operates behind 4G/5G cellular or MiFi Symmetric CGNAT (`116.106.97.208` / `192.168.8.172`), while `iosteam-mac-mini` sits behind an unforwarded NAT gateway (`192.168.10.1` -> `1.54.174.244`, `{PCP:false, PMP:false, UPnP:false}`). Because neither side has an inbound port mapping, 100% of WireGuard traffic between the two machines routes over TCP-based `DERP(hkg)` (`derp-20`, ~36ms base latency).
2. Routing `macbook-pro-m5` coding agents through Tailscale Serve's `:443` HTTPS reverse proxy (`https://iosteam-mac-mini.tailc6b508.ts.net`) introduced userspace Go TLS termination and HTTP/2 single-connection stream multiplexing on top of TCP-over-DERP. Whenever the CGNAT link rotated ports or dropped packets, HTTP/2 suffered head-of-line blocking across all active agent streams until `http2: received GOAWAY` or `http: TLS handshake error ... read tcp 100.70.16.83:443: connection reset by peer` aborted every in-flight turn.
3. Furthermore, `Orca.app` (`PID 92094` on `iosteam-mac-mini`) dialed `ws://100.101.64.56:6768` every 5 seconds while `macbook-pro-m5` was asleep/offline, and a 12.5-hour stale `ssh vinhlk@100.101.64.56` socket remained `ESTABLISHED`, generating continuous `open-conn-track` timeouts, `13,347` `CallMeMaybe` disco probes, and `28,793` dropped DERP send-queue packets (`magicsock_send_derp_dropped`).

## Goals / Non-Goals

**Goals:**
- Expose L4 raw TCP forwarders (`20128`, `20129`, `20132`) via `tailscale serve` on `iosteam-mac-mini` alongside existing `:443` and `:8443` HTTPS proxies while keeping Docker ports bound exclusively to `127.0.0.1`.
- Provide an idempotent `--check` / `--apply` provisioning and verification script (`~/Developer/scripts/setup-macbook-omniroute-client.sh`) that configures `macbook-pro-m5` coding-agent CLIs, shell environment variables, and Claude Code launchers to connect directly via IPv4 L4 TCP (`http://100.70.16.83:20128/v1` and `http://100.70.16.83:20129`).
- Preserve unified cross-Mac Layer-2 Redis Semantic Cache and Qdrant+BM25 Hybrid Memory pooling by authenticating `macbook-pro-m5` requests with the shared `mac-mini-1` `OMNIROUTE_API_KEY` (`id: 6a72d8ab-88db-4d49-973b-864c6cbdace5`).
- Enforce cross-node SSH keepalives (`ServerAliveInterval 15`, `ServerAliveCountMax 3`) and background peer socket hygiene to prevent `magicsock` DERP send-queue exhaustion.

**Non-Goals:**
- Exposing Docker ports (`20128`, `20129`, `20132`, `6333`, `6334`) on `0.0.0.0` or the physical LAN (`192.168.10.0/24`).
- Modifying OmniRoute combo definitions (`gemini-4-argon*`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`, `muse-spark-1.3`), compression settings, or container runtime patches in `~/Omniroute/scripts/container-entrypoint-compat.sh`.
- Exposing Qdrant (`6333`/`6334`) or Redis (`6379`) over Tailscale Serve.

## Decisions

### 1. L4 Raw TCP Forwarding (`20128`, `20129`, `20132`) vs. `:443` HTTPS Reverse Proxy for Coding Agents
- **Decision**: Maintain `:443` HTTPS (`https://iosteam-mac-mini.tailc6b508.ts.net`) for web browser dashboard access and `:8443` HTTPS for Hermes WebUI, while registering L4 raw TCP forwarders (`tailscale serve --bg --tcp=20128 127.0.0.1:20128`, `--tcp=20129 127.0.0.1:20129`, `--tcp=20132 127.0.0.1:20132`) for all coding-agent CLI and SDK traffic from `macbook-pro-m5`.
- **Rationale**:
  - WireGuard already encrypts and authenticates all Tailnet packets (`ChaCha20-Poly1305`). Adding a second TLS 1.3 + HTTP/2 layer inside `tailscaled` on `:443` creates HTTP/2 single-TCP-connection head-of-line blocking over `DERP(hkg)` and fails with TLS alert 35 whenever a client dials the raw Tailscale IP.
  - L4 TCP forwarding on `:20128` and `:20129` streams raw bytes directly to OmniRoute's Node.js HTTP/1.1 server, allowing independent TCP connections per concurrent subagent turn, zero TLS handshake overhead, and `26–35ms` catalog latency.
- **Alternatives Considered**:
  - *Binding Docker to `0.0.0.0:20128`*: Rejected because `REQUIRE_API_KEY=false` would expose keyless inference to untrusted devices on the physical LAN.

### 2. Literal Tailscale IPv4 (`100.70.16.83`) vs. MagicDNS Hostname in Client Configs
- **Decision**: Configure coding-agent CLIs on `macbook-pro-m5` to use the literal Tailscale IPv4 address (`http://100.70.16.83:20128/v1` and `http://100.70.16.83:20129`).
- **Rationale**:
  - MagicDNS (`100.100.100.100`) publishes both `A` (`100.70.16.83`) and `AAAA` (`fd7a:115c:a1e0::a938:1053`) records. Node.js/Bun/Rust/Python clients on cellular or CGNAT links without IPv6 routing can stall on `AAAA` connection attempts or DNS resolution timeouts when switching networks.
  - The Tailscale IPv4 address `100.70.16.83` is static for the node identity (`iosteam-mac-mini`), requires zero DNS lookup, and routes deterministically into `utun`.

### 3. Idempotent Provisioning Script (`~/Developer/scripts/setup-macbook-omniroute-client.sh`)
- **Decision**: Encapsulate all `macbook-pro-m5` client checks, backups, and config updates in `~/Developer/scripts/setup-macbook-omniroute-client.sh` taking only `--check` and `--apply` (supporting standard `HOME` environment override for isolated staging tests and `ssh vinhlk@100.101.64.56 'bash -s -- --check'` for remote execution).
- **Rationale**:
  - Follows the minimal two-flag convention of `~/Developer/scripts/maccy-setup.sh`.
  - Scopes URL replacement strictly to `(localhost|127\.0\.0\.1):(20128|20129)` across coding-agent configs, `~/.zshrc` (`omniroute` and `cockpit`), and `~/.claude/profiles/{omniroute-pm,cockpit}.json` (`env.ANTHROPIC_BASE_URL`), leaving `shopapikey` (`https://api.phanmemvip.shop`), local Cockpit (`:51006`), and local MCP Router (`:3282`) untouched.
  - Enforces mode-`0600` pre-mutation backups and additive SHA-256 manifest merging (`sha256-manifest.json`, preserving prior `.bak` files across repeated `--apply` runs) in `~/.omniroute/backups/configure-macbook-pro-m5-tailscale-omniroute-client/`, preserves Rust Serde Chat-Completions exceptions (`goose` and `grok`), and verifies end-to-end sentinel inference across `/v1/responses`, `/v1/chat/completions`, and `/v1/messages`.

### 4. Cross-Node SSH Keepalives & Background Socket Hygiene
- **Decision**: Configure `Host 100.70.16.83 iosteam-mac-mini* 100.101.64.56 macbook-pro*` in `~/.ssh/config` with `ServerAliveInterval 15`, `ServerAliveCountMax 3`, and `TCPKeepAlive yes`, and include a socket health check in `setup-macbook-omniroute-client.sh` that flags/clears hung SSH processes and `SYN_SENT` loops to `:6768`.
- **Rationale**:
  - Prevents dead TCP sessions from lingering 12+ hours after laptop lid-close and stops `magicsock` from overflowing its per-peer DERP packet queue while `macbook-pro-m5` is offline.

## Risks / Trade-offs

- **Remote Node Sleep / Offline Window During Central Apply**:
  - *Risk*: `macbook-pro-m5` (`100.101.64.56`) may be asleep (`RxBytes: 0` on DERP) when central tasks run on `iosteam-mac-mini`.
  - *Mitigation*: `setup-macbook-omniroute-client.sh` is verified locally with `--check` and isolated staging `HOME` overrides on `iosteam-mac-mini`, and executes on `macbook-pro-m5` directly or via `ssh vinhlk@100.101.64.56 'bash -s -- --apply' < ~/Developer/scripts/setup-macbook-omniroute-client.sh`.
- **Dual-Context Config Sync (Local `iosteam-mac-mini` vs. Remote `macbook-pro-m5`)**:
  - *Risk*: Running `--apply` accidentally on `iosteam-mac-mini` could rewrite `iosteam-mac-mini`'s own `localhost:20128` configs to `100.70.16.83:20128`.
  - *Mitigation*: `check_tailscale_and_serve` computes the effective role once (`"host"` only when `Self.TailscaleIPs` contains `100.70.16.83` and `TARGET_HOME == REAL_HOME`, otherwise `"client"`), so staging `HOME` runs exercise the full client path (including `tailscale ping`) and `--apply` refuses to overwrite the gateway host's own `/Users/androidteam` configs.
