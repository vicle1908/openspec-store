# dev-performance-sprint-scoping Specification

## Purpose
TBD - created by archiving change dev-performance-sprint-scoping. Update Purpose after archive.
## Requirements
### Requirement: dev-performance SHALL default to sprint period

The dev-performance report SHALL use the sprint date range from `config.toml` (via workbook title) as the default data collection window.

#### Scenario: Sprint dates available

- **WHEN** `config.toml` has `current_sprint` and the workbook title contains valid dates
- **THEN** the report SHALL use sprint start date as `window_start` and sprint end date as `window_end`
- **AND** the JQL query SHALL filter by `updated >= '<sprint_start>' AND updated <= '<sprint_end>'`

#### Scenario: Sprint dates unavailable

- **WHEN** `config.toml` has no `current_sprint` or workbook title has no dates
- **THEN** the report SHALL fall back to the 30-day lookback window
- **AND** SHALL log a warning: "Sprint dates unavailable, using 30-day lookback"

### Requirement: dev-performance SHALL support override via CLI flag

The dev-performance CLI SHALL accept a `--lookback-days` flag to override the sprint period.

#### Scenario: CLI override specified

- **WHEN** the user runs `jira-daily-reports dev-performance --lookback-days 30`
- **THEN** the report SHALL use 30-day lookback instead of sprint dates
- **AND** the `--lookback-days` value SHALL take precedence over sprint dates

#### Scenario: CLI override not specified

- **WHEN** the user runs `jira-daily-reports dev-performance` without `--lookback-days`
- **THEN** the report SHALL use sprint dates (default behavior)

### Requirement: dev-performance SHALL support override via env var

The `DEV_PERFORMANCE_LOOKBACK_HOURS` env var SHALL override sprint dates when set.

#### Scenario: Env var override specified

- **WHEN** `DEV_PERFORMANCE_LOOKBACK_HOURS=720` is set
- **THEN** the report SHALL use 30-day lookback instead of sprint dates
- **AND** the env var SHALL take precedence over sprint dates

#### Scenario: Env var not specified

- **WHEN** `DEV_PERFORMANCE_LOOKBACK_HOURS` is not set
- **THEN** the report SHALL use sprint dates (default behavior)

### Requirement: dev-performance SHALL support override via config.toml

The `[dev_performance]` section SHALL support `sprint_scoped` and `lookback_hours` options.

#### Scenario: sprint_scoped=false in config.toml

- **WHEN** `[dev_performance] sprint_scoped = false` and `lookback_hours = 720`
- **THEN** the report SHALL use 30-day lookback instead of sprint dates

#### Scenario: sprint_scoped=true in config.toml (default)

- **WHEN** `[dev_performance] sprint_scoped = true` (or absent, defaults to true)
- **THEN** the report SHALL use sprint dates (default behavior)

### Requirement: Override precedence SHALL be documented

The override precedence SHALL be (highest to lowest):

1. CLI flag: `--lookback-days`
2. ENV var: `DEV_PERFORMANCE_LOOKBACK_HOURS`
3. Config: `[dev_performance] sprint_scoped = false` + `lookback_hours`
4. Sprint dates from config.toml (default)
5. Hardcoded fallback: 720 hours (30 days)

#### Scenario: Multiple overrides specified

- **WHEN** `--lookback-days 30` CLI flag AND `DEV_PERFORMANCE_LOOKBACK_HOURS=600` env var are both set
- **THEN** the CLI flag SHALL take precedence (30 days = 720 hours)
- **AND** the env var SHALL be ignored

#### Scenario: Only config.toml override

- **WHEN** `[dev_performance] sprint_scoped = false` and `lookback_hours = 480` and no CLI/env override
- **THEN** the report SHALL use 480 hours (20 days) lookback

### Requirement: Backward compatibility SHALL be maintained

Existing `DEV_PERFORMANCE_LOOKBACK_HOURS` env var usage SHALL continue to work as override.

#### Scenario: Existing env var usage

- **WHEN** `DEV_PERFORMANCE_LOOKBACK_HOURS=720` is set (existing behavior)
- **THEN** the report SHALL use 30-day lookback (same as before)
- **AND** SHALL NOT break any existing scheduler workflows

### Requirement: Window calculation SHALL be consistent

The `window_start` and `window_end` values passed to row builders SHALL match the JQL query filter.

#### Scenario: Sprint-scoped window

- **WHEN** sprint dates are 20 Jul – 31 Jul 2026
- **THEN** `window_start` SHALL be `2026-07-20 00:00:00`
- **AND** `window_end` SHALL be `2026-07-31 23:59:59`
- **AND** JQL SHALL filter `updated >= '2026-07-20' AND updated <= '2026-07-31'`

#### Scenario: Lookback window

- **WHEN** lookback is 720 hours (30 days)
- **THEN** `window_start` SHALL be `now - 720 hours`
- **AND** `window_end` SHALL be `now`
- **AND** JQL SHALL filter `updated >= -720h`

