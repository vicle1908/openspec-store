# Proposal: OmniRoute Docker Compose

## Why

OmniRoute is installed at `~/Omniroute` (v3.8.49) but was not running. The project provides a `docker-compose.yml` with multi-stage builds, but building from source takes ~15 minutes per update. Docker Hub publishes pre-built images (`diegosouzapw/omniroute`) for every release. The ecosystem requires a single port for all services (dashboard, API, WebSocket).

## What Changes

1. **Use Docker Hub image via `docker-compose.override.yml`** — overrides the `omniroute-base` service to use `diegosouzapw/omniroute:latest` instead of building from source
2. **Single-port mode** — configure `API_PORT=20128`, `LIVE_WS_PORT=20128`, `DASHBOARD_PORT=20128` in `.env` so everything runs on port 20128 (matches ecosystem standard)
3. **Start services** via `docker compose --profile base up -d --no-build`
4. **Verify persistence** — bind mount, restart policy, Docker Desktop autostart
5. **Update workflow** — `docker compose --profile base pull && up -d --no-build` (30s vs 15min build)

**Out of scope:**
- No spec delta (`skip_specs: true`) — infrastructure/config only
- No code changes to OmniRoute source
- Pre-existing `.env` and `data/` directory already configured
