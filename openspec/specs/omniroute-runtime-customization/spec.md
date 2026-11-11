# omniroute-runtime-customization Specification

## Purpose
Define evidence-backed operating boundaries for workstation customizations and independently evaluated optional capabilities without treating documentation or dependency presence as deployment proof.

## Requirements

### Requirement: Versioned Deployment and Customization Evidence
The operating record SHALL identify the source revision, deployed image identity, configuration authority, local overrides, and verification state separately, SHALL distinguish observations from proposals and unverified capabilities, and SHALL resolve upstream image index digests via keychain-free OCI Registry HTTP API v2 or isolated `DOCKER_CONFIG` probes without silent error suppression.

#### Scenario: Reviewing an image with local runtime changes
- **WHEN** an operator reviews a deployed image built from upstream sources with local runtime modifications
- **THEN** the record SHALL identify both the upstream image and the modifications, without describing a clean source checkout as an unmodified running application.

#### Scenario: Evaluating an upstream update
- **WHEN** a new upstream release becomes available or `~/Omniroute/scripts/check-upstream.sh` executes
- **THEN** the record SHALL preserve the previously validated identity until the candidate's compatibility is established, rather than requiring immediate parity with a moving branch
- **AND** `check-upstream.sh` SHALL resolve the remote multi-arch index digest primarily via the OCI Distribution Specification v1.1 Registry HTTP API v2 on Docker Hub (`diegosouzapw/omniroute:latest`) with automatic secondary OCI v2 mirror fallback to official GHCR (`ghcr.io/cheaper-inference/omniroute:latest`), falling back to `docker buildx imagetools inspect` under an ephemeral mode-`0700` `DOCKER_CONFIG` directory containing `{"auths":{},"credHelpers":{"index.docker.io":"","https://index.docker.io/v1/":"","registry-1.docker.io":"","docker.io":"","ghcr.io":""}}` plus `DOCKER_HOST` preservation

#### Scenario: Headless upstream update detection without macOS Keychain dependency
- **WHEN** `com.omniroute.update-check` executes `~/Omniroute/scripts/check-upstream.sh` in a non-interactive launchd session while `~/.docker/config.json` sets `"credsStore": "osxkeychain"`
- **THEN** `check-upstream.sh` SHALL execute under `umask 077`, SHALL NOT invoke `docker-credential-osxkeychain` (`errSecAuthFailed -25293`), SHALL compare the resolved `sha256:...` index digest against the running `omniroute` container's single extracted image digest (`IMG_ID=$(docker inspect omniroute --format '{{.Image}}')` -> `docker image inspect "$IMG_ID" --format '{{range .RepoDigests}}{{println .}}{{end}}' | grep -oE 'sha256:[a-f0-9]+' | head -n 1`, falling back to `diegosouzapw/omniroute:latest` only when the container is absent), and SHALL write `~/.omniroute/update-available` (`mode 0600`) when remote differs from local

#### Scenario: Explicit diagnostic logging when remote digest lookup fails
- **WHEN** both the OCI Registry HTTP API v2 probe and the isolated `DOCKER_CONFIG` `docker buildx imagetools inspect` fallback fail due to network unreachability or invalid digest format
- **THEN** `check-upstream.sh` SHALL log the captured diagnostic error details to `~/.omniroute/update-check.log` rather than discarding stderr to `/dev/null`

### Requirement: Persistent Data and Recoverable Updates
The workstation deployment SHALL retain its database in the named Docker volume, SHALL align timeouts, loopback bindings, and Redis health-gated startup ordering with OmniRoute's `SETUP_GUIDE.md` and `DOCKER_GUIDE.md`, SHALL suppress routine pre-write backup bloat with bounded retention, SHALL pull images under an isolated `DOCKER_CONFIG`, and SHALL enforce owner-only (`go-rwx`) host hygiene in `~/.omniroute/`.

#### Scenario: Recreating the application container
- **WHEN** the application container is recreated with the existing named volume
- **THEN** the documented procedure SHALL preserve that volume, rebind any replaced single-file host mounts, and verify retained data without claiming that the storage choice prevents every form of corruption.

#### Scenario: Failed post-deployment verification
- **WHEN** an upgrade fails a required verification gate
- **THEN** the operating record SHALL report failure, retain recovery references, restore any pre-deploy image digest pin in `docker-compose.override.yml` inside the exit handler before releasing `~/.omniroute/update.lock` so neither manual rollback nor watchdog restarts redeploy the failed image, and state whether rollback requires operator action; it SHALL NOT report automatic recovery or uninterrupted availability without evidence.

#### Scenario: Suppression of routine pre-write database backup bloat and keychain-free upgrade pulls
- **WHEN** `omniroute` runs under `--profile base` or `~/Omniroute/scripts/update.sh` executes Gate 2 (`pull`)
- **THEN** `/Users/androidteam/Omniroute/.env` SHALL configure `DISABLE_SQLITE_AUTO_BACKUP=true`, `DB_BACKUP_MAX_FILES=2`, `DB_BACKUP_RETENTION_DAYS=2`, `REQUEST_TIMEOUT_MS=600000`, `STREAM_IDLE_TIMEOUT_MS=600000`, `OMNIROUTE_BASE_URL=http://127.0.0.1:20128`, `APP_BIND_HOST=127.0.0.1`, `REDIS_BIND_HOST=127.0.0.1`, and `OMNIROUTE_USE_TURBOPACK=0` (loaded via `docker-compose.yml` `env_file: .env` without duplicating those keys in `docker-compose.override.yml`, with `backup: { autoBackupEnabled: false, keepLastNBackups: 2 }` persisted via `PATCH /api/settings/database`), `/Users/androidteam/Omniroute/docker-compose.override.yml` SHALL pin `omniroute-base` to the latest official stable release (`diegosouzapw/omniroute@sha256:b52a17661a1aff42ffb78f349f423e986dfc55b57274f28559f8387622ef8ee4`, `v3.8.53`) with `depends_on: { redis: { condition: service_healthy } }` and `services.redis.image` to the latest official stable `docker.io/library/redis:8.10.3-alpine@sha256:71885d8cc6e42f2bc0aa2eb853bfc4be200b5108a46ac50e117ae1df0531fb80`, and live `/app/data/storage.sqlite` SHALL pass `PRAGMA wal_checkpoint(TRUNCATE)` and `PRAGMA quick_check = ok` immediately before existing `db_*_pre-write.sqlite` copies are unlinked
- **AND** `update.sh` SHALL execute under `umask 077`, enforce `chmod 0600` on Gate 1 host snapshots copied via `docker cp`, prune `~/.omniroute/snapshots/*.sqlite` in Gate 9 to retain at most the 5 most recent verified snapshots, and execute `docker pull "$IMAGE_REF"` followed by `docker compose --profile base pull "$SERVICE" redis` in Gate 2 under an ephemeral mode-`0700` `DOCKER_CONFIG` (`credHelpers` empty-string overrides + `DOCKER_HOST` preservation, cleaned via `trap`) so `diegosouzapw/omniroute:latest` refreshes for Gate 3 despite `override.yml`'s digest pin and both `omniroute-base` and `redis` pull cleanly without macOS Keychain `-25293` failures

#### Scenario: Host `~/.omniroute/` legacy artifact cleanup, snapshot cap, and permission hardening
- **WHEN** `/Users/androidteam/.omniroute/`, `/Users/androidteam/.omniroute/snapshots/`, and `/Users/androidteam/Omniroute/` are inspected
- **THEN** obsolete pre-Docker host artifacts (`~/.omniroute/storage.sqlite`, `storage.sqlite-wal`, `storage.sqlite-shm`, `db_backups/`, `server.log`, `server.err`, `call_logs/`, `logs/`, `log_archives/`, and `/Users/androidteam/Omniroute/data.bak-20260824/`) SHALL be absent so host CLI tools cannot open stale world-readable pre-Docker SQLite databases
- **AND** `~/.omniroute/snapshots/` SHALL retain at most the 5 most recent verified `.sqlite` snapshots consolidated in `journal_mode=delete` with zero `*.sqlite-wal` or `*.sqlite-shm` sidecars, and POSIX permissions across `~/.omniroute/` SHALL enforce `go-rwx` (`0700` on directories and executable scripts/binaries, and `0600` on snapshots, logs, and data files, preserving `~/.omniroute/backups/scale-omniroute-concurrency-and-add-gemini-4-carbon/` intact)

### Requirement: Compatibility Behavior and Patch Retirement Gates
The compatibility ledger SHALL map each local modification in `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`3` non-chunk patches and `7` chunk replacements = `10` modifications in `v3.8.53+`) to its behavior, `15` fail-closed markers across `6` server chunks, and removal gate. Modifications SHALL use atomic sibling temp-file renames (`fs.renameSync`), `ensure-muse-wire-compat.sh` SHALL wait for PID 1 entrypoint completion, and missing markers SHALL fail closed.

#### Scenario: Retiring one upstreamed fix
- **WHEN** a validated upstream release supplies a replacement for a local modification
- **THEN** only that modification SHALL become eligible for retirement after its behavior passes verification, and unrelated modifications SHALL remain accounted for.

#### Scenario: Missing required compatibility state
- **WHEN** a candidate deployment cannot demonstrate a required compatibility condition or a target chunk or server file for any of the 15 required markers (`3` non-chunk and `12` chunk markers across `6` compiled server chunk files) is absent or renamed
- **THEN** `/app/container-entrypoint-compat.sh` SHALL fail closed with `[COMPAT_ERROR]` and exit `1` rather than silently skipping verification, and SHALL NOT promote the deployment as compatible.

#### Scenario: Atomic compatibility file writes and entrypoint readiness serialization
- **WHEN** `/app/container-entrypoint-compat.sh` patches `/app/peer-stamp.mjs`, Next.js server route files, or server chunks, or when `~/Omniroute/scripts/ensure-muse-wire-compat.sh` verifies container runtime patches after `docker compose up -d`
- **THEN** `/app/container-entrypoint-compat.sh` SHALL write modified contents via `atomicWriteFileSync` (sibling `.tmp-<pid>-<ts>` write followed by `fs.renameSync` with error-path `fs.unlinkSync` cleanup) so interruption or concurrent inspection can never leave a 0-byte truncated or orphaned temp file in the container writable layer
- **AND** `ensure-muse-wire-compat.sh` SHALL poll `/proc/1/cmdline` (`! grep -qF "container-entrypoint-compat.sh" /proc/1/cmdline`) up to 15 seconds until PID 1 finishes `container-entrypoint-compat.sh` before invoking `/app/container-entrypoint-compat.sh --patch-only`.

### Requirement: Hybrid Retrieval Evaluation and Isolation
The evaluation plan SHALL compare lexical and semantic retrieval on the same authorized query set and corpus (covering embedding, filtering, ranking, reranking, and fallback costs) and SHALL enforce owner and `expires_at` filtering across SQLite `memories`, `memory_fts`, `vec_memories`, and Qdrant `fetchMemoriesByIds` paths. It SHALL retain the existing hybrid deployment until an alternative passes acceptance and cutover approval.

#### Scenario: Comparing local and external vector backends
- **WHEN** an evaluator compares supported local hybrid retrieval with Qdrant-backed retrieval
- **THEN** the report SHALL include relevance, end-to-end latency, resource use, configuration, and sample conditions; isolated keyword-query timings SHALL NOT be presented as equivalent semantic-search performance.

#### Scenario: Deleted, expired, or differently owned memories
- **WHEN** retrieval evaluates deleted or expired records (`expires_at <= datetime('now')`) or records outside the caller's authorized owner scope across `fetchMemoriesByIds`, `VectorStoreImpl.searchVector`, or `VectorStoreImpl.searchHybrid`
- **THEN** those records SHALL NOT appear in returned candidates or injected context, including on vector and hybrid fallback paths.

#### Scenario: Vector backend failure
- **WHEN** an evaluated vector backend fails or has no usable vectors
- **THEN** the report SHALL identify the fallback actually used and its quality impact rather than counting lexical fallback as successful semantic retrieval.

### Requirement: Independent Optional Capability Readiness
Optional capabilities SHALL be assessed independently against a named use case, supported deployment path, prerequisites, security boundary, resource budget, and observable acceptance criteria. Unverified candidates SHALL NOT be described as enabled or production-ready.

#### Scenario: Installed dependency without runtime assets
- **WHEN** an ML or browser package resolves but its required model assets or executable is absent
- **THEN** readiness SHALL remain unverified until the required execution succeeds through the supported runtime path.

#### Scenario: Optional pack installation source
- **WHEN** an optional pack installation procedure is documented
- **THEN** it SHALL distinguish indexed local pack archives from registry package installation and SHALL identify whether the operation targets the host, desktop application, or container.

#### Scenario: Selecting an optional extension
- **WHEN** one optional extension is selected for evaluation
- **THEN** its activation SHALL NOT require unrelated extensions merely because they were grouped into an enterprise profile.

### Requirement: Relay Backend Boundary and Failure Semantics
The Bifrost evaluation record SHALL limit its integration claims to supported relay routes, distinguish native inference processing from relay forwarding, and describe fallback by failure class and selected mode.

#### Scenario: Native coding-agent request
- **WHEN** a client uses the ordinary native inference surface
- **THEN** enabling a relay backend SHALL NOT be reported as proof that the request used Bifrost or preserved native features through Bifrost.

#### Scenario: Relay failure before or after output begins
- **WHEN** an evaluated relay backend encounters a transport error, an upstream HTTP error, or a partial-stream failure
- **THEN** evidence SHALL identify which cases return errors, permit fallback, or cannot be transparently replayed, without promising automatic retry for all failures.

### Requirement: High-Concurrency Heavyweight Chat Admission, Queue Byte Budgets, and Libuv Threadpool Scaling via Configuration Only
The OmniRoute gateway deployment (`/Users/androidteam/Omniroute/.env` and `/Users/androidteam/Omniroute/docker-compose.override.yml`) SHALL configure `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=32`, `OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES=67108864`, `OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES=268435456`, `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=30000`, and `UV_THREADPOOL_SIZE=32` while keeping zero tracked git modifications in `/Users/androidteam/Omniroute` and fast-forwarding local `main` to `origin/main`.

#### Scenario: 32 primary heavy slots plus 32 healthy-heap headroom slots admit up to 64 concurrent tool-bearing agent streams without queueing
- **WHEN** the `omniroute` container is running under `--profile base` and `docker exec omniroute env` is inspected
- **THEN** `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT` SHALL be `32`, `OMNIROUTE_CHAT_ADMISSION_MAX_QUEUED_BYTES` SHALL be `67108864` (`64 MB`), `OMNIROUTE_CHAT_MAX_INFLIGHT_BYTES` SHALL be `268435456` (`256 MB`), `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS` SHALL be `30000` (`30s`), and `UV_THREADPOOL_SIZE` SHALL be `32`
- **AND** up to 64 concurrent heavy requests (`tools.length >= 64` or `content-length >= 256 KB`) while V8 heap utilization is below `0.75` and total active request bytes are below `256 MB` SHALL be admitted immediately without entering the wait queue or returning `HTTP 503 chat_admission_busy`

#### Scenario: Burst overflow beyond active heavy slots parks up to 64 MB in the fairness queue without premature 4 MB byte-budget shedding
- **WHEN** a burst of concurrent heavy requests exceeds active heavy admission slots and waits in `acquireHeavyWithin(30000)`
- **THEN** parked waiters up to `67,108,864` bytes (`64 MB`) total buffered payload SHALL remain queued for up to `30,000 ms` rather than being immediately shed at the legacy `4,194,304` byte (`4 MB`) default with `reason: "queued_bytes_budget"`

#### Scenario: Upstream git checkout remains clean and fast-forwarded for official release upgrades
- **WHEN** `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` and `git -C /Users/androidteam/Omniroute rev-list --left-right --count HEAD...origin/main` are executed
- **THEN** `git status --porcelain --untracked-files=no` SHALL output zero lines (all runtime tuning confined to untracked `.env`, `docker-compose.override.yml`, and the `omniroute-data` SQLite volume)
- **AND** local `main` SHALL be fast-forwarded to `origin/main` (`0` commits behind) so `~/Omniroute/scripts/update.sh` Gate P and Gate 8b (`MEM_OFF|CACHE_ALIGNED|COMP_OFF|TTFT_ZERO|PATCH_OK`) pass without manual conflict resolution
