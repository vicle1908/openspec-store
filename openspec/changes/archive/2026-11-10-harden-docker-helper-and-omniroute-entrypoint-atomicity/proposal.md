# Proposal: Harden Docker Desktop Socket Helper User-Flag Provisioning, Upgrade Lock Coordination, and OmniRoute Entrypoint Atomic Writes

## Why

During the scheduled `08:00 AM` workstation maintenance upgrade of Docker Desktop (`4.98.0 -> 4.99.0`, build `245822`) on `2026-11-10`, two interacting failures occurred:

1. **Modal macOS `SecurityAgent` Admin Password Prompt on Docker Startup (`PID 46689` & `PID 47330`)**:
   - In `~/Developer/scripts/docker-service.sh` (`ensure_helpers()`), `/Applications/Docker.app/Contents/MacOS/install socket-symlink-on-startup` was invoked **without** `--user "$target_user"`.
   - Unlike `install config --user <user>`, `install socket-symlink-on-startup` has its own independent `--user <user>` flag. Invoking it without `--user` wrote an empty `<string></string>` second `ProgramArguments` entry into `/Library/LaunchDaemons/com.docker.socket.plist` and booted out `system/com.docker.socket` (unlinking `/var/run/docker.sock`).
   - When `com.docker.backend` started, `com.docker.backend.cmdline` logged `[W] the argument "" in the socket task plist does not match "androidteam"` and `path "/var/run/docker.sock" does not exist`, and immediately spawned `/usr/bin/osascript` (`do shell script ... with administrator privileges`) to run `install config --user androidteam set-docker-socket`, raising an interactive macOS password dialog.

2. **OmniRoute Post-Upgrade Crash Loop from 0-Byte `/app/peer-stamp.mjs` Race**:
   - In `~/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`, `step_homebrew_update()` stopped Docker Desktop (`08:02:14`) before running `brew upgrade --cask docker-desktop` (`08:02:54`–`08:04:17`) without holding `~/.omniroute/update.lock`.
   - At `08:03:37` (mid-upgrade), `com.omniroute.watchdog` (`omniroute-watchdog.sh`) fired, saw `docker info` unreachable, and started Docker + OmniRoute (`08:03:44`).
   - `ensure-muse-wire-compat.sh` immediately executed `docker exec omniroute /app/container-entrypoint-compat.sh --patch-only` while PID 1 (`/app/container-entrypoint-compat.sh`) was still running its initial boot patch pass, saw `patched`, and ran `docker restart omniroute` (`08:04:11`) right as `fs.writeFileSync("/app/peer-stamp.mjs", next)` truncated `/app/peer-stamp.mjs` (`O_TRUNC`), leaving a **0-byte `/app/peer-stamp.mjs`** persisted in the container's overlayfs writable layer. Every subsequent restart failed closed on `[COMPAT_ERROR] Required non-chunk marker peer_stamp_muse_rewrite missing in /app/peer-stamp.mjs! Fail closed.`.

## What Changes

1. **Docker Desktop Socket Helper `--user` Provisioning & Synchronous Symlink Guarantee (`docker-service.sh`)**:
   - Pass `--user "$target_user"` to `sudo -n "$install_bin" socket-symlink-on-startup --user "$target_user"`.
   - Add synchronous `sudo -n ln -sfn "$socket_path" /var/run/docker.sock` after `launchctl kickstart -p system/com.docker.socket` so `/var/run/docker.sock` is guaranteed to exist before `com.docker.backend` launches, eliminating the asynchronous `launchd` startup race.
   - Tighten `is_socket_helper_up()` to require `grep -q "<string>${target_user}</string>" /Library/LaunchDaemons/com.docker.socket.plist` and the `/var/run/docker.sock -> ${socket_path}` symlink.
   - Mirror changes byte-for-byte to `~/Developer/platform/openspec-store/scripts/docker-service.sh`.

2. **Atomic Compatibility File Writes & Entrypoint Readiness Serialization (`container-entrypoint-compat.sh`, `ensure-muse-wire-compat.sh`, `omniroute-watchdog.sh`)**:
   - Replace all direct `fs.writeFileSync(path, ...)` (`O_TRUNC`) writes in `~/Omniroute/scripts/container-entrypoint-compat.sh` with `atomicWriteFileSync(targetPath, content)` (writes to sibling `.tmp-<pid>-<ts>` with preserved file mode, followed by atomic `fs.renameSync`), preventing 0-byte or partial file truncation under `SIGTERM`/`SIGKILL` or concurrent reads.
   - Add a bounded readiness loop (up to 15s) in `~/Omniroute/scripts/ensure-muse-wire-compat.sh` that waits for PID 1 `container-entrypoint-compat.sh` to complete before invoking `--patch-only`.
   - Update `~/Developer/scripts/omniroute-watchdog.sh` (and its mirror in `openspec-store/scripts/omniroute-watchdog.sh`) so that when `omni_status == "restarting"`, it passes `--no-build --pull never --force-recreate` to `docker compose --profile base up -d` to replace any corrupted container writable layer cleanly.

3. **Exclusive Maintenance Lock Across `docker-desktop` Cask Upgrades (`workstation_update.py`)**:
   - Acquire `~/.omniroute/update.lock` (`fcntl.flock(..., LOCK_EX | LOCK_NB)`) across the entire `docker-desktop` cask `stop -> brew upgrade --cask -> start -> up` lifecycle in `shb_schedule.workflows.workstation_update.step_homebrew_update` so `com.omniroute.watchdog` skips its cycle while Docker Desktop is being upgraded.

## Capabilities

### Modified Capabilities
- `workstation-remote-and-agent-permissions`: Require `--user <user>` on `install socket-symlink-on-startup`, plist user-argument verification, and synchronous `/var/run/docker.sock` symlink creation in `docker-service.sh`.
- `docker-lifecycle`: Require `is_socket_helper_up()` plist user-argument and symlink checks, `update.lock` coordination during `docker-desktop` cask upgrades, and `--force-recreate` recovery in `omniroute-watchdog.sh` when `omniroute` is stuck in `restarting`.
- `omniroute-runtime-customization`: Update compatibility patch metrics to `v3.8.53` (`3` non-chunk + `7` chunk replacements = `10` modifications, `15` fail-closed markers across `6` server chunks) and require atomic `fs.renameSync` writes in `container-entrypoint-compat.sh` plus entrypoint completion serialization in `ensure-muse-wire-compat.sh`.

## Impact

- `~/Developer/scripts/docker-service.sh` & `~/Developer/platform/openspec-store/scripts/docker-service.sh`
- `~/Developer/scripts/omniroute-watchdog.sh` & `~/Developer/platform/openspec-store/scripts/omniroute-watchdog.sh`
- `~/Omniroute/scripts/container-entrypoint-compat.sh` & `~/Omniroute/scripts/ensure-muse-wire-compat.sh`
- `~/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`
- `~/Developer/wiki/entities/omniroute.md`
