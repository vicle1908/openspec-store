# hermes-cron-run-reliability Specification

## Purpose
Define requirements for deterministic, state-change-driven Hermes cron execution for shell-native health checks and read-only reporters. Replaces LLM-agent execution for tasks that do not require reasoning.

## Requirements

### Requirement: Deterministic cron jobs SHALL use script-only mode

Hermes cron jobs whose output is fully determined by script logic SHALL use `--no-agent` mode with an explicit `--script` path. They SHALL NOT route through an LLM agent. Job mutations SHALL use `hermes cron edit`, not direct `jobs.json` editing.

#### Scenario: Health check runs deterministically

- **WHEN** the mcp-router-watchdog cron job fires
- **THEN** it SHALL execute the wrapper script directly without LLM inference
- **AND** the script SHALL produce deterministic output based on current system state

#### Scenario: Read-only reporter runs deterministically

- **WHEN** the weekly freshness report cron job fires
- **THEN** it SHALL execute the wrapper script directly without LLM inference
- **AND** the script SHALL produce a report based on existing status data

#### Scenario: Job mutation uses supported CLI

- **WHEN** a cron job definition needs modification
- **THEN** the operator SHALL use `hermes cron edit <job_id>` with documented flags
- **AND** direct editing of `jobs.json` SHALL NOT be performed

### Requirement: Cron scripts SHALL emit output only on state changes

A deterministic cron script SHALL emit empty stdout (suppressing delivery) when the observed state is healthy and unchanged from the previous check. It SHALL emit a concise alert only when state changes, recovery is needed, or the script encounters an error.

#### Scenario: Healthy state produces no output

- **WHEN** the health check script runs and all servers are healthy
- **AND** the state has not changed since the last check
- **THEN** stdout SHALL be empty
- **AND** the delivery target SHALL NOT receive a message

#### Scenario: State change produces alert

- **WHEN** the health check script runs and a previously healthy server is now missing
- **THEN** stdout SHALL contain a concise one-line alert identifying the changed state
- **AND** the delivery target SHALL receive the alert

#### Scenario: Historical crash pattern is reported with deduplication

- **WHEN** the health check script detects crash_count_24h >= 3
- **AND** the current status is healthy
- **THEN** the alert SHALL distinguish historical crash pattern from current outage
- **AND** it SHALL NOT trigger unnecessary recovery actions
- **AND** the same historical-crash alert SHALL NOT repeat on consecutive ticks (use the state file to deduplicate)

### Requirement: Cron scripts SHALL handle malformed input safely

When a health check script receives malformed or missing JSON, it SHALL emit a bounded error message and exit nonzero rather than silently succeeding or crashing.

#### Scenario: Malformed health JSON

- **WHEN** the health check script receives non-JSON output from the underlying health command
- **THEN** it SHALL emit a one-line error message
- **AND** it SHALL exit with a nonzero code
- **AND** it SHALL NOT perform recovery actions on unparseable state

#### Scenario: Missing state file

- **WHEN** the health check script cannot read the previous state file
- **THEN** it SHALL treat the previous state as unknown
- **AND** it SHALL proceed with the current check normally

#### Scenario: State file in /tmp is absent after reboot

- **WHEN** the system rebooted and /tmp was cleared
- **AND** the health check script runs
- **THEN** it SHALL treat previous state as unknown
- **AND** it SHALL NOT treat this as an error condition

### Requirement: Recovery SHALL be based on current health JSON

Recovery decisions SHALL be based on the health script's JSON stdout (the live system state), NOT on the mutable `${HERMES_HOME:-$HOME/.hermes}/state/mcp-router-watchdog.json` file. The `/tmp` state file SHALL be used only for alert deduplication (suppressing repeated identical alerts) and SHALL be validated as a regular, user-owned, non-symlink file before reading.

#### Scenario: Recovery decisions use health JSON

- **WHEN** the health check script produces JSON output
- **THEN** recovery decisions (escalate, restart, skip) SHALL be based on `critical_missing`, `medium_missing`, and `restart_needed` fields from the JSON
- **AND** the `/tmp` state file SHALL NOT influence whether recovery is attempted

#### Scenario: State file is read defensively

- **WHEN** the wrapper reads the state file for alert deduplication
- **THEN** it SHALL treat missing or unreadable state as "no previous state" (first run)
- **AND** it SHALL proceed with the current health check normally

#### Scenario: Recovery succeeds

- **WHEN** the health check script performs escalation and the service recovers
- **THEN** the state file SHALL be updated with the new status
- **AND** the next tick SHALL emit empty stdout (healthy, unchanged)

### Requirement: Script-only cron jobs SHALL have version-controlled canonical sources

New wrapper scripts used by `--no-agent` cron jobs SHALL have a version-controlled canonical source. The design SHALL identify which repository owns the scripts and document the deployment path to the runtime location.

#### Scenario: Wrapper script has a documented owner

- **WHEN** a new wrapper script is created for a cron job
- **THEN** its canonical source location SHALL be documented
- **AND** the deployment path from source to runtime location SHALL be specified
- **AND** the owning repository or directory SHALL be identified

### Requirement: Wiki lint cron SHALL be read-only

The weekly wiki lint cron job SHALL perform validation only. It SHALL NOT commit, modify, or delete wiki files. Wiki persistence and linting are separate responsibilities.

#### Scenario: Lint detects issues

- **WHEN** the wiki lint job finds missing frontmatter fields or broken links
- **THEN** it SHALL report the findings
- **AND** it SHALL NOT modify any files
- **AND** it SHALL NOT commit to the wiki repository

#### Scenario: Lint finds no issues

- **WHEN** the wiki lint job finds all pages pass validation
- **THEN** it SHALL emit empty stdout (suppressing delivery)

### Requirement: This change SHALL not modify historical execution records

This change SHALL NOT delete, modify, or archive failed or unknown execution rows in the cron execution database. Long-term retention and archival policy is a separate concern.

#### Scenario: Existing execution history remains unchanged

- **WHEN** this change is applied
- **THEN** existing failed and unknown execution rows SHALL remain unchanged
- **AND** no task, migration, or rollback command SHALL mutate `executions.db`
