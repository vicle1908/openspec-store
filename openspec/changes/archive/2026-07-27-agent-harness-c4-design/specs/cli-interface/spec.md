## ADDED Requirements

### Requirement: Workflow CLI commands

The harness SHALL expose `run`, `status`, and `report` commands through Typer.

#### Scenario: Run

- **WHEN** an authorized user runs `harness run <ticket-id>`
- **THEN** the CLI SHALL validate configuration/evidence prerequisites, create a unique workflow run ID, and start the typed graph
- **AND** selected repositories, durability mode, and output mode SHALL be explicit options

#### Scenario: Status

- **WHEN** a user runs `harness status <run-id>`
- **THEN** the CLI SHALL report ticket, current stage, status, completed/revised stages, pending gate, evidence warnings, and errors

#### Scenario: Report

- **WHEN** a user runs `harness report <run-id>`
- **THEN** the CLI SHALL return the stored verification report or an explicit not-yet-available status
- **AND** an output file SHALL be allowed only inside an explicitly approved path

### Requirement: Gate decision commands

The CLI SHALL expose `approve` and `reject` for the current pending native interrupt.

#### Scenario: Approve

- **WHEN** an authenticated authorized actor runs `harness approve <run-id> <decision-id>`
- **THEN** the CLI SHALL validate the current checkpoint/decision and resume with a typed `GateDecision`

#### Scenario: Reject

- **WHEN** an authenticated authorized actor runs `harness reject <run-id> <decision-id> --reason <text> [--backtrack <stage>]`
- **THEN** the CLI SHALL validate the target and resume with the typed rejection

#### Scenario: Actor identity

- **WHEN** a CLI decision is submitted
- **THEN** actor identity SHALL come from the authenticated operating-system/session context
- **AND** an arbitrary `--actor` value SHALL not replace authentication

### Requirement: Parseable output

Commands SHALL support human-readable and JSON output without mixing formats.

#### Scenario: JSON mode

- **WHEN** `--json` is selected
- **THEN** stdout SHALL contain schema-valid JSON records/results only
- **AND** diagnostics SHALL use stderr

#### Scenario: Secret-safe error

- **WHEN** a command fails
- **THEN** the error SHALL identify operation, run/stage when applicable, and remediation
- **AND** it SHALL not include credentials, full prompts, or protected artifact contents

### Requirement: Stable exit codes

The CLI SHALL publish stable exit codes.

#### Scenario: Exit outcome

- **WHEN** a command completes
- **THEN** success, invalid input/config, not found, unauthorized/stale decision, blocked/incomplete evidence, and internal failure SHALL have distinct documented exit codes

### Requirement: Canonical configuration loading

The CLI SHALL use `TDT_HOME`-aware shared loading.

#### Scenario: CLI startup

- **WHEN** any command starts
- **THEN** it SHALL load `$TDT_HOME/.env`, harness config, and workspace config through supported loaders
- **AND** a missing required file SHALL identify the resolved path without exposing secrets
