# Design: OmniRoute Docker Compose

## Architecture

```
macOS Login
  └─ Docker Desktop (AutoStart: True)
       └─ docker compose --profile base up -d --no-build
            ├─ redis:7-alpine       ──→  port 6379  (rate limiter)
            └─ diegosouzapw/omniroute:latest  ──→  port 20128 (dashboard + API)
                                                  20129 (API only)
                                                  20132 (Live WS)

Volume mounts:
  ./data:/app/data     → SQLite + backups (persist on host)
  redis-data:/data     → Redis persistence (named volume)

Env:
  ./env                → All secrets, OAuth tokens, config
```

## Image Strategy

The `docker-compose.override.yml` overrides the `omniroute-base` service image:

```yaml
services:
  omniroute-base:
    image: diegosouzapw/omniroute:latest
```

This replaces the upstream `build:` + `image: omniroute:base` with the pre-built Docker Hub image. The `build:` section is inherited but ignored when using `--no-build`.

## Update Workflow

```bash
cd ~/Omniroute
docker compose --profile base pull           # 30s — pulls latest from Docker Hub
docker compose --profile base up -d --no-build  # restarts with new image
```

## Trade-offs

| Factor | Docker Hub image | Build from source |
|--------|-----------------|-------------------|
| Update time | ~30s | ~15min |
| Customization | None | Full control |
| Resource usage | Low | High (8 CPU, 4GB RAM during build) |
| Data safety | ✅ Bind mount preserved | ✅ Same |
| Standard workflow | ✅ `pull + up` | ✅ `build + up` |

## Persistence Chain

```
macOS restart → Docker Desktop starts (AutoStart) → Docker daemon →
  containers auto-restart (restart: unless-stopped) →
    bind mount recovers ./data from host → service ready
```
