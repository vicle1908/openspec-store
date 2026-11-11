# Implementation & Verification Evidence: `harden-omniroute-update-oci-burst-pacing-and-storage-hygiene`

## 1. Pre-Flight Backups, Transactional SQLite Snapshot, and Clean Upstream Git Baseline (Tasks 1.1–1.3)
- **Backup directory (`mode 0700`)**: `/Users/androidteam/.omniroute/backups/harden-omniroute-update-oci-burst-pacing-and-storage-hygiene/` with `0600` pre-mutation copies (`dotenv.bak`, `docker-compose.override.yml`, `check-upstream.sh`, `update.sh`) and `sha256-manifest.json` (`2026-11-11T13:18:18Z`).
- **Transactional SQLite snapshot (`mode 0600`)**: `/Users/androidteam/.omniroute/snapshots/pre-hygiene-20261111-201818.sqlite` (`181,686,272` bytes), captured via `better-sqlite3` `.backup()`, consolidated with `PRAGMA wal_checkpoint(TRUNCATE); PRAGMA journal_mode=DELETE;` (`delete`), verified `PRAGMA quick_check = ok`, zero `-wal`/`-shm` sidecars.
- **Upstream Git cleanliness**: `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` returned `0` lines before and after all mutations.

## 2. Keychain-Free Dual-Registry OCI v2 Update Checker & Isolated `DOCKER_CONFIG` Upgrade Pulls (Tasks 2.1–2.3)
- **`/Users/androidteam/Omniroute/scripts/check-upstream.sh` (`mode 0755`, `umask 077`)**:
  - Resolves single-line running-container image digest via `docker inspect omniroute --format '{{.Image}}'` -> `docker image inspect "$IMG_ID" --format '{{range .RepoDigests}}{{println .}}{{end}}' | grep -oE 'sha256:[a-f0-9]+' | head -n 1` (fallback to `$IMAGE` only when container is absent).
  - Resolves remote multi-arch index digest via OCI Distribution Spec v1.1 Registry HTTP API v2 on Docker Hub (`diegosouzapw/omniroute:latest`) with automatic secondary OCI v2 mirror failover to official GHCR (`ghcr.io/cheaper-inference/omniroute:latest`), then isolated mode-`0700` `DOCKER_CONFIG` (`credHelpers` empty-string overrides + `DOCKER_HOST` preservation) `docker buildx imagetools inspect` fallback, and explicit single-line stderr logging on failure (zero `rm -rf`).
  - Live CLI + `launchctl kickstart -k gui/502/com.omniroute.update-check` verification (`~/.omniroute/update-check.log` at `2026-11-11 20:34:48`):
    - `Local:  sha256:b52a17661a1aff42ffb78f349f423e986dfc55b57274f28559f8387622ef8ee4`
    - `Remote: sha256:b52a17661a1aff42ffb78f349f423e986dfc55b57274f28559f8387622ef8ee4`
    - `Up to date` in ~1s with zero `-25293` or `Could not fetch remote digest` warnings.
- **`/Users/androidteam/Omniroute/scripts/update.sh` (`mode 0755`, `umask 077`)**:
  - Gate 1 enforces `chmod 0600 "${SNAPSHOT_DIR}/${SNAPSHOT_NAME}"` immediately after `docker cp` + SQLite consolidation.
  - Gate 2 runs `docker pull "$IMAGE_REF"` followed by `docker compose --profile base pull "$SERVICE" redis` under isolated mode-`0700` `DOCKER_CONFIG` (`credHelpers` empty-string overrides + `DOCKER_HOST` preservation), refreshing `:latest` for Gate 3 despite `override.yml`'s digest pin.
  - `cleanup_update()` restores `PRE_DEPLOY_OVERRIDE_DIGEST` in `docker-compose.override.yml` before releasing `fd 9` (`~/.omniroute/update.lock`) on any post-swap gate failure; Gate 9 prunes `~/.omniroute/snapshots/*.sqlite` to at most the 5 newest verified snapshots.
- **Automated Test Suite**: `pytest tests/test_omniroute_*.py -v` -> **`25 passed in 18.16s`** (including 3 new behavioral/unit tests in `tests/test_omniroute_lock_and_watchdog.py` covering multi-digest `RepoDigests`, Docker Hub 503 -> GHCR 200 failover with poison `docker-credential-osxkeychain`, isolated `DOCKER_CONFIG` Gate 2 dual pull, Gate 1 `0600` mode, Gate 9 5-snapshot retention, and automatic `override.yml` digest rollback on Gate 5/Gate 8 failures).

## 3. Official Stable Container Stack, Redis `8.10.3-alpine`, & Single-Source `.env` Alignment (Task 3.1)
- **`/Users/androidteam/Omniroute/.env` (`mode 0600`, single source via `env_file: .env`)**: Verified inside live `omniroute` PID 1 `/proc/1/environ`:
  - `DISABLE_SQLITE_AUTO_BACKUP=true`, `DB_BACKUP_MAX_FILES=2`, `DB_BACKUP_RETENTION_DAYS=2`
  - `REQUEST_TIMEOUT_MS=600000`, `STREAM_IDLE_TIMEOUT_MS=600000`, `OMNIROUTE_BASE_URL=http://127.0.0.1:20128`
  - `APP_BIND_HOST=127.0.0.1`, `REDIS_BIND_HOST=127.0.0.1`, `OMNIROUTE_USE_TURBOPACK=0`
- **`/Users/androidteam/Omniroute/docker-compose.override.yml` (`mode 0644`)**:
  - `omniroute-base`: `diegosouzapw/omniroute@sha256:b52a17661a1aff42ffb78f349f423e986dfc55b57274f28559f8387622ef8ee4` (`v3.8.53`), `depends_on: { redis: { condition: service_healthy } }`, zero duplicated `.env` keys.
  - `redis`: `docker.io/library/redis:8.10.3-alpine@sha256:71885d8cc6e42f2bc0aa2eb853bfc4be200b5108a46ac50e117ae1df0531fb80` (`redis_version:8.10.3`, `PONG`, `healthy`).
  - Stack recreated under `/usr/bin/lockf -s -t 60 9` (`~/.omniroute/update.lock`); `~/Omniroute/scripts/ensure-muse-wire-compat.sh` -> `already_ok`; zero `warnConflictingHeapLimits` in `docker logs omniroute`.
  - `PATCH /api/settings/database` persisted `backup: { autoBackupEnabled: false, keepLastNBackups: 2 }`.

## 4. Zero-Gap Burst Pacing, Provider Quarantine, 14-Combo Reconciliation & Storage Hygiene (Tasks 4.1–4.3)
- **Request Queue (`GET /api/resilience`)**: `concurrentRequests: 64`, `requestsPerMinute: 600`, `minTimeBetweenRequestsMs: 0`, `maxWaitMs: 15000`; all 14 active `agy` connections have `rate_limit_protection = 0`.
- **Provider & Combo Hygiene**:
  - `f3aaa87c-4af7-4a83-a636-98983119b9bc` (`pm`): `is_active = 0`, `health_check_interval = 0`; `omniroute status` reports `23 active / 45 configured (23 healthy, 22 disabled)` and `17 closed, 0 half-open, 0 open` breakers.
  - Deleted unused combo `phanmemvip` (`ad4dace4-9072-42a8-8503-e6188e325890`); 14 active workstation combos remain (`setup-macbook-omniroute-client.sh --check` -> `SUCCESS`, `18` client files verified).
  - Reconciled `compression_combo_assignments` to exact `14` active combo UUIDs; all `9` inactive banned `agy` rows (`is_active = 0`, `test_status = 'banned'`) preserved.
- **Volume & Host Storage Hygiene**:
  - Live `/app/data/storage.sqlite` passed `PRAGMA wal_checkpoint(TRUNCATE)` and `PRAGMA quick_check = ok`; unlinked both legacy `db_*_pre-write.sqlite` (`184.7 MB`) copies in `/app/data/db_backups/`.
  - Removed all 10 obsolete pre-Docker host paths (`~/.omniroute/{storage.sqlite,storage.sqlite-wal,storage.sqlite-shm,db_backups,server.log,server.err,call_logs,logs,log_archives}` and `~/Omniroute/data.bak-20260824`), consolidated and pruned `~/.omniroute/snapshots/` to the 5 newest `journal_mode=delete` (`quick_check=ok`) `.sqlite` files with `0` sidecars (~1.7 GB reclaimed), preserved all 19 files in `~/.omniroute/backups/scale-omniroute-concurrency-and-add-gemini-4-carbon/`, and enforced `go-rwx` (`0700` dirs/executables, `0600` data/logs/snapshots) across user-owned `~/.omniroute/` entries.

## 5. End-to-End Concurrent Burst Verification (Task 5.1)
- Fired a 16-request simultaneous burst across `deepseek-v4.1-flash` (6 parallel requests on an auto-protected API-key provider), `gemini-3.8-flash-high` (6 parallel requests), and `gemini-4-carbon-low` (4 parallel requests): **`16/16 HTTP 200` (`100%`)**, with all 6 `deepseek-v4.1-flash` requests completing concurrently in **`2.382s–2.993s`** (confirming zero `200 ms` serial Bottleneck spacing delay).
- Fired a 32-way full-headroom concurrent live burst across 8 `deepseek-v4.1-flash`, 12 `gemini-3.8-flash-high`, 6 `gemini-4-carbon-low`, 4 `claude-sonnet-5.5`, and 2 `gemini-4-argon-low` requests: **`32/32 HTTP 200` (`100%` success, `0` HTTP 503, `0` HTTP 429)**, with all 8 `deepseek-v4.1-flash` requests completing concurrently in **`2.530s–3.183s`** (`min=2.172s`, `p50=4.071s`, `p90=13.930s`).
- Fleet & Tailscale Serve Consistency: `reconcile-agent-cli-coverage.py` verified `0` undeclared models across 22 installed agents; `setup-macbook-omniroute-client.sh --check` verified 6-port Tailscale Serve (`20128`, `20129`, `20132`, `3111` L4 TCP + `443`, `8443` HTTPS), `1,084` models + all 14 required combos on `:20128`/`20129`, LiveWS `:20132`, and all 18 client configuration files (`SUCCESS`).
