# Spec Delta

## MODIFIED Requirements

### Requirement: OmniRoute SHALL expose an OpenAI-compatible model API

The deployment SHALL expose `http://127.0.0.1:20128/v1` (`/chat/completions`, `/responses`, `/models`) bound to loopback by default. `HEAD /v1/models` SHALL return HTTP 200 publicly. Since v3.8.50, catalog authentication is opt-out (`requireAuthForModels`): anonymous `GET /v1/models` SHALL return HTTP 401 (`invalid_api_key`) when enabled or HTTP 200 when disabled, while requests with a valid Bearer API key SHALL receive HTTP 200 with a non-empty catalog in either posture.

#### Scenario: Chat completion through the proxy

- **WHEN** a valid OpenAI Chat Completions request is sent to `http://127.0.0.1:20128/v1/chat/completions`
- **THEN** OmniRoute returns an OpenAI-compatible completion response from the selected provider

#### Scenario: Models endpoint lists available models

- **WHEN** a client sends an authenticated `GET http://127.0.0.1:20128/v1/models` with a valid Bearer API key
- **THEN** OmniRoute returns the models exposed by the configured provider set

#### Scenario: No LAN exposure by default

- **WHEN** the standard local profile is running
- **THEN** the model API is reachable from the host loopback interface and is not exposed to the LAN

#### Scenario: HEAD models probe is public

- **WHEN** a client sends `HEAD http://127.0.0.1:20128/v1/models` without credentials
- **THEN** OmniRoute returns HTTP 200 as the availability probe

#### Scenario: Anonymous catalog access follows the configured auth posture

- **WHEN** catalog authentication is enabled and a client sends an unauthenticated `GET http://127.0.0.1:20128/v1/models`
- **THEN** OmniRoute returns HTTP 401 with an `invalid_api_key` error
- **AND** when catalog authentication is disabled the same request returns HTTP 200 with a non-empty catalog

### Requirement: OmniRoute SHALL expose a dashboard and health status

The service SHALL serve its dashboard on the configured main port and expose the health endpoint probed by `node healthcheck.mjs` with a 30-second interval, 15-second timeout, 3 retries, and 120-second start period in `docker-compose.override.yml` so background model and credential synchronization does not trigger false-positive health check timeouts.

#### Scenario: Dashboard is accessible locally

- **WHEN** a client requests `http://127.0.0.1:20128/`
- **THEN** the OmniRoute dashboard responds (directly or via redirect to login) and reports the local proxy status

#### Scenario: Compose health check passes

- **WHEN** the service is running and its model proxy process is ready
- **THEN** `docker inspect --format='{{.State.Health.Status}}' omniroute` returns `healthy`

#### Scenario: Health check failure is visible

- **WHEN** the proxy process cannot serve its configured endpoint
- **THEN** the Compose health status becomes `unhealthy` and the container logs retain the diagnostic output

### Requirement: OmniRoute image upgrades SHALL be fail-closed and evidence-gated

OmniRoute upgrades SHALL pull the verified Docker Hub image and recreate the container without source compilation under a persistent kernel lock (`~/.omniroute/update.lock` via `/usr/bin/lockf`). The workflow SHALL pass a bounded pre-pull SQLite snapshot gate (`PRAGMA quick_check = ok`, fail-closed `wal_checkpoint(TRUNCATE)`, post-checkpoint `quick_check = ok`), verify pulled digest equality, and verify health, version, image ID, endpoints, and post-deploy data before clearing the flag.

#### Scenario: Snapshot gate blocks an unsafe upgrade

- **WHEN** the pre-update SQLite snapshot fails, live or host `PRAGMA quick_check` is not `ok`, or host snapshot `PRAGMA wal_checkpoint(TRUNCATE)` does not return `0|*` (`busy == 0`)
- **THEN** the update stops before any image pull, cleans up any temporary in-container snapshot file before releasing the kernel lock on `~/.omniroute/update.lock` (without unlinking the persistent lockfile or removing uncheckpointed host `-wal`/`-shm` sidecars), and retains the update flag

#### Scenario: Digest mismatch blocks deployment

- **WHEN** the pulled `diegosouzapw/omniroute:latest` RepoDigest differs from the flagged target digest
- **THEN** the update stops before container recreation and the update flag is retained

#### Scenario: Flag cleared only after full verification

- **WHEN** the health, version, image-id, endpoint, and post-deploy data gates all pass
- **THEN** the update flag is removed and the success is recorded in the update log

#### Scenario: Failed gate retains the flag

- **WHEN** any verification gate fails during or after deployment
- **THEN** the update flag remains present, the failed gate is logged, and no success notification is sent

#### Scenario: Upgrade does not change unrelated infrastructure

- **WHEN** an application image upgrade is applied
- **THEN** the Redis image remains the currently deployed major version, no new Compose profile is activated, published ports remain bound to 127.0.0.1, `/app/data` remains on the `omniroute-data` named volume, and the SOCKS5 proxy flags remain disabled

#### Scenario: Upgrade script coordinates exclusive maintenance lock via kernel descriptor locking

- **WHEN** `~/Omniroute/scripts/update.sh <expected-version>` runs past Gate 0 and argument validation
- **THEN** it SHALL open persistent `~/.omniroute/update.lock` on file descriptor `9` (`umask 077`) and acquire a non-blocking exclusive kernel lock via `/usr/bin/lockf -s -t 0 9` before `pre-state`, exiting `1` and retaining `~/.omniroute/update-available` on contention (`rc = 75`) or failing closed non-zero on other lock errors
- **AND** once locked, its `EXIT` trap SHALL preserve the original exit status, remove any temporary `/tmp/pre-update-*.sqlite` inside the container before shell exit closes FD `9`, and never parse PID/epoch metadata or unlink `~/.omniroute/update.lock`

## ADDED Requirements

### Requirement: Startup database health checks SHALL not block gateway readiness

The OmniRoute deployment SHALL defer startup SQLite health checks off the synchronous initialization path via `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED=true` and `OMNIROUTE_SKIP_DB_HEALTHCHECK=1` in `docker-compose.override.yml` so HTTP readiness probes respond within `start_period`, managed repairs never run `PRAGMA quick_check` inside `BEGIN IMMEDIATE`, and physical integrity checks execute out of band.

#### Scenario: Container reaches healthy state without main-thread SQLite scan deadlock

- **WHEN** `omniroute-base` starts against the `/app/data/storage.sqlite` database on the `omniroute-data` (`omniroute_omniroute-data`) volume
- **THEN** `getDbInstance()` SHALL complete without running a synchronous main-thread `PRAGMA quick_check` or full `quota_snapshots` table scan before HTTP listeners accept requests
- **AND** `GET http://127.0.0.1:20128/healthz` SHALL return `ok` (HTTP 200) and container health SHALL transition to `healthy` within the configured `start_period`

#### Scenario: Deferred startup and managed health checks skip in-transaction quick_check

- **WHEN** `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED=true` and `OMNIROUTE_SKIP_DB_HEALTHCHECK=1` are configured in `~/Omniroute/docker-compose.override.yml`
- **THEN** startup, periodic 6-hour, and manual managed health checks (`core.ts:954` / `healthCheckWorker.ts`) SHALL execute logical table checks out of band in the child worker while skipping `PRAGMA quick_check` so `autoRepair` passes inside `BEGIN IMMEDIATE` do not stall main-process writes
- **AND** physical SQLite B-tree verification SHALL run out of band via read-only `PRAGMA quick_check` in `update.sh` and bounded 6-hour read-only full `PRAGMA integrity_check` (`~/.omniroute/integrity-last-ok`) in `omniroute-watchdog.sh`

### Requirement: Named-volume SQLite storage SHALL maintain bounded retention and snapshot hygiene

The `omniroute-data` (`omniroute_omniroute-data`) volume at `/app/data` SHALL not retain orphaned in-volume snapshot backup files alongside `storage.sqlite` and SHALL enforce bounded retention windows for high-volume telemetry tables (`conversation_turn_nodes`, `quota_snapshots`, `call_logs`) backed by verified host snapshots in `~/.omniroute/snapshots/`.

#### Scenario: Orphaned in-volume snapshot backups are removed and current host backup is retained

- **WHEN** `/app/data/storage.sqlite.snapshot.bak` or superseded pre-migration backups in `/app/data/db_backups/` exist inside `/app/data` on `omniroute-data`
- **THEN** a verified host snapshot in `~/.omniroute/snapshots/` (`PRAGMA quick_check = ok`, consolidated via fail-closed `PRAGMA wal_checkpoint(TRUNCATE)`, matching live `api_keys`, `provider_connections`, and `combos` counts) SHALL be maintained on the host
- **AND** redundant in-volume backup files SHALL be removed so `/app/data` retains only active SQLite database files (`1000:1000` `node:node` ownership) and managed runtime directories

#### Scenario: High-volume telemetry tables are pruned and compacted cleanly

- **WHEN** `conversation_turn_nodes`, `quota_snapshots`, or `call_logs` exceed their configured retention window (`conversationTurnNodes <= 7` days, `quotaSnapshots <= 14` days, `callLogs <= 30` days) during offline maintenance under `/usr/bin/lockf -k -t 0 ~/.omniroute/update.lock`
- **THEN** both flat and dotted `retention.*` keys in `key_value` (`namespace = 'databaseSettings'`) and the ISO-8601 `T`/`Z`-cutoff deletions of expired `conversation_turn_nodes`, orphaned `agentic_conversations`, and `quota_snapshots` SHALL execute in a single joint transaction
- **AND** offline `PRAGMA wal_checkpoint(TRUNCATE)` and `VACUUM` SHALL run as UID:GID `1000:1000` followed by fail-closed programmatic assertions that `PRAGMA quick_check = ok` and `api_keys`, `provider_connections`, and `combos` counts are preserved
