# Design

## Context

See `proposal.md - Why` for motivation. Technical constraints and facts observed
on this workstation that shape the approach:

- **Docker Version & Topology**: Docker Desktop 4.94.0 (build 241994, Engine 29.8.2),
  Compose v5.5.1, macOS Darwin 27.0.0 on Apple Silicon (`arm64`). Active context is
  `desktop-linux`, communicating over `~/.docker/run/docker.sock` (symlinked from
  `/var/run/docker.sock`). Sockets are owned by `androidteam:staff` (`0755`).
- **Official CLI Plugin Available**: The official `docker desktop` CLI plugin (v0.4.4)
  is installed at `/Applications/Docker.app/Contents/Resources/cli-plugins/docker-desktop`
  and symlinked into `~/.docker/cli-plugins/docker-desktop`. It natively supports:
  - `docker desktop start [-d] [--timeout seconds]`
  - `docker desktop stop [-d] [--force] [--timeout seconds]`
  - `docker desktop restart [-d] [--timeout seconds]`
  - `docker desktop status [--format pretty|json]`
- **Root Helper Configuration**: Privileged helpers `/Library/PrivilegedHelperTools/com.docker.socket`
  and `com.docker.vmnetd` are installed, owned by root, and running under system launchd
  (PIDs active). Passwordless sudo is available (`sudo -n true` succeeds).
- **AutoStart & Login Item State**: `Docker Desktop` is already registered in macOS
  System Events login items (`path: /Applications/Docker.app/Contents/MacOS/Docker Desktop.app`).
  However, in `~/Library/Group Containers/group.com.docker/settings-store.json`, `"AutoStart"`
  is currently `false`, meaning the LinuxKit VM and Docker Engine do not start automatically.
- **VirtioFS File Sharing**: File sharing is enabled for `/Users`, `/Volumes`, `/private`, `/tmp`,
  and `/var/folders` using Apple Virtualization Framework with VirtioFS. Official Docker
  documentation explicitly advises: "For non-code items such as cache directories or databases,
  store in Linux VM using a named volume". VirtioFS host bind mounts corrupt SQLite WAL indexes.
- **Host Disk Headroom**: Host storage `/System/Volumes/Data` is at 95% capacity (24 GiB free).
  `Docker.raw` occupies 30 GB with ~13.5 GiB reclaimable across unused images (12.15 GB),
  volumes (1.01 GB), and build cache (419 MB).

## Goals / Non-Goals

**Goals:**
- Unify workstation Docker lifecycle management on the official `docker desktop` CLI.
- Enable native unattended auto-start via `settings-store.json` without conflicting LaunchAgents.
- Provide a workstation service wrapper (`docker-service.sh`) that adds pre-shutdown compose
  stack draining, connectivity validation, and machine-readable health output.
- Enforce compose conventions: named volumes for SQLite/WAL, `user: "502:20"` for dev bind
  mounts, and loopback-only port bindings.
- Establish a safe, volume-preserving disk reclamation routine (`docker-disk-guard.sh`).

**Non-Goals:**
- Migrating to Colima or OrbStack.
- Touching macOS SIP-protected TCC databases.
- Installing redundant LaunchAgents that trigger relaunch loops.

## Decisions

### D1. Leverage Official `docker desktop` CLI as Core Lifecycle Engine
*Alternative considered*: Bespoke `open -g -j -a Docker` with custom sleep loops and AppleScript `osascript -e 'quit app "Docker"'`.
*Decision*: Use `docker desktop start --timeout 90`, `docker desktop stop --timeout 30`, and
`docker desktop status --format json`.
*Rationale*: The `docker desktop` CLI plugin is officially maintained by Docker specifically for
local automation and headless CI workflows. It natively handles process coordination, IPC with
`com.docker.backend`, and engine readiness checks, eliminating fragile custom poll loops.

### D2. Native AutoStart in `settings-store.json` Over Redundant LaunchAgents
*Alternative considered*: Creating a custom LaunchAgent (`com.workspace.docker-lifecycle.plist`)
with `KeepAlive: true`.
*Decision*: Configure `"AutoStart": true` directly in `~/Library/Group Containers/group.com.docker/settings-store.json`.
*Rationale*: A LaunchAgent with `KeepAlive: true` invoking a start script creates an infinite
fork loop on macOS because the start command exits after the daemon becomes ready. Furthermore,
macOS already has `Docker Desktop` registered in login items. Setting `"AutoStart": true` allows
Docker Desktop's native initialization flow to start the VM cleanly on login as officially
documented.

### D3. Pre-Shutdown Compose Stack Draining in `docker-service.sh`
*Alternative considered*: Calling `docker desktop stop` immediately while stacks are writing.
*Decision*: The `docker-service.sh stop` command iterates active compose projects (`~/Omniroute`,
`~/Developer/platform/claude-code-provider-adapter`), executes `docker compose down --timeout 30`,
and only then delegates to `docker desktop stop --timeout 30`.
*Rationale*: Abrupt VM termination during active database transactions risks corrupting WAL files
even inside named volumes. Bounded graceful stack draining ensures clean container shutdown.

### D4. Mandatory Named Volumes for SQLite/WAL Databases
*Alternative considered*: Permitting host bind mounts with cache flush flags.
*Decision*: Strictly require named Docker volumes (e.g. `omniroute-data:/app/data`) for any
containerized SQLite database running in WAL mode.
*Rationale*: Official Docker documentation notes that host-shared file systems introduce
filesystem notification latency and locking inconsistencies. VirtioFS has documented concurrency
bugs with POSIX byte-range file locking required by SQLite WAL mode. Named volumes execute
directly within the LinuxKit VM ext4/overlayfs layer with 100% POSIX compliance.

### D5. Non-Root UID/GID (`502:20`) Mapping on Development Bind Mounts
*Alternative considered*: Running containers as `root` and relying on host `sudo chown` cleanup.
*Decision*: Require `user: "502:20"` (matching `androidteam:staff`) on development services
that bind-mount host workspace trees.
*Rationale*: Prevents container-generated files, logs, and caches from becoming root-owned on
the host filesystem, which causes permission errors in IDEs and git operations.

### D6. Safe Volume-Preserving Disk Reclamation Policy
*Alternative considered*: Running aggressive `docker system prune -a --volumes` without guards.
*Decision*: `docker-disk-guard.sh --prune` executes:
1. `docker image prune -a --filter "until=24h" -f` (preserves images built/pulled in the last 24h).
2. `docker builder prune -f` (purges dangling BuildKit cache).
3. `docker volume prune -f` (without `--all`, which by official Docker semantics strictly removes
   unused anonymous volumes while keeping all named volumes intact).
*Rationale*: The host volume is at 95% capacity (24 GiB free). Reclaiming ~13.5 GiB of obsolete
cache and images prevents out-of-disk kernel panics without risking stateful database volumes.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Cold start timeout under heavy system load | Default timeout set to 90s; `docker desktop start --timeout 90` exits with informative diagnostics if exceeded. |
| Inadvertent deletion of recent images | `--filter "until=24h"` guarantees actively tested base images and caches from the current workday are retained. |
| Accidental named volume deletion | Pruning uses `docker volume prune -f` without `--all`, which official Docker documentation guarantees will never prune named volumes. |
| Stale process credentials after reboot | Socket permissions are verified by `docker-service.sh status`, and passwordless sudo is available if helper reload is ever required. |
