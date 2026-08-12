# Design: Hermes WebUI remote access via Tailscale

## Architecture

Hermes WebUI runs as a Python server on the Mac Mini, bound to `127.0.0.1:8787`
(loopback only). Tailscale Serve accepts HTTPS connections at
`https://iosteam-mac-mini.tailc6b508.ts.net` and proxies them to the loopback
backend over plain HTTP.

```
iPhone (Hermex)
  → Tailscale WireGuard tunnel
    → MagicDNS hostname resolves to 100.70.16.83
      → tailscale serve terminates TLS, proxies to 127.0.0.1:8787
        → Hermes WebUI (Python, password auth)
```

## Security model

- **Transport**: WireGuard end-to-end encryption via Tailscale VPN
- **Termination**: Tailscale Serve provides HTTPS with automatic ACME certificate
- **Application auth**: Password-based login via `HERMES_WEBUI_PASSWORD`
- **Binding**: Loopback-only — no direct network exposure, even from Tailscale peers
- **Cookie security**: Secure flag auto-detected from TLS evidence; SameSite=Lax

## Port allocation

| Service | Container port | Host port | Binding | Owner |
|---|---|---|---|---|
| Hermes WebUI | 8787 | 8787 | 127.0.0.1 | Python (launchd) |
| Claude adapter | 8787 | 8788 | 127.0.0.1 | Docker |

The adapter was moved from host port 8787 to 8788 to free port 8787 for Hermes.
Internal container port remains 8787. Adapter consumers (cockpit.json, models.yml)
were updated to `localhost:8788`.

## Persistence

macOS launchd manages the WebUI process via
`~/Library/LaunchAgents/com.victory1908.hermes-webui.plist`. The `--foreground`
flag ensures launchd owns the long-lived server process directly (no orphan-PID
double-fork). `KeepAlive=true` restarts the server on crash. `ThrottleInterval=10`
prevents rapid restart loops.

## Constraints

- Tailscale Serve HTTPS self-curl from the same machine may timeout due to
  local hairpin behavior — this does not indicate a configuration error
- The Tailscale CLI version (1.102.2) differs from the daemon (1.98.9) — a
  client upgrade is recommended but not blocking
- Device-side acceptance (Safari / Hermex) transferred to
  `verify-hermes-webui-iphone-access` — not tested in this change
