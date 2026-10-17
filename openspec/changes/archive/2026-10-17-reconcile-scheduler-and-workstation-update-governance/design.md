# Design

## Context

See `proposal.md` for motivation and scope. Primary-source inspection of the live `shb-schedule` stack (`~/Developer/shb/shb-schedule`), PostgreSQL container `shb-schedule-db-1`, host SQLite `~/.shb/scheduler.db`, `~/Developer/scripts/docker-service.sh`, `~/Developer/scripts/workstation-daily-update.sh`, and `/Users/androidteam/Developer/platform/openspec-store` established the following baseline constraints:

1. **Mount-Induced Dual Execution (`shb-schedule/compose.yaml:53`)**:
   - The Linux container `shb-schedule-scheduler-1` mounts `${HOME}/.shb/schedules:/etc/shb/schedules:ro`.
   - Because `~/.shb/schedules/workstation-daily-update.yaml` is required by `portable-workstation-toolchain` to reside in `~/.shb/schedules/` so host CLI invocations (`shb-schedule validate`, `list`, `run-now`) can discover it (`cli.py:139`), the Linux container daemon also discovers it and registers `workstation-daily-update` in PostgreSQL `shb_scheduler.workflow_schedules`.
   - At 08:00 AM (`01:00 UTC`), both the Linux container daemon and the macOS host LaunchAgent (`com.developer.workstation-daily-update.plist`) execute `workstation_update_workflow` simultaneously.
2. **In-Tree Workflow & Lifecycle Defects**:
   - `workstation_update.py:546` checks `if report_data.get("status") != "completed":`, whereas `plain_workstation_update_workflow` (`line 632`) sets `status` to `"SUCCESS"` or `"PARTIAL"`, triggering Telegram degradation alerts on clean runs.
   - `workstation_update.py:60, 392` resolves `shutil.which(cmd[0])` (`npm`) for `codex`, probing `npm --version` (`11.20.0`) instead of `codex --version`, and checks directory `~/.qoder/entry` instead of executable `~/.local/bin/qodercli`.
   - `workstation_update.py:205, 220` truncates multi-word Mac App Store names via `line.split(maxsplit=2)` and enforces a 300s timeout on `mas upgrade`, timing out on `Xcode` (`497799835`).
   - `docker-service.sh:108, 236` defaults `cmd_drain` and `stop` to `timeout_sec=30`, preempting `shb-schedule`'s `stop_grace_period: 60s`.
3. **Central Store Multi-Root & Immutable Archive Boundaries**:
   - `platform/openspec-store` governs planning (`allowedEditRoots: ["/Users/androidteam/Developer/platform/openspec-store"]`). Modifications to `~/Developer/shb/shb-schedule`, `~/Developer/scripts`, and `~/.shb/schedules` execute via explicit external execution gates during apply.
   - Archived changes under `openspec/changes/archive/` are strictly immutable.

## Goals / Non-Goals

**Goals:**
- Prevent the Linux `shb-schedule` container from registering or executing host-only macOS cron schedules while preserving `~/.shb/schedules/workstation-daily-update.yaml` for host CLI discovery and validation.
- Repair all 8 validated defects across `workstation_update.py`, `cli.py`, `workstation-daily-update.sh`, `docker-service.sh`, and `toolchain_updater_registry.py`.
- Close the `validate-archive-readiness.py` verification blind spot by requiring `.openspec.yaml` and a non-empty `evidence.md` whenever verification tasks exist.
- Record forward value-blind reconciliation evidence for `2026-10-16-harden-shb-scheduler-docker-lifecycle` and `2026-10-13-durable-workstation-updater`.

**Non-Goals:**
- Mutating any file under `openspec/changes/archive/`.
- Enabling writable host repository bind mounts inside the production `shb-schedule` container.
- Running live upstream package upgrades (`brew upgrade`, `mas upgrade`, `npm install -g`) during test verification.

## Decisions

### Decision 1: Manifest `execution_target` Partitioning in `ScheduleManifest`, `ScheduleReconciler`, and `HotReloader`
- **Choice**: Add `execution_target: Literal["any", "container", "host"] = "any"` to `ScheduleManifest` (`src/shb_schedule/manifests/schema.py`) and set `execution_target: host` in `~/.shb/schedules/workstation-daily-update.yaml` (mode `0600`). Define a shared predicate `should_persist(manifest: ScheduleManifest) -> bool` on `ScheduleReconciler` returning `not (manifest.execution_target == "host" and sys.platform != "darwin")`. In `ScheduleReconciler.reconcile` (`src/shb_schedule/engine/reconciliation.py`), filter active candidate schedules by `should_persist`, computing `candidate_names` strictly from eligible schedules so any previously persisted schedule row in `DBOS.list_schedules()` matching a host-only schedule on Linux is identified in `retired = list(active_names - candidate_names)` and retired via `_retire_schedule` (`DBOS.delete_schedule`). In `HotReloader.reload` (`src/shb_schedule/engine/reloader.py`), filter `expected_sigs` in the reload exception rollback block using `self.reconciler.should_persist(res.manifest)`.
- **Rationale**: Moving `workstation-daily-update.yaml` out of `~/.shb/schedules/` would violate the canonical path requirement in `portable-workstation-toolchain` and break `shb-schedule run-now workstation-daily-update` (`cli.py:139`), which discovers manifests from `settings.schedules_dir` (`~/.shb/schedules`). Filtering by `execution_target` during candidate evaluation in `reconcile()` keeps the manifest discoverable in `~/.shb/schedules/`, automatically deletes the stale `workstation-daily-update` schedule row from container PostgreSQL on hot-reload, and prevents Linux container execution. Filtering `expected_sigs` in `reloader.py` prevents a false `persisted_sigs != expected_sigs` mismatch on rollback that would otherwise trigger `RollbackDegraded` and demote the active leader.
- **Alternatives Considered**:
  - *Separate `~/.shb/host-schedules/` directory*: Rejected because it requires overriding `SHB_SCHEDULER_SCHEDULES_DIR` on every host CLI call and breaks existing `portable-workstation-toolchain` path invariants.
  - *Filtering only at DBOS registration step*: Rejected because leaving host-only schedules in `candidate_names` prevents `retired = list(active_names - candidate_names)` from detecting and deleting existing persisted rows in PostgreSQL, and leaves `expected_sigs` in `reloader.py` out of sync with persisted state.
### Decision 2: Structured Agent CLI Probe & Update Specification
- **Choice**: Replace flat command lists in `workstation_update.py` with structured entries pairing an explicit version probe binary (`probe_bin`) and update argv (`update_cmd`), aligned with `platform/openspec-store/scripts/toolchain_updater_registry.py`:
  - `claude`: probe `claude`, update `["claude", "update"]`
  - `codex`: probe `codex`, update `["npm", "--prefix", f"{Path.home()}/.npm-global", "install", "--global", "@openai/codex"]`
  - `pi`: probe `pi`, update `["pi", "update", "--self"]`
  - `kilo`: probe `kilo`, update `["kilo", "update"]`
  - `qoder`: probe `qodercli`, update `["qodercli", "update"]` (resolved via `~/.local/bin/qodercli` $\rightarrow$ `~/.qoder/bin/qodercli`)
  - `kimi`: probe `kimi`, update `["kimi", "update"]` (adding `~/.kimi-code/bin` to `STANDARD_PATH`)
- **Rationale**: Decoupling `probe_bin` from `update_cmd[0]` prevents npm-wrapped agent updates from probing `npm --version` (`11.20.0`) and ensures `qodercli` and `kimi` are accurately inventoried and governed across both `shb-schedule` and `openspec-store`.
- **Alternatives Considered**:
  - *Subshell string commands*: Rejected due to command injection risks and `portable-workstation-toolchain` discrete-argv security rules.

### Decision 3: Regex `mas outdated` Parser and Large-Bundle Exclusion
- **Choice**: Parse each `mas outdated` line in `step_mas_update` using `MAS_LINE_PATTERN = re.compile(r"^(\d+)\s+(.+?)\s+\((.+?)\s*->\s*(.+?)\)$")` so multi-word application names (`Telegram 2`, `Parallels Desktop`) are captured intact before `pgrep -x`. Maintain an explicit `MAS_EXCLUDED_LARGE_BUNDLE_IDS = {"497799835": "Xcode"}` set so multi-gigabyte Xcode bundles are recorded under `skipped_large_bundle` rather than timing out after 300s and degrading the entire daily run.
- **Rationale**: `mas outdated` separates fields with variable whitespace and wraps version transitions in trailing parentheses. Regex extraction is immune to spaces inside application names, and excluding multi-GB Xcode from unattended 300s `mas upgrade` eliminates recurring daily timeout failures.

### Decision 4: Graceful Drain Alignment in `docker-service.sh`
- **Choice**: Increase default `timeout_sec` in `cmd_drain` and `stop` (`~/Developer/scripts/docker-service.sh`) from `30` to `65` seconds, and extend `cmd_status` / `status_json` to query `docker compose --project-directory "$stack_dir" ps` for each path in `COMPOSE_STACKS`.
- **Rationale**: `shb-schedule/compose.yaml` configures `stop_grace_period: 60s` so inflight DBOS steps and PostgreSQL session advisory locks can finish cleanly. Passing `--timeout 65` to `docker compose down` ensures the compose CLI never sends a premature `SIGKILL` at 30 seconds.

### Decision 5: Fail-Closed `evidence.md` Verification in `validate-archive-readiness.py`
- **Choice**: Update `check_change_readiness` in `platform/openspec-store/scripts/validate-archive-readiness.py` to distinguish active change readiness checks (`--change`) from historical range audits (`--range`):
  - For active change readiness (`--change`), require that `.openspec.yaml` exists and that whenever a change contains verification tasks (or completed implementation tasks), either `evidence.md` exists with `st_size > 0` or a legacy `evidence/` directory is non-empty (unless `--skip-specs` / no-verification exemption applies).
  - For range audits (`audit_git_range` / `--range`), verify task completion and delta specs while accepting either `evidence.md` or legacy `evidence/`, maintaining backwards compatibility with historical archives that pre-date `.openspec.yaml` or standardized `evidence.md`.
- **Rationale**: Closes the gate gap that allowed active changes to report `Status: READY` without `evidence.md`, while preventing historical git range audits from breaking against immutable past archives.

### Decision 6: Dual Validation Mode Separation (Per-Change Strict vs. Whole-Store Runtime)
- **Choice**: Maintain strict specification hygiene (`openspec validate <change> --strict --json --store openspec-store`, requiring requirement descriptions `<= 500` characters and 0 warnings) for active changes, while preserving standard non-strict validation (`openspec validate --all --store openspec-store`) for whole-store runtime integrity checks in `workstation_update.py:511` (`step_integrity_and_store_validation`).
- **Rationale**: Active changes must satisfy full schema strictness and description bounds before apply and archive. However, running `--strict` across all 150+ historical specs in the catalog triggers pre-existing warnings on legacy long descriptions without operational benefit. Separating the gates guarantees strict standards for new changes while keeping automated workstation updates resilient.

## Risks / Trade-offs

- **[Risk] Hot-reloading `shb-schedule` inside the running container after setting `execution_target: host` deletes the scheduled row from PostgreSQL** → **Mitigation**: `ScheduleReconciler` uses `DBOS.delete_schedule("workstation-daily-update")` inside its existing thread-safe reload lock, preserving all historical workflow execution rows in `shb_scheduler.workflow_status` while stopping future 08:00 AM container dispatches.
- **[Risk] Reload exception rollback false degraded state from signature mismatch** → **Mitigation**: `HotReloader.reload` filters `expected_sigs` using `self.reconciler.should_persist(res.manifest)`, guaranteeing that post-reconciliation signature readback matches the filtered DBOS state and prevents false `RollbackDegraded` demotion.
- **[Risk] Editing `~/Developer/scripts/workstation-daily-update.sh` invalidates the SHA-256 digest in `config/script-provenance-manifest.tsv`** → **Mitigation**: Synchronize `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` in the same step and immediately update the recorded SHA-256 digest in `config/script-provenance-manifest.tsv`.

## Migration Plan

1. Update central store scripts (`toolchain_updater_registry.py`, `reconcile-agent-cli-coverage.py`, `test-version-authority-governance.py`, `validate-archive-readiness.py`) and spec deltas in `/Users/androidteam/Developer/platform/openspec-store`.
2. Update `schema.py`, `reconciliation.py`, `cli.py`, `workstation_update.py`, and unit tests in `/Users/androidteam/Developer/shb/shb-schedule`.
3. Update `~/.shb/schedules/workstation-daily-update.yaml` (`execution_target: host`, mode `0600`), rebuild/reload `shb-schedule` container, and verify `workstation-daily-update` is retired from container PostgreSQL `workflow_schedules` while remaining discoverable on host `shb-schedule list` / `validate`.
4. Update `~/Developer/scripts/docker-service.sh` and `~/Developer/scripts/workstation-daily-update.sh` (plus store mirror and `script-provenance-manifest.tsv`), run full test suites and strict OpenSpec validation, and record value-blind verification outputs in `evidence.md`.
