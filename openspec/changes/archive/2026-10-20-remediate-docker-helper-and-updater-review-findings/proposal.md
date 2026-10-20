# Proposal: Remediate Docker Helper and Updater Review Findings

## Why

Post-implementation adversarial code review (`ponytail-review`) of `2026-10-20-harden-docker-desktop-homebrew-upgrade-lifecycle` identified four defects across `docker-service.sh`, `workstation-daily-update.sh`, and `shb-schedule` that can cause false startup failures while `com.docker.backend` is mid-boot, false-positive `com.docker.socket` helper health when `/Library/PrivilegedHelperTools/com.docker.socket` is deleted, redundant `docker compose up` calls on failed starts or no-op cask updates, and missing negative-path unit test coverage.

Elaboration:
1. **Mid-Boot `docker desktop start` Race & Temp Directory Accumulation (`scripts/docker-service.sh:64-70, 131-135`)**: When `ensure_helpers` unblocks a stuck `osascript` dialog for an already-running `com.docker.backend` process, `com.docker.backend` immediately resumes booting the LinuxKit VM; invoking `docker desktop start` milliseconds later can return non-zero while `com.docker.backend` is mid-transition, causing `cmd_start` to exit `1` before entering the 90-second socket readiness loop. Furthermore, `/tmp/docker-desktop-privileged*` directories are left on disk after cleanup, causing subsequent `start` invocations to re-run `pkill` against stale paths.
2. **Missing `/Library/PrivilegedHelperTools/com.docker.socket` Check & Unprivileged `pgrep -x com.docker.vmnetd` Visibility (`scripts/docker-service.sh:55-59, 83-88, 270-275`)**: Homebrew's `docker-desktop` cask `uninstall` stanza deletes `/Library/PrivilegedHelperTools/com.docker.socket` (mode `0711`) and unloads `com.docker.socket`, but leaves `/var/run/docker.sock` symlink on disk. `ensure_helpers` did not check `[[ -x "/Library/PrivilegedHelperTools/com.docker.socket" ]]` or verify that `/var/run/docker.sock` resolves to `${socket_path}`, and both `status_json` and `cmd_status` reported `com.docker.socket` as active based solely on the lingering symlink. Additionally, unprivileged `pgrep -x com.docker.vmnetd` returns non-zero (`1`) in sandboxed/non-root contexts for root-owned `com.docker.vmnetd` (UID `0`), so `vmnetd` health checks must also verify `/Library/LaunchDaemons/com.docker.vmnetd.plist`, `/Library/PrivilegedHelperTools/com.docker.vmnetd`, and `/var/run/com.docker.vmnetd.sock` (or `sudo -n pgrep -x com.docker.vmnetd`).
3. **Unconditional `docker-service.sh up` After Failed Start or No-Op Cask Run (`shb-schedule/src/shb_schedule/workflows/workstation_update.py:202-223`, `scripts/workstation-daily-update.sh:636-639`)**: In `workstation_update.py`, `docker-service.sh up` is executed even when `docker-service.sh start` returns non-zero, waiting up to 120 seconds against an unreachable daemon and appending a redundant error. In `workstation-daily-update.sh`, `docker-service.sh start` and `up` run after every `brew upgrade --cask` even when the daemon and helpers are already healthy, needlessly re-running `docker compose up -d` and `ensure-muse-wire-compat.sh`.
4. **Missing Negative-Path Test Coverage (`shb-schedule/tests/test_workstation_update_workflow.py:97-124`)**: Unit tests cover the happy path for `docker-desktop` cask upgrades in `step_homebrew_update()`, but do not test the failure path when `docker-service.sh start` returns a non-zero exit code.

## Non-Goals

- Changing Homebrew's upstream `docker-desktop` cask definition or modifying Docker Desktop's internal binaries under `/Applications/Docker.app`.
- Adding `docker-desktop` to `CASK_PROCESS_NAMES` (which would suppress automated Docker Desktop upgrades when the daemon is running).
- Altering container compose topologies or port mappings in `/Users/androidteam/Omniroute` or `/Users/androidteam/Developer/shb/shb-schedule`.

## Ownership Boundaries

- **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns the change planning artifacts, canonical specifications (`openspec/specs/docker-lifecycle/spec.md` and `openspec/specs/portable-workstation-toolchain/spec.md`), recorded script mirrors (`scripts/docker-service.sh` and `scripts/workstation-daily-update.sh`), and `config/script-provenance-manifest.tsv`.
- **Host Workstation Scripts (`/Users/androidteam/Developer/scripts`)**: Owns the executed copies of `docker-service.sh` and `workstation-daily-update.sh` (governed via SHA-256 byte-identity in `config/script-provenance-manifest.tsv`).
- **SHB Durable Scheduler (`/Users/androidteam/Developer/shb/shb-schedule`)**: Owns `src/shb_schedule/workflows/workstation_update.py` (`step_homebrew_update`) and `tests/test_workstation_update_workflow.py`.

## What Changes

- **Harden `ensure_helpers`, `cmd_start`, `status_json`, and `cmd_status` in `docker-service.sh` (and store mirror)**:
  - Introduce `is_vmnetd_up()` and `is_socket_helper_up()` helpers verifying `/Library/LaunchDaemons/com.docker.{vmnetd,socket}.plist`, `/Library/PrivilegedHelperTools/com.docker.{vmnetd,socket}`, `/var/run/com.docker.vmnetd.sock` (or `sudo -n pgrep -x com.docker.vmnetd`), and `/var/run/docker.sock -> ${socket_path}`, plus `sudo -n cmp -s` binary parity in `ensure_helpers()`.
  - In `ensure_helpers()`, only write `0` to `exitcode.txt`, `pkill -f "$priv_dir"`, and `sleep 1` when `pgrep -f "$priv_dir"` is active, then remove `"$priv_dir/exitcode.txt"`, `"$priv_dir/cmd"`, and `"$priv_dir"` (`rm -f` + `rmdir`) so stale directories (`/tmp/docker-desktop-privileged2552015699`, `/tmp/docker-desktop-privileged3444944064`) are cleaned up without `rm -rf`.
  - In `cmd_start()`, if `docker desktop start --timeout "$timeout_sec"` exits non-zero while `pgrep -x com.docker.backend` is active (or `is_daemon_up` succeeds), fall through to the bounded `while ((waited < timeout_sec))` socket readiness polling loop instead of failing immediately.
  - In `status_json()` and `cmd_status()`, use `is_vmnetd_up()` and `is_socket_helper_up()` so helper status is accurate in both root and non-root/sandboxed shells.
- **Gate Post-Upgrade Stack Bring-Up in `shb-schedule` and `workstation-daily-update.sh` (and store mirror)**:
  - In `shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`step_homebrew_update`), execute `docker-service.sh up` only in the `else:` branch when `start_proc.returncode == 0`.
  - In `scripts/workstation-daily-update.sh` (Stage 1), invoke `docker-service.sh start` and `docker-service.sh up` after `brew upgrade --cask` only when Docker Desktop or its privileged helpers require recovery (`! docker info >/dev/null 2>&1 || [[ ! -S "/var/run/com.docker.vmnetd.sock" ]] || [[ ! -r "/Library/PrivilegedHelperTools/com.docker.vmnetd" ]] || [[ ! -x "/Library/PrivilegedHelperTools/com.docker.socket" ]]`), and gate `docker-service.sh up` behind a successful `docker-service.sh start`.
- **Add Negative-Path Unit Test in `shb-schedule`**:
  - Add `test_step_homebrew_update_records_error_when_docker_start_fails()` in `tests/test_workstation_update_workflow.py` verifying that a non-zero exit from `docker-service.sh start` marks `step_homebrew_update()` as `DEGRADED`, records the failure in `errors`, and skips `docker-service.sh up`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `docker-lifecycle`: Strengthen `Non-interactive privileged helper provisioning on start and restart` to verify `com.docker.vmnetd` (`/var/run/com.docker.vmnetd.sock` and binary/plist presence) and `com.docker.socket` (`/Library/PrivilegedHelperTools/com.docker.socket` executable presence and plist), clean up `/tmp/docker-desktop-privileged*` directories after unblocking `osascript`, and fall through to socket polling when `com.docker.backend` is already booting.
- `portable-workstation-toolchain`: Strengthen `Post-cask-upgrade Docker Desktop helper and stack restoration` so `docker-service.sh up` is gated behind `docker-service.sh start` success and `workstation-daily-update.sh` skips redundant Compose stack restarts when the daemon and helpers remain healthy after `brew upgrade --cask`.

## Impact

- **Files Modified (during `/opsx:apply`)**:
  - `/Users/androidteam/Developer/scripts/docker-service.sh` & `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh`
  - `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` & `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`
  - `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`
  - `/Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py`
- **Breaking Changes**: None.
