# Fix OmniRoute SOCKS5 Proxy Hang

## Problem

The OmniRoute container became unhealthy after ~14 hours of uptime:

- `/api/v1/models` timed out at 30s
- `/login` page took 11-13s TTFB
- `/api/monitoring/health` timed out (healthcheck 15s limit, 18 consecutive failures)
- Container logs flooded with `PROXY_UNREACHABLE` / `UND_ERR_SOCKET` errors
- Credential health checks all timing out (30-70s each)

## Root Cause

`~/Omniroute/.env` had `ENABLE_SOCKS5_PROXY=true` and `NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=true`
set, but the actual proxy URLs (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) were all
commented out. The app's global fetch proxy patch wrapped every outbound request through
a nonexistent SOCKS5 proxy, causing each fetch to hang until its individual timeout.

The cascade:
1. Credential health checks (10 connections) each hang 30-70s waiting for proxy
2. Background schedulers (quota, model sync, arena ELO) pile up pending fetches
3. Event loop saturates with pending socket operations
4. Inbound HTTP requests (including healthcheck) queue behind the backlog
5. Container marked unhealthy

## Fix

Disabled the SOCKS5 proxy flags in `.env` and restarted the container:

```
ENABLE_SOCKS5_PROXY=false
NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false
```

## Impact

- Deployment config only (`~/Omniroute/.env`) — no code changes
- No spec impact — this corrects a misconfiguration, not a behavior change
- Container restored to healthy; all endpoints respond in <2s after warmup
