# Evidence: configure-macbook-pro-m5-tailscale-omniroute-client

**Date:** 2026-10-26
**Change:** `configure-macbook-pro-m5-tailscale-omniroute-client`

---

## 1. Host 5-Port Tailscale Serve Topology & Docker Loopback Binding (`Task 1.1`)

Verified `tailscale serve status --json` and `docker ps --filter name=omniroute` on `iosteam-mac-mini` (`100.70.16.83`):

```json
{
  "TCP": {
    "20128": {
      "TCPForward": "127.0.0.1:20128"
    },
    "20129": {
      "TCPForward": "127.0.0.1:20129"
    },
    "20132": {
      "TCPForward": "127.0.0.1:20132"
    },
    "443": {
      "HTTPS": true
    },
    "8443": {
      "HTTPS": true
    }
  },
  "Web": {
    "iosteam-mac-mini.tailc6b508.ts.net:443": {
      "Handlers": {
        "/": {
          "Proxy": "http://127.0.0.1:20128"
        }
      }
    },
    "iosteam-mac-mini.tailc6b508.ts.net:8443": {
      "Handlers": {
        "/": {
          "Proxy": "http://127.0.0.1:8787"
        }
      }
    }
  }
}
```

```text
omniroute        127.0.0.1:20128-20129->20128-20129/tcp, 127.0.0.1:20132->20132/tcp
omniroute-qdrant 127.0.0.1:6333-6334->6333-6334/tcp
omniroute-redis  6379/tcp
```

---

## 2. Tailnet SSH Keepalives & Stale Socket Remediation (`Task 1.2`)

Configured `~/.ssh/config` (`mode 0600`) with:

```sshconfig
Host 100.70.16.83 iosteam-mac-mini* 100.101.64.56 macbook-pro*
    ServerAliveInterval 15
    ServerAliveCountMax 3
    TCPKeepAlive yes
```

Terminated the 12.5-hour stale `ssh vinhlk@100.101.64.56` socket (`PID 30243`, `100.70.16.83:64315 -> 100.101.64.56:22`) and audited background `Orca` (`100.101.64.56:6768`) `SYN_SENT` activity.

---

## 3. Provisioning Script Implementation & Verification (`Tasks 2.1, 2.2, 2.3, 3.1`)

Implemented `/Users/androidteam/Developer/scripts/setup-macbook-omniroute-client.sh` (`304` lines, Bash 3.2 compatible, `set -euo pipefail`) and executed:

1. **Host `--check` verification (`iosteam-mac-mini`)**:
   ```text
   $ /bin/bash /Users/androidteam/Developer/scripts/setup-macbook-omniroute-client.sh --check
   [omniroute-client] Verified Tailscale CLI wrapper: /usr/local/bin/tailscale (non-symlink).
   [omniroute-client] Tailscale node healthy (role=host, BackendState=Running, KeyExpiry=Never, RandomizeClientPort=true, Relay=hkg).
   [omniroute-client] Verified 5-port Tailscale Serve topology on host (20128, 20129, 20132 L4 TCP + 443, 8443 HTTPS).
   [omniroute-client] Verified http://100.70.16.83:20128/v1/models -> HTTP 200 (1055 models).
   [omniroute-client] Verified http://100.70.16.83:20129/v1/models -> HTTP 200.
   [omniroute-client] Verified tcp://100.70.16.83:20132 LiveWS listener -> socket connected.
   [omniroute-client] Verified SSH keepalive rules in /Users/androidteam/.ssh/config.
   [omniroute-client] Verified 16 configuration file(s) (role=host, mode=check).
   [omniroute-client] SUCCESS (check)
   ```

2. **Host-self `--apply` guard verification**:
   ```text
   $ /bin/bash /Users/androidteam/Developer/scripts/setup-macbook-omniroute-client.sh --apply
   [omniroute-client] ERROR: Refusing to run --apply on OmniRoute host (100.70.16.83) with HOME=/Users/androidteam.
   HOST_GUARD_VERIFIED
   ```

3. **Isolated staging `HOME` verification across all 16 client files (including two-pass `--apply` manifest & `.bak` preservation)**:
   - Pre-apply `--check` exited `1` (detected drift across all 16 files).
   - Pass 1 `--apply` exited `0`, created 16 mode-`0600` backups + `sha256-manifest.json` under `.omniroute/backups/configure-macbook-pro-m5-tailscale-omniroute-client/`, rewrote `(localhost|127\.0\.0\.1):(20128|20129)` to `100.70.16.83:\1`, and preserved `shopapikey` (`https://api.phanmemvip.shop`), local Cockpit (`:51006`), local MCP Router (`:3282`), `goose` (`chat/completions`), and `grok` (`chat_completions`).
   - Pass 2 `--apply` (after simulating single-file drift on `.config/muse/settings.json`) exited `0` and preserved all 16 entries in `sha256-manifest.json` and the original `.bak` file byte-for-byte (`TWO-PASS STAGING & MANIFEST PRESERVATION VERIFIED`).
   - Post-apply `--check` exited `0`.

4. **End-to-End Sentinel Inference Probes over Tailscale IP (`100.70.16.83`)**:
   - `POST http://100.70.16.83:20128/v1/chat/completions` (`gemini-3.8-flash-high`) -> `HTTP 200` (`content: "HELLO_FROM_TAILSCALE"`)
   - `POST http://100.70.16.83:20128/v1/responses` (`gemini-3.8-flash-high`) -> `HTTP 200` (`status: "completed"`)
   - `POST http://100.70.16.83:20128/v1/messages` (`gemini-3.8-flash-high`) -> `HTTP 200`
   - `POST http://100.70.16.83:20129/v1/chat/completions` (`gemini-3.8-flash-high`) -> `HTTP 200` (`content: "BRIDGE_PORT_20129_OK..."`)
   - `GET http://100.70.16.83:20128/v1/models` -> `HTTP 200` (`1,055` models, `0.035s`)
   - `GET http://100.70.16.83:20129/v1/models` -> `HTTP 200` (`1,055` models, `0.026s`)

---

## 4. Curated LLM Wiki & Strict OpenSpec Validation (`Task 3.2`)

- Updated `/Users/androidteam/Developer/wiki/entities/tailscale.md`, `/Users/androidteam/Developer/wiki/entities/omniroute.md`, `/Users/androidteam/Developer/wiki/index.md`, and `/Users/androidteam/Developer/wiki/log.md`.
- Verified `openspec validate configure-macbook-pro-m5-tailscale-omniroute-client --strict --json --store openspec-store` -> `valid: true`, `0` issues.
