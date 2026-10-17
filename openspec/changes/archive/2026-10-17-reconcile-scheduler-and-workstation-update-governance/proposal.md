# Proposal

## Why

Recent scheduling and workstation update changes (`2026-10-13-durable-workstation-updater` and `2026-10-16-harden-shb-scheduler-docker-lifecycle`) introduced a daily 08:00 AM container-versus-host dual-execution race condition, eight implementation defects in `shb-schedule` and `docker-service.sh`, unregistered Kimi CLI version authority, and four archived changes that bypassed `evidence.md` verification gates. Reconciling these defects now restores deterministic single-owner scheduling, accurate toolchain telemetry, and fail-closed OpenSpec archive governance without mutating immutable archive history.

## What Changes

- **Host vs. Container Schedule Partitioning (`shb-schedule`)**:
  - Extend `ScheduleManifest` (`shb-schedule/v1`) with an optional `execution_target` field (`"any" | "container" | "host"`, defaulting to `"any"`, with `workstation-daily-update.yaml` set to `"host"` and mode `0600`).
  - Update `shb-schedule` schedule reconciliation (`ScheduleReconciler.reconcile` in `reconciliation.py`) and hot reloading (`HotReloader.reload` in `reloader.py`) with a shared `should_persist(manifest) -> bool` predicate (`not (manifest.execution_target == "host" and sys.platform != "darwin")`).
  - Filter candidate manifests in `ScheduleReconciler.reconcile` so non-Darwin/Linux container daemons skip registering `execution_target: "host"` cron schedules in PostgreSQL and retire any previously persisted `workstation-daily-update` schedule record via `_retire_schedule` (`DBOS.delete_schedule`), eliminating the 08:00 AM container/host dual-execution race while keeping `workstation-daily-update.yaml` discoverable by host CLI `validate`, `list`, and `run-now`.
  - Filter `expected_sigs` in `HotReloader.reload` rollback verification using `self.reconciler.should_persist(res.manifest)` so `persisted_sigs == expected_sigs` holds consistently across reload attempts and prevents false `RollbackDegraded` scheduler demotions.
  - Update `shb-schedule run-now` (`cli.py`) to accept both positional `<job_name>` and `--workflow <job_name>` (`-w`) so documented and scripted invocations behave identically.
- **Workstation Update Workflow Repairs (`workstation_update.py` & `workstation-daily-update.sh`)**:
  - **Fix False Telegram Degradation Alerts**: Change `step_record_telemetry_and_notify` (`workstation_update.py:546`) from `if report_data.get("status") != "completed":` to `if report_data.get("status") not in ("SUCCESS", "completed", "paused"):` so neither clean `SUCCESS` runs nor intentional `paused` runs trigger degradation alerts.
  - **Fix Agent CLI Version Probing & Registry Alignment**: Decouple version probe binaries (`codex --version`, `qodercli --version`, `kimi --version`) from update commands in `step_agent_cli_update` so `codex` no longer records `npm --version` (`11.20.0`) and `qoder` no longer fails against directory `~/.qoder/entry`. Add `~/.kimi-code/bin` to `STANDARD_PATH` and register `kimi` (`~/.kimi-code/bin/kimi`, `kimi update`) in `toolchain_updater_registry.py` and `reconcile-agent-cli-coverage.py`, and update `test-version-authority-governance.py` for `~/.qoder/bin/qodercli`.
  - **Fix Mac App Store (`mas`) Parsing & Large-Bundle Timeout**: Replace `line.split(maxsplit=2)` in `step_mas_update` with regex `^(\d+)\s+(.+?)\s+\((.+?)\s*->\s*(.+?)\)$` so multi-word app names (`Telegram 2`, `Parallels Desktop`) are preserved for `pgrep -x`, and exclude or bound multi-GB `Xcode` (`497799835`) so a 300s download timeout does not degrade daily runs.
  - **Fix Skills Metrics, OpenSpec CWD, and LaunchAgent Log Duplication**: Parse numeric counts from `skills update` output in `step_skills_refresh`, pass `cwd=str(store_dir)` to `openspec validate` in `step_integrity_and_store_validation`, and guard `tee -a "${LOG_FILE}"` in `workstation-daily-update.sh` (plus sync its mirror in `platform/openspec-store/scripts/` and `config/script-provenance-manifest.tsv`) when stdout is already redirected by `launchd`.
- **Docker Lifecycle & Graceful Drain Alignment (`docker-service.sh`)**:
  - Increase the default drain/stop timeout in `~/Developer/scripts/docker-service.sh` (`cmd_drain` and `stop`) from `30` to `65` seconds so `docker compose down --timeout` respects `shb-schedule`'s `stop_grace_period: 60s`.
  - Extend `docker-service.sh status` and `status --json` to inspect and report per-stack container status for all registered `COMPOSE_STACKS` (`Omniroute` and `shb-schedule`).
- **OpenSpec Archive Readiness Gate & Strict Spec Hygiene (`platform/openspec-store`)**:
  - Update `platform/openspec-store/scripts/validate-archive-readiness.py` so `check_change_readiness` requires `.openspec.yaml` and a non-empty `evidence.md` (or non-empty legacy `evidence/` directory) for active change readiness (`--change`) whenever verification tasks are present, while preserving backwards compatibility in `audit_git_range` (`--range`) for historical archives.
  - Reformat the overlong requirement clause in `openspec/specs/tdt-scheduler-ownership-contract/spec.md` (`<500` characters) so strict validation passes cleanly, and record forward immutable-archive reconciliation in `evidence.md` for `2026-10-16-harden-shb-scheduler-docker-lifecycle` and `2026-10-13-durable-workstation-updater`.
### Explicit Non-Goals

- Editing, moving, or adding files inside any archived directory under `openspec/changes/archive/` (archived directories remain strictly immutable).
- Executing live third-party package upgrades (`brew upgrade`, `mas upgrade`, `npm update`) during planning or verification tests.
- Modifying unrelated active OpenSpec changes (`upgrade-mcp-router-multi-key-load-balancing`, `agent-core-integrate-jev-system-one`) or altering `tdt-core` / `hermes` runtime services.

### Affected Ownership Boundaries

- **Central Planning & Governance Root**: `/Users/androidteam/Developer/platform/openspec-store` (`store_id: openspec-store`, `allowedEditRoots: ["/Users/androidteam/Developer/platform/openspec-store"]`).
- **External Implementation Roots** (governed via explicit external execution gates during apply):
  - `/Users/androidteam/Developer/shb/shb-schedule` (SHB durable scheduler repository)
  - `/Users/androidteam/Developer/scripts` (`docker-service.sh`, `workstation-daily-update.sh`)
  - `/Users/androidteam/.shb/schedules` (`workstation-daily-update.yaml`)

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `shb-schedule-engine`: Add `execution_target` host/container schedule partitioning to prevent Linux container execution of host-only schedules, support `--workflow` option parity on `shb-schedule run-now`, clarify fail-closed container behavior when workspace/ledger volumes are unmounted, and align `docker-service.sh` drain timeout (`65s`) and stack status reporting with `stop_grace_period: 60s`.
- `portable-workstation-toolchain`: Fix `step_mas_update` multi-word app name parsing and large-app timeout handling, decouple agent CLI version probing (`codex`, `qodercli`, `kimi`) from installer binaries, register `kimi` in `toolchain_updater_registry.py`, fix `step_record_telemetry_and_notify` alert status condition, enforce `cwd` on `openspec validate`, and eliminate duplicate LaunchAgent stdout logging.
- `cleanup-archive-verification`: Enforce `.openspec.yaml` and non-empty `evidence.md` verification gates in `validate-archive-readiness.py` and record forward immutable-archive reconciliation for scheduling changes archived without `evidence.md`.
- `tdt-scheduler-ownership-contract`: Refactor overlong `Requirement: Health endpoint surfaces schedules_applied` text (`<500` characters) into scenario clauses to satisfy `openspec validate --strict`.

## Impact

- **`~/Developer/shb/shb-schedule`**:
  - `src/shb_schedule/manifests/schema.py`, `src/shb_schedule/engine/reconciliation.py`, `src/shb_schedule/cli.py`
  - `src/shb_schedule/workflows/workstation_update.py`
  - `tests/test_workstation_update_workflow.py`, `tests/test_reconciliation.py`, `tests/test_cli.py`
- **`~/Developer/scripts` & `~/.shb/schedules`**:
  - `~/Developer/scripts/docker-service.sh`
  - `~/Developer/scripts/workstation-daily-update.sh`
  - `~/.shb/schedules/workstation-daily-update.yaml` (mode `0600`, `execution_target: host`)
- **`~/Developer/platform/openspec-store`**:
  - `scripts/toolchain_updater_registry.py`, `scripts/reconcile-agent-cli-coverage.py`, `scripts/test-version-authority-governance.py`
  - `scripts/validate-archive-readiness.py`
  - `scripts/workstation-daily-update.sh` & `config/script-provenance-manifest.tsv`
  - `openspec/specs/shb-schedule-engine/spec.md`, `openspec/specs/portable-workstation-toolchain/spec.md`, `openspec/specs/cleanup-archive-verification/spec.md`, `openspec/specs/tdt-scheduler-ownership-contract/spec.md`
