# gws-agent-skills Specification

## Purpose
Defines the execution contracts, CLI parameter conventions, authentication verification, and structured JSON output handling for official Google Workspace agent skills (`gws-*`) powered by the `gws` command-line interface and managed via `npx skills`.

## Requirements

### Requirement: Official Google Workspace agent skills SHALL execute via gws CLI

Official Google Workspace agent skills (`gws-calendar`, `gws-drive`, `gws-gmail`, `gws-docs`, `gws-sheets`, `gws-tasks`) SHALL execute against the system-installed `/opt/homebrew/bin/gws` binary with native subcommands rather than deprecated custom Python wrapper scripts.

#### Scenario: Agent executes calendar insertion
- **WHEN** an agent creates a Google Calendar event using `gws-calendar`
- **THEN** the skill SHALL invoke `gws calendar events insert` or `gws calendar +insert`
- **AND** the command SHALL produce parseable JSON on stdout

#### Scenario: Agent handles missing binary cleanly
- **WHEN** `gws` is not found on PATH or `/opt/homebrew/bin/gws`
- **THEN** the skill SHALL report an actionable error instructing Homebrew installation
- **AND** the invocation SHALL exit with non-zero status without crashing

### Requirement: Official skills SHALL verify credential validity before mutating operations

Official Google Workspace skills SHALL inspect authentication state via `gws auth status` prior to executing multi-step mutating workflows, ensuring encrypted credentials exist and `token_valid` is true.

#### Scenario: Skill checks token before mutating operations
- **WHEN** an agent initiates a calendar event creation or file upload
- **THEN** the skill SHALL check `gws auth status` JSON fields
- **AND** if `token_valid` is false, the agent SHALL halt before API execution and advise re-authentication

#### Scenario: Skill handles valid token
- **WHEN** `gws auth status` reports `token_valid: true`
- **THEN** the skill SHALL proceed directly to API execution without prompting for login
