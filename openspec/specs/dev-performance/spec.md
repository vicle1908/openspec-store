# dev-performance Specification

## Purpose

Generate a developer-centric performance report showing per-person delivery throughput (merged MRs, deploys to dev, reopens, stale tickets, cycle time) in the sprint spreadsheet. Joins Jira ticket data with GitLab MR and deployment data to produce a Developer Performance tab.

## Requirements

### Requirement: Per-developer ticket rows

The system SHALL produce one row per (developer, ticket) pair in the Developer Performance tab. Developer identity cells SHALL merge vertically across their tickets. Per-ticket metrics appear in right-hand columns.

#### Scenario: Developer has multiple tickets
- **WHEN** a developer is assigned 3 tickets
- **THEN** the report shows 3 rows with the developer name merged across all 3

### Requirement: GitLab MR and deployment join

The system SHALL link each ticket to its GitLab MRs using remote-link first, then branch-name regex fallback. It SHALL capture `merged_at` and earliest deployment to dev environment.

#### Scenario: Ticket has linked MR via remote link
- **WHEN** a Jira ticket has a remote link to a GitLab MR
- **THEN** the report uses that MR's merge timestamp and deployment data

#### Scenario: No remote link, fallback to branch regex
- **WHEN** no remote link exists but a branch matches `KEY-.*`
- **THEN** the system finds the MR by branch name pattern

### Requirement: Per-developer aggregates

The system SHALL compute per-developer aggregates: median and p90 cycle time (In Progress → first deploy to dev), median and p90 reopens, ticket counts (assigned/merged/deployed/stale). Aggregates appear in a per-developer footer band.

#### Scenario: Developer has 5+ tickets
- **WHEN** a developer has 5 tickets with cycle times
- **THEN** the footer shows median and p90 cycle time across those tickets

### Requirement: Stale ticket detection

The system SHALL detect stale tickets based on per-status thresholds configurable via `DEV_PERFORMANCE_STALE_*_DAYS` environment variables. Default threshold is 7 days for unknown statuses.

#### Scenario: Ticket stale in current status
- **WHEN** a ticket has been in its current status for more than the configured threshold
- **THEN** it is flagged as stale in the report

### Requirement: SQLite diff cache

The system SHALL use a local SQLite cache (`~/.tdt/state/jira-daily-reports/dev_performance_cache.sqlite`) so hourly runs only emit changed rows to the Sheets API.

#### Scenario: No changes since last run
- **WHEN** the diff cache shows no changes for a developer's tickets
- **THEN** the system writes 0 cells to the spreadsheet for that developer

### Requirement: Schedule registration

The system SHALL register a `dev-performance` schedule with cron `0 * * * *` (hourly) in the canonical `_CRON_*` pattern.

#### Scenario: Schedule is registered
- **WHEN** the scheduler loads all jira-daily-reports schedules
- **THEN** `jira-dev-performance` appears in the schedule list with hourly cadence
