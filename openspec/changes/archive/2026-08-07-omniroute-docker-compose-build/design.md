# Design: OmniRoute Docker Compose

## Architecture

```
macOS Login
  └─ Docker Desktop (AutoStart: True)
       └─ docker compose --profile base up -d --no-build
            ├─ redis:7-alpine       ──→  port 6379  (rate limiter)
            └─ diegosouzapw/omniroute:latest  ──→  port 20128 (everything)

Single port 20128: dashboard + API + WebSocket
```

## Image Strategy

`docker-compose.override.yml` overrides the upstream `omniroute-base` service:
- Replaces `image: omniroute:base` (local build) with `image: diegosouzapw/omniroute:latest` (Docker Hub)
- The `build:` section is inherited but ignored with `--no-build`

## Port Strategy

Single-port mode: all services on 20128.
- `PORT=20128` — main server port
- `API_PORT=20128` — collapse API to same port
- `LIVE_WS_PORT=20128` — collapse WebSocket to same port
- `DASHBOARD_PORT=20128` — dashboard on same port

Docker Compose deduplicates identical port mappings, so only `20128:20128` is published.

## Update Workflow

```bash
cd ~/Omniroute
docker compose --profile base pull           # 30s — pulls latest from Docker Hub
docker compose --profile base up -d --no-build  # restarts with new image
```

## Persistence Chain

```
macOS restart → Docker Desktop starts (AutoStart) → Docker daemon →
  containers auto-restart (restart: unless-stopped) →
    bind mount recovers ./data from host → service ready
```
