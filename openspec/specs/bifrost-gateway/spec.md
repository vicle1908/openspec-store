# OmniRoute Proxy Specification

## Purpose

This specification defines the local OmniRoute proxy deployment and its integration with agent-core's native pydantic-ai model API. OmniRoute provides an OpenAI-compatible endpoint; agent consumers resolve a pydantic-ai `Model` with `create_model()` and pass it through the `model=` parameter.

## Requirements

### Requirement: OmniRoute SHALL run as a Docker Compose service

The system SHALL deploy OmniRoute from `~/Omniroute/docker-compose.yml` with the `base` profile. The local override SHALL use the pre-built `diegosouzapw/omniroute:latest` image, and the service SHALL be named `omniroute` with `restart: unless-stopped`.

#### Scenario: Service starts successfully
- **WHEN** `docker compose --profile base up -d --no-build` is run from `~/Omniroute/`
- **THEN** the `omniroute` container starts and its Compose health check becomes healthy

#### Scenario: Service restarts automatically
- **WHEN** the OmniRoute container crashes or the host restarts Docker
- **THEN** Docker restarts the container using the `unless-stopped` policy

### Requirement: OmniRoute SHALL persist runtime data

The deployment SHALL persist OmniRoute runtime state on the Docker named
volume `omniroute-data` mounted at `/app/data`. Host filesystem bind mounts
SHALL NOT be used for `/app/data` because Docker Desktop for Mac virtiofs
bind mounts corrupt SQLite WAL databases and OmniRoute hardcodes WAL mode.
Redis rate-limiter state SHALL use the named `omniroute-redis-data` volume,
and the Redis service SHALL NOT publish any port to the host.

#### Scenario: Configuration persists across restarts

- **WHEN** OmniRoute runtime configuration is changed and the container is restarted
- **THEN** the configuration and runtime data remain available after restart

#### Scenario: Named volume survives container recreation

- **WHEN** `docker compose --profile base up -d --no-build` recreates the `omniroute` container
- **THEN** the `omniroute-data` volume is reattached at `/app/data` and the SQLite database and its runtime state remain intact

#### Scenario: Data directory is created if missing

- **WHEN** the `omniroute-data` named volume does not yet exist and the Compose profile is started
- **THEN** Docker creates the named volume mounted at `/app/data` and the service can initialize its data store

#### Scenario: Redis is not host-published

- **WHEN** the rendered Compose configuration is inspected
- **THEN** the `redis` service has no published ports and is reachable only via the Compose network

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

### Requirement: Native model resolution SHALL be the consumer integration boundary

Agent-core consumers SHALL resolve the configured model through `create_model()` and pass the resulting pydantic-ai `Model` through `model=`. Endpoint, API key, and timeout overrides SHALL be represented by `ModelSettings` or explicit `create_model()` keyword arguments; consumers SHALL NOT construct a separate proxy client abstraction.

#### Scenario: Consumer resolves an OmniRoute model
- **WHEN** a consumer loads `model.primary` and `model.base_url` from its settings
- **THEN** it calls `create_model(model_id, base_url=base_url, api_key=api_key)` and receives a pydantic-ai `Model`
- **AND** it passes that instance to agent construction as `model=model`

#### Scenario: Explicit model settings override environment defaults
- **WHEN** `create_model()` receives an explicit `ModelSettings` value or explicit endpoint and API-key arguments
- **THEN** those values take precedence over the process environment and provider defaults

#### Scenario: Upstream model failure is typed
- **WHEN** OmniRoute returns an API failure or cannot reach the selected provider
- **THEN** the model call raises `ModelAPIError` with a safe diagnostic category and without exposing credentials

### Requirement: Native retry and fallback SHALL handle provider failures

Consumers SHALL use pydantic-ai's native retry behavior and `FallbackModel` for optional provider failover. They SHALL NOT add a second resilience wrapper around OmniRoute calls. A fallback SHALL be attempted only for configured retryable model failures; authentication and invalid-request failures SHALL remain terminal.

#### Scenario: Transient model failure is retried
- **WHEN** a model call fails with a timeout, connection error, or retryable 5xx response
- **THEN** native model retry applies the configured retry limit and backoff before returning failure

#### Scenario: Fallback model is attempted
- **WHEN** the primary OmniRoute-backed model fails with a retryable `ModelAPIError` and a fallback model is configured
- **THEN** `FallbackModel` attempts the fallback model

#### Scenario: Non-retryable model failure is not hidden
- **WHEN** the provider returns an authentication or invalid-request error
- **THEN** the error is surfaced immediately and no fallback attempt is made

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

### Requirement: OmniRoute SHALL follow local deployment conventions

The deployment SHALL use Docker Compose v2 commands, keep the `base` profile opt-in, use loopback-only bindings for local model traffic by default, and keep secrets in the untracked `.env` file or an approved secret manager. The compose project and primary container name SHALL be `omniroute`.

#### Scenario: Docker Compose v2 is used
- **WHEN** the service is managed from the deployment directory
- **THEN** `docker compose` commands are used rather than the legacy `docker-compose` command

#### Scenario: Secrets are not committed
- **WHEN** the deployment is prepared for a new workstation
- **THEN** provider API keys are supplied through `.env` or an approved secret store and no secret value is committed to the repository

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

#### Scenario: Endpoint gate validates Muse Code catalog routes advertise muse-spark-1.3

- **WHEN** `~/Omniroute/scripts/update.sh` runs Gate 8 (`endpoints`) against the deployed OmniRoute container
- **THEN** Gate 8 SHALL verify that `GET /v1/muse-code/models` and `GET /muse-code/models` both return HTTP `200` with a JSON `data` array containing model entry `id === "muse-spark-1.3"`
- **AND** if either endpoint returns a non-200 status or an empty/missing `muse-spark-1.3` catalog entry, Gate 8 SHALL fail closed and retain `~/.omniroute/update-available`

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
- **AND** redundant in-volume backup files (including `db_state-*_pre-migration.sqlite` snapshots created during image upgrade migrations once Gate 9 post-deploy `PRAGMA quick_check = ok` and baseline counts succeed) SHALL be removed so `/app/data` retains only active SQLite database files (`1000:1000` `node:node` ownership) and managed runtime directories

#### Scenario: High-volume telemetry tables are pruned and compacted cleanly

- **WHEN** `conversation_turn_nodes`, `quota_snapshots`, or `call_logs` exceed their configured retention window (`conversationTurnNodes <= 7` days, `quotaSnapshots <= 14` days, `callLogs <= 30` days) during offline maintenance under `/usr/bin/lockf -k -t 0 ~/.omniroute/update.lock`
- **THEN** both flat and dotted `retention.*` keys in `key_value` (`namespace = 'databaseSettings'`) and the ISO-8601 `T`/`Z`-cutoff deletions of expired `conversation_turn_nodes`, orphaned `agentic_conversations`, and `quota_snapshots` SHALL execute in a single joint transaction
- **AND** offline `PRAGMA wal_checkpoint(TRUNCATE)` and `VACUUM` SHALL run as UID:GID `1000:1000` followed by fail-closed programmatic assertions that `PRAGMA quick_check = ok` and `api_keys`, `provider_connections`, and `combos` counts are preserved

### Requirement: OmniRoute deployment SHALL configure coding-agent runtime limits and stream resilience

The local OmniRoute Docker deployment override SHALL configure runtime memory sizing, tool definition limits, and stream resilience calibrated for local workstation coding agents (`OMNIROUTE_MEMORY_MB`, `OMNIROUTE_MAX_TOOLS_LIMIT`, `STREAM_READINESS_STALL_RETRY`, and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED`).

#### Scenario: Coding agent runtime memory and tool limits are configured
- **WHEN** the `omniroute-base` container is deployed with `docker-compose.override.yml`
- **THEN** its environment SHALL contain `OMNIROUTE_MEMORY_MB=4096`
- **AND** its environment SHALL contain `OMNIROUTE_MAX_TOOLS_LIMIT=256`
- **AND** its environment SHALL contain `STREAM_READINESS_STALL_RETRY=true` and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true`
- **AND** `STREAM_RECOVERY_ENABLED` SHALL NOT be forced to `true` globally to avoid imposing a mandatory 750 ms time-to-first-token holdback latency penalty on interactive streams
