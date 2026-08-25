# Design: Fix OmniRoute SOCKS5 Proxy Hang

## Diagnosis Sequence (Verified Facts)

1. **Container state**: `omniroute` Up 14h, status `unhealthy`, FailingStreak 18,
   every healthcheck: "Health check exceeded timeout (15s)". Redis healthy.
2. **Endpoint latency** (pre-fix): `/` 0.7s, `/login` 3.7s, `/api/v1/models` 30s timeout.
3. **Logs**: repeated `[ProxyFetch] Undici dispatcher failed ... code=PROXY_UNREACHABLE`
   plus `[CredentialHealth] ... timed out after 30s` for github, ollama-cloud, jina-ai,
   voyage-ai, and multiple openai-compatible connections.
4. **Health endpoint from inside container**: `fetch http://127.0.0.1:20128/api/monitoring/health`
   aborted at 20s — the server process itself could not answer.
5. **Event loop probe** (fresh `node -e` inside container): 19ms lag — the loop is not
   CPU-starved; requests block on I/O.
6. **DB probe**: `storage.sqlite` 14.9MB, WAL 4MB, 117 tables, `sqlite_master` query 1ms —
   database is healthy and not the bottleneck.
7. **Proxy config**: container env shows `ENABLE_SOCKS5_PROXY=true`,
   `NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=true`; `.env` section "8. OUTBOUND PROXY" has
   `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` / `NO_PROXY` all commented out.
   Startup log confirms: `[STARTUP] Global fetch proxy patch initialized`.
8. **No proxy in DB**: no `proxy_configs` table, no proxy keys in settings — the proxy
   feature was enabled purely by env flag with no endpoint configured.

## Root Cause

The global fetch proxy patch (applied at startup when `ENABLE_SOCKS5_PROXY=true`) wraps
outbound fetches through a proxy agent. With no proxy endpoint configured, each outbound
request fails slowly (`PROXY_UNREACHABLE` after socket timeout) instead of failing fast.
Ten credential health checks × 30-70s timeouts, plus quota/model-sync schedulers, create
a standing backlog that delays inbound request handling, including the healthcheck probe.

## Decision

Disable the proxy feature entirely for this deployment:

```
ENABLE_SOCKS5_PROXY=false
NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false
```

Rationale:
- This machine has direct internet access; no SOCKS5/HTTP proxy is needed.
- The proxy URL variables were already commented out — the feature was never actually
  configured, only half-enabled.
- Re-enabling later requires setting BOTH the enable flags AND a reachable
  `ALL_PROXY`/`HTTPS_PROXY` endpoint, then verifying with a container-level fetch test.

## Secondary Observation (Not Fixed Here)

First page render after a container restart takes ~10s (Next.js warms the root layout:
i18n message load ~600KB-1MB JSON per locale + deep-merge, metadata generation). Warm
requests are <2s. Concurrent requests render in parallel (not serialized), so this is
cold-start cost, not event-loop blocking. Accepted as normal for this image; the relaxed
healthcheck in `docker-compose.override.yml` (15s timeout, 120s start_period) already
covers it.

## Verification (Post-Fix)

| Endpoint | Pre-fix | Post-fix (warm) |
|---|---|---|
| `/` | 0.7s | 0.08s |
| `/login` | 11-13s | 1.5s |
| `/api/monitoring/health` | >20s timeout | 0.34s |
| POST `/api/auth/login` | 7s | 1.7s |
| Container status | unhealthy (streak 18) | healthy |

## Rollback

If a proxy is ever needed: set a reachable proxy endpoint in `.env`
(`ALL_PROXY=socks5://host:port` etc.), flip both flags back to `true`, and restart.
