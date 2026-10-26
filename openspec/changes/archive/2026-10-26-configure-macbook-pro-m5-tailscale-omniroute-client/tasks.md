# Tasks

## 1. Host Tailscale Serve 5-Port Topology & Socket Hygiene (`iosteam-mac-mini`)

- [x] 1.1 Verify and enforce all five `tailscale serve` listeners on `iosteam-mac-mini` (`100.70.16.83`): L4 raw TCP forwarders `20128` (`127.0.0.1:20128`), `20129` (`127.0.0.1:20129`), and `20132` (`127.0.0.1:20132`) alongside HTTPS proxies `443` (`http://127.0.0.1:20128`) and `8443` (`http://127.0.0.1:8787`), while confirming Docker containers remain strictly bound to `127.0.0.1`.
- [x] 1.2 Configure Tailnet SSH keepalive rules (`Host 100.70.16.83 iosteam-mac-mini* 100.101.64.56 macbook-pro*` with `ServerAliveInterval 15`, `ServerAliveCountMax 3`, `TCPKeepAlive yes`) in `~/.ssh/config` and audit/clear stale `100.101.64.56:22` and `100.101.64.56:6768` sockets that saturate `magicsock` DERP send queues.

## 2. Cross-Mac OmniRoute Client Provisioning Script (`~/Developer/scripts/setup-macbook-omniroute-client.sh`)

- [x] 2.1 Implement `~/Developer/scripts/setup-macbook-omniroute-client.sh` (Bash 3.2 compatible, `set -euo pipefail`) supporting `--check` (read-only audit) and `--apply` (atomic mode-`0600` backups preserving existing `.bak` files + additive merge into `sha256-manifest.json` in `~/.omniroute/backups/` + convergence), verifying that `command -v tailscale` resolves to a non-symlink wrapper (`! -L`).
- [x] 2.2 Compute effective role once in `check_tailscale_and_serve` (`"host"` only when `100.70.16.83` is in `Self.TailscaleIPs` and `TARGET_HOME == REAL_HOME`, else `"client"`) so staging `HOME` runs exercise `tailscale ping --until-direct=false -c 3 100.70.16.83` and `--apply` on `iosteam-mac-mini` with `HOME=/Users/androidteam` refuses to overwrite the gateway host's own `localhost:20128` client configs.
- [x] 2.3 Implement `--apply` convergence for `macbook-pro-m5` matching only `(localhost|127\.0\.0\.1):(20128|20129)` across `~/.zshrc` (`OMNIROUTE_BASE_URL`, `COPILOT_PROVIDER_BASE_URL`, `omniroute`, `cockpit`), `~/.claude/profiles/{omniroute-pm,cockpit}.json` (`env.ANTHROPIC_BASE_URL`), and installed coding-agent CLI configs (`omp`, `pi`, `prime-agent`, `opencode`, `kilo`, `goose`, `codex`, `muse`, `qwen`, `kimi-code`, `grok`, `factory`), leaving `shopapikey`, `:51006`, and `:3282` untouched while preserving `goose`/`grok` Chat-Completions exceptions and `mac-mini-1` `OMNIROUTE_API_KEY` indirection.

## 3. End-to-End Verification & Knowledge Base Sync

- [x] 3.1 Verify `~/Developer/scripts/setup-macbook-omniroute-client.sh --check` on `iosteam-mac-mini` and test `HOME=<staging-dir> ~/Developer/scripts/setup-macbook-omniroute-client.sh --apply` (including a second partial-drift `--apply` run verifying additive `sha256-manifest.json` preservation) + `--check`, confirming HTTP `200` sentinel responses across `http://100.70.16.83:20128/v1/models`, `/v1/chat/completions`, `/v1/responses`, `/v1/messages`, and `http://100.70.16.83:20129/v1/chat/completions`.
- [x] 3.2 Update `~/Developer/wiki/entities/tailscale.md` (with clean blank-line separation after markdown tables) and `~/Developer/wiki/entities/omniroute.md` (plus `~/Developer/wiki/index.md` and `~/Developer/wiki/log.md`) to document the 5-port Tailscale Serve topology and `macbook-pro-m5` direct IPv4 L4 TCP client architecture, and validate with `openspec validate configure-macbook-pro-m5-tailscale-omniroute-client --strict --store openspec-store`.
