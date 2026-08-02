# CLI Interface

## Purpose

Define the harness CLI surface: commands, output formats, exit codes, gate operations, configuration loading, ticket context commands, observability commands, and multi-variant support.

## Requirements

### Requirement: Workflow CLI commands

The harness SHALL expose run, status, and report commands through Typer.

#### Scenario: Run

- **WHEN** an authorized user runs harness run ticket-id
- **THEN** the CLI SHALL validate configuration and evidence prerequisites, create a unique workflow run ID, and start the typed graph
- **AND** selected repositories, durability mode, and output mode SHALL be explicit options

#### Scenario: Status

- **WHEN** a user runs harness status run-id
- **THEN** the CLI SHALL report ticket, current stage, status, completed or revised stages, pending gate, evidence warnings, and errors

#### Scenario: Report

- **WHEN** a user runs harness report run-id
- **THEN** the CLI SHALL return the stored verification report or an explicit not-yet-available status
- **AND** an output file SHALL be allowed only inside an explicitly approved path

### Requirement: Gate decision commands

The CLI SHALL expose approve and reject for the current pending native interrupt.

#### Scenario: Approve

- **WHEN** an authenticated authorized actor runs harness approve run-id decision-id
- **THEN** the CLI SHALL validate the current checkpoint and decision and resume with a typed GateDecision

#### Scenario: Reject

- **WHEN** an authenticated authorized actor runs harness reject run-id decision-id with reason and optional backtrack
- **THEN** the CLI SHALL validate the target and resume with the typed rejection

#### Scenario: Actor identity

- **WHEN** a CLI decision is submitted
- **THEN** actor identity SHALL come from the authenticated operating-system or session context
- **AND** an arbitrary actor value SHALL not replace authentication

### Requirement: Parseable output

Commands SHALL support human-readable and JSON output without mixing formats.

#### Scenario: JSON mode

- **WHEN** json output is selected
- **THEN** stdout SHALL contain schema-valid JSON records and results only
- **AND** diagnostics SHALL use stderr

#### Scenario: Secret-safe error

- **WHEN** a command fails
- **THEN** the error SHALL identify operation, run or stage when applicable, and remediation
- **AND** it SHALL not include credentials, full prompts, or protected artifact contents

### Requirement: Stable exit codes

The CLI SHALL publish stable exit codes.

#### Scenario: Exit outcome

- **WHEN** a command completes
- **THEN** success, invalid input or config, not found, unauthorized or stale decision, blocked or incomplete evidence, and internal failure SHALL have distinct documented exit codes

### Requirement: Canonical configuration loading

The CLI SHALL use TDT_HOME-aware shared loading.

#### Scenario: CLI startup

- **WHEN** any command starts
- **THEN** it SHALL load TDT_HOME environment, harness config, and workspace config through supported loaders
- **AND** a missing required file SHALL identify the resolved path without exposing secrets

### Requirement: Ticket context commands

The CLI SHALL expose ticket context to query, update, append, validate, and export ticket context.

#### Scenario: Query context

- **WHEN** ticket context query is run with ticket ID and optional section
- **THEN** the CLI SHALL return the requested section or full context

#### Scenario: Update context

- **WHEN** ticket context update is run with section and body
- **THEN** the CLI SHALL update the section and confirm

#### Scenario: Validate context

- **WHEN** ticket context validate is run
- **THEN** the CLI SHALL return validation status with missing required sections

#### Scenario: Export context

- **WHEN** ticket context export is run with format option
- **THEN** the CLI SHALL export the full context in the requested format

### Requirement: Observability commands

The CLI SHALL expose observe status, observe export, observe memory, and observe audit-log.

#### Scenario: Status

- **WHEN** observe status is run with format option
- **THEN** the CLI SHALL return the latest observability snapshot

#### Scenario: Export

- **WHEN** observe export is run with time range and format
- **THEN** the CLI SHALL export the requested telemetry

#### Scenario: Memory

- **WHEN** observe memory is run
- **THEN** the CLI SHALL return memory summary with retention policy, size, and session list

#### Scenario: Audit log

- **WHEN** observe audit-log is run with optional filters
- **THEN** the CLI SHALL return filtered audit entries

### Requirement: Multi-variant support

The CLI SHALL support variant selection to choose agent type such as researcher, coder, or planner.

#### Scenario: Variant selection

- **WHEN** variant option is provided
- **THEN** the CLI SHALL load the variant-specific skill set and behavioral configuration
- **AND** all commands SHALL operate within the variant capability scope

### Requirement: Workspace commands

The CLI SHALL expose workspace init, workspace status, and workspace doctor.

#### Scenario: Init

- **WHEN** workspace init is run
- **THEN** the CLI SHALL initialize a workspace with configuration

#### Scenario: Status

- **WHEN** workspace status is run
- **THEN** the CLI SHALL report workspace health and configuration

#### Scenario: Doctor

- **WHEN** workspace doctor is run
- **THEN** the CLI SHALL validate workspace configuration and report issues
