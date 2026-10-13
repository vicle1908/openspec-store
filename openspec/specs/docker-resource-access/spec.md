# docker-resource-access

## Purpose

Standardize how container workloads on this workstation access host resources
and protect system disk space. This covers mandatory named volumes for SQLite/WAL
workloads (mitigating VirtioFS corruption), non-root UID/GID mapping for development
bind mounts, loopback-only port exposure, and safe volume-preserving storage reclamation.

## Requirements

### Requirement: Mandatory named volumes for database persistence

Containers running on Docker Desktop for Mac SHALL use Docker-managed named volumes
(or in-VM storage) for any database utilizing write-ahead logging (SQLite WAL) or
stateful transaction ledgers; direct host directory bind mounts for such databases
are prohibited due to documented VirtioFS synchronization and locking bugs.

#### Scenario: OmniRoute database persistence

- **WHEN** OmniRoute's `docker-compose.override.yml` is deployed
- **THEN** its SQLite storage (`/app/data`) is mounted to a named Docker volume
  (`omniroute-data`) and not a host-bound filesystem path

#### Scenario: Violation detection on host-bound database

- **WHEN** a compose configuration declares a host bind mount for a directory
  containing SQLite `.sqlite`, `-wal`, or `-shm` database files
- **THEN** the validation script `docker-standardize-check.sh` fails the stack with
  a clear error mandating migration to a named volume

### Requirement: Development bind mounts MUST map to host UID/GID

Development services in compose files that bind-mount workspace source directories
into containers SHALL configure a non-root user matching the host developer account
(`user: "502:20"` or `user: "${UID:-502}:${GID:-20}"`) so that files created inside
the container remain writable and owned by `androidteam:staff` on the host.

#### Scenario: Source mount with host UID/GID mapping

- **WHEN** a compose service declares a development bind mount (e.g. `./src:/app/src`)
- **THEN** the service declares `user: "502:20"`, and all artifacts generated during
  the container run are owned by UID 502 on the macOS host

#### Scenario: Missing user mapping flagged

- **WHEN** a development service binds a host source directory without a `user` directive
- **THEN** `docker-standardize-check.sh` flags the service with a warning and
  remediation example

### Requirement: Port binding defaults to loopback interface

All development and internal tool compose services SHALL bind published ports explicitly
to `127.0.0.1` (or `localhost`) rather than exposing them across all host network
interfaces (`0.0.0.0`), unless an external access requirement is explicitly approved.

#### Scenario: Hardened loopback port binding

- **WHEN** a service publishes an HTTP or administrative port (e.g. `20128:20128`)
- **THEN** the port mapping is formatted as `"127.0.0.1:20128:20128"`

#### Scenario: Insecure wildcard port mapping detected

- **WHEN** a service defines port mappings without an interface prefix (e.g. `"20128:20128"`)
- **THEN** `docker-standardize-check.sh` reports a security finding requiring
  explicit loopback binding

### Requirement: Safe volume-preserving disk reclamation

The disk headroom safeguard SHALL monitor available storage on `/System/Volumes/Data`
and execute pruning that removes dangling objects, expired build cache, and anonymous
volumes, while strictly preserving all named volumes and recent images.

#### Scenario: Low disk space triggers warning

- **WHEN** available disk space on the host volume falls below 30 GiB
- **THEN** `docker-disk-guard.sh` logs an urgent alert indicating reclaimable storage
  reported by `docker system df`

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
