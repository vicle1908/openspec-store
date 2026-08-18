## Why

agent-core/scheduler_setup.py owns workflow functions that belong to code-daily-scan and jira-epic-report, creating cross-repo coupling via `sys.path.insert` hacks. Additionally, `tdt-core/scheduler/cli.py` hardcodes `"agent_core.scheduler_setup"` as the default module to import at runtime, creating a second coupling point. The `register_fn` pattern — proven by jira-daily-reports and webhook-receiver — should be adopted uniformly so each repo registers its own scheduled workflows. The `stale_workflow_cleaner` maintenance workflow belongs in tdt-core alongside the DBOS engine. Finally, 8 dead workflow functions (~180 lines) in scheduler_setup.py exist because YAML manifests now own schedule registration.

## What Changes

- **Move `stale_workflow_cleaner`** from `agent-core/scheduler_setup.py` to `tdt-core/scheduler/maintenance.py` as a built-in framework maintenance workflow.
- **Move `daily_epic_report` + `_run_epic_report`** from `agent-core/scheduler_setup.py` to `jira_epic_report/dbos_scheduling.py` via the `register_all_schedules` pattern.
- **Create `code_daily_scan/dbos_scheduling.py`** with `register_all_schedules()` owning `daily_android_scan` and `daily_ios_scan` workflows (subprocess pattern matching jira-daily-reports).
- **Remove 8 dead functions** (~180 lines) from `agent-core/scheduler_setup.py`: `_load_code_daily_scan_config`, `_get_android_config`, `_get_ios_config`, `_platform_scan_command`, `_run_platform_scan`, `daily_android_scan`, `daily_ios_scan`, `_PLATFORM_SHEET_ENV`, plus `_android_config`/`_ios_config` globals. These are unreachable because YAML manifests own schedule registration.
- **Remove `sys.path.insert` hacks** from `agent-core/scheduler_setup.py` for code-daily-scan/jira-daily-reports paths.
- **Update `tdt-core/scheduler/cli.py`** to remove 3 hardcoded `"agent_core.scheduler_setup"` string literals and 3 `sys.path.insert` blocks. The `serve` command relies on the YAML manifest system rather than dynamically importing a hardcoded module.
- **Update YAML manifests** for code-daily-scan and jira-epic-report to use `register_fn:`.
- **Update manifest generators** (`generators/code_daily_scan.py`, `generators/jira_epic_report.py`) to produce `register_fn` YAML.
- **Remove `scripts/generate_schedule_manifest.py`** — the `@_ENGINE` decorator parser is obsolete.
- **Dockerfile unchanged** — COPY scope retained because generators and `uv pip install -e` still need sibling repo source trees. The `sys.path.insert` removal in scheduler_setup.py reduces Python-level coupling; the Docker-level COPY is defense-in-depth.
- **Update stale docstrings/comments** in jira-daily-reports, webhook-receiver, code-daily-scan, and ops-automation-suite.

**BREAKING**: `agent-core/scheduler_setup.py` public API changes significantly (6 functions + stale_workflow_cleaner removed). `tdt-core/scheduler/cli.py` hardcoded default module changes. GitNexus confirms 0 upstream callers for moved functions.

## Capabilities

### Modified Capabilities

- `agent-core-scheduler-setup`: Ownership of `stale_workflow_cleaner`, `daily_android_scan`, `daily_ios_scan`, and `daily_epic_report` moves from agent-core. 8 dead functions removed.
- `scheduled-epic-report`: Manifest wiring changes to `register_fn: jira_epic_report.dbos_scheduling:register_all_schedules`.
- `scheduler-cli`: Hardcoded `"agent_core.scheduler_setup"` default module removed; CLI relies on YAML manifest system.

### New Capabilities

None.

## Non-Goals

- Changing the `tdt-scheduler-ownership-contract`.
- Changing the YAML manifest schema.
- Modifying jira-daily-reports or webhook-receiver (already migrated).
- Changing the scheduler Docker image base or Python version.
- Changing the DBOS engine or tdt-core scheduler framework internals.

## Ownership Boundaries

| Component | Current owner | After change |
|---|---|---|
| `stale_workflow_cleaner` | agent-core | tdt-core/scheduler |
| `daily_android_scan` workflow | agent-core (dead code) | code-daily-scan |
| `daily_ios_scan` workflow | agent-core (dead code) | code-daily-scan |
| `daily_epic_report` workflow | agent-core (active) | jira-epic-report |
| `_run_epic_report` helper | agent-core (active) | jira-epic-report |
| Scheduler CLI hardcoded module | tdt-core/scheduler/cli.py | YAML manifest system (canonical) |
| Manifest generators | agent-core/deployments/scheduler/generators | agent-core (output changes) |
| Dockerfile/compose | agent-core | agent-core (simplified) |
| YAML manifest loading | tdt-core/scheduler | tdt-core/scheduler (unchanged) |

## Impact

- **Code repos touched**: agent-core, tdt-core, code-daily-scan, jira-epic-report, jira-daily-reports (docs), webhook-receiver (docs), ops-automation-suite (docs) — 7 repos
- **Specs modified**: agent-core-scheduler-setup, scheduled-epic-report, scheduler-cli (3 specs)
- **Dead code removed**: ~180 lines from agent-core/scheduler_setup.py
- **Runtime**: tdt-core/scheduler/cli.py no longer hardcodes agent_core.scheduler_setup as default module
- **Risk**: MEDIUM — scheduler CLI (tdt-core), scheduler setup (agent-core), Docker build, and generators are all modified; register_fn proven by 2 repos but blast radius is wider than a single-file change; mitigate with integration verification (Group 9) and comprehensive rollback plan
