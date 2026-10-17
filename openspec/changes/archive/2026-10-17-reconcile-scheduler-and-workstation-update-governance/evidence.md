# Verification Evidence: `reconcile-scheduler-and-workstation-update-governance`

- **Change Name**: `reconcile-scheduler-and-workstation-update-governance`
- **Planning Store**: `/Users/androidteam/Developer/platform/openspec-store` (`store_id: openspec-store`)
- **External Implementation Roots**:
  - `/Users/androidteam/Developer/shb/shb-schedule`
  - `/Users/androidteam/Developer/scripts`
  - `/Users/androidteam/.shb/schedules`
- **Date**: `2026-10-17`

---

## 1. Central Store Toolchain & Archive Readiness Gate Verification (Group 1)

- **Version Authority Governance Suite**:
  - Command: `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py`
  - Result: `Ran 23 tests in 3.222s — OK` (`exit code 0`).
  - Verified `("kimi", "vendor_download")` registered in `SUPPORTED_UPDATER_REGISTRY` (`supported_verb="kimi update"`, `updater_dispatch="native"`) and `qoder` active install root assertion aligned with `~/.qoder/bin/qodercli`.
- **Agent CLI Coverage Reconciliation**:
  - Command: `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/reconcile-agent-cli-coverage.py --json`
  - Result: `total_installed: 17`, `undeclared_count: 0`, `lacking_update_path: []`, `"kimi": "kimi update"` covered (`exit code 0`).
- **Archive Readiness Gate (`validate-archive-readiness.py`)**:
  - Verified fail-closed behavior before `evidence.md` creation: reported `status: "blocked"`, `"evidence": false`, and error `"Missing or empty evidence.md (required before archiving a change with tracked verification tasks)"`.
  - Preserved `is_range_audit=True` backward compatibility for historical `--range` git range audits.

---

## 2. `shb-schedule` Host/Container Partitioning & CLI Parity Verification (Group 2)

- **Manifest Schema & Mode (`~/.shb/schedules/workstation-daily-update.yaml`)**:
  - Added `execution_target: host`; verified file mode `-rw-------` (`0600`) inside directory `~/.shb/schedules` (`0700`).
  - Command: `uv run --no-sync --project /Users/androidteam/Developer/shb/shb-schedule shb-schedule validate`
  - Result: `✓ All 4 manifests valid and approved in /Users/androidteam/.shb/schedules` (`exit code 0`).
- **Container Rebuild, Hot-Reload & PostgreSQL Schedule Retirement**:
  - Command: `docker compose -f /Users/androidteam/Developer/shb/shb-schedule/compose.yaml -f /Users/androidteam/Developer/shb/shb-schedule/compose.override.yaml up -d --build scheduler`
  - Health Probe (`http://127.0.0.1:9110/scheduler/health`):
    `{"status":"healthy","app":"shb-schedule","is_leader":true,"backend":"postgres","error":null}`
  - Container Reconciler Log: `Hot reload succeeded: +0 added, ~0 updated, -1 retired, =3 retained.`
  - PostgreSQL `workflow_schedules` Verification:
    - `SELECT count(*) FROM shb_scheduler.workflow_schedules WHERE schedule_name = 'workstation-daily-update';` $\rightarrow$ `0`
    - `SELECT schedule_name FROM shb_scheduler.workflow_schedules ORDER BY schedule_name;` $\rightarrow$ `daily-shb-docs-sync`, `eod-settlement-recon`, `nightly-compliance-scan` (`3` rows).
- **CLI `run-now` Option Parity (`cli.py`)**:
  - Verified both positional `shb-schedule run-now <job>` and option `shb-schedule run-now --workflow <job>` (`-w`) in `tests/test_cli.py` (`16/16` passed).

---

## 3. Workstation Update Workflow Defect Remediation (Group 3)

- **Agent CLI Probing (`workstation_update.py`)**:
  - Added `~/.kimi-code/bin` to `STANDARD_PATH`.
  - Decoupled `AGENT_PROBE_BINARIES` (`claude`, `codex`, `pi`, `kilo`, `qodercli`, `kimi`) from `STATIC_AGENT_COMMANDS`, preventing `codex` from probing `npm --version` (`11.20.0`) and resolving `qodercli` instead of directory `~/.qoder/entry`.
- **Mac App Store (`step_mas_update`)**:
  - Implemented `MAS_OUTDATED_LINE_PATTERN = re.compile(r"^(\d+)\s+(.+?)\s+\((.+?)\s*->\s*(.+?)\)$")` to preserve multi-word application names (`Telegram 2`, `Parallels Desktop`) before `pgrep -x`.
  - Excluded multi-GB `Xcode` (`497799835`) via `MAS_LARGE_BUNDLE_IDS` (`skipped_large_bundle`) so unattended runs do not time out after 300s.
- **Skills Metrics, OpenSpec CWD & Telegram Alert Gating**:
  - Parsed numeric skill counts in `step_skills_refresh`.
  - Passed `cwd=str(store_dir)` to `openspec validate --all --store openspec-store` in `step_integrity_and_store_validation`.
  - Updated `step_record_telemetry_and_notify` alert condition to `report_data.get("status") not in ("SUCCESS", "completed", "paused")`.

---

## 4. Host Lifecycle Scripts & Provenance Verification (Group 4)

- **`docker-service.sh` (`~/Developer/scripts/docker-service.sh`)**:
  - Updated default drain/stop timeout from `30` to `65` seconds (honoring `shb-schedule` `stop_grace_period: 60s`).
  - Extended `status` and `status --json` to report per-stack container counts across `COMPOSE_STACKS` (`/Users/androidteam/Omniroute`: 2 running; `/Users/androidteam/Developer/shb/shb-schedule`: 2 running).
- **`workstation-daily-update.sh` & Provenance Sync**:
  - Guarded `run_pipeline | tee -a "${LOG_FILE}"` with `stat -f '%d:%i'` device/inode comparison on `/dev/fd/1` vs `${LOG_FILE}` to eliminate duplicate log lines under `launchd`.
  - Synchronized `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` and `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` (`SHA-256: ebbbe8ad29a7525c5263fd7bd6a4e453f1397b8d18ad474da41bff88426a3f25` in `config/script-provenance-manifest.tsv`; `checked=7 drifted=0 missing_record=0`).

---

## 5. Full Test Suite, Immutable Archive Preservation & Forward Reconciliation (Group 5)

- **Isolated `shb-schedule` Test Suite & Linter**:
  - Command: `uv run --no-sync --project /Users/androidteam/Developer/shb/shb-schedule pytest -v`
  - Result: **92 passed in 101.11s, 0 failed** (`exit code 0`).
  - Command: `uv run --no-sync --project /Users/androidteam/Developer/shb/shb-schedule ruff check src/ tests/`
  - Result: `All checks passed!` (`exit code 0`).
- **Immutable Archive Preservation**:
  - Command: `git -C /Users/androidteam/Developer/platform/openspec-store diff --name-only -- openspec/changes/archive`
  - Result: Empty (`0` files modified in `openspec/changes/archive/`).
- **Forward Reconciliation Ledger for Prior Scheduling Archives**:
  - `2026-10-16-harden-shb-scheduler-docker-lifecycle` (archived at commit `422af351` without `evidence.md`): Container `StopTimeout: 60` and JSON log rotation (`10m` / `3` files) verified live via `docker inspect`; `docker-service.sh` 30s drain truncation and stack status reporting remediated in Task 4.1.
  - `2026-10-13-durable-workstation-updater` (archived at commit `d41856c5` without `evidence.md`): Dual-execution 08:00 AM container/host race, `codex` version probe bug, `qoder` directory bug, `kimi` registry omission, `mas` multi-word truncation / Xcode timeout, `openspec validate` cwd omission, and Telegram false alert condition remediated in Tasks 1.1, 2.1–2.3, 3.1–3.3, and 4.2.
- **Canonical Main Spec Sync & Strict Validation (`openspec/specs/`)**:
  - Synced all 4 capability delta specs into their canonical main specs under `/Users/androidteam/Developer/platform/openspec-store/openspec/specs/`:
    - `tdt-scheduler-ownership-contract/spec.md` (`openspec validate tdt-scheduler-ownership-contract --type spec --strict --json --store openspec-store` $\rightarrow$ `valid: true, issues: []`)
    - `shb-schedule-engine/spec.md` (`openspec validate shb-schedule-engine --type spec --strict --json --store openspec-store` $\rightarrow$ `valid: true, issues: []`)
    - `portable-workstation-toolchain/spec.md` (`openspec validate portable-workstation-toolchain --type spec --strict --json --store openspec-store` $\rightarrow$ `valid: true, issues: []`)
    - `cleanup-archive-verification/spec.md` (`openspec validate cleanup-archive-verification --type spec --strict --json --store openspec-store` $\rightarrow$ `valid: true, issues: []`)
  - `openspec validate --specs --json --store openspec-store` $\rightarrow$ `449/449 passed, 0 failed`.
- **External Repository Commit & Live E2E Runtime Probes**:
  - Committed verified implementation in `/Users/androidteam/Developer/shb/shb-schedule`: commit `16ff5bd1b7fdb4986f217ea12cc9c0fec3e29c84` (`fix(schedule): partition host execution_target and remediate workstation_update defects`, 9 files changed, 480 insertions, 41 deletions).
  - Live HTTP Hot-Reload Probe (`curl -s -X POST http://127.0.0.1:9110/scheduler/reload`):
    `{"status":"reloaded","added":[],"updated":[],"retired":[],"retained":["daily-shb-docs-sync","eod-settlement-recon","nightly-compliance-scan"],"changed_count":0}`
  - Live Hermetic CLI `--workflow` Probe (`SHB_SCHEDULER_ENABLED=false shb-schedule run-now --workflow eod-settlement-recon`):
    `Execution completed with notice: workflow=eod-settlement-recon status=ACTION_REQUIRED` (`exit code 0`).
