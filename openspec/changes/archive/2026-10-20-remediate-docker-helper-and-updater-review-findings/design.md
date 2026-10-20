# Design: Remediate Docker Helper and Updater Review Findings

## Context

See `proposal.md` for motivation and scope. During adversarial review (`ponytail-review`) of `2026-10-20-harden-docker-desktop-homebrew-upgrade-lifecycle` (`platform/openspec-store` commit `a276e1f4`, `shb/shb-schedule` commit `b461470`), read-only inspection and live binary permission checks revealed four edge cases:

1. **Permission & Process Visibility Model of `com.docker.socket` and `com.docker.vmnetd`**:
   - Unlike `/Library/PrivilegedHelperTools/com.docker.vmnetd` (`-r-xr--r--`, mode `0544`), `/Applications/Docker.app/Contents/MacOS/install` installs `/Library/PrivilegedHelperTools/com.docker.socket` with mode `0711` (`-rwx--x--x`, owned by `root:wheel`). An unprivileged `cmp -s` against `/Library/PrivilegedHelperTools/com.docker.socket` fails with `Permission denied (os error 13)`, whereas `[[ -x "/Library/PrivilegedHelperTools/com.docker.socket" ]]` and `sudo -n cmp -s` work deterministically.
   - Furthermore, `com.docker.vmnetd` runs as `root` (UID `0`) and is socket-activated via `/var/run/com.docker.vmnetd.sock` (`srw-rw-rw-`). In non-root or sandboxed subshells where UID `0` processes are hidden from unprivileged `pgrep -x com.docker.vmnetd`, checking only `pgrep -x com.docker.vmnetd` returns `1` (`false`) even when `system/com.docker.vmnetd` is active. Checking `/Library/LaunchDaemons/com.docker.vmnetd.plist`, `/Library/PrivilegedHelperTools/com.docker.vmnetd`, and `[[ -S "/var/run/com.docker.vmnetd.sock" ]]` (with `pgrep` / `sudo -n pgrep` fallback) works across all execution contexts.
2. **Mid-Boot `com.docker.backend` Race & `/tmp/docker-desktop-privileged*` Lifecycle**:
   - When `com.docker.backend` is auto-launched right after `brew upgrade --cask docker-desktop` and blocks on `osascript`, `ensure_helpers()` satisfies `exitcode.txt` and terminates `osascript`.
   - `com.docker.backend` immediately resumes booting the LinuxKit VM, so a subsequent `docker desktop start --timeout "$timeout_sec"` call can return non-zero while the backend is mid-transition. Additionally, leaving `/tmp/docker-desktop-privileged*` on disk causes every future `docker-service.sh start` call to iterate over stale temp directories.
3. **Updater Recovery Gating**:
   - In `shb-schedule` (`workstation_update.py:202-223`), `docker-service.sh up` was invoked unconditionally after `docker-service.sh start`, even when `start_proc.returncode != 0`.
   - In `workstation-daily-update.sh:636-639`, `docker-service.sh start` and `up` ran unconditionally after `brew upgrade --cask`, triggering `docker compose up -d` and `ensure-muse-wire-compat.sh` even when Docker Desktop was already healthy and untouched.

## Goals / Non-Goals

**Goals:**
- Ensure `ensure_helpers()`, `status_json()`, and `cmd_status()` in `docker-service.sh` accurately verify both `com.docker.vmnetd` and `com.docker.socket` (`/Library/LaunchDaemons/com.docker.socket.plist`, `/Library/PrivilegedHelperTools/com.docker.socket`, and `/var/run/docker.sock -> ${socket_path}`).
- Clean up `/tmp/docker-desktop-privileged*` directories after unblocking `osascript`, and fall through to socket polling in `cmd_start()` when `com.docker.backend` is actively booting.
- Gate `docker-service.sh up` behind `docker-service.sh start` success in both `workstation_update.py` and `workstation-daily-update.sh`, and skip redundant Compose restarts in `workstation-daily-update.sh` when the daemon and helpers are already healthy.
- Add negative-path unit test coverage in `tests/test_workstation_update_workflow.py` for `docker-service.sh start` failures.

**Non-Goals:**
- Modifying Docker Desktop's internal binaries or Homebrew's upstream cask formula.
- Using `rm -rf` anywhere in `docker-service.sh` (cleanup uses targeted `rm -f "$priv_dir/exitcode.txt" "$priv_dir/cmd" && rmdir "$priv_dir"`).

## Decisions

### Decision 1: Verify `com.docker.vmnetd` and `com.docker.socket` via `is_vmnetd_up()` and `is_socket_helper_up()`
- **Choice**:
  - Define `is_vmnetd_up()` (`[[ -f "/Library/LaunchDaemons/com.docker.vmnetd.plist" ]] && [[ -r "/Library/PrivilegedHelperTools/com.docker.vmnetd" ]] && { [[ -S "/var/run/com.docker.vmnetd.sock" ]] || pgrep -x com.docker.vmnetd >/dev/null 2>&1 || sudo -n pgrep -x com.docker.vmnetd >/dev/null 2>&1; }`) and `is_socket_helper_up()` (`[[ -f "/Library/LaunchDaemons/com.docker.socket.plist" ]] && [[ -x "/Library/PrivilegedHelperTools/com.docker.socket" ]] && { { [[ -L "/var/run/docker.sock" ]] && [[ "$(readlink /var/run/docker.sock 2>/dev/null)" == "${socket_path}" ]]; } || pgrep -x com.docker.socket >/dev/null 2>&1; }`) in `docker-service.sh`.
  - Use `is_vmnetd_up()` and `is_socket_helper_up()` across `ensure_helpers()`, `status_json()`, and `cmd_status()`, plus `cmp -s` / `sudo -n cmp -s` binary parity checks in `ensure_helpers()`.
- **Rationale**: Eliminates both false positives (when `/var/run/docker.sock` symlink lingers after Homebrew deletes `/Library/PrivilegedHelperTools/com.docker.socket`) and false negatives (when unprivileged `pgrep -x com.docker.vmnetd` cannot see UID `0` `com.docker.vmnetd` or unprivileged `cmp -s` cannot read mode-`0711` `com.docker.socket`).

### Decision 2: Clean Up Live and Stale `/tmp/docker-desktop-privileged*` Directories and Allow Mid-Boot Fallthrough
- **Choice**:
  - In `ensure_helpers()`, for each `/tmp/docker-desktop-privileged*` directory, if `pgrep -f "$priv_dir" >/dev/null 2>&1` is true (a live `osascript` is waiting), write `0` to `"$priv_dir/exitcode.txt"`, call `pkill -f "$priv_dir"`, and `sleep 1` so `com.docker.backend` reads `exitcode.txt`; then unconditionally remove `"$priv_dir/exitcode.txt"` and `"$priv_dir/cmd"` with `rm -f` and remove the directory with `rmdir "$priv_dir" 2>/dev/null || true`.
  - In `cmd_start()`, if `docker desktop start --timeout "$timeout_sec"` returns non-zero, check `if ! pgrep -x com.docker.backend >/dev/null 2>&1 && ! is_daemon_up; then return 1; fi`; otherwise log that `com.docker.backend` is active and continue into the `while ((waited < timeout_sec))` socket reachability loop.
- **Rationale**: Cleans up both live and stale `/tmp/docker-desktop-privileged*` directories without `rm -rf` or premature `exitcode.txt` deletion, and prevents false startup failures when `com.docker.backend` is mid-boot.

### Decision 3: Gate `docker-service.sh up` and Avoid Redundant Compose Restarts
- **Choice**:
  - In `shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`step_homebrew_update`), place the `docker-service.sh up` `subprocess.run(...)` call inside the `else:` branch of `if start_proc.returncode != 0:`.
  - In `scripts/workstation-daily-update.sh` (Stage 1), after `brew upgrade --cask 2>&1 || true`, check `if ! docker info >/dev/null 2>&1 || [[ ! -S "/var/run/com.docker.vmnetd.sock" ]] || [[ ! -r "/Library/PrivilegedHelperTools/com.docker.vmnetd" ]] || [[ ! -x "/Library/PrivilegedHelperTools/com.docker.socket" ]]; then` before running `"${WORKSPACE_DIR}/scripts/docker-service.sh" start` and (if `start` succeeds) `"${WORKSPACE_DIR}/scripts/docker-service.sh" up`.
- **Rationale**: Uses filesystem/socket checks that do not depend on root `pgrep` visibility, prevents 120-second `docker compose up` timeouts against a stopped daemon, and avoids unnecessary container recreation on days when `brew upgrade --cask` does not touch `docker-desktop`.

## Risks / Trade-offs

- **[Risk] Editing `~/Developer/scripts/docker-service.sh` and `~/Developer/scripts/workstation-daily-update.sh` causes script provenance drift if store mirrors are not updated simultaneously** → **Mitigation**: Synchronize both executed scripts with `/Users/androidteam/Developer/platform/openspec-store/scripts/{docker-service.sh,workstation-daily-update.sh}` in the same task and verify `detect_script_drift` reports `checked=9 drifted=0 missing_record=0`.
