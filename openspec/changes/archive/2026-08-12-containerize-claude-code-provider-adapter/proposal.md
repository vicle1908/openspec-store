# Proposal: containerize-claude-code-provider-adapter

## Why

The cockpit provider adapter (`~/Developer/claude-code-provider-adapter/`) currently runs as a manual foreground process. Every `cockpit()` session requires the user to manually start the adapter, and it dies when the terminal closes. This change containerizes the adapter with Docker Compose so it starts automatically with Docker and survives terminal closures.

## Scope

This change containerizes the **adapter only**. Cockpit (`cockpit-cli` PID 64609) is a native macOS binary listening on `localhost:51006` — it is NOT a Docker container. The adapter container reaches it through `host.docker.internal:51006`.

## Evidence

| Fact | Source |
|---|---|
| cockpit is a native macOS process | `lsof -i :51006` → `cockpit-cli` PID 64609 |
| cockpit is NOT in Docker | `docker ps` shows only omniroute + omniroute-redis |
| Docker Desktop available | `docker --version` → 29.7.2, `docker compose` → v5.3.1 |
| Existing compose patterns | `realtime/docker-compose.yml`, `jira-skill/docker-compose.yml` |
| Adapter repo has `uv.lock` | Committed at `b3e11c3`, 45 tests pass |

## What Changes

### Phase 1: Docker Build Infrastructure

- Create `Dockerfile` in adapter repo: multi-stage build using Python 3.14-slim + uv
- Create `docker-compose.yml` with `restart: unless-stopped`, `host.docker.internal`, health check
- Create `.env.example` with `HERMES_CUSTOM_COCKPIT_API_KEY=` placeholder
- Ensure `.env` is gitignored

### Phase 2: Config Adjustment

- Update `config.py` default `COCKPIT_UPSTREAM_URL` to `http://host.docker.internal:51006/v1/responses` when `ADAPTER_HOST=0.0.0.0` (container mode)
- Keep `127.0.0.1` default for local (non-container) usage

### Phase 3: Launcher Integration

- Update `cockpit()` shell function to check if adapter is already running before complaining
- Add `cockpit_up()` / `cockpit_down()` convenience functions for Docker lifecycle

### Phase 4: Acceptance

- `docker compose build` succeeds
- `docker compose up -d` starts container
- `/health` returns 200 from published port
- Container reaches host-native cockpit via `host.docker.internal`
- Text, streaming, and tool-use requests succeed through the container
- `docker compose down` cleans up
- `uv run pytest` remains green
- No secrets in Docker image, compose file, or artifacts

## Risks

- **Medium**: `host.docker.internal` behavior on Docker Desktop for Mac — verified available
- **Low**: Python 3.14-slim image availability — use pinned tag
- **Unknown**: Whether `restart: unless-stopped` survives Docker Desktop restart without prior `docker compose up` — documented as limitation

## Rollback

```bash
docker compose down
rm Dockerfile docker-compose.yml .env .env.example
```
