# Tasks

## 1. Environment Limits, Stream Resilience & Compose Deployment

- [x] 1.1 Add `OMNIROUTE_MEMORY_MB=4096`, `OMNIROUTE_MAX_TOOLS_LIMIT=256`, `STREAM_READINESS_STALL_RETRY=true`, and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true` to the `omniroute-base.environment` list in `/Users/androidteam/Omniroute/docker-compose.override.yml`, and verify with `docker compose -f /Users/androidteam/Omniroute/docker-compose.yml -f /Users/androidteam/Omniroute/docker-compose.override.yml config --services` that the compose file parses without error.
- [x] 1.2 Recreate the `omniroute-base` container under `/usr/bin/lockf` on `~/.omniroute/update.lock` via `docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base`, and verify `docker inspect omniroute --format '{{json .Config.Env}}'` contains all four environment overrides.
- [x] 1.3 Verify live container health: confirm `curl -fsS http://127.0.0.1:20128/livez` returns `ok` and `curl -fsS http://127.0.0.1:20128/api/health | jq '.status'` returns `"ok"`. If container fails to boot healthy within 60s, execute rollback by restoring previous `docker-compose.override.yml` and running `docker compose --profile base up -d`.

## 2. Host CLI Bridge `providers list` Interception & Test Suite

- [x] 2.1 Add `runRemoteProvidersList()` to `/Users/androidteam/.local/bin/omniroute` that queries `/api/providers?limit=5000` via `fetchDaemonJson`, sanitizes fields matching upstream `publicConnection`, and renders both formatted table and `{ "providers": [ ... ] }` JSON output for `omniroute providers` and `omniroute providers list`.
- [x] 2.2 Verify `omniroute providers list` outputs all configured provider connections with status colors and `omniroute providers list --output json | jq '.providers | length > 0'` returns `true` (matching the live connection count from `/api/providers`).
- [x] 2.3 Add automated unit tests to `/Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_cli_bridge.py` verifying that `omniroute providers list` queries `/api/providers` and formats table and `{ providers: [...] }` JSON outputs without reading from local SQLite, and verify `uv run pytest /Users/androidteam/Developer/platform/openspec-store/tests/test_omniroute_cli_bridge.py` passes.
