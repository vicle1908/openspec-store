# agent-cli-inventory-coverage Specification

## Purpose
Defines the reconciliation contract between the agent CLIs a maintenance runner declares it
covers and the agent CLIs actually installed, so that no installed tool is silently ignored,
silently updated without a declaration, or removed for being undeclared. Every installed CLI is
retained; coverage governs update handling, not tool retention.

## Requirements

### Requirement: Covered set and installed set are reconciled

The workstation maintenance runner SHALL reconcile its declared covered set of agent CLIs
against the agent CLIs actually installed, and SHALL report every installed agent CLI that is
absent from the declared set. Each installed agent CLI SHALL be either covered with a scriptable
update verb or explicitly declared uncovered, and an undeclared CLI MUST NOT be treated as
removable.

#### Scenario: Installed CLI is absent from the declared set

- **WHEN** an agent CLI is installed and executable on the path and does not appear in either
  the covered set or the declared uncovered set
- **THEN** the runner SHALL report it as an undeclared installation
- **AND** the report SHALL distinguish it from a CLI that is declared uncovered

#### Scenario: Every installed CLI is declared

- **WHEN** every installed agent CLI appears in either the covered set or the declared uncovered
  set
- **THEN** the runner SHALL report no undeclared installations

#### Scenario: Undeclared CLI is never removed

- **WHEN** an installed agent CLI is undeclared
- **THEN** the runner MUST NOT uninstall, disable, or remove it
- **AND** it SHALL remain available on the path unchanged

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

### Requirement: Each CLI's installation source is recorded

For every declared agent CLI the inventory SHALL record its installation source — the package
manager that owns it, an ecosystem package manager, or a vendor download — together with the
update verb appropriate to that source, so that a CLI is never updated through a manager that
does not own it.

#### Scenario: Update verb matches the owning source

- **WHEN** a declared agent CLI is owned by a package manager
- **THEN** its recorded update verb SHALL be that package manager's upgrade path
- **AND** the runner MUST NOT apply an ecosystem package manager's update verb to it

#### Scenario: Source cannot be determined

- **WHEN** an installed agent CLI's owning source cannot be determined from its resolved path
- **THEN** the inventory SHALL record the source as unknown with the resolved path
- **AND** the CLI SHALL be treated as uncovered rather than updated through a guessed manager

#### Scenario: Vendor-downloaded CLI is recorded as such

- **WHEN** an installed agent CLI resolves to a vendor download outside every sanctioned
  location
- **THEN** the inventory SHALL record it as a vendor download with its path
- **AND** the report SHALL note that no package manager governs its version
