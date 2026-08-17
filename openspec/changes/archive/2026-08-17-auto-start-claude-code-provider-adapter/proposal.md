# Proposal: auto-start-claude-code-provider-adapter

## Why

The cockpit adapter container uses `restart: unless-stopped` in docker-compose.yml. This restarts a container that Docker Desktop already knows about, but does NOT create the container after:
- Fresh Docker Desktop installation
- `docker compose down` followed by Docker Desktop restart
- First login on a new machine

The user wants the adapter to "start along with Docker." On macOS, this requires a `launchd` LaunchAgent that runs `docker compose up -d` when the user session starts and Docker becomes ready.

## Scope

- macOS `launchd` LaunchAgent (user-level, `~/Library/LaunchAgents/`)
- Wrapper script that waits for Docker, then starts the adapter
- Install/uninstall/status helpers
- Scope is operational tooling only (`skip_specs: true`)

## Evidence

| Fact | Source |
|---|---|
| `restart: unless-stopped` behavior | Docker Compose docs: restarts existing containers only |
| cockpit is native macOS process on 51006 | `lsof -i :51006` → `cockpit-cli` PID 64609 |
| Adapter container works via `host.docker.internal` | Live tests pass (text, streaming, tool-use, system prompt) |
| Docker Desktop available | `docker --version` → 29.7.2, `docker compose` → v5.3.1 |
| No existing LaunchAgents for adapter | `ls ~/Library/LaunchAgents/` → no matching plist |

## What Changes

### Phase 1: Create wrapper script and LaunchAgent

- Wrapper script `start-adapter.sh`: waits for Docker readiness, verifies `.env`, runs `docker compose up -d`
- LaunchAgent plist: runs wrapper at login, bounded stdout/stderr logs, `KeepAlive: false`

### Phase 2: Install helpers

- `install-launchagent.sh`: copies plist to `~/Library/LaunchAgents/`, bootstraps with `launchctl`
- `uninstall-launchagent.sh`: unloads and removes plist
- `adapter-status.sh`: checks container state and LaunchAgent status

### Phase 3: Acceptance

- `launchctl bootstrap` succeeds
- `adapter-status.sh` shows healthy
- `docker compose down` + restart login → adapter auto-starts
- Logs do not expose credentials

### Phase 4: Documentation

- Update adapter README with auto-start section
- Document conflict avoidance with `cockpit_up`/`cockpit_down` shell helpers

## Risks

- **Medium**: LaunchAgent may fire before Docker Desktop is ready — mitigated with retry loop
- **Medium**: `docker compose up -d` recreates container after intentional `docker compose down` — documented, with unload command
- **Low**: `.env` path hardcoded in wrapper — acceptable for single-machine deployment

## Rollback

1. `launchctl bootout gui/$(id -u)` to unload
2. Remove plist from `~/Library/LaunchAgents/`
3. `docker compose down` to stop container
