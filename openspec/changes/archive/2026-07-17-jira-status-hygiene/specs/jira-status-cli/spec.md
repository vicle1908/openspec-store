# jira-status-cli Specification

## Purpose

Define the `jira-skill status` CLI subcommand group: the command-line interface for auditing, classifying, deduping, and merging Jira statuses across the `psplit.atlassian.net` instance.

## ADDED Requirements

### Requirement: CLI module location

The CLI SHALL live at `jira-skill/src/jira_skill/status/` as a `typer.Typer()` subcommand group registered under `jira-skill status`. The module SHALL import from `tdt_core.clients.jira_workflow`, `tdt_core.clients.jira`, and `tdt_sheets`.

#### Scenario: CLI registration
- **WHEN** `uv run jira-skill status --help` is called
- **THEN** it SHALL display the subcommand group with all 8 subcommands

### Requirement: jira-skill status audit

`jira-skill status audit [--projects <CSV>] [--output <format>]` SHALL:

1. Read all 200+ projects from Jira via `PatchedJira`.
2. For each project, fetch current statuses via `StyleHandler`.
3. Diff live statuses against the canonical taxonomy and `status_catalog`.
4. Write results to `audit_log` tab.
5. If `newly_diverged > 0`, post a structured alert to the same channel as `webhook-receiver selftest`.
6. If `fully_standard` drops below a configurable threshold, escalate.

#### Scenario: Daily audit run
- **WHEN** `jira-skill status audit` runs (triggered by DBOS scheduler daily at 07:00 UTC)
- **THEN** it SHALL write one row to `audit_log`
- **AND** if `newly_diverged > 0`, it SHALL post to the configured alert channel

#### Scenario: Output formats
- **WHEN** `jira-skill status audit --output tabular` is called
- **THEN** it SHALL print a human-readable summary table to stdout
- **WHEN** `jira-skill status audit --output json` is called
- **THEN** it SHALL print machine-readable JSON to stdout

### Requirement: jira-skill status diff

`jira-skill status diff --project <KEY>` SHALL show what a merge would do for a given project without making any changes.

#### Scenario: Dry-run diff
- **WHEN** `jira-skill status diff --project PDS` is called
- **THEN** it SHALL print: (a) statuses that match canonical, (b) statuses that diverge, (c) missing canonical statuses, (d) project-private statuses
- **AND** it SHALL NOT call any Jira API that changes state

### Requirement: jira-skill status preflight

`jira-skill status preflight --project <KEY>` SHALL classify the project's current statuses and emit a verdict.

#### Scenario: Clean verdict
- **WHEN** `jira-skill status preflight --project PWM` is called for a project that matches the canonical template
- **THEN** it SHALL emit `verdict: clean` and exit 0

#### Scenario: Divergent verdict with acknowledgment
- **WHEN** `jira-skill status preflight --project PWM` is called for a project with divergence
- **THEN** it SHALL emit `verdict: divergent` with a list of mismatches
- **AND** the `setup-project` preflight chain SHALL require `--acknowledge-divergence "reason"` to proceed

#### Scenario: Unknown verdict
- **WHEN** `jira-skill status preflight --project NEW-PROJECT` is called for a project not in `project_manifest`
- **THEN** it SHALL emit `verdict: unknown` and require `--force` to proceed

### Requirement: jira-skill status merge

`jira-skill status merge --project <KEY> [--yes-i-understand-this-is-irreversible]` SHALL merge statuses for a single project.

`jira-skill status merge --projects <CSV> [--yes-i-understand-this-is-irreversible]` SHALL merge statuses for multiple projects sequentially, stopping on first failure.

#### Scenario: Sign-off gate
- **WHEN** `jira-skill status merge --project PDS` is called without both sign-off columns filled in `project_manifest`
- **THEN** it SHALL refuse with: `"Instance admin sign-off required. Run: jira-skill status signoff --project PDS --role instance_admin"`

#### Scenario: Batch merge stops on first failure
- **WHEN** `jira-skill status merge --projects PDS,PWM,RMD` is called
- **THEN** it SHALL run merges sequentially
- **AND** if `merge_status == completed` for PDS, it SHALL refuse to re-merge PDS
- **AND** if PWM fails, it SHALL stop and not attempt RMD
- **AND** it SHALL write one row per project to `merge_log`

### Requirement: jira-skill status dedupe

`jira-skill status dedupe [--global-confirm]` SHALL perform instance-wide deduplication.

`jira-skill status dedupe --dry-run` SHALL preview the dedupe plan without executing.

`jira-skill status dedupe --cluster <id> [--confirm]` SHALL target a specific cluster only.

#### Scenario: Dry-run preview
- **WHEN** `jira-skill status dedupe --dry-run` is called
- **THEN** it SHALL read `status_catalog` and print: (a) list of clusters with `cluster_size > 1`, (b) for each cluster: the `is_canonical_target` record, (c) total estimated issue transitions
- **AND** it SHALL NOT call any Jira API that changes state

#### Scenario: Execution gate
- **WHEN** `jira-skill status dedupe` is called without `--global-confirm`
- **THEN** it SHALL refuse with: `"Dedupe is irreversible. Pass --global-confirm to proceed."`

#### Scenario: Dedupe execution
- **WHEN** `jira-skill status dedupe --global-confirm` is called
- **THEN** for each `duplicate_cluster_id` with `cluster_size > 1`:
  - It SHALL select the `is_canonical_target=true` record
  - For team-managed clusters: it SHALL call `bulk_transition_for_dedupe` per project
  - For company-managed clusters: it SHALL call `bulk_transition_global`
- **AND** for each `bucket=mislabeled` singleton: it SHALL call Jira to fix the category field
- **AND** for each `bucket=alias` singleton: it SHALL call `bulk_transition` to the canonical target, then delete the record
- **AND** it SHALL write one row to `dedupe_log` per cluster
- **AND** it SHALL write one row to `merge_log` per individual project transition

### Requirement: jira-skill status classify-singletons

`jira-skill status classify-singletons [--dry-run]` SHALL analyze the 180 singleton records and propose a `bucket` classification for each.

#### Scenario: Proposed classification written to Sheet
- **WHEN** `jira-skill status classify-singletons` is called
- **THEN** it SHALL read all singleton records from `status_catalog`
- **AND** for each, set the `bucket` column to one of: `mislabeled` (if category doesn't match the majority for that name), `alias` (if an alias match exists in the taxonomy), `garbage` (if `in_use=false` and name is a Jira default), `keep` (otherwise)
- **AND** it SHALL NOT apply the classification without confirmation

### Requirement: jira-skill status signoff

`jira-skill status signoff --project <KEY> --role <ROLE>` SHALL write a sign-off record to `signoff_log`.

#### Scenario: Sign-off records
- **WHEN** `jira-skill status signoff --project PDS --role instance_admin` is called
- **THEN** it SHALL look up the account ID for the current user from Jira
- **AND** write one row to `signoff_log`
- **AND** update `project_manifest` with `instance_admin_signoff_at = now()`

### Requirement: jira-skill status render-sheet

`jira-skill status render-sheet [--tab <TAB>]` SHALL regenerate the Sheet from live Jira data.

#### Scenario: Full render
- **WHEN** `jira-skill status render-sheet` is called
- **THEN** it SHALL call `GET /rest/api/3/status` (all 749 records)
- **AND** populate `status_catalog` tab with all rows
- **AND** update `in_use`, `used_by_projects`, `category` from live Jira data

### Requirement: jira-skill status standardize

`jira-skill status standardize --projects <CSV> [--dry-run]` SHALL be an alias for running `classify-singletons`, `extend-project` for each, and `merge` for each, in sequence.

#### Scenario: Batch standardize
- **WHEN** `jira-skill status standardize --projects PDS,PWM,RMD --dry-run` is called
- **THEN** it SHALL emit the full diff for all 3 projects
- **AND** it SHALL NOT make any changes

### Requirement: Error exit codes

The CLI SHALL exit with code 0 on success, 1 on user-facing errors (missing sign-off, rate limit, argument errors), and 2 on unexpected exceptions.

#### Scenario: Missing sign-off exits with code 1
- **WHEN** `jira-skill status merge --project PDS` is called without sign-off
- **THEN** it SHALL print an error and exit with code 1
