# Spec Delta

## ADDED Requirements

### Requirement: Covered updater declarations match the supported registry
Every covered CLI declaration SHALL match a supported updater entry for its resolved installation source, authority, and target scope. A declaration that is syntactically nonempty but unsupported, misaligned, or owned by another manager MUST be reported as an update-path defect and MUST NOT be executed.

#### Scenario: Manager command targets another authority
- **WHEN** a covered CLI's declared command uses a package manager that does not own the active installation
- **THEN** the report SHALL identify the owning authority and the incompatible command
- **AND** the runner MUST suppress that command

#### Scenario: Unknown source is declared covered
- **WHEN** active provenance cannot establish the owning source or target scope
- **THEN** the CLI SHALL be treated as unsupported or uncovered for automated updates
- **AND** the report SHALL preserve the evidence gap

### Requirement: Manager deny filters normalize package identities
Before applying a manager-specific deny roster, the runner SHALL normalize package identities so that scoped names and version-suffixed output from package-manager queries compare by package identity rather than by display formatting.

#### Scenario: npm outdated emits a version suffix
- **WHEN** a denied package is returned as `@scope/package@version`
- **THEN** normalization SHALL match the denied identity `@scope/package`
- **AND** the package MUST NOT be passed to the npm mutation command

#### Scenario: Independent npm package remains eligible
- **WHEN** an npm package is not present in the normalized deny roster and has a valid declared authority
- **THEN** it MAY remain eligible for the npm stage
- **AND** denial of another package MUST NOT suppress it

### Requirement: Post-update reporting separates idempotence from channel currency
The agent stage SHALL report local execution outcome, whether the active version changed, and release-channel currency as separate facts. An unchanged local version MUST be reported as idempotent or unmodified, but SHALL be labeled currency unknown unless a supported channel comparison verified that it is current.

#### Scenario: Update succeeds without a channel comparison
- **WHEN** an update command exits successfully and the before and after versions are equal without a channel check
- **THEN** the report SHALL identify the execution as successful and the local version as unchanged
- **AND** it MUST report channel currency as unverified or unknown, never as current

#### Scenario: Channel comparison proves current
- **WHEN** an authorized updater succeeds and a supported channel comparison matches the active version
- **THEN** the report MAY mark channel currency current
- **AND** it SHALL retain the separate local mutation result

#### Scenario: Updater returns success while emitting an error
- **WHEN** an updater exits zero but emits a recognized error or failure diagnostic
- **THEN** the runner SHALL record an update execution failure
- **AND** it MUST NOT classify the invocation as a successful current result

### Requirement: Covered and uncovered rosters share one authoritative classification
The inventory, coverage reporter, runbook, and maintenance runner SHALL derive each CLI's covered, uncovered, source, authority, and updater classification from one consistent declaration model. A tool moved to uncovered status because its updater is invalid or failed SHALL not retain a contradictory covered native updater in inventory output.

#### Scenario: Kilo has no currently accepted path
- **WHEN** Kilo is declared uncovered because its previous updater path is invalid or unsupported
- **THEN** all reports SHALL show the same uncovered or manager-governed status
- **AND** no agent-stage native update command SHALL execute for Kilo

#### Scenario: A supported path is restored
- **WHEN** a verified supported updater and source mapping are added for a CLI
- **THEN** the covered status, command, source, and pipeline eligibility SHALL change together
- **AND** the next audit SHALL not report contradictory classifications
