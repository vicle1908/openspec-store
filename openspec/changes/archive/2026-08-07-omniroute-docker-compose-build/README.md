# OmniRoute Docker Compose — Single-Port Deployment

## Summary

OmniRoute v3.8.49 (AI gateway, 290+ providers) deployed via Docker Compose using the
pre-built Docker Hub image (`diegosouzapw/omniroute:latest`) on single port 20128.

## Architecture

```
macOS Login → Docker Desktop (AutoStart) → Docker daemon →
  containers auto-restart (restart: unless-stopped) →
    bind mount recovers ./data from host → service ready
```

| Component | Image | Port | Persistence |
|-----------|-------|------|-------------|
| omniroute | `diegosouzapw/omniroute:latest` | 20128 | `~/Omniroute/data:/app/data` |
| omniroute-redis | `redis:7-alpine` | 6379 | `omniroute-redis-data` (named volume) |

## Key Decisions

- **Docker Hub image** (not build-from-source): 30s pull vs 15min build
- **Single port 20128**: dashboard + API + WebSocket on one port (ecosystem standard)
- **`docker-compose.override.yml`**: overrides upstream `image:` to use Docker Hub

## Update Workflow

```bash
cd ~/Omniroute
docker compose --profile base pull
docker compose --profile base up -d --no-build
```

## Commands

| Action | Command |
|--------|---------|
| Start | `cd ~/Omniroute && docker compose --profile base up -d --no-build` |
| Stop | `cd ~/Omniroute && docker compose --profile base down` |
| Logs | `cd ~/Omniroute && docker compose --profile base logs -f` |
| Update | `docker compose --profile base pull && docker compose --profile base up -d --no-build` |
| Status | `docker ps --filter name=omniroute` |

## Files

- `docker-compose.override.yml` — Docker Hub image override
- `.env` — all config (password, ports, OAuth secrets)
- `data/` — SQLite database + backups (bind mount, persists on host)
