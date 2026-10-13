# Spec Delta: docker-resource-access

## MODIFIED Requirements

### Requirement: Safe volume-preserving disk reclamation

The disk headroom safeguard SHALL monitor available storage on `/System/Volumes/Data` and execute pruning that removes dangling objects, expired build cache, and anonymous volumes, while strictly preserving all named volumes and recent images.

#### Scenario: Low disk space triggers warning
- **WHEN** available disk space on the host volume falls below 30 GiB
- **THEN** `docker-disk-guard.sh` logs an urgent alert indicating reclaimable storage reported by `docker system df`

#### Scenario: Safe automated pruning execution
- **WHEN** `docker-disk-guard.sh --prune` is executed
- **THEN** it executes:
  1. `docker image prune -a --filter "until=24h" -f` (removes unused images older than 24h)
  2. `docker builder prune -f` (cleans dangling BuildKit build cache)
  3. `docker volume prune -f` (removes unused anonymous volumes only, preserving named volumes)
  and outputs the exact reclaimed byte count without touching any named data volumes

#### Scenario: Storage headroom restoration above operational threshold
- **WHEN** `docker-disk-guard.sh --prune` completes successfully on a host volume reporting critical low disk space
- **THEN** available storage on `/System/Volumes/Data` MUST increase and the post-prune free space SHALL be reported in machine logs without corrupting any stateful named volumes.
