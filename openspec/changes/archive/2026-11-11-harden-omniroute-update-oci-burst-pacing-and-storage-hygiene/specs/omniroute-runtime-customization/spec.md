# omniroute-runtime-customization Spec Delta

## MODIFIED Requirements

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
