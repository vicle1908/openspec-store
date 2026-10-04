# Spec Delta

## MODIFIED Requirements

### Requirement: Each CLI's installation source is recorded

For every declared agent CLI the inventory SHALL record its installation source — the package
manager that owns it, an ecosystem package manager, or a vendor download — together with the
update verb appropriate to that source, so that a CLI is never updated through a manager that
does not own it. The recorded update verb SHALL be the verb belonging to the CLI's version
authority, and the runner MUST NOT apply a manager's upgrade path where that manager does not own
the CLI's version.

#### Scenario: Update verb matches the owning source

- **WHEN** a declared agent CLI is owned by a package manager
- **THEN** its recorded update verb SHALL be that package manager's upgrade path
- **AND** the runner MUST NOT apply an ecosystem package manager's update verb to it

#### Scenario: Update verb follows the version authority

- **WHEN** a declared agent CLI can update itself and therefore holds version authority,
  regardless of which manager installed it
- **THEN** its recorded update verb SHALL be its own self-update verb
- **AND** the runner MUST NOT apply the installing manager's upgrade path in a way that reverts
  the self-updated version

#### Scenario: Source cannot be determined

- **WHEN** an installed agent CLI's owning source cannot be determined from its resolved path
- **THEN** the inventory SHALL record the source as unknown with the resolved path
- **AND** the CLI SHALL be treated as uncovered rather than updated through a guessed manager

#### Scenario: Vendor-downloaded CLI is recorded as such

- **WHEN** an installed agent CLI resolves to a vendor download outside every sanctioned
  location
- **THEN** the inventory SHALL record it as a vendor download with its path
- **AND** the report SHALL note that no package manager governs its version

## ADDED Requirements

### Requirement: Coverage reporting distinguishes drift from coverage findings

Where a declared agent CLI's version authority conflicts with the manager that installed it, the
runner SHALL report that condition as a version-authority drift finding, distinct from an
undeclared-coverage finding and distinct from an update failure, so the three conditions are
never conflated.

#### Scenario: Drift is reported distinctly

- **WHEN** a covered agent CLI self-updates and its installing manager pins version
- **THEN** the runner SHALL report a drift finding naming the CLI, its self-update verb, and the
  pinning manager
- **AND** it MUST NOT report the CLI as undeclared or as an update failure

#### Scenario: A covered CLI is declared with a non-authority update verb

- **WHEN** a covered agent CLI's declared update verb belongs to a manager that does not own its
  version
- **THEN** the runner SHALL report the declaration as inconsistent with the CLI's version
  authority
- **AND** it SHALL name the self-update verb the declaration should use instead

#### Scenario: No drift exists

- **WHEN** no covered agent CLI's version authority conflicts with its installing manager
- **THEN** the runner SHALL report no drift findings

### Requirement: Every declared CLI has a declared update path

Coverage SHALL require every installed agent CLI to have a declared update path, which for a
self-updating CLI SHALL be its self-update verb. The runner SHALL invoke each declared update
path as a backstop on every run, and SHALL report a CLI that has no declared update path as
lacking one rather than silently leaving it unmanaged.

#### Scenario: Declared CLI has a self-update path

- **WHEN** a declared agent CLI provides a self-update verb
- **THEN** that verb SHALL be recorded as its declared update path
- **AND** the runner SHALL invoke it during the agent-CLI stage

#### Scenario: Declared CLI has no update path

- **WHEN** a declared agent CLI provides neither a self-update verb nor a native background
  auto-update
- **THEN** the runner SHALL report the CLI as having no available update path
- **AND** it MUST NOT resolve the gap by invoking a package manager's upgrade path

#### Scenario: Backstop run leaves current tools unchanged

- **WHEN** the runner invokes the declared update path of an already-current CLI
- **THEN** the CLI's version SHALL remain unchanged and the invocation SHALL succeed
- **AND** the run summary MUST NOT record an update failure for it
