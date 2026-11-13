# Spec Delta

## ADDED Requirements

### Requirement: Systematic multi-tier package cache eviction

The storage hygiene workflow SHALL execute rebuildable package and download cache eviction across Homebrew, npm, Python uv, Bun, and Go using only official vendor tool commands, purging transient archives without deleting project configurations, locked dependencies, or active source trees.

#### Scenario: Homebrew download bottle cache is pruned
- **WHEN** the operator triggers Tier 1 package cache cleanup
- **THEN** the system SHALL run `brew cleanup --prune=all` to remove all cached bottle archives, installer dmgs, and downloads
- **AND** the system SHALL verify that active formula and cask installations in `/opt/homebrew/Cellar` and `/opt/homebrew/Caskroom` remain intact.

#### Scenario: Node and npm temporary caches are flushed
- **WHEN** the operator triggers Tier 1 package cache cleanup
- **THEN** the system SHALL run `npm cache clean --force` to flush cached tarballs
- **AND** the system SHALL run `rm -rf ~/.npm/_npx/*` to purge unreferenced binary downloads
- **AND** globally installed npm packages in `~/.npm-global` SHALL remain unaffected.

#### Scenario: Python uv wheel archive cache is purged
- **WHEN** the operator triggers Tier 1 package cache cleanup
- **THEN** the system SHALL run `uv cache clean` to remove cached wheels, sdists, and build archives from `~/.cache/uv`
- **AND** virtual environments in active workspace projects (`.venv`) SHALL remain operational.

#### Scenario: Bun package cache is cleared
- **WHEN** the operator triggers Tier 1 package cache cleanup
- **THEN** the system SHALL run `bun pm cache rm` to remove transient package tarballs from `~/.bun/install/cache`.

#### Scenario: pnpm unreferenced package store is pruned
- **WHEN** the operator triggers Tier 1 package cache cleanup
- **THEN** the system SHALL run `pnpm store prune` to delete unreferenced package files from `~/.pnpm-store`.

#### Scenario: Go compilation cache is cleared
- **WHEN** the operator triggers Tier 1 package cache cleanup
- **THEN** the system SHALL run `go clean -cache` to clear rebuildable build objects from `~/Library/Caches/go-build`
- **AND** active module definitions in `go.mod` SHALL remain unchanged.

#### Scenario: Simulator dyld shared caches are purged via simctl
- **WHEN** the operator triggers simulator cache cleanup
- **THEN** the system SHALL run `xcrun simctl runtime dyld_shared_cache remove --all` to remove rebuildable runtime caches from `/Library/Developer/CoreSimulator/Caches/dyld`
- **AND** installed runtime disk images SHALL remain ready.

### Requirement: Docker builder cache and image pruning with container volume safety

The storage hygiene workflow SHALL reclaim disk blocks from Docker Desktop build cache and unreferenced images while strictly protecting active containers, essential named database volumes, and persistent storage.

#### Scenario: Docker builder cache is cleared
- **WHEN** Docker daemon is running and reports reclaimable builder cache
- **THEN** the system SHALL execute `docker builder prune -a -f`
- **AND** the system SHALL verify that running container services (`omniroute`, `omniroute-redis`, `shb-schedule-scheduler-1`, `shb-schedule-db-1`) remain healthy.

#### Scenario: Unreferenced Docker images are pruned
- **WHEN** Docker reports dangling or unreferenced images
- **THEN** the system SHALL execute `docker image prune -a -f`
- **AND** images required by active containers SHALL NOT be removed.

#### Scenario: Named database volumes are safeguarded
- **WHEN** any Docker pruning operation executes
- **THEN** the workflow MUST NOT execute blanket `docker volume prune -a`
- **AND** named and mounted database volumes `omniroute_omniroute-data`, `omniroute-redis-data`, `omniroute-qdrant-data`, `shb-schedule_shb-scheduler-pgdata`, and `685eacfa...` SHALL be preserved.

#### Scenario: Orphaned test volumes are decommissioned by explicit identifier
- **WHEN** historical audit or smoke-test volumes are confirmed obsolete
- **THEN** the workflow SHALL delete only explicitly confirmed unattached volume names (`0b050242...`, `shb-audit-*`, `shb-verification-*`, `smoke_scheduler_*`) via `docker volume rm`.

### Requirement: Obsolete local development build artifact and database dump retirement

The storage hygiene workflow SHALL identify and decommission unmounted host build artifacts and stale historical database dumps outside active repository tracking.

#### Scenario: Unmounted OmniRoute host build cache is retired
- **WHEN** the host directory `~/Omniroute/.build` is unmounted and OmniRoute runs exclusively via Docker container
- **THEN** the system SHALL permit removal of `~/Omniroute/.build` to recover host disk space
- **AND** the containerized OmniRoute runtime on ports 20128 and 20129 SHALL remain unaffected.

#### Scenario: Historical audit database dumps are retired
- **WHEN** a historical database dump file older than 90 days (`vds-scripts/docker/backups/pre-p0-audit.dump`) is unreferenced by active pipelines
- **THEN** the workflow SHALL permit removal or compression of the snapshot file after explicit operator authorization.

### Requirement: Post-cleanup APFS Data volume headroom gate

The storage hygiene workflow SHALL verify filesystem capacity and availability before and after each tier, confirming that the workstation recovers sufficient operational headroom.

#### Scenario: Headroom exceeds safe operational threshold
- **WHEN** Tier 1 and Tier 2 cleanup phases complete
- **THEN** the system SHALL verify available capacity on `/System/Volumes/Data` via `df -h`
- **AND** available capacity SHALL exceed 40 GiB
- **AND** the workflow SHALL record net reclaimed gigabytes in the execution report.
