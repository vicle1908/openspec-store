# Evidence: `stabilize-omniroute-startup-and-update-readiness`

**Date**: 2026-10-19  
**Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)  
**Implementation Roots**:
- `/Users/androidteam/Omniroute` (`docker-compose.override.yml`, `scripts/update.sh`, git `main`)
- `/Users/androidteam/Developer/scripts/omniroute-watchdog.sh` (mirrored to `/Users/androidteam/Developer/platform/openspec-store/scripts/omniroute-watchdog.sh`)
- Docker Engine volume `omniroute_omniroute-data` (`/app/data/storage.sqlite`)

---

## 1. Maintenance Lock, Watchdog Provenance Mirror & Updater Hardening (Tasks 1.1 & 1.2 — Historical Initial Run)

- **Task 1.1 (`omniroute-watchdog.sh` + Provenance Mirror)**:
  - Updated `/Users/androidteam/Developer/scripts/omniroute-watchdog.sh` to evaluate `~/.omniroute/update.lock` at Step 0 using `set -euo pipefail`-safe `read -r lock_pid lock_epoch _ < "$LOCK_FILE" 2>/dev/null || true`, `^[0-9]+$` regex validation, and `lock_age=$(( now_epoch - lock_epoch ))`.
  - Mirrored byte-for-byte to `/Users/androidteam/Developer/platform/openspec-store/scripts/omniroute-watchdog.sh`:
    - `shasum -a 256`: `df2668dafa3e6f8cbe94713126ec2a8a8254c9d0f0d90c40786b8db659d5084e` (identical on both paths; `8/8` scripts in `config/script-provenance-manifest.tsv` verified with `0` drift).
  - Live verification in `~/.omniroute/watchdog.log` during both synthetic test and 10-minute offline `VACUUM`:
    ```text
    [2026-10-19 10:12:50] INFO: Maintenance lock active (pid=61957, age=0s). Skipping watchdog cycle.
    [2026-10-19 10:33:46] INFO: Maintenance lock active (pid=7995, age=47s). Skipping watchdog cycle.
    [2026-10-19 10:35:46] INFO: Maintenance lock active (pid=7995, age=167s). Skipping watchdog cycle.
    [2026-10-19 10:37:46] INFO: Maintenance lock active (pid=7995, age=287s). Skipping watchdog cycle.
    [2026-10-19 10:39:47] INFO: Maintenance lock active (pid=7995, age=408s). Skipping watchdog cycle.
    [2026-10-19 10:41:48] INFO: Maintenance lock active (pid=7995, age=528s). Skipping watchdog cycle.
    [2026-10-19 10:43:48] INFO: Maintenance lock active (pid=7995, age=649s). Skipping watchdog cycle.
    ```
- **Task 1.2 (`~/Omniroute/scripts/update.sh`)**:
  - Added ownership-verified `~/.omniroute/update.lock` acquisition (`LOCK_OWNED=true` and `lock_pid == $$` in `cleanup_update` `EXIT` trap, cleaning up both `$LOCK_FILE` and `/tmp/${SNAPSHOT_NAME}`), `{readonly:true, timeout:15000}` on all `better-sqlite3` queries, and `PRAGMA quick_check` in Gate 1 (`LIVE_INTEGRITY`, `SNAP_INTEGRITY`) and Gate 9 (`POST_INTEGRITY`).
  - `bash -n /Users/androidteam/Omniroute/scripts/update.sh` exited `0`.

*(See Section 5 below for the post-apply audit findings and native `/usr/bin/lockf` + Step 3 periodic read-only `PRAGMA integrity_check` remediation superseding the PID/epoch lock implementation in Tasks 1.1 and 1.2.)*

---

## 2. Non-Blocking Startup Override & SQLite Volume Reclamation (Tasks 2.1, 2.2 & 2.3 — Historical Initial Run)

- **Task 2.1 (`~/Omniroute/docker-compose.override.yml`)**:
  - Added `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED=true` and `OMNIROUTE_SKIP_DB_HEALTHCHECK=1` to `services.omniroute-base.environment`.
  - Verified rendered configuration with `docker compose -f /Users/androidteam/Omniroute/docker-compose.yml -f /Users/androidteam/Omniroute/docker-compose.override.yml --profile base config` (exit `0`).
- **Task 2.2 (Host Snapshot Verification & Orphaned Backup Cleanup)**:
  - Verified existing `/Users/androidteam/.omniroute/snapshots/pre-update-20261003-220431.sqlite`: `PRAGMA quick_check = ok`, `api_keys = 1`, `provider_connections = 20`. *(Audit correction in Section 5: this 2026-10-03 snapshot held 20 providers rather than the 32 providers present in the live 2026-10-19 database prior to pruning.)*
  - Removed orphaned `/app/data/storage.sqlite.snapshot.bak` (`3,022,114,816` bytes) and `/app/data/db_backups/*_pre-migration.sqlite` (`2,033,078,272` bytes across 3 files) = **`5,055,193,088` bytes (~4.71 GiB)** reclaimed.
- **Task 2.3 (Retention Upsert, ISO-8601 Pruning, WAL Checkpoint & Offline VACUUM)**:
  - Upserted `('databaseSettings', 'conversationTurnNodes', '7')`, `('databaseSettings', 'retention.conversationTurnNodes', '7')`, `('databaseSettings', 'quotaSnapshots', '14')`, `('databaseSettings', 'retention.quotaSnapshots', '14')`, `('databaseSettings', 'callLogs', '30')`, `('databaseSettings', 'retention.callLogs', '30')`.
  - Pruned with ISO-8601 `toISOString()` cutoffs (`cutoff7dISO = 2026-10-12T03:33:04.068Z`, `cutoff14dISO = 2026-10-05T03:33:04.071Z`) and executed `PRAGMA wal_checkpoint(TRUNCATE); VACUUM;` (`49.69s`) as UID:GID `1000:1000` (`node:node`):

| Metric | Before | After | Delta |
| :--- | ---: | ---: | ---: |
| `storage.sqlite` size | `4,024,639,488` B (~3.75 GiB) | `1,069,002,752` B (~0.996 GiB) | **`-2,955,636,736` B (-73.4%)** |
| `storage.sqlite-wal` size | `86,927,912` B (~82.9 MiB) | `0` B (post-checkpoint) | **`-86,927,912` B** |
| Orphaned in-volume backups | `5,055,193,088` B (~4.71 GiB) | `0` B | **`-5,055,193,088` B (-100%)** |
| **Total Volume Bytes Reclaimed** | `9,166,760,488` B (~8.54 GiB) | `1,069,002,752` B (~0.996 GiB) | **`-8,097,757,736` B (-7.54 GiB)** |
| `PRAGMA page_count` (`4096` B/page) | `982,581` | `260,987` | `-721,594` pages |
| `PRAGMA quick_check` | `ok` | `ok` | Verified |
| `conversation_turn_nodes` rows | `4,850,169` | `986,137` | `-3,864,032` rows |
| `agentic_conversations` rows | `16,435` | `5,820` | `-10,615` rows |
| `quota_snapshots` rows | `426,489` | `319,585` | `-106,904` rows |
| `api_keys` / `provider_connections` / `combos` | `1` / `32` / `5` | `1` / `32` / `5` | `0` (100% preserved) |

---

## 3. Upstream Source Sync, Live Runtime Recovery & Governance Verification (Tasks 3.1, 3.2 & 3.3 — Historical Initial Run)

- **Task 3.1 (`~/Omniroute` Git Fast-Forward)**:
  - Fast-forwarded `/Users/androidteam/Omniroute` `main` from `fd95f823d` to `origin/main` `e62b4b71c` (`ci: make the .113 omni-build slot opt-in on main (USE_VPS_BUILD_RUNNER) (#16835)`), 0 commits behind, untracked deployment files preserved.
- **Task 3.2 (Container Recreation & Endpoint Verification)**:
  - Recreated `omniroute-base`; time to `/healthz = ok` and `State.Health.Status = healthy`: **`9.80s`** (down from `>270–300s` crash loop).
  - Container logs confirmed `[DB] SQLite database ready: /app/data/storage.sqlite` and active 7d/14d/30d auto-cleanup pass.
  - Endpoints verified:
    - `GET http://127.0.0.1:20128/healthz` → `ok` (HTTP 200)
    - `GET http://127.0.0.1:20128/api/monitoring/health` → `{"status":"healthy","setupComplete":true}` (HTTP 200)
    - `HEAD http://127.0.0.1:20128/v1/models` → HTTP 200
    - `GET http://127.0.0.1:20128/v1/muse-code/models` → HTTP 200
    - `/Users/androidteam/.local/bin/omniroute status` → exit `0` *(Audit note in Section 5: `omniroute status` inspects local bridge metadata only, not the daemon.)*
- **Task 3.3 (Upstream Digest Check, Watchdog Run, Provenance & OpenSpec Validation)**:
  - `/Users/androidteam/Omniroute/scripts/check-upstream.sh` → `Local == Remote == sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218` (`Up to date`).
  - `/Users/androidteam/Developer/scripts/omniroute-watchdog.sh` → exit `0`, zero restarts.
  - `config/script-provenance-manifest.tsv` → `8 scripts checked, 0 drift`.
  - `openspec validate "stabilize-omniroute-startup-and-update-readiness" --strict --json --store openspec-store` → `valid: true, issues: []`.
  - `openspec validate --changes --strict --json --store openspec-store` → `3/3 passed, 0 failed`.

---

## 4. End-to-End Live Stack, Inference & Lifecycle Verification (Historical Initial Run)

- **Workstation Docker Lifecycle (`docker-service.sh status --json`)**:
  - Exit `0` (`1.35s`); `"status":"running"`, `"helpers":{"vmnetd":true,"socket":true}`, `~/Omniroute` (`running_containers: 2`) and `~/Developer/shb/shb-schedule` (`running_containers: 2`, `GET http://127.0.0.1:9110/scheduler/health` → `HTTP 200` in `6.0ms`).
- **Live Inference Verification (`http://127.0.0.1:20128`)**:
  - `POST /v1/chat/completions` (`model: "gemini-3.8-flash-high"`, `max_tokens: 32`) → `HTTP 200` (`7,176 ms`), reply `"PONG"`, `finish_reason: "stop"`.
  - `POST /v1/responses` (`model: "gemini-3.8-flash-high"`, `stream: true`) → `HTTP 200` (`6,076 ms`), reply `"PONG"`, initial keepalive frame emitted `"id":"resp_keepalive"` (`"id": null` count = `0`).
  - Authenticated `GET /v1/models` → `HTTP 200` (`1,196` models); `GET /v1/muse-code/models` & `GET /muse-code/models` → `HTTP 200` (`13` models).
- **Watchdog & Updater Lock/Contention E2E Scenarios (Historical PID/Epoch Lock)**:
  - Watchdog Scenario A (healthy, no lock) → exit `0`, container `StartedAt` unchanged (`2026-10-19T03:44:56.396236718Z`).
  - Watchdog Scenario B (active lock `61957 1792382120`) → exit `0`, logged `INFO: Maintenance lock active (pid=61957, age=0s). Skipping watchdog cycle.`, lock retained.
  - Watchdog Scenario C (stale lock `999999 1792378520`) → exit `0`, logged `WARNING: Removing stale or invalid maintenance lock...`, lock automatically removed.
  - Updater Scenario A (Gate 0 no flag) → exit `0`, logged `No update flagged`.
  - Updater Scenario B (concurrent lock contention `61957 1792382147` + active `update-available`) → exit `1`, logged `Update lock active at ... Retaining ... and exiting`, and preserved both `update.lock` (`LOCK_RETAINED:true`) and `update-available` (`FLAG_RETAINED:true`) without clobbering the active lock in its `EXIT` trap.
- **Host CLI Bridge Isolation (`~/.local/bin/omniroute`)**:
  - Executed `omniroute --version` (`3.8.51`), `omniroute status`, `omniroute combo list --output json` (`5` active combos), and `omniroute keys list --output json` using isolated `/tmp/omniroute-cli-bridge-*`; host `/Users/androidteam/.omniroute/storage.sqlite` mtime remained untouched (`1792031065 Oct 15 09:24:25 2026`).

---

## 5. Independent Post-Apply Audit & Corrective Remediation Record (2026-10-19)

### 5.1 Audit Corrections to Historical Sections 1–4

1. **PID/Epoch Lockfile Race & Expiry Defects (Correction to Section 1 & Section 4)**:
   - The PID/epoch lockfile implementation in Tasks 1.1 and 1.2 (`[[ -f "$LOCK_FILE" ]]` followed by `printf '%s %s\n' "$$" "$(date +%s)" > "$LOCK_FILE"`) was not an exclusive atomic lock: deterministic concurrent execution of the acquisition block allowed two contenders to both observe the lock absent and set `LOCK_OWNED=true`.
   - In `omniroute-watchdog.sh`, a live lock owner with `lock_age >= 1800` had its lock deleted (`rm -f "$LOCK_FILE"`) and fell through to container actions; additionally, an invalid octal epoch token (such as `08`, which passes `^[0-9]+$` regex validation) caused an arithmetic error in `lock_age=$(( now_epoch - lock_epoch ))` or fell through to unlink and container actions.
   - **Remediation Design (Tasks 4.1 & 4.2)**: Replace all PID/epoch/age/unlink lock logic in `omniroute-watchdog.sh` (plus its provenance mirror in `openspec-store/scripts/omniroute-watchdog.sh`) and `update.sh` with macOS native `/usr/bin/lockf` kernel descriptor locking on persistent inode `~/.omniroute/update.lock` (`umask 077`, `exec 9>>"$LOCK_FILE"`, `/usr/bin/lockf -s -t 0 9`). `omniroute-watchdog.sh` holds FD `9` across its entire cycle (closing `9>&-` on child invocations, exiting `0` on `EX_TEMPFAIL` `rc = 75`, failing closed non-zero on other lock errors). `update.sh` acquires FD `9` after Gate 0 and argument validation before `pre-state` (retaining `update-available` and exiting `1` on `rc = 75`), cleans up `/tmp/${SNAPSHOT_NAME}` inside `cleanup_update` **before** shell exit releases FD `9` while preserving original `exit_rc`, bounds `docker`/`sqlite3` probes and backup with `gtimeout` (`run_bounded`), and fails closed in Gate 1 if host `PRAGMA wal_checkpoint(TRUNCATE)` does not return `0|*` (`busy == 0`) before removing `-wal`/`-shm` sidecars (re-verifying post-checkpoint `PRAGMA quick_check = ok`). Manual maintenance uses `/usr/bin/lockf -k -t 0 ~/.omniroute/update.lock <command>`.
2. **Historical Pre-Prune Backup Gap & Transaction/Assertion Scope (Correction to Section 2)**:
   - Task 2.2 verified `/Users/androidteam/.omniroute/snapshots/pre-update-20261003-220431.sqlite` (captured on `2026-10-03` with `api_keys = 1` and `provider_connections = 20`) rather than capturing a fresh pre-prune snapshot of the `2026-10-19` live database (`api_keys = 1`, `provider_connections = 32`, `combos = 5`). While all `1` `api_keys`, `32` `provider_connections`, and `5` `combos` were preserved intact in `/app/data/storage.sqlite` across the prune and `VACUUM`, that historical pre-prune backup gap between `2026-10-03` (20 providers) and `2026-10-19` (32 providers) cannot be retrospectively repaired; capturing a fresh current host snapshot of the 32-provider compacted database is tracked in Task 4.3.
   - In Task 2.3, the historical one-shot pruning script executed `DELETE` statements on `conversation_turn_nodes`, `agentic_conversations`, and `quota_snapshots` in autocommit mode rather than inside a single joint `BEGIN IMMEDIATE ... COMMIT` transaction, and logged post-VACUUM counts/integrity for inspection rather than enforcing programmatic fail-closed assertions.
3. **Integrity Policy, `OMNIROUTE_SKIP_DB_HEALTHCHECK=1` Scope & `timeout: 15000` Semantics (Correction to Section 1 & Section 2)**:
   - In `src/lib/db/core.ts:954`, `OMNIROUTE_SKIP_DB_HEALTHCHECK=1` sets `skipIntegrityCheck = true` globally for **all** managed health checks (deferred startup, 6-hour periodic scheduler, and manual `POST /api/db/health`), not only initial startup. In `src/lib/db/healthCheckWorker.ts:29-35`, whenever `autoRepair` detects any logical issue, it re-runs `runDbHealthCheck` inside `connection.immediate()` (`BEGIN IMMEDIATE` with 5,000 ms busy timeout); keeping both `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED=true` and `OMNIROUTE_SKIP_DB_HEALTHCHECK=1` prevents a ~6.45s `PRAGMA quick_check` + 321k-row `scanQuotaSnapshots` scan from holding an exclusive `BEGIN IMMEDIATE` write lock on live traffic.
   - To provide physical B-tree integrity verification out of band without write-lock contention, `omniroute-watchdog.sh` Step 3 runs a read-only full `PRAGMA integrity_check` (`better-sqlite3` `{readonly:true, fileMustExist:true, timeout:15000}`, no `autoRepair`) every 6 hours (`21600s` mtime check on `~/.omniroute/integrity-last-ok`) when the container is `running`, `health != starting`, and `/healthz` returns HTTP 200, bounded by inner `child_process.spawnSync` (`110s` `SIGKILL`) and outer `gtimeout --signal=TERM --kill-after=5s 120s`. It touches `~/.omniroute/integrity-last-ok` only when all rows equal `'ok'` and logs/exits non-zero on failure without restarting an otherwise healthy gateway.
   - In `better-sqlite3`, `{ readonly: true, timeout: 15000 }` configures SQLite's `busy_timeout` lock-wait interval (15 seconds), not a wall-clock execution limit on running queries.
4. **Updater Failure-Gate Coverage vs. Runtime Probes & CLI Daemon Verification (Correction to Section 3 & Section 4)**:
   - Section 3 and Section 4 verified live container startup, HTTP health/model endpoints, and live chat/responses inference on `v3.8.51`. For `~/Omniroute/scripts/update.sh`, only Gate 0 (missing flag no-op exit `0`) and pre-flight lock contention (retaining `update-available` and exiting `1`) were exercised; Gates 1–9 failure branches (snapshot failure, digest mismatch, deploy failure, health timeout, version/image-id mismatch, endpoint failure, and post-deploy count regression) were **not** exercised end-to-end.
   - In the upstream CLI executed under the host bridge (`~/.local/bin/omniroute`), `omniroute status` (`bin/cli/commands/status.mjs`) read only local `package.json` and local bridge `DATA_DIR` metadata (`/tmp/omniroute-cli-bridge-*/storage.sqlite`) without contacting the HTTP daemon, and `omniroute keys list` (`bin/cli/commands/keys.mjs`) hit HTTP 404 on `/api/v1/providers/keys` and silently fell back to opening the empty local bridge SQLite file (`{"keys":[]}`). Neither command in its unhardened upstream form proved a healthy running daemon; Task 4.4 hardens `~/.local/bin/omniroute` so `status` queries live `/api/monitoring/health` + `/api/omniroute/status` (failing non-zero when unreachable) and `keys list` queries canonical `GET /api/providers?limit=5000` (`authType === "apikey" && apiKey`, masked metadata only, failing closed when unreachable), alongside native remote-backed `omniroute health --json`, `omniroute quota status`, and `omniroute combo list --output json`.
5. **OpenSpec Change Artifact Reconciliation**:
   - Reconciled all active change artifacts (`proposal.md`, `design.md`, `tasks.md`, `evidence.md`, `specs/bifrost-gateway/spec.md`, `specs/docker-lifecycle/spec.md`) in `/Users/androidteam/Developer/platform/openspec-store/openspec/changes/stabilize-omniroute-startup-and-update-readiness/` per user instruction (`update changes where needed`) and verified strict validation.

### 5.2 Current Live Read-Only Inspection (2026-10-19 Post-Audit Baseline)

- Read-only inspection of `/app/data/storage.sqlite` inside `omniroute` (`better-sqlite3` `{ readonly: true, fileMustExist: true, timeout: 15000 }`):
  - `storage.sqlite`: `1,111,265,280` bytes (~1.035 GiB, `page_count = 271,313`, `page_size = 4096`, `freelist_count = 0`, `journal_mode = "wal"`, `PRAGMA auto_vacuum = 2` / `INCREMENTAL`).
  - `storage.sqlite-wal` / `-shm`: `10,460,712` bytes / `32,768` bytes.
  - Read-only `PRAGMA quick_check`: `ok` in `6,454 ms` (~6.45s).
  - Critical table counts: `api_keys = 1`, `provider_connections = 32` (`26` active, `6` disabled), `combos = 5` (`quota_snapshots = 321,297` rows with `0` orphan rows).
  - `key_value` state: `scheduler/vacuumDrift = "null"` (`scheduler/vacuum` `autoVacuumDrift: null`), `databaseSettings` flat `autoVacuumMode = "\"INCREMENTAL\""` and `scheduledVacuum = "\"weekly\""` (dotted `optimization.*` keys absent), `feature_flags = []` (no DB override for `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED`; container env `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED="true"` and `OMNIROUTE_SKIP_DB_HEALTHCHECK="1"` govern).

### 5.3 Verified Post-Audit Remediation Results (2026-10-19)

- **Task 4.1 (`omniroute-watchdog.sh` + store mirror native `/usr/bin/lockf` locking & Step 3 6-hour read-only `PRAGMA integrity_check`) — VERIFIED**:
  - `/bin/bash -n` passed (exit `0`) on both `/Users/androidteam/Developer/scripts/omniroute-watchdog.sh` and `/Users/androidteam/Developer/platform/openspec-store/scripts/omniroute-watchdog.sh`.
  - `shasum -a 256` match: `9e7b9629e7217d055a7b3fa79b34824bc12dda83d7c44463ce154e00d4419f19` (`8/8` scripts in `config/script-provenance-manifest.tsv` verified with `0` drift).
  - Live watchdog execution ran bounded read-only `PRAGMA integrity_check` against `/app/data/storage.sqlite`, logged `[2026-10-19 12:07:23] INFO: Periodic SQLite physical integrity_check passed (ok). Updated /Users/androidteam/.omniroute/integrity-last-ok.`, and created `/Users/androidteam/.omniroute/integrity-last-ok`.
- **Task 4.2 (`~/Omniroute/scripts/update.sh` native `/usr/bin/lockf` locking, pre-release trap cleanup, `gtimeout` probe bounds, fail-closed Gate 1 `wal_checkpoint(TRUNCATE)` `0|*`, and pytest suite) — VERIFIED**:
  - `/bin/bash -n /Users/androidteam/Omniroute/scripts/update.sh` passed (exit `0`).
  - `uv run --project /Users/androidteam/Developer/platform/openspec-store pytest tests/test_omniroute_lock_and_watchdog.py` → **8/8 tests passed**, exercising simultaneous updater lock contention, watchdog exclusion while lock is held (ignoring ancient/corrupt lockfile contents), lock release on exit, temp snapshot cleanup while lock is still held, non-contention lock open failure, Gate 1 `wal_checkpoint(TRUNCATE)` failure preserving `-wal`/`-shm` sidecars, Gate 3 digest mismatch stopping before container recreation, Gate 9 post-deploy baseline count regression retaining `update-available`, and Watchdog Step 3 6-hour physical `integrity_check` pass/fresh-skip/fail behavior.
- **Task 4.3 (Fresh post-compaction 32-provider host backup in `~/.omniroute/snapshots/` under `/usr/bin/lockf`) — VERIFIED**:
  - Executed `/bin/bash /Users/androidteam/Omniroute/scripts/update.sh 3.8.51` through all 10 gates (`ALREADY_TARGET` verification run):
    - Captured and verified `/Users/androidteam/.omniroute/snapshots/pre-update-20261019-120627.sqlite` (`1.1 GB`, `live + host quick_check ok`, `wal_checkpoint=0|0|0`, sidecars consolidated).
    - Verified counts in `/Users/androidteam/.omniroute/snapshots/pre-update-20261019-120627.sqlite`: `PRAGMA quick_check = ok`, `api_keys = 1`, `provider_connections = 32`, `combos = 5`.
    - Verified Gate 8 endpoints (`anonymous GET /v1/models=401` + `authenticated GET=200 count=1196`, `/healthz=ok`, `dashboard=HTTP307`, `monitoring=healthy/setupComplete=true`, `HEAD /v1/models=200`, `muse_v1=200`, `muse_rewrite=200`) and Gate 9 (`quick_check=ok api_keys=1(>=1) provider_connections=32(>=32)`).
- **Task 4.4 (`~/.local/bin/omniroute` remote-truth hardening, `tests/test_omniroute_cli_bridge.py`, and OpenSpec artifact reconciliation) — VERIFIED**:
  - `uv run --project /Users/androidteam/Developer/platform/openspec-store pytest tests/test_omniroute_cli_bridge.py` → **6/6 tests passed** (`14/14` total with `test_omniroute_lock_and_watchdog.py`; `ruff check` passed with 0 issues).
  - Live `/Users/androidteam/.local/bin/omniroute status --output json` returned `{"status":"healthy","gateway":"healthy","version":"3.8.51","cliVersion":"3.8.51","database":{"status":"healthy","connected":true,"source":"remote"},"providers":{"configured":32,"active":26,"healthy":25,"disabled":6},"circuitBreakers":{"open":0,"halfOpen":0,"closed":24}}`.
  - Live `/Users/androidteam/.local/bin/omniroute keys list --output json` returned `13` configured API-key provider connections with `all_masked: true`.
  - Applied reconciled artifacts to `/Users/androidteam/Developer/platform/openspec-store/openspec/changes/stabilize-omniroute-startup-and-update-readiness/` and verified `openspec validate "stabilize-omniroute-startup-and-update-readiness" --strict --json --store openspec-store` (`valid: true, issues: []`) and `validate-archive-readiness.py --strict` (`status: ready, exit_code: 0`).
