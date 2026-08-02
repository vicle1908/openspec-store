## Why

Epic analysis is currently run on-demand via `epic-report generate <keys>`. Stakeholders want a fresh, daily snapshot of a curated set of epics landing in the existing dedicated epic-report workbook (`~/.tdt/epic-report-config.toml [output].spreadsheet_url`) without someone remembering to invoke the CLI. The allow-list of which epics to analyze must be editable in `~/.tdt`, and the scheduling must follow the proven `code-daily-scan` / `jira-daily-reports` pattern so the operator's mental model stays consistent and so the change does not conflict with the existing `scheduler-cli`, `scheduler-cron-migration`, or `jira-daily-reports` ecosystem contracts.

## What Changes

- Add a new `epic-report scheduled-run` Typer subcommand that reads the `[schedule]` section from `~/.tdt/epic-report-config.toml` via the existing `AppConfig.from_env()` loader and, when `enabled = true`, invokes the existing `generate` path with the configured epic keys, format, and spreadsheet URL. When `enabled = false` (or the section is absent), the subcommand exits 0 without invoking `generate`.
- Extend `~/.tdt/epic-report-config.toml` with a new `[schedule]` table: `enabled`, `epics` (list of epic keys), `cron`, `timezone` (optional — defaults to the resolved workspace timezone per `scheduler-cron-migration`'s "Scheduled workflows pin an explicit cron timezone" requirement), `format`, and optional `spreadsheet_url` (defaults to `[output].spreadsheet_url`). The TOML parser in `epic_report.config` is extended to hydrate a new `ScheduleConfig` dataclass attached to `AppConfig`.
- Add a new schedule manifest generator at `agent-core/deployments/scheduler/generators/jira_epic_report.py` that emits a `tdt-schedule/v1` manifest under `~/.tdt/schedules/jira-epic-report.yaml` with **one schedule named `daily-epic-report`** (following the `code-daily-scan` `daily-<platform>-scan` naming convention, not the `jira-daily-reports` `jira-*` prefix convention — chosen because `daily-epic-report` is the canonical name already used in operator docs and matches the workflow function `daily_epic_report` that lives in `agent_core.scheduler_setup`). The factory is registered via `generators.register("jira-epic-report", ...)` and the new submodule is added to `_import_submodules()`.
- Add a thin `@_dbos.DBOS.workflow()` named `daily_epic_report` in `agent_core.scheduler_setup` that runs the existing scheduler pattern — a subprocess invocation of `epic-report scheduled-run` with the same env-var forwarding shape as `_run_platform_scan`. The schedule MUST register with `automatic_backfill=False` to align with `scheduler-cron-migration`'s "Scheduled workflows disable automatic backfill (default policy)" requirement, and MUST pin an explicit cron timezone (not `None`).
- Wire the generator into the scheduler container by adding `jira-epic-report` to the loop in `agent-core/deployments/scheduler/entrypoint.sh`, adding it to `HOSTED_WORKLOADS` and `ENTRY_MODULES` in `dependency_integrity_gate.py`, and adding the source bind-mount to `agent-core/compose.yaml`.
- Add `jira-epic-report` to the Dockerfile COPY block, the `sed` rewrite step, and the editable-install chain in `agent-core/deployments/scheduler/Dockerfile`. Because `jira-epic-report/pyproject.toml:21` declares `jira-skill` as a first-party dep, the install-order MUST place `jira-epic-report` **after** `jira-skill` (the comment in `Dockerfile:88-107` documents the load-bearing leaf-first ordering).
- This change does NOT introduce a host-local fallback (launchd timer, cron entry) for missed-tick replay; missed ticks are skipped, per the existing `scheduler-cron-migration` "Missed tick is not replayed" requirement applied uniformly across the scheduler.
- This change does NOT modify `epic_report.collector`'s direct `jira.jql(...)` call sites. `jira-daily-reports` spec (line 90) explicitly permits "Existing direct call sites outside `jira_daily_reports` (e.g. `person_worklog_source._search_jql_issues`, `epic_report.collector`) are acceptable as long as they implement the same cursor protocol locally; they are owned by their respective OpenSpec changes." Cursor pagination is therefore a soft obligation inherited by this change but out of scope here.

## Capabilities

### New Capabilities

- `scheduled-epic-report`: end-to-end behavior that schedules `epic-report generate` for a configurable allow-list of epic keys on a cron, writing to the existing dedicated epic-report Google Sheets workbook via the `EPIC_REPORT_SPREADSHEET_URL` env-var forwarding pattern, and conforming to the existing `scheduler-cron-migration` schedule conventions (service-prefix or `daily-*` name, explicit cron timezone, `automatic_backfill=False`, no missed-tick replay).

### Modified Capabilities

None. The change introduces a new capability; it does not modify the requirements of `scheduler-cli`, `jira-daily-reports`, `scheduler-cron-migration`, `deployable-env-loading`, or any existing spec. The new workflow participates in the existing scheduler pipeline without altering its contract.

## Impact

- **Code**:
  - `jira-epic-report/epic_report/config.py` — new `ScheduleConfig` dataclass + TOML parsing for `[schedule]` (extends the existing `_parse_toml_config` block that already parses `[output]` and `[defaults]`).
  - `jira-epic-report/epic_report/cli.py` — new `scheduled-run` Typer command. Reuses the existing `generate()` command's CLI machinery internally via `AppConfig.from_env`; **does NOT** introduce a `--spreadsheet-url` flag (spreadsheet URL flows from config + `EPIC_REPORT_SPREADSHEET_URL` env var, matching existing convention).
  - `jira-epic-report/epic_report/reporters/spreadsheet_reporter.py` — no change. The existing `generate_spreadsheet(spreadsheet_url=...)` path already handles the reuse-of-existing-workbook case.
  - `agent-core/deployments/scheduler/generators/jira_epic_report.py` — new manifest generator module (mirror of `code_daily_scan.py`).
  - `agent-core/deployments/scheduler/generators/__init__.py` — append `"jira_epic_report"` to the `_import_submodules()` list.
  - `agent-core/deployments/scheduler/entrypoint.sh` — append `jira-epic-report` to the `for repo in ...` loop on line 66.
  - `agent-core/deployments/scheduler/dependency_integrity_gate.py` — add `"jira-epic-report"` to `HOSTED_WORKLOADS` and add `("epic_report.cli",)` to `ENTRY_MODULES`.
  - `agent-core/deployments/scheduler/Dockerfile` — three edits: COPY block (after line 52, mirroring the `code-daily-scan` block 49-52), sed rewrite block (line 61-81 pattern — add `jira-epic-report` to the path-rewrites), and editable-install chain (after `jira-skill` and `jira-daily-reports` because `jira-epic-report` depends on `jira-skill` per its pyproject).
  - `agent-core/compose.yaml` — append `- ../jira-epic-report/src:/workspace/jira-epic-report/src:ro` to the scheduler's volumes block.
  - `agent-core/src/agent_core/scheduler_setup.py` — add `_run_epic_report` private helper + `@_dbos.DBOS.workflow() async def daily_epic_report(...)` thin launcher (mirror of `_run_platform_scan`/`daily_android_scan`).
- **Operator config**: `~/.tdt/epic-report-config.toml` gains a new `[schedule]` table. Backward compatible — absence of the section or `enabled = false` is a no-op.
- **Runtime state**: new `~/.tdt/schedules/jira-epic-report.yaml` manifest; new DBOS schedule `daily-epic-report`.
- **No new external dependencies.** Uses existing `typer`, `tdt_core.clients.jira.JiraClientFactory`, and the same `googleapiclient` paths the reporter already uses.
- **No impact on `poems-mobile3-ios` / `poems-mobile3-android`** — backend/scheduling change only.
- **Non-goals**:
  - JQL-driven epic discovery (Phase 2; "enhance later").
  - Cutoff-date derivation from sprint ends (Phase 2).
  - LM/dep-analysis depth (scheduled runs always use the fast heuristic path).
  - Dedicated scheduled workbook (the existing `[output].spreadsheet_url` is reused — manual and scheduled runs share one workbook, which is its intended purpose per the existing config comment).
  - Cross-project auto-detection of related epics.
  - Cursor-pagination refactor of `epic_report.collector` (inherited from `jira-daily-reports` spec; out of scope for this change).
  - Host-local fallback for missed ticks (per `scheduler-cron-migration` policy).