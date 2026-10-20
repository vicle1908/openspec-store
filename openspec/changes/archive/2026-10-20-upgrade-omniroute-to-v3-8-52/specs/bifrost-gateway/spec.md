# Spec Delta

## MODIFIED Requirements

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
