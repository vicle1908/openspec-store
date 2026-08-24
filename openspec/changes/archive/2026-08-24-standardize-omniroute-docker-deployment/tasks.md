## 1. Pre-flight Verification (no downtime)

- [x] 1.1 Docker daemon + compose plugin healthy: `docker info` and `docker compose version`
- [x] 1.2 Hub image reachable for arm64: `docker manifest inspect diegosouzapw/omniroute:latest | grep arm64`
- [x] 1.3 Secret parity between `~/Omniroute/.env` and `~/.omniroute/.env`: diff `JWT_SECRET`, `API_KEY_SECRET`, `STORAGE_ENCRYPTION_KEY`, `STORAGE_ENCRYPTION_KEY_VERSION`
- [x] 1.4 Deployment override present and renders Hub image: `test -f ~/Omniroute/docker-compose.override.yml && grep -q diegosouzapw/omniroute ~/Omniroute/docker-compose.override.yml`
- [x] 1.5 Record baseline: live version, provider connection count (`sqlite3 ~/.omniroute/storage.sqlite "SELECT COUNT(*) FROM provider_connections;"`), disk space for image
- [x] 1.6 Pre-pull image BEFORE any downtime: `cd ~/Omniroute && docker compose --profile base pull`; record `docker image inspect --format '{{.RepoDigests}}' diegosouzapw/omniroute:latest`
- [x] 1.7 Verify: all six checks pass; image digest recorded

## 2. Quiesce + Retire launchd (downtime starts)

- [x] 2.1 Boot out both launchd agents FIRST (KeepAlive respawn + hourly updater race): `launchctl bootout gui/$(id -u)/com.omniroute.server; launchctl bootout gui/$(id -u)/com.omniroute.updater`
- [x] 2.2 Kill the manual dev-mode server process on :20128
- [x] 2.3 Verify: `lsof -i :20128` empty; `pgrep -f run-next` empty; `launchctl list | grep omniroute` empty

## 3. Fix Deployment Config

- [x] 3.1 In `~/Omniroute/.env`: set `API_PORT=20129` (was 20128, duplicating DASHBOARD_PORT)
- [x] 3.2 In `~/Omniroute/.env`: set `REDIS_URL=redis://redis:6379` (was redis://localhost:6379)
- [x] 3.3 Extend `~/Omniroute/docker-compose.override.yml`: override the redis service to publish no host ports (`ports: !reset []` — a bare empty list is concatenated by compose, not cleared)
- [x] 3.4 Verify rendered config from `~/Omniroute`: `docker compose --profile base config` shows THREE unique published ports (20128, 20129, 20132), `REDIS_URL: redis://redis:6379`, image `diegosouzapw/omniroute:latest`, and NO redis host port

## 4. Switch Data Store to Named Volume (virtiofs/WAL fix)

> Discovered during cutover: the compose default bind mount (`./data:/app/data`)
> corrupts SQLite WAL databases on Docker Desktop for Mac (virtiofs lacks the
> mmap/shm semantics WAL needs). The first migration attempt produced a zeroed
> DB header + `database disk image is malformed` errors. Fix: named volume.

- [x] 4.1 First attempt (bind mount) executed and FAILED: DB header zeroed, container logs show `database disk image is malformed`; source `~/.omniroute/storage.sqlite` verified intact
- [x] 4.2 Root cause confirmed: OmniRoute hardcodes `journal_mode = WAL` (`src/lib/db/core.ts`); virtiofs bind mount incompatible
- [x] 4.3 Stop the corrupted stack: `cd ~/Omniroute && docker compose --profile base down`
- [x] 4.4 Remove the corrupted bind-mount data: `rm -rf ~/Omniroute/data` (the `data.bak-<date>` backup of the stale dir remains)
- [x] 4.5 Update `docker-compose.override.yml`: replace the bind mount with a named volume — `omniroute-base: volumes: !reset ["omniroute-data:/app/data"]` + top-level `volumes: omniroute-data: {}`
- [x] 4.6 Verify rendered config: `docker compose --profile base config` shows the volume mount (no `./data` bind) and the three unique ports

## 5. Migrate Data into the Volume

- [x] 5.1 Fresh backup from source (previous target was corrupted): `sqlite3 ~/.omniroute/storage.sqlite ".backup /tmp/omniroute-migrate.sqlite"`
- [x] 5.2 Verify backup: `sqlite3 /tmp/omniroute-migrate.sqlite "PRAGMA integrity_check;"` = `ok`; connection count = 10
- [x] 5.3 Start the stack so the volume exists: `cd ~/Omniroute && docker compose --profile base up -d --no-build` (will boot on empty DB — fine, we seed next)
- [x] 5.4 Stop the app container only (keep volume): `docker compose --profile base stop omniroute-base`
- [x] 5.5 Seed the volume + fix ownership via root utility container: `docker run --rm -v omniroute_omniroute-data:/data -v /tmp/omniroute-migrate.sqlite:/src.sqlite:ro alpine sh -c "cp /src.sqlite /data/storage.sqlite && chown -R 1000:1000 /data"` (verify exact volume name via `docker volume ls | grep omniroute`)
- [x] 5.6 Verify from inside a container (host cannot read VM-internal volume files): `docker run --rm -v omniroute_omniroute-data:/data alpine sh -c "apk add --no-cache sqlite >/dev/null 2>&1; sqlite3 /data/storage.sqlite 'PRAGMA integrity_check; SELECT COUNT(*) FROM provider_connections;'"` = `ok` + `10`
- [x] 5.7 Start the app: `docker compose --profile base start omniroute-base`; wait for healthy (bounded 90s)

## 6. End-to-End Verification

- [x] 6.1 Dashboard: `curl -s -o /dev/null -w "%{http_code}" http://localhost:20128/` = 307; follow → /login = 200
- [x] 6.2 Login: `curl -s -X POST http://localhost:20128/api/auth/login -H "Content-Type: application/json" -d '{"password":"<existing>"}'` = `{"success":true}`
- [x] 6.3 API catalog: `curl -s http://localhost:20128/api/v1/models | head -c 200` returns model list JSON
- [x] 6.4 LiveWS port: `nc -z localhost 20132` succeeds
- [x] 6.5 Redis wiring from inside: `docker exec omniroute printenv REDIS_URL` = `redis://redis:6379`; redis PING from the omniroute container = `+PONG`
- [x] 6.6 **No corruption**: `docker logs omniroute 2>&1 | grep -c "database disk image is malformed"` = 0; DB writes succeed (new rows appear after a request)
- [x] 6.7 Record running version: `docker exec omniroute node -e "console.log(require('/app/package.json').version)"` (record, don't fail on drift)

## 7. Clean Up Legacy Mechanisms

- [x] 7.1 Remove launchd artifacts: `rm ~/Library/LaunchAgents/com.omniroute.server.plist ~/Library/LaunchAgents/com.omniroute.updater.plist ~/Library/LaunchAgents/omniroute-update.sh`
- [x] 7.2 Final ownership assertion: `lsof -i :20128 -i :20129 -i :20132` shows only docker-proxy; no host node process for OmniRoute

## 8. Update Documentation

- [x] 8.1 Update `openspec-store/openspec/config.yaml` OmniRoute section (deployment, ports, redis internal, update command, on-demand updates) — NOTE: needs one more edit for named volume
- [x] 8.2 Verify: config.yaml matches the running deployment exactly (including named volume)

## 9. Final Acceptance (single consolidated checklist)

- [x] 9.1 Single-mechanism: no launchd omniroute entries, no manual dev process, compose stack is the only runtime
- [x] 9.2 Reboot-survival scope confirmed: Docker Desktop login item present + `restart: unless-stopped` in rendered config (documented as "recovers after user login"; a real reboot test is optional evidence, not required)
- [x] 9.3 Rollback copy intact: `~/.omniroute/storage.sqlite` unmodified since pre-flight (valid header + mtime)
- [x] 9.4 Connection count matches baseline (10); image digest recorded (task 1.6)

## 10. Archive

- [x] 10.1 `openspec validate standardize-omniroute-docker-deployment --type change --strict --store openspec-store`
- [x] 10.2 `cd ~/Developer && openspec archive standardize-omniroute-docker-deployment --store openspec-store --yes`
- [x] 10.3 Commit ONLY the archived change dir + config.yaml: `cd ~/Developer/openspec-store && git add openspec/changes/archive/<date>-standardize-omniroute-docker-deployment openspec/config.yaml && git diff --cached --name-status` (inspect before commit; leave other uncommitted work untouched)
