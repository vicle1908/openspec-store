# Spec Delta

## Purpose

Defines the reconciliation contract between the agent CLIs a maintenance runner declares it
covers and the agent CLIs actually installed, so that an installed tool is never silently
ignored or updated without an explicit declaration.

## ADDED Requirements

### Requirement: Covered set and installed set are reconciled

The workstation maintenance runner SHALL reconcile its declared covered set of agent CLIs
against the agent CLIs actually installed, and SHALL report every installed agent CLI that is
absent from the declared set. Each installed agent CLI SHALL be either covered with a scriptable
update verb or explicitly declared uncovered.

#### Scenario: Installed CLI is absent from the declared set

- **WHEN** an agent CLI is installed and executable on the path and does not appear in either
  the covered set or the declared uncovered set
- **THEN** the runner SHALL report it as an undeclared installation
- **AND** the report SHALL distinguish it from a CLI that is declared uncovered

#### Scenario: Every installed CLI is declared

- **WHEN** every installed agent CLI appears in either the covered set or the declared uncovered
  set
- **THEN** the runner SHALL report no undeclared installations

### Requirement: Undeclared installations are reported, not silently updated

An agent CLI that is installed but undeclared MUST NOT be updated by the runner, and MUST NOT be
silently ignored. It SHALL be reported so the operator can declare it covered or uncovered.

#### Scenario: Undeclared CLI is left untouched

- **WHEN** the runner encounters an installed but undeclared agent CLI
- **THEN** it MUST NOT execute an update verb for that CLI
- **AND** it SHALL report the CLI's name and resolved path

#### Scenario: Declaring the CLI resolves the finding

- **WHEN** an undeclared agent CLI is added to the covered set or the declared uncovered set
- **THEN** the next run SHALL NOT report it as undeclared

### Requirement: Coverage declarations are authoritative and inspectable

The declared covered and uncovered sets SHALL be inspectable from the runner without executing
an update, and each covered entry SHALL name its binary, its label, and its update verb.

#### Scenario: Declared set is reported before any update

- **WHEN** the runner begins its agent-CLI stage
- **THEN** it SHALL report the declared covered set and the declared uncovered set before
  executing any update
- **AND** the reporting SHALL require no network access

#### Scenario: A covered updater fails

- **WHEN** a covered agent CLI's update verb fails or exceeds its time bound
- **THEN** the runner SHALL report that CLI as failed while continuing to report the remaining
  declared set
- **AND** the failure SHALL NOT be recorded as an undeclared-coverage finding
