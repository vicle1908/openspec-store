# Proposal

## Why

Docker on this macOS workstation cannot be reliably operated by unattended
automation because Docker Desktop is configured with `"AutoStart": false`,
existing stacks lack codified permission standards (leading to VirtioFS SQLite-WAL
corruption risks and root-owned host bind mounts), and host disk space is critically
constrained at 95% capacity (24 GiB free) despite Docker retaining ~13.5 GiB in
reclaimable storage. While Docker Desktop 4.94.0 natively provides the official
`docker desktop` CLI plugin (`start`, `stop`, `restart`, `status`), automation currently
lacks a standardized lifecycle wrapper with stack-drainage safety, preflight
health checks, and safe disk reclamation.

## What Changes

- **Enable Native AutoStart** in `~/Library/Group Containers/group.com.docker/settings-store.json`
  (`"AutoStart": true`) to align with the existing macOS Login Item (`Docker Desktop.app`),
  ensuring the LinuxKit VM and Docker Engine start automatically on login without
  requiring interactive GUI intervention.
- **Adopt Official Docker Desktop CLI Operations** for workstation lifecycle control:
  - Standardize on `docker desktop start --timeout 90`, `docker desktop stop --timeout 30`,
    `docker desktop restart --timeout 90`, and `docker desktop status --format json`.
  - Provide a workstation service wrapper (`docker-service.sh`) that integrates
    these official commands with automated stack draining (`docker compose down`),
    preflight connectivity assertions (`docker info`), and machine-readable health output.
- **Standardize Resource Access & Compose Conventions**:
  - Enforce named Docker volumes (e.g. `omniroute-data`) for databases using write-ahead
    logging (SQLite WAL), adhering to official Docker documentation that advises against
    storing non-code database files on macOS VirtioFS virtual file shares.
  - Enforce explicit non-root UID/GID mapping (`user: "502:20"`) on development host bind mounts
    so files written by containers remain owned by `androidteam:staff` instead of `root`.
  - Enforce loopback-only (`127.0.0.1:`) port binding as the default security baseline.
- **Implement a Low-Disk Safeguard**:
  - Reclaim ~13.5 GiB of storage via official, safe Docker pruning:
    `docker image prune -a --filter "until=24h"`, `docker builder prune -f`, and
    anonymous-only volume pruning (`docker volume prune -f` without `--all`),
    strictly protecting named data volumes.
  - Provide a disk-headroom monitoring guard (`docker-disk-guard.sh`) that warns when
    host free space drops below 30 GiB.
- **Document the Workstation Permission Baseline**:
  - Record the verified security posture: `/Users/androidteam/.docker/run/docker.sock` owned
    by `androidteam:staff` (`0755`), passwordless sudo available for daemon maintenance,
    privileged helpers (`com.docker.socket`, `com.docker.vmnetd`) active, and system TCC
    Accessibility granted.

## Non-Goals

- Migrating workloads to alternative runtimes (OrbStack or Colima).
- Modifying application source code or third-party image internals.
- Granting Docker file-sharing access outside existing shared trees
  (`/Users`, `/Volumes`, `/private`, `/tmp`, `/var/folders`).
- Bypassing or modifying macOS SIP-protected TCC databases.
- Installing redundant LaunchAgents with keep-alive loops that conflict with native
  Docker Desktop login item management.

## Capabilities

### New Capabilities
- `docker-lifecycle` — Automated, headless lifecycle control using official Docker Desktop
  CLI commands and native auto-start configuration.
- `docker-resource-access` — Standardized host-resource access patterns: named volumes
  for databases, non-root bind-mount user mapping, loopback port bindings, and safe
  disk-space reclamation.

## Affected Ownership Boundaries
- `~/Library/Group Containers/group.com.docker/settings-store.json` (`AutoStart: true`).
- `~/Developer/scripts/docker-service.sh` (new workstation lifecycle utility).
- `~/Developer/scripts/docker-disk-guard.sh` (new storage headroom safeguard).
- `~/Developer/scripts/docker-standardize-check.sh` (new compose convention validator).
