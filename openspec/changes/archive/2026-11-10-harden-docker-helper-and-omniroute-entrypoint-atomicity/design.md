# Design: Harden Docker Desktop Socket Helper User-Flag Provisioning, Upgrade Lock Coordination, and OmniRoute Entrypoint Atomic Writes

## Context

Forensic inspection of `~/Library/Containers/com.docker.docker/Data/log/host/com.docker.backend.log.20261110-084146.469`, `~/Library/Logs/docker-service/service.log`, `~/.omniroute/watchdog.log`, and macOS unified `authd` logs after the `2026-11-10 08:02` workstation maintenance run revealed a 3-way interaction during the `docker-desktop` (`4.98.0 -> 4.99.0`) cask upgrade:

1. **Empty Plist Argument from `install socket-symlink-on-startup` (`docker-service.sh`)**:
   - `/Applications/Docker.app/Contents/MacOS/install` defines two distinct `--user` flags:
     - `install config --user <string>`
     - `install socket-symlink-on-startup --user <string>`
   - Calling `install socket-symlink-on-startup` without `--user` writes `<string></string>` as the username argument in `/Library/LaunchDaemons/com.docker.socket.plist` and boots out `system/com.docker.socket` (removing `/var/run/docker.sock`).
   - When `com.docker.backend` starts, `com.docker.backend.cmdline` validates that the second `ProgramArguments` element in `/Library/LaunchDaemons/com.docker.socket.plist` equals `<USER>` (`androidteam`) and that `/var/run/docker.sock` exists. When either check fails, `com.docker.backend.sudo` executes `/usr/bin/osascript` (`do shell script "/Applications/Docker.app/Contents/MacOS/install ... config --user androidteam set-docker-socket" with administrator privileges`), triggering `SecurityAgent.ExecuteWithPrivileges`.

2. **Mid-Upgrade Watchdog Race (`workstation_update.py` vs `omniroute-watchdog.sh`)**:
   - `workstation_update.py` stopped Docker Desktop at `08:02:14` and ran `brew upgrade --cask docker-desktop` (`08:02:54`–`08:04:17`).
   - Because `~/.omniroute/update.lock` was not held by `workstation_update.py`, `omniroute-watchdog.sh` fired at `08:03:37` and started Docker Desktop + OmniRoute mid-upgrade.

3. **Non-Atomic `fs.writeFileSync` + Concurrent `--patch-only` Restart Race (`container-entrypoint-compat.sh` & `ensure-muse-wire-compat.sh`)**:
   - `container-entrypoint-compat.sh` previously used `fs.writeFileSync(peerPath, next)` (`O_TRUNC`).
   - `ensure-muse-wire-compat.sh` invoked `docker exec omniroute /app/container-entrypoint-compat.sh --patch-only` immediately after `docker compose up -d` while PID 1 (`container-entrypoint-compat.sh`) was still patching, received `patched`, and executed `docker restart omniroute` (`08:04:11`) during an `O_TRUNC` write, leaving `/app/peer-stamp.mjs` at `0` bytes in the container's overlayfs writable layer.

## Decisions

1. **Pass `--user "$target_user"` to `socket-symlink-on-startup` and Synchronously Create `/var/run/docker.sock`**:
   - In `ensure_helpers()`, invoke:
     ```bash
     sudo -n "$install_bin" remove-vmnetd >/dev/null 2>&1 || true
     sudo -n "$install_bin" config --user "$target_user" >/dev/null 2>&1 || true
     sudo -n "$install_bin" socket-symlink-on-startup --user "$target_user" >/dev/null 2>&1 || true
     sudo -n launchctl kickstart -p system/com.docker.socket >/dev/null 2>&1 || true
     sudo -n ln -sfn "$socket_path" /var/run/docker.sock >/dev/null 2>&1 || true
     ```
   - In `is_socket_helper_up()`, verify `grep -q "<string>${target_user}</string>" /Library/LaunchDaemons/com.docker.socket.plist` and `[[ -L "/var/run/docker.sock" ]] && [[ "$(readlink /var/run/docker.sock 2>/dev/null)" == "${socket_path}" ]]`.

2. **Atomic Temp-File + `fs.renameSync` Writes in `container-entrypoint-compat.sh` and Entrypoint Serialization in `ensure-muse-wire-compat.sh`**:
   - Define `atomicWriteFileSync(targetPath, content)` in `container-entrypoint-compat.sh` that writes to `targetPath + ".tmp-" + process.pid + "-" + Date.now()` and calls `fs.renameSync(tmpPath, targetPath)`.
   - In `ensure-muse-wire-compat.sh`, poll up to 15 seconds until `! pgrep -f "container-entrypoint-compat.sh"` inside the container before invoking `/app/container-entrypoint-compat.sh --patch-only`.
   - In `omniroute-watchdog.sh`, pass `--no-build --pull never --force-recreate` when recovering a container in `restarting` status.

3. **Hold `~/.omniroute/update.lock` (`fcntl.flock`) During `docker-desktop` Cask Upgrades in `workstation_update.py`**:
   - Acquire `fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)` on `~/.omniroute/update.lock` before `docker-service.sh stop` and release it in a `finally:` block after `docker-service.sh start && docker-service.sh up`.
