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
does not own it. The recorded update verb SHALL correspond to the CLI's elected version authority,
preferring native updaters where supported for that installation, verified against active
executable provenance and prefix scope on the system path. The runner MUST NOT apply an
uncoordinated manager's upgrade path where that manager does not own the CLI's version.

#### Scenario: Update verb matches the owning source

- **WHEN** a declared agent CLI is owned by a package manager
- **THEN** its recorded update verb SHALL be that package manager's upgrade path or a compatible
  tool-native command that delegates to that package manager for the active installation
- **AND** the runner MUST NOT apply an uncoordinated ecosystem package manager's update verb to it

#### Scenario: Update verb follows the version authority

- **WHEN** a declared agent CLI holds version authority through an internal self-updater
- **THEN** its recorded update verb SHALL be its verified tool-native update command targeting its
  authoritative installation location
- **AND** the runner MUST NOT apply an uncoordinated manager upgrade path that reverts or conflicts
  with the tool's version

#### Scenario: Source cannot be determined

- **WHEN** an installed agent CLI's owning source cannot be determined from its resolved path
- **THEN** the inventory SHALL record the source as unknown with the resolved path
- **AND** the CLI SHALL be treated as uncovered rather than updated through a guessed manager

#### Scenario: Vendor-downloaded CLI is recorded as such

- **WHEN** an installed agent CLI resolves to a vendor download outside every sanctioned location
- **THEN** the inventory SHALL record it as a vendor download with its path
- **AND** the report SHALL note that no package manager governs its version

#### Scenario: Active executable provenance and wrapper chain determine source identity

- **WHEN** an agent CLI executable on `$PATH` resolves through symlinks or wrapper scripts, such as
  `~/.qoder/entry/qoder`
- **THEN** the inventory SHALL determine source identity and update verb from the underlying
  installation target and executable provenance
- **AND** display labels or symlink container directories MUST NOT override physical target identity

### Requirement: Coverage reporting distinguishes drift from coverage findings

The maintenance runner SHALL distinguish version-authority drift findings, undeclared-coverage findings, explicitly declared uncovered status, update execution failures, and reporter measurement failures into independent reporting classes. A declared uncovered status SHALL NOT preclude or mask the reporting of coexisting drift, failure, or update-gap findings. Valid reports matching the documented exit contract SHALL be distinguished from reporter crashes or incomplete output.

#### Scenario: Drift is reported distinctly alongside coverage status

- **WHEN** a covered agent CLI possesses an elected native self-updater that conflicts with a
  configured or scheduled independent package manager
- **THEN** the runner SHALL report a drift finding naming the CLI, its update verb, and the
  conflicting manager
- **AND** the finding SHALL co-exist with its coverage declaration without masking or altering it

#### Scenario: Declared uncovered tools coexist with independent status checks

- **WHEN** an installed agent CLI is explicitly declared uncovered because it is governed by an
  earlier pipeline stage or maintained manually
- **THEN** the runner SHALL record it as declared uncovered, satisfying the undeclared-coverage check
- **AND** the declared uncovered status SHALL NOT suppress any independently detected version drift,
  execution failure, or missing update-path findings for that tool

#### Scenario: Reporter domain findings are distinguished from execution failures

- **WHEN** a coverage reconciliation reporter completes execution with exit code 1 and outputs a
  complete, valid report matching the documented contract for undeclared CLI findings
- **THEN** the runner SHALL record the undeclared CLI count and findings from the report
- **AND** the runner MUST NOT classify the reconciliation stage as a measurement failure or crash

#### Scenario: Reporter crash, timeout, or malformed output degrades measurement

- **WHEN** a coverage reconciliation reporter crashes, times out, or produces incomplete or malformed
  output, regardless of whether its exit status is code 1 or another nonzero value
- **THEN** the runner SHALL set a measurement failure flag indicating coverage status is unknown and
  degraded
- **AND** the runner MUST NOT claim healthy zero findings for that stage, while preserving any
  independently reported findings from other stages

#### Scenario: Update execution failure is reported independently

- **WHEN** a covered tool's update command times out or returns a failing execution outcome
- **THEN** the runner SHALL record an update execution failure for that tool
- **AND** the failure SHALL NOT be reported as an undeclared-coverage defect

### Requirement: Every declared CLI has an authoritative handling declaration

Coverage SHALL require every declared agent CLI to have an authoritative handling declaration. Covered CLIs SHALL have a verified automated update path, preferring a compatible native updater or delegator and accepting a supported manager path where native updaters are absent. Uncovered CLIs SHALL declare an explicit governing channel or manual status. The agent stage MUST NOT update uncovered CLIs, and all stages MUST NOT update undeclared CLIs. Gaps SHALL be reported independently.

#### Scenario: Declared CLI with compatible native updater

- **WHEN** a declared agent CLI provides a compatible tool-native update command or compatible
  manager delegation
- **THEN** that command SHALL be recorded as its covered update path
- **AND** the runner SHALL invoke it during apply mode as a backstop

#### Scenario: Declared CLI without compatible native updater uses manager authority

- **WHEN** a declared agent CLI has no compatible tool-native update command but is managed by
  a supported package manager
- **THEN** the package manager's upgrade command SHALL be recorded as its update path
- **AND** the runner SHALL NOT report the tool as lacking an update path

#### Scenario: Explicitly uncovered CLI retains authoritative non-execution in agent stage

- **WHEN** an installed agent CLI is declared in the known uncovered set with an explicit channel
  or manual handling status
- **THEN** the runner SHALL record it as declared uncovered
- **AND** the runner MUST NOT invoke an update for it during the agent-CLI coverage stage
- **AND** earlier pipeline stages MAY update it only if governed by declared verified authority and scope

#### Scenario: Undeclared CLI is protected from unmanaged updates across all stages

- **WHEN** an installed agent CLI is neither declared covered nor declared uncovered
- **THEN** the runner SHALL report it as an undeclared installation defect
- **AND** all pipeline stages MUST NOT invoke any update or removal command on that CLI

#### Scenario: Apply mode executes backstop with verified outcome

- **WHEN** the runner invokes the declared update verb for an already current covered CLI
- **THEN** the tool SHALL complete with an observable successful outcome
- **AND** the active executable on the path SHALL be verified current against the elected
  channel version within its active installation root
