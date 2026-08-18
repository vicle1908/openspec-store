# scheduled-epic-report Specification

## Purpose

Enable automated daily Jira epic report generation via the DBOS scheduler. Provides a `scheduled-run` CLI subcommand that reads configuration from `~/.tdt/epic-report-config.toml`, invokes the existing `epic-report generate` pipeline, and propagates the spreadsheet URL for managed output. The manifest generator produces a `daily-epic-report` schedule wired through `agent_core.scheduler_setup`, with backward-compatible configuration that defaults to disabled when no `[schedule]` section exists.

## Requirements

### Requirement: Scheduled run CLI subcommand

The system SHALL provide an `epic-report scheduled-run` Typer subcommand that calls `AppConfig.from_env()` to read the `[schedule]` table from `~/.tdt/epic-report-config.toml`. When `schedule.enabled = false` (or the `[schedule]` section is absent), the subcommand SHALL log a `scheduled_run.disabled` message and exit 0 with no Jira API calls and no spreadsheet writes. When `schedule.enabled = true`, the subcommand SHALL invoke the existing `epic-report generate` Typer command internally with `epic_keys=schedule.epics` and `fmt=schedule.format`, propagate the generated spreadsheet URL by setting `EPIC_REPORT_SPREADSHEET_URL=schedule.spreadsheet_url` (resolved as `[schedule].spreadsheet_url` if present, falling back to `[output].spreadsheet_url`) in the subprocess environment, and exit with the same code `generate()` returns.

#### Scenario: Schedule disabled — no-op

- **WHEN** the operator sets `[schedule].enabled = false` (or omits the `[schedule]` section entirely)
- **THEN** `epic-report scheduled-run` exits with code 0 and produces no Jira API calls and no spreadsheet writes

#### Scenario: Schedule enabled — full run

- **WHEN** the operator sets `[schedule].enabled = true` with `epics = ["RMD-4160", "PUB-1234"]`, `format = "spreadsheet"`, and a valid `spreadsheet_url`
- **THEN** `epic-report scheduled-run` invokes `generate()` with exactly those epic keys and that format, the configured spreadsheet URL is propagated via the `EPIC_REPORT_SPREADSHEET_URL` environment variable, and the subcommand exits with the same code `generate()` returns

#### Scenario: CLI subcommand — missing required fields exit non-zero

- **WHEN** `[schedule].enabled = true` but `epics` is empty or missing at the **CLI invocation** layer
- **THEN** `epic-report scheduled-run` exits non-zero with a clear error message identifying the missing field and makes no spreadsheet writes (this is the CLI-layer pre-flight check; the manifest-generator layer also raises on the same condition — see the "Manifest generator module — Enabled with missing epics" scenario below)

#### Scenario: Default spreadsheet URL fallback

- **WHEN** `[schedule].spreadsheet_url` is absent
- **THEN** `epic-report scheduled-run` uses `[output].spreadsheet_url` from the same TOML file when propagating `EPIC_REPORT_SPREADSHEET_URL`

### Requirement: ScheduleConfig loader

The system SHALL provide a `ScheduleConfig` dataclass in `epic_report.config` hydrated by `AppConfig.from_env()` from the `[schedule]` table of `~/.tdt/epic-report-config.toml`. The loader MUST tolerate a missing `[schedule]` section (returning `ScheduleConfig(enabled=False)`) and MUST validate that when `enabled=True`, both `epics` and `cron` are present and non-empty. `validate()` returns errors as a list (matching the existing Jira-validation convention in this module). The `timezone` field is optional: when omitted from the TOML, the loader MUST resolve it via `jira_daily_reports.config.workspace_timezone_name()` (the canonical resolver per `scheduler-cron-migration`'s "Scheduled workflows pin an explicit cron timezone" requirement) rather than hardcoding a value.

#### Scenario: Missing section

- **WHEN** `~/.tdt/epic-report-config.toml` contains no `[schedule]` table
- **THEN** `AppConfig.from_env()` returns `schedule = ScheduleConfig(enabled=False)` and no validation error

#### Scenario: Enabled without epics

- **WHEN** the config sets `[schedule].enabled = true` but `epics = []`
- **THEN** `AppConfig.validate()` includes `"schedule.epics required when enabled"` in its error list

#### Scenario: Valid enabled schedule

- **WHEN** `[schedule].enabled = true`, `epics = ["RMD-4160"]`, `cron = "0 7 * * *"`, `timezone = "Asia/Ho_Chi_Minh"`
- **THEN** `schedule` is a fully-populated `ScheduleConfig` with no validation errors

#### Scenario: Timezone defaulting to workspace resolver

- **WHEN** `[schedule].enabled = true` and `[schedule].timezone` is omitted
- **THEN** `ScheduleConfig.timezone` equals the value returned by `jira_daily_reports.config.workspace_timezone_name()` so the resolved value matches every other migrated schedule in the system (per `scheduler-cron-migration`'s "Cron timezone is consistent across all migrated schedules" requirement)

### Requirement: Manifest generator module

The system SHALL provide a manifest generator module at `agent-core/deployments/scheduler/generators/jira_epic_report.py`. The module MUST define a `jira_epic_report_manifest()` factory function returning a dict conforming to the `tdt-schedule/v1` schema (matching the structure of `code_daily_scan.py`'s `code_daily_scan_manifest()`), MUST call `register("jira-epic-report", jira_epic_report_manifest)` at module import time so the dispatcher in `generators.GENERATORS` can find it, and MUST be discoverable by adding `"jira_epic_report"` to the `_import_submodules()` list in `generators/__init__.py`.

The manifest SHALL use the `register_fn` pattern: `workflow.register_fn = "jira_epic_report.dbos_scheduling:register_all_schedules"` instead of the previous `module:function` wiring through `agent_core.scheduler_setup`. This decouples workflow ownership from agent-core.

**Namespace clarification:** The manifest owner name (`jira-epic-report`) and the DBOS schedule name (`daily-epic-report`) are distinct namespaces. The `jira-` prefix in the owner identifies the codebase/repo; the `daily-*` prefix in the schedule name follows the scheduler naming convention (same shape as `code-daily-scan` `daily-<platform>-scan`). These MUST NOT be conflated — the owner is for manifest routing, the schedule name is for DBOS registration.

#### Scenario: Module registers itself on import

- **WHEN** `agent-core/deployments/scheduler/generators/__init__.py` imports the new submodule
- **THEN** `GENERATORS["jira-epic-report"]` resolves to `jira_epic_report_manifest`

#### Scenario: Enabled — emits one schedule

- **WHEN** `[schedule].enabled = true` with valid cron and timezone
- **THEN** the generated manifest contains one `ScheduleSpec` named `daily-epic-report` whose `workflow.register_fn = "jira_epic_report.dbos_scheduling:register_all_schedules"`, `cron` matches `schedule.cron`, `timezone` matches the resolved workspace timezone, and `automatic_backfill = False` (the latter per `scheduler-cron-migration`'s "Scheduled workflows disable automatic backfill (default policy)" requirement)

#### Scenario: Schedule name follows the `daily-*` convention

- **WHEN** the manifest is emitted
- **THEN** the schedule name SHALL be `daily-epic-report` (matching the `code-daily-scan` `daily-<platform>-scan` convention) and SHALL NOT carry a `jira-` prefix (the `jira-daily-reports` `jira-*` prefix is reserved for that codebase; `code-daily-scan` and `jira-epic-report` both use the `daily-*` shape)

#### Scenario: Disabled — emits zero schedules

- **WHEN** `[schedule].enabled = false` or the section is absent
- **THEN** the factory returns `{"apiVersion": "tdt-schedule/v1", "owner": "jira-epic-report", "version": "1.0.0", "schedules": []}` so the dispatcher's `len(schedules) == 0` skip-write path silently skips the file write — no stale `daily-epic-report` row remains in DBOS

#### Scenario: Manifest generator — Enabled with missing epics fails loudly

- **WHEN** `[schedule].enabled = true` but `epics` is empty or missing
- **THEN** the manifest generator SHALL raise a `ValueError` identifying the missing epics field, and no schedule manifest SHALL be written

### Requirement: DBOS workflow wiring

The system SHALL provide an `@_dbos.DBOS.workflow()` named `daily_epic_report` in `agent_core.scheduler_setup`. The workflow MUST delegate to `await asyncio.to_thread(_run_epic_report)` and SHALL NOT contain any Jira or Google Sheets logic of its own. `_run_epic_report` MUST build the subprocess command `[sys.executable, "-m", "epic_report", "scheduled-run"]` and MUST forward `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` (from `os.environ`, sourced via `tdt_core.clients.jira.JiraClientFactory.from_env()` inside `epic-report`), `GOOGLE_APPLICATION_CREDENTIALS`, and `EPIC_REPORT_SPREADSHEET_URL` from the host environment into the subprocess.

#### Scenario: Manifest references the workflow

- **WHEN** `~/.tdt/schedules/jira-epic-report.yaml` is loaded by `ScheduleRegistryLoader.apply_from_yaml()`
- **THEN** `daily_epic_report` resolves as the target workflow and registers with DBOS

#### Scenario: Subprocess failure surfaces

- **WHEN** `epic-report scheduled-run` exits non-zero
- **THEN** `_run_epic_report` propagates `subprocess.CalledProcessError` so DBOS records the failure for retries / observability

#### Scenario: Missed tick is not replayed

- **WHEN** the scheduler service is offline at the scheduled tick time and comes back later
- **THEN** the missed `daily-epic-report` tick SHALL NOT be replayed by any host-local fallback (launchd timer, cron entry, or in-process retry) — the next execution SHALL occur on the next scheduled DBOS cron tick. This is a direct application of the `scheduler-cron-migration` "Missed tick is not replayed" requirement to this new schedule.

### Requirement: Entrypoint integration

The container's scheduler `entrypoint.sh` MUST include `jira-epic-report` in its manifest-generation loop (the `for repo in ...` block on line 66) alongside `jira-daily-reports`, `code-daily-scan`, and `tdt-observability`. Failure to generate `jira-epic-report` MUST abort container startup via the existing `set -euo pipefail` semantics on line 11.

#### Scenario: Generator failure aborts startup

- **WHEN** `jira-epic-report` manifest generation raises (e.g., invalid cron in `[schedule]`)
- **THEN** `entrypoint.sh` exits non-zero and the container restart policy re-runs the entrypoint on the next attempt

#### Scenario: Generator succeeds — reload touch fires once

- **WHEN** all four manifest generators (including `jira-epic-report`) complete successfully
- **THEN** exactly one `~/.tdt/schedules/.reload` sentinel write occurs, as before

### Requirement: Dependency-integrity gate coverage

The system MUST add `jira-epic-report` to `HOSTED_WORKLOADS` in `dependency_integrity_gate.py` and MUST add `("epic_report.cli",)` to its `ENTRY_MODULES` mapping. The build-time and startup-time integrity checks MUST then exercise `epic-report`'s dependency closure, catching drift between `epic-report`'s declared `[project.dependencies]` and the venv before a scheduled tick fires.

#### Scenario: Build-time gate covers epic-report

- **WHEN** the Dockerfile runs `dependency_integrity_gate.py --mode build`
- **THEN** every declared dependency of `jira-epic-report` (per its pyproject.toml — currently `tdt-core[jira]`, `tdt-sheets`, `jira-skill`, plus `atlassian-python-api`, `typer`, etc.) is imported under the scheduler venv, and any `ModuleNotFoundError` fails the build

#### Scenario: Startup gate imports epic_report.cli

- **WHEN** `entrypoint.sh` runs `dependency_integrity_gate.py --mode startup`
- **THEN** `import epic_report.cli` is exercised; a drift-induced import failure aborts startup

### Requirement: Dockerfile + compose wiring

The system MUST extend the scheduler `Dockerfile` and `compose.yaml` so `jira-epic-report` is available inside the container the same way `code-daily-scan` is. Specifically: a `COPY --chown=agent:agent jira-epic-report/pyproject.toml jira-epic-report/README.md /workspace/jira-epic-report/` and `COPY --chown=agent:agent jira-epic-report/src /workspace/jira-epic-report/src` block; a corresponding entry in the `sed` rewrite step that points `../jira-epic-report` → `/workspace/jira-epic-report` in any pyproject.toml/uv.lock that references it; a `uv pip install --python /opt/scheduler/.venv/bin/python3 -e /workspace/jira-epic-report` line in the editable-install chain (placed **after** `jira-skill` and `jira-daily-reports` because `jira-epic-report/pyproject.toml:21` declares `jira-skill` as a first-party dep — the Dockerfile comment at lines 88-107 explicitly documents this leaf-first ordering); and a `- ../jira-epic-report/src:/workspace/jira-epic-report/src:ro` bind-mount in `agent-core/compose.yaml` under the `scheduler.volumes` block.

#### Scenario: Image build includes jira-epic-report

- **WHEN** `docker compose up --build -d scheduler` is run
- **THEN** the built image contains `/workspace/jira-epic-report/src` (from COPY or compose bind-mount) and the scheduler venv can `import epic_report`

#### Scenario: Host-mounted source edits picked up

- **WHEN** the operator edits `~/Developer/tdt/jira-epic-report/...` on the host
- **THEN** the change is visible inside the container at `/workspace/jira-epic-report/src` on the next container restart (bind-mount), without a rebuild

### Requirement: Backward compatibility

The system MUST remain backward-compatible with existing `~/.tdt/epic-report-config.toml` files that lack a `[schedule]` section. Operators on such configs SHALL see no behavior change — epic analysis continues to be available exclusively via the existing `epic-report generate` CLI.

#### Scenario: Existing TOML without [schedule]

- **WHEN** `~/.tdt/epic-report-config.toml` contains only `[output]` and `[defaults]` tables (the current state)
- **THEN** `AppConfig.from_env()` returns `schedule = ScheduleConfig(enabled=False)` and the manifest factory returns the empty-schedules dict, so the scheduler registers no `daily-epic-report` schedule

#### Scenario: Existing epic-report generate invocations

- **WHEN** an operator runs `epic-report generate <keys>` directly
- **THEN** the command behaves identically to before this change

### Requirement: Cursor pagination inheritance

The system SHALL NOT introduce new direct `jira.jql(...)` call sites in this change. The pre-existing direct call sites in `epic_report.collector` remain accepted per `jira-daily-reports` spec line 90 ("Existing direct call sites outside `jira_daily_reports` (e.g. `person_worklog_source._search_jql_issues`, `epic_report.collector`) are acceptable as long as they implement the same cursor protocol locally; they are owned by their respective OpenSpec changes"). This change inherits that soft obligation and MUST NOT regress the cursor-pagination behavior of `epic_report.collector`.

#### Scenario: No new direct jira.jql call sites

- **WHEN** the implementation adds new Jira-querying code paths in `epic_report`
- **THEN** those paths SHALL delegate to a shared helper (either the existing `jira_daily_reports.client._jql_paginated` via an importable seam, or an internal `epic_report` helper that implements the same cursor protocol) instead of calling `jira.jql(...)` directly
