# Design: auto-start-claude-code-provider-adapter

## Architecture

```
Login → Docker Desktop starts → launchd fires LaunchAgent
    → start-adapter.sh
        → poll `docker info` (bounded retry)
        → verify `.env` exists (never print contents)
        → run `docker compose up -d --remove-orphans`
        → exit 0 (one-shot, not supervising)
```

`restart: unless-stopped` in `docker-compose.yml` handles container restarts after creation. The LaunchAgent handles initial creation at login.

## macOS LaunchAgent Lifecycle

| Action | Command |
|---|---|
| Install | `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist` |
| Uninstall | `launchctl bootout gui/$(id -u)/com.workspace.claude-code-provider-adapter` |
| Status | `launchctl list com.workspace.claude-code-provider-adapter` |
| Logs | `~/Library/Logs/com.workspace.claude-code-provider-adapter.{out,err}` |

Plist properties:
- `RunAtLoad: true` — fires once at login
- `KeepAlive: false` — NOT a supervised loop; one-shot `docker compose up -d` exits after starting
- `StandardOutPath` / `StandardErrorPath` — absolute paths to log files
- `WorkingDirectory` — absolute path to adapter repo

## Wrapper Script (`start-adapter.sh`)

```
#!/bin/bash
set -euo pipefail

REPO="$HOME/Developer/claude-code-provider-adapter"
LOG_TAG="claude-code-provider-adapter"

# 1. Wait for Docker Desktop (bounded retry)
TIMEOUT=120
INTERVAL=2
ELAPSED=0
while ! docker info >/dev/null 2>&1; do
    ELAPSED=$((ELAPSED + INTERVAL))
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "$(date -u '+%%Y-%%m-%%dT%%H:%%M:%%SZ') TIMEOUT: Docker not ready after ${TIMEOUT}s" >&2
        exit 1
    fi
    sleep "$INTERVAL"
done

# 2. Verify .env exists (never print contents)
if [ ! -f "$REPO/.env" ]; then
    echo "$(date -u '+%%Y-%%m-%%dT%%H:%%M:%%SZ') ERROR: $REPO/.env missing" >&2
    exit 1
fi

# 3. Start adapter
cd "$REPO"
docker compose up -d --remove-orphans

echo "$(date -u '+%%Y-%%m-%%dT%%H:%%M:%%SZ') Adapter started"
```

## Shell Helper Interaction

- `cockpit_up` becomes idempotent: `docker compose up -d` is safe to re-run
- `cockpit_down` intentionally stops container; next login will recreate it via LaunchAgent
- To long-term disable: `launchctl bootout` first, then `docker compose down`

## Verification

1. `plutil -lint` on plist → no errors
2. `bash -n start-adapter.sh` → no syntax errors
3. `launchctl bootstrap gui/$(id -u)` → success
4. `launchctl list com.workspace.claude-code-provider-adapter` → loaded
5. `curl http://127.0.0.1:8787/health` → 200
6. `docker compose ps` → container healthy
7. `grep -r KEY ~/.ssh ~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist ~/Developer/claude-code-provider-adapter/start-adapter.sh` → no matches

## Rollback

1. `launchctl bootout gui/$(id -u)/com.workspace.claude-code-provider-adapter`
2. Remove `~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist`
3. Remove `~/Developer/claude-code-provider-adapter/start-adapter.sh`
4. `docker compose down` (optional — stops container)
