# Tasks: Remediate Docker Helper and Updater Review Findings

## 1. Central Store Script Mirrors (`platform/openspec-store`)

- [x] 1.1 Update `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh` to define `is_vmnetd_up()` and `is_socket_helper_up()` (checking `/Library/LaunchDaemons/com.docker.{vmnetd,socket}.plist`, `/Library/PrivilegedHelperTools/com.docker.{vmnetd,socket}`, `/var/run/com.docker.vmnetd.sock`, and `/var/run/docker.sock -> ${socket_path}`), verify binary parity via `cmp -s` / `sudo -n cmp -s` in `ensure_helpers()`, and clean up live/stale `/tmp/docker-desktop-privileged*` directories (`rm -f "$priv_dir/exitcode.txt" "$priv_dir/cmd" && rmdir "$priv_dir"`)
- [x] 1.2 Update `cmd_start()`, `status_json()`, and `cmd_status()` in `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh` so `cmd_start()` falls through to the socket reachability loop when `docker desktop start` exits non-zero while `com.docker.backend` is running, and `status_json()`/`cmd_status()` use `is_vmnetd_up()` and `is_socket_helper_up()`
- [x] 1.3 Update `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` (Stage 1) so `docker-service.sh start` and `docker-service.sh up` run after `brew upgrade --cask` only when `! docker info >/dev/null 2>&1 || [[ ! -S "/var/run/com.docker.vmnetd.sock" ]] || [[ ! -r "/Library/PrivilegedHelperTools/com.docker.vmnetd" ]] || [[ ! -x "/Library/PrivilegedHelperTools/com.docker.socket" ]]`, with `docker-service.sh up` gated behind `docker-service.sh start` succeeding

## 2. External Execution Gate: Host Scripts & SHB Durable Scheduler (`~/Developer/scripts` & `shb/shb-schedule`)

- [x] 2.1 Synchronize `/Users/androidteam/Developer/scripts/docker-service.sh` and `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` with their recorded mirrors in `/Users/androidteam/Developer/platform/openspec-store/scripts/`, and verify `bash -n` and `detect_script_drift` (`checked=9 drifted=0 missing_record=0`)
- [x] 2.2 Update `step_homebrew_update()` in `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` so `docker-service.sh up` executes only in the `else:` branch when `start_proc.returncode == 0`
- [x] 2.3 Add `test_step_homebrew_update_records_error_when_docker_start_fails()` in `/Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py` verifying that a non-zero `docker-service.sh start` exit marks `step_homebrew_update()` as `DEGRADED`, records the error in `errors`, and skips `docker-service.sh up`; run `uv run pytest` and `uv run ruff check`

## 3. End-to-End Verification & OpenSpec Governance

- [x] 3.1 Verify `~/Developer/scripts/docker-service.sh status` and `status --json` when `/Library/PrivilegedHelperTools/com.docker.socket` is simulated absent vs restored via `docker-service.sh start`, and record outputs in `evidence.md`
- [x] 3.2 Validate change and canonical specs strictly via `openspec validate remediate-docker-helper-and-updater-review-findings --strict --json --store openspec-store` and `validate-archive-readiness.py --change remediate-docker-helper-and-updater-review-findings --strict`
