# auto-discover-epics Specification

## Purpose

Enable automatic epic discovery from the Epic Plan mapping as an optional feature, while keeping hardcoded epic lists as the default operational mode. The `[schedule].epics` field accepts either explicit epic keys or `"from_plan"` as a special value.

## ADDED Requirements

### Requirement: Explicit epic list (default mode)

The `[schedule].epics` field SHALL accept a list of explicit Jira epic keys. These keys are used directly for analysis.

#### Scenario: hardcoded keys from multiple projects
- **WHEN** `[schedule].epics = ["TJ-1635", "AU-348", "TJ-1773", "TJ-1960", "RMD-4160"]`
- **THEN** the scheduler analyzes all 5 epics across TJ, AU, and RMD projects

#### Scenario: single epic key
- **WHEN** `[schedule].epics = ["RMD-4160"]`
- **THEN** `schedule.epics` = `["RMD-4160"]` (backward compatible)

### Requirement: Auto-discover epics from plan mapping

When `[schedule].epics = ["from_plan"]`, the system SHALL read all mapped epic keys from `[epic_plan].epics` and use them as the epic list for the scheduled report. The resolution happens in `AppConfig.from_env()` so downstream code receives a resolved list.

#### Scenario: from_plan with mapped epics
- **WHEN** `[schedule].epics = ["from_plan"]` and `[epic_plan].epics` contains `{"RMD-4160": {...}, "TJ-1656": {...}}`
- **THEN** `schedule.epics` resolves to `["RMD-4160", "TJ-1656"]` and the scheduler analyzes both

#### Scenario: from_plan with empty epic_plan
- **WHEN** `[schedule].epics = ["from_plan"]` and `[epic_plan]` is disabled or has no epics
- **THEN** `schedule.epics` resolves to `[]`, the scheduler logs a warning, and exits cleanly

### Requirement: Fallback when epic_plan disabled

When `[epic_plan].enabled = false` and `[schedule].epics = ["from_plan"]`, the system SHALL return an empty epic list without error.

#### Scenario: epic_plan disabled with from_plan
- **WHEN** `[epic_plan].enabled = false` and `[schedule].epics = ["from_plan"]`
- **THEN** `schedule.epics` = `[]`, scheduler logs warning and exits cleanly

### Requirement: CLI override

The `scheduled-run` subcommand SHALL accept `--epics` flag to override the config value. When provided, CLI value takes precedence over config.

#### Scenario: CLI override
- **WHEN** `epic-report scheduled-run --epics RMD-4160,TJ-1656`
- **THEN** those epics are analyzed regardless of config value

### Requirement: Operational verification of spreadsheet output

After running with hardcoded epic keys, the spreadsheet written to `[schedule].spreadsheet_url` SHALL contain all configured epics across every relevant tab.

#### Scenario: multi-project epics produce complete spreadsheet
- **WHEN** `epic-report scheduled-run` executes with `[schedule].epics = ["TJ-1635", "AU-348", "TJ-1773", "TJ-1960", "RMD-4160"]`
- **THEN** the spreadsheet SHALL contain:
  - An **Epic Overview** tab with one row per epic (key, project, status, risk, tasks, completion)
  - A dedicated **detail tab** per epic with task-level breakdown
  - A **Delivery Plan Analysis** tab with plan-state alignment for each epic
  - A **Risks** tab listing all identified risks per epic
- **AND** no epic from `[schedule].epics` is missing from the spreadsheet

#### Scenario: spreadsheet row count matches epic count
- **WHEN** `[schedule].epics` has N keys
- **THEN** the **Epic Overview** tab SHALL contain exactly N data rows (excluding header)
