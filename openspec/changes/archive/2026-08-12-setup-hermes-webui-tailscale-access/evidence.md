# Evidence: setup-hermes-webui-tailscale-access

**Date:** 2026-08-12
**Verifier:** Hermes Agent (MoA aggregator)
**Change:** setup-hermes-webui-tailscale-access

---

## 1. LaunchAgent state

```
$ launchctl print gui/$(id -u)/com.victory1908.hermes-webui | grep -E 'state =|pid =|runs ='
    state = running
    runs = 8
    pid = 38256
```

```
$ launchctl print-disabled gui/$(id -u) | grep hermes-webui
    "com.victory1908.hermes-webui" => enabled
```

## 2. Persistence test

- **Old PID:** 38256 (received `kill` / SIGTERM)
- **New PID:** 39747 (appeared within 12 seconds)
- **Result:** PASS — launchd restarted the process automatically

## 3. Port ownership

| Port | Process | Owner | Binding | Result |
|------|---------|-------|---------|--------|
| 8787 | cpython3.11 (PID 39747) | androidteam | 127.0.0.1 | Python ✅ |
| 8788 | com.docker.backend (PID 41367) | androidteam | 127.0.0.1 | Docker ✅ |

## 4. Hermes health

```
$ curl -fsS http://127.0.0.1:8787/health
{"status": "ok", "sessions": 0, "active_streams": 0, ...}
```

## 5. Auth battery (5 tests)

| Test | Endpoint | Expected | Actual | Result |
|------|----------|----------|--------|--------|
| Health | GET /health | 200 + status=ok | 200 + status=ok | ✅ |
| Root redirect | GET / | 302→/login | 302 | ✅ |
| Unauthenticated API | GET /api/sessions | 401 | 401 | ✅ |
| Correct password login | POST /api/auth/login | 200 + set-cookie | 200 | ✅ |
| Authenticated API | GET /api/sessions (with cookie) | 200 | 200 | ✅ |
| Wrong password | POST /api/auth/login | 401 | 401 | ✅ |

## 6. Adapter checks

| Check | Result |
|-------|--------|
| `docker compose config --quiet` | OK |
| `bash -n scripts/adapter-status.sh` | OK |
| `scripts/adapter-status.sh` runtime | Container healthy on 127.0.0.1:8788 |
| `uv run --with pytest ... pytest -q` | 55 passed (0.29s) |
| `curl http://127.0.0.1:8788/health` | status=ok, adapter=claude-code-provider-adapter |

## 7. Real provider smoke test

```
$ omp --no-session --model cockpit/gpt-5.6-luna -p "Reply with exactly: pong"
pong
```

**Result:** PASS — model call routed through adapter on port 8788, inference returned correctly.

## 8. Tailscale Serve

```
$ tailscale serve status
https://iosteam-mac-mini.tailc6b508.ts.net (tailnet only)
|-- / proxy http://127.0.0.1:8787
```

**DNS:** `iosteam-mac-mini.tailc6b508.ts.net` → `100.70.16.83`

## 9. iPhone connectivity

```
$ tailscale ping -c 3 iphone-15-pro-max
pong from iphone-15-pro-max (100.118.93.42) via DERP(sin) in 372ms
pong from iphone-15-pro-max (100.118.93.42) via DERP(sin) in 168ms
pong from iphone-15-pro-max (100.118.93.42) via DERP(sin) in 328ms
direct connection not established
```

**Result:** iPhone reachable via DERP relay. Direct path not established — not a connectivity failure, just a NAT traversal state.

## 10. Negative cases

- **Same-Mac HTTPS hairpin:** `curl https://iosteam-mac-mini.tailc6b508.ts.net/health` — timed out (expected macOS hairpin behavior)
- **Direct tailnet IP:** `curl http://100.70.16.83:8787/health` — connection refused (loopback-only binding, by design)

## 11. Security posture

- `.env` permissions: `-rw-------@` (mode 600) ✅
- LaunchAgent plist contains zero password references ✅
- Password not printed in any evidence artifact ✅
- Tailscale Serve routes to loopback-only — no direct network exposure ✅

## 12. Deferred

iPhone device-side acceptance (Safari `/health`, Hermex URL/password, authenticated chat)
has been transferred to the dedicated follow-up change
`verify-hermes-webui-iphone-access`. All server-side infrastructure work in this
setup change is complete.
