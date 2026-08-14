# workspace-index-freshness Specification

## Purpose

Define automated, non-destructive GitNexus and Graphify index freshness for all workspace repositories with existing indexes, using scheduled LaunchAgent execution.

## ADDED Requirements

### Requirement: Scheduled automated index refresh

The workspace SHALL provide a scheduled refresh mechanism that keeps GitNexus and Graphify indexes current with each repository's latest committed HEAD.

#### Scenario: Nightly refresh runs automatically

- **WHEN** the scheduled LaunchAgent fires (nightly at 02:30 local time)
- **THEN** the refresh script SHALL discover all repositories under `~/Developer/` with existing `.gitnexus/` or `graphify-out/` state
- **AND** for each discovered repository, it SHALL run `gitnexus analyze . --index-only --default-branch main` (if GitNexus state exists) and `graphify update .` (if Graphify state exists)
- **AND** the operation SHALL complete without user interaction

#### Scenario: Repository has no index state

- **WHEN** a repository under `~/Developer/` has neither `.gitnexus/` nor `graphify-out/`
- **THEN** the refresh script SHALL skip it silently without error

#### Scenario: GitNexus CLI is not installed

- **WHEN** the refresh script runs and `gitnexus` is not on PATH
- **THEN** the script SHALL skip GitNexus operations for all repos and log a warning
- **AND** it SHALL still run Graphify operations for repos with Graphify state

#### Scenario: Graphify CLI is not installed

- **WHEN** the refresh script runs and `graphify` is not on PATH
- **THEN** the script SHALL skip Graphify operations for all repos and log a warning
- **AND** it SHALL still run GitNexus operations for repos with GitNexus state

### Requirement: Concurrency safety

The refresh mechanism SHALL prevent overlapping runs through a non-blocking lockfile.

#### Scenario: Previous run is still active

- **WHEN** the scheduled refresh fires and a previous run holds the lockfile
- **THEN** the new run SHALL exit cleanly without waiting or killing the previous run
- **AND** the exit SHALL be logged as "skipped: previous run active"

#### Scenario: Previous run crashed and left a stale lockfile

- **WHEN** the lockfile exists but its owning process is no longer running
- **THEN** the refresh script SHALL detect the stale lockfile and acquire it
- **AND** the stale lockfile SHALL be replaced with the current run's PID

### Requirement: Observable refresh status

The workspace SHALL provide a status command that reports index freshness across all repositories.

#### Scenario: Status is checked manually

- **WHEN** a developer runs `~/Developer/scripts/knowledge-status.sh`
- **THEN** it SHALL list every repository with existing index state
- **AND** for each, it SHALL report: tool (GitNexus/Graphify), last refresh time, current HEAD revision, indexed revision, freshness status (current/stale/unknown)

#### Scenario: Refresh log is available

- **WHEN** a developer inspects `~/Developer/.knowledge-refresh/refresh.log`
- **THEN** it SHALL contain timestamped entries for each repo refresh attempt
- **AND** entries SHALL include: timestamp, repo name, tool, status (success/failure/skipped), duration

### Requirement: Non-destructive operations

The refresh mechanism SHALL not modify application code, credentials, or configuration.

#### Scenario: Refresh affects only index state

- **WHEN** the refresh runs
- **THEN** it SHALL modify only `.gitnexus/` and `graphify-out/` directories
- **AND** it SHALL NOT modify source code, `.env` files, `pyproject.toml`, `go.mod`, or other application files

#### Scenario: Repository is in merge or rebase state

- **WHEN** a repository is in the middle of a merge, rebase, or cherry-pick
- **THEN** the refresh script SHALL skip that repository
- **AND** the skip SHALL be logged with the reason "repo in merge state"

### Requirement: Documentation accuracy

Workspace documentation SHALL accurately describe the refresh mechanism without stale claims.

#### Scenario: AGENTS.md describes refresh automation

- **WHEN** a developer reads AGENTS.md for refresh information
- **THEN** it SHALL describe the actual LaunchAgent-based automation
- **AND** it SHALL NOT contain stale claims about weekly crons that don't exist

#### Scenario: CLAUDE.md reflects current staleness policy

- **WHEN** a developer reads CLAUDE.md for knowledge graph guidance
- **THEN** it SHALL reference the automated refresh mechanism
- **AND** the staleness warning SHALL be updated to reflect that automation is in place
