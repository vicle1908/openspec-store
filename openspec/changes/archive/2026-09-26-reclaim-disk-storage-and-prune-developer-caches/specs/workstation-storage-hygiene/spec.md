## Purpose

Extends workstation storage hygiene with automated, multi-tiered rebuildable package cache evacuation and historical developer backup reclamation procedures.

## ADDED Requirements

### Requirement: Multi-tiered rebuildable package cache reclamation

The storage hygiene workflow SHALL execute automated cache eviction commands using only official native vendor tools (`brew`, `npm`, `uv`, `pnpm`, `go`, and `docker`) to reclaim disk space from ephemeral download caches and build artifacts without deleting project dependencies or active files.

#### Scenario: Native package manager caches are pruned
- **WHEN** the operator executes Tier 1 cache reclamation
- **THEN** the system SHALL run `brew cleanup --prune=all -s` to remove all cached Homebrew bottles
- **AND** the system SHALL run `npm cache clean --force` to flush global npm tarball caches
- **AND** the system SHALL run `uv cache clean` to purge unreferenced python wheels
- **AND** the system SHALL run `pnpm store prune` to delete unreferenced pnpm package files
- **AND** the system SHALL run `go clean -cache` to clear Go build objects.

### Requirement: Obsolete development backup archive purging

The storage hygiene workflow SHALL identify and purge obsolete, historical vector database backup directories and unreferenced container build layers while strictly preserving live operational databases, active repositories, and running container volumes.

#### Scenario: Historical Qdrant backup directories in context-please are purged
- **WHEN** historical timestamped backup directories matching `qdrant_storage.bak_*` are detected in `~/Developer/mcp-servers/context-please`
- **THEN** the system SHALL verify they are not the active `qdrant_storage` directory
- **AND** the system SHALL delete the historical backup folders to reclaim disk space.

#### Scenario: Dangling Docker builder cache is cleared
- **WHEN** Docker daemon is running and reports reclaimable build cache
- **THEN** the system SHALL execute `docker builder prune -f`
- **AND** active images and container volumes SHALL remain protected.
