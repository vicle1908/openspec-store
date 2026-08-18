## MODIFIED Requirements

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
