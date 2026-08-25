# workspace-artifact-retention-policy Specification

## Purpose

Provide a reviewed workspace retention contract so cleanup decisions separate safe caches, active indexes, persistent runtime state, and retained evidence instead of treating them as one disposable class.

## Requirements

### Requirement: Retention classes and states

Every retained workspace path SHALL be classified into exactly one reviewed retention class and one policy state.

Retention classes SHALL include:

- active index state
- generated index or cache
- tracked permanent fixture
- temporary or ephemeral test fixture
- runtime state or database
- retained evidence or report
- retained rollback or snapshot
- operator-owned preserved file

Policy states SHALL be `PROTECTED`, `REVIEW_REQUIRED`, `RECLAIMABLE`, or `RECLAIMED`.

#### Scenario: Path belongs to multiple owners

- **WHEN** a path is used both as generated index output and as retained evidence
- **THEN** the classification SHALL use the most protective applicable class and state
- **AND** the inventory SHALL record all ownership signals

#### Scenario: Tracked permanent fixture

- **WHEN** a fixture is tracked by a repository or referenced by a published test contract
- **THEN** it SHALL be classified as a tracked permanent fixture
- **AND** it SHALL remain `PROTECTED` unless the owning repository changes its contract

#### Scenario: Ephemeral fixture

- **WHEN** a fixture is untracked, explicitly disposable, and has no active test, evidence, or runtime owner
- **THEN** it MAY be `REVIEW_REQUIRED` or `RECLAIMABLE` after review evidence
- **AND** age or naming alone SHALL NOT establish reclaimability

### Requirement: Protected retention state

The following classes SHALL remain `PROTECTED` indefinitely unless a separate reviewed policy authorizes later reclamation:

- active index state
- runtime state or database
- retained evidence or report
- retained rollback or snapshot
- operator-owned preserved file
- tracked permanent fixture

#### Scenario: Active index owner exists

- **WHEN** a path is owned by an approved index refresh contract or active watcher
- **THEN** the path SHALL be classified as active index state
- **AND** cleanup proposals SHALL NOT remove or relocate it

#### Scenario: Runtime ownership uncertain

- **WHEN** runtime ownership cannot be confirmed
- **THEN** the path SHALL remain `PROTECTED` or `REVIEW_REQUIRED`
- **AND** the inventory SHALL report the uncertain owner as `UNKNOWN`

#### Scenario: Active or rollback evidence

- **WHEN** evidence or rollback artifacts are referenced by an active change, incident, release, or recovery procedure
- **THEN** they SHALL remain `PROTECTED`
- **AND** they SHALL not be superseded without an explicit replacement reference and owner approval

### Requirement: Candidate reclamation only after review

Generated index or cache state and temporary or ephemeral test fixtures SHALL become review candidates only after a separate review record proves the item is not referenced by current index contracts, active processes, workflows, or evidence owners. Cleanup and retention workflows SHALL classify the item as a review candidate, not as an approved deletion target.

#### Scenario: Candidate is referenced by an index owner

- **WHEN** a generated path is still covered by approved refresh or watcher ownership
- **THEN** the item SHALL remain `PROTECTED`
- **AND** it SHALL NOT be listed as a reclamation candidate

#### Scenario: Candidate has no current owner

- **WHEN** a generated path has no active index, process, or evidence owner
- **THEN** the retention policy MAY classify it as `RECLAIMABLE`
- **AND** it SHALL record the basis, provenance, and required re-generation behavior before approval

### Requirement: Retention inventory

A reviewed retention inventory SHALL be stored at `~/Developer/.workspace-retention/retention-inventory.json` and SHALL record for each path: canonical path, class, policy state, current owner, provenance, justification, last reference or observation, candidate status, and review metadata.

#### Scenario: Inventory stability

- **WHEN** the same workspace is rescanned without material changes
- **THEN** the retention inventory SHALL produce stable path membership and stable classifications
- **AND** it SHALL not recommend deletions or moves on its own

#### Scenario: Inventory provenance is stale

- **WHEN** an inventory entry references an outdated repository revision, missing owner, or stale evidence timestamp
- **THEN** the entry SHALL become `REVIEW_REQUIRED`
- **AND** cleanup SHALL not treat it as `RECLAIMABLE`

### Requirement: Cleanup consumes retention policy

Workspace cleanup workflows SHALL read the retention inventory and treat `PROTECTED` classes and states as exclusion lists. Cleanup SHALL NOT delete or relocate a protected path unless a separate approved retirement action exists that supersedes the retention record.

#### Scenario: Cleanup sees protected evidence

- **WHEN** a cleanup workflow inspects a retained report, rollback snapshot, permanent fixture, or active index path
- **THEN** it SHALL skip the path
- **AND** it SHALL record the protected-class and owner reason in the cleanup manifest

#### Scenario: Cleanup encounters a candidate

- **WHEN** a cleanup workflow sees a `RECLAIMABLE` candidate
- **THEN** it MAY propose the candidate for operator review
- **AND** it SHALL NOT delete the item without the explicit approved action
