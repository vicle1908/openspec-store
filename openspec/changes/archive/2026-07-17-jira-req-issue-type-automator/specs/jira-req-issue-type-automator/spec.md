# jira-req-issue-type-automator

## Purpose

Standardize how requirements-clarification work is filed as a distinct Jira
issue type ("Req") across all **classic** projects in the PSplit Jira
instance, so that ambiguous requirements do not masquerade as Tasks or get
tracked informally in comments.

## ADDED Requirements

### Requirement: TDT Core exposes a Jira issue-type REST client

`tdt-core/src/tdt_core/clients/jira_types.py` SHALL provide a thin
wrapper around the Jira REST endpoints required to manage global and
project-scoped issue types and issue type schemes:

- `GET /rest/api/3/issuetype` — list all global issue types
- `POST /rest/api/3/issuetype` — create a new global issue type
- `PUT /rest/api/3/issuetype/{id}` — update name / description / avatar
- `GET /rest/api/3/issuetascheme` — list all schemes
- `GET /rest/api/3/issuetascheme/project?projectId={id}` — fetch scheme for a project
- `PUT /rest/api/3/issuetascheme/{schemeId}/issuetype/{issueTypeId}` —
  add an issue type to a scheme

The client SHALL be constructed via the existing
`JiraClientFactory` (no new auth or env handling).

#### Scenario: Client module imports cleanly

- **WHEN** `from tdt_core.clients.jira_types import JiraIssueTypeClient` is executed
- **THEN** the import succeeds without side effects, and `JiraIssueTypeClient(session=...)` instantiates

#### Scenario: List call round-trips against a sandbox project

- **WHEN** `list()` is called against an empty test Jira instance
- **THEN** the client returns a `list[JiraIssueType]` object — never raises on a 200 response, surfaces HTTP errors verbatim otherwise

### Requirement: jira-skill gains an `issue-type` sub-app with three subcommands

`jira-skill/src/jira_skill/issue_type.py` SHALL register a Typer
sub-app under `app.add_typer(issue_type_app, name="issue-type")` exposing
three subcommands:

1. `jira-skill issue-type create --name Req --description ... [--dry-run]`
2. `jira-skill issue-type update --id 12345 [--name ...] [--description ...] [--dry-run]`
3. `jira-skill issue-type list [--scheme-only] [--json]`

#### Scenario: Create subcommand writes the new global type

- **WHEN** `jira-skill issue-type create --name "Req" --description "..."` is invoked against a Jira instance that does not already have a "Req" global type
- **AND** the operator holds the "Administer Jira" global permission
- **THEN** the new global issue type is created and the assigned numeric ID is printed

#### Scenario: Create is idempotent

- **WHEN** the same `create` is invoked twice with the same `--name`
- **THEN** the second invocation detects the existing type, prints its ID, and exits without raising

#### Scenario: Dry-run prints a plan and exits without writing

- **WHEN** `--dry-run` is passed to either `create` or `update`
- **THEN** the command prints the planned HTTP requests (method + URL + payload summary) and exits with code 0 before any mutation call hits the API

#### Scenario: Update propagates to all schemes containing the type

- **WHEN** `jira-skill issue-type update --id 12345 --name "Requirements"` runs
- **THEN** the global type's name is updated; schemes are untouched (the name change is inherently visible everywhere the type appears)

### Requirement: Classic-project wiring is driven by the `JIRA_CLASSIC_PROJECTS` env var

The `create` subcommand SHALL read `JIRA_CLASSIC_PROJECTS` from
`~/.tdt/.env` (a comma-separated list of project keys, e.g.
`35 existing keys`) and SHALL iterate the unique issue type schemes
covering those projects, adding the new global type to each scheme.

#### Scenario: All classic projects inherit the new type

- **WHEN** `create --name Req` is invoked with `JIRA_CLASSIC_PROJECTS` defining 35 projects across 20 distinct schemes
- **THEN** for each scheme, the type is added exactly once and the operation is recorded in a summary table

#### Scenario: Team-managed projects are silently skipped

- **WHEN** a project is **not** in `JIRA_CLASSIC_PROJECTS` (i.e. it is team-managed)
- **THEN** the wiring loop does not touch its scheme and the summary table reports it as `skipped: team-managed`

### Requirement: Limits are documented in CLI help

`jira-skill issue-type --help` SHALL explain:

- The tool operates only on classic projects; team-managed are skipped
- `create` requires the operator to hold "Administer Jira"
- Schema assignment to a scheme requires the operator to hold "Administer
  Jira" or project-level "Administer Project" on each affected project
- Re-running is safe (idempotent)

#### Scenario: Help text enumerates all three subcommands and the team-managed caveat

- **WHEN** the user invokes `jira-skill issue-type --help`
- **THEN** the three subcommands are listed and the docstring explains the classic-only limitation

## MODIFIED Requirements

### Requirement: jira-skill CLI surface gains an `issue-type` command family

The `jira-skill` CLI SHALL register the new `issue-type` sub-app under
the existing CLI entry point. No existing command is renamed, removed,
or has its flag surface changed.

#### Scenario: Existing commands remain available

- **WHEN** `jira-skill --help` is invoked after this change
- **THEN** both pre-existing commands (e.g. `issue`, `sprint`) and the new `issue-type` subcommand are listed

## REMOVED Requirements

_(none)_

## Cross-references

- Implementation tracking: `tdt-meta/openspec/changes/jira-req-issue-type-automator/tasks.md`
- Design notes: `tdt-meta/openspec/changes/jira-req-issue-type-automator/design.md`
- Atlassian live-API verification embedded in `proposal.md` under
  "API Verification (Live Tests against PSplit, 2026-06-23)"
