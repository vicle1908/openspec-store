# jira-catalog-scheduling Specification

## Purpose

Define the `jira-daily-reports catalog` CLI subcommand family and the daily DBOS scheduled workflow that drives the catalog refresh. The CLI is the on-demand entry point (used by humans and the scheduler); the workflow is the always-on driver. The contract keeps the schedule aligned with the `centralized-scheduling-module` binding: all movable cron lives in the central `tdt-scheduler` Docker service, not in the `jira-daily-reports` process.

## Requirements

## ADDED Requirements

### Requirement: The CLI MUST expose a `catalog` subcommand group on the existing `jira-daily-reports` script

The `uv run jira-daily-reports` CLI MUST add a `catalog` subcommand group (implemented as a `typer` app, mirroring the existing `planning` subcommand shape). The subcommand group MUST expose four subcommands: `build`, `refresh`, `show`, and `diff`. All four MUST read their env config from `~/.tdt/.env` via `tdt_core.env.load_tdt_env()`.

#### Scenario: The CLI exposes the four catalog subcommands

- **WHEN** the operator runs `uv run jira-daily-reports catalog --help`
- **THEN** the help text MUST list `build`, `refresh`, `show`, and `diff` as subcommands.

#### Scenario: Each subcommand reads its config from the env

- **WHEN** the operator runs `uv run jira-daily-reports catalog build`
- **THEN** the subcommand MUST call `tdt_core.env.load_tdt_env()`
- **AND** MUST read `JIRA_CATALOG_TAB_NAME`, `JIRA_CATALOG_LOOKBACK_DAYS`, `JIRA_CATALOG_PROJECTS`, and `SPREADSHEET_ID` from the loaded env
- **AND** MUST NOT require any command-line flag for those values.

### Requirement: The four subcommands MUST have distinct, well-defined behaviors

The four subcommands SHALL behave as follows:

- `build` — runs the full pipeline (collector → joiner → differ → writer) and writes a complete snapshot to the catalog tab. If the tab does not exist, it creates it (per the writer spec). If the tab does exist, `build` MUST clear the data rows (rows 2..N) before writing — `build` is destructive.
- `refresh` — runs the same pipeline but the differ is authoritative: `appended` rows are inserted, `updated` rows have only machine-owned columns overwritten, and `removed` rows are marked with `Status = Removed`. `refresh` is non-destructive and is the default for the scheduled workflow.
- `show` — reads the current catalog tab and prints it to stdout as a tabular report (no writes). `--kind <kind>` filters by `Kind`. `--status <status>` filters by `Status`.
- `diff` — runs the collector and joiner but does not write; instead it prints a human-readable diff of what the next `refresh` would change (counts of `appended` / `updated` / `removed`, plus the first 20 rows of each category).

#### Scenario: `build` clears the data area on a re-run

- **WHEN** the catalog tab already has 200 data rows and the operator runs `uv run jira-daily-reports catalog build`
- **THEN** the writer MUST delete rows 2..201 before writing the new snapshot
- **AND** MUST NOT preserve any row from the previous run.

#### Scenario: `refresh` does not touch human-owned columns

- **WHEN** the operator runs `uv run jira-daily-reports catalog refresh` after humans have filled in `Description` and `Purpose`
- **THEN** the differ MUST classify rows with changed usage data as `updated`
- **AND** the writer MUST update only the machine-owned columns
- **AND** the human-edited `Description` and `Purpose` cells MUST remain byte-identical to the pre-refresh values.

#### Scenario: `diff` prints what refresh would change without writing

- **WHEN** the operator runs `uv run jira-daily-reports catalog diff`
- **THEN** the CLI MUST run collector + joiner + differ
- **AND** MUST print `appended: <N>`, `updated: <N>`, `removed: <N>` plus a sample of each
- **AND** MUST NOT call any write method on `SheetsClient`.

#### Scenario: `show --kind Custom Field` filters the printed report

- **WHEN** the operator runs `uv run jira-daily-reports catalog show --kind "Custom Field"`
- **THEN** the CLI MUST read the full tab
- **AND** MUST print only rows where `Kind = Custom Field`
- **AND** MUST include the row counts in a header line.

### Requirement: A DBOS scheduled workflow MUST run `refresh` daily inside the central scheduler

A scheduled workflow named `jira-catalog-refresh` SHALL be registered with the central `tdt-scheduler` Docker service (per the binding `centralized-scheduling-module` change). The workflow MUST run at `0 3 * * *` (03:00 UTC daily) via the `_make_workflow("catalog-refresh", "0 3 * * *", engine=engine)` registration call added to `dbos_scheduling.py` inside `register_all_schedules()`. The existing `_run_report()` helper inside `_make_workflow` already runs `uv run python -m jira_daily_reports catalog-refresh` via subprocess in `/workspace/agent-core`.

A CLI entry `@app.command("catalog-refresh")` MUST be added to `jira-daily-reports/src/jira_daily_reports/cli.py` that is a one-liner invoking the `refresh` subcommand. This is the contract between the DBOS workflow and the catalog package.

#### Scenario: The workflow is registered and visible in tdt-scheduler

- **WHEN** the operator runs `tdt-scheduler list` on the host
- **THEN** the output MUST include a row `jira-catalog-refresh | 0 3 * * * | jira-daily-reports`
- **AND** the row MUST show `next_run` as a UTC timestamp within the next 24 hours.

#### Scenario: The scheduled run produces a delta-only write

- **WHEN** the scheduled workflow fires at 03:00 UTC on a day with no changes
- **THEN** the collector MUST produce a snapshot
- **AND** the differ MUST classify all rows as `unchanged`
- **AND** the writer MUST issue zero `write` and zero `batch_update` calls
- **AND** the workflow MUST log `catalog.refresh_no_changes` and exit 0.

#### Scenario: The scheduled run produces a delta write on a day with churn

- **WHEN** a new label `mobile-android-v3` appears in 5 tickets in the lookback window
- **THEN** the differ MUST classify the row `(Kind=Label, Name=mobile-android-v3)` as `appended`
- **AND** the writer MUST compute the next free row and call `write(spreadsheet_id, f"Catalog!A{row_count+1}", rows)` with that one row
- **AND** the workflow MUST log `catalog.refresh_appended=1 updated=0 removed=0` and exit 0.

### Requirement: The catalog subcommand family MUST integrate with the existing CLI exit-code and log conventions

`build` and `refresh` MUST exit 0 on success and non-zero on failure. On partial failure (some metadata endpoints failed but the snapshot is still usable), the CLI MUST exit 0 but MUST print a `Warnings:` section to stderr listing each `catalog.metadata_warning` line. `show` and `diff` MUST exit 0 even when the catalog tab is empty (a fresh install).

#### Scenario: A partial metadata failure exits 0 with warnings

- **WHEN** the collector logs `catalog.metadata_warning: SR/component HTTP 500` and the other endpoints succeed
- **THEN** the `build` or `refresh` subcommand MUST exit 0
- **AND** MUST print `Warnings:` to stderr with the warning line
- **AND** MUST still write the partial snapshot to the tab.

#### Scenario: A complete Jira outage exits non-zero

- **WHEN** `JiraClientFactory.from_env()` raises or the JQL call raises an unrecoverable error
- **THEN** the subcommand MUST exit non-zero
- **AND** MUST print a structured error to stderr
- **AND** the scheduled workflow MUST record the failure in DBOS so `tdt-scheduler list` shows the run as `failed`.

