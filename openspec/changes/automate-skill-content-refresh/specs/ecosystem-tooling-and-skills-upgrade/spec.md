# Spec Delta

## ADDED Requirements

### Requirement: Scheduled upstream skill content refresh

The daily maintenance job SHALL refresh upstream-sourced skill content in the canonical store as a scheduled stage, so that content currency does not depend on a human running the skills CLI by hand.

#### Scenario: Upstream content is refreshed on schedule
- **WHEN** the daily maintenance job runs and upstream-sourced skills have newer content available
- **THEN** it SHALL pull the updated content into the canonical store without interactive prompts
- **AND** the refreshed entries SHALL resolve to readable `SKILL.md` content

#### Scenario: Refresh runs after link parity and before store validation
- **WHEN** the daily maintenance job executes its stages
- **THEN** the content refresh SHALL run after the skills parity check
- **AND** it SHALL run before the OpenSpec store validation gate

#### Scenario: Local skills are not refreshed from upstream
- **WHEN** a skill in the canonical store has no declared upstream source
- **THEN** the refresh SHALL NOT modify or remove that skill

### Requirement: Skill content refresh outcomes are reported

The refresh stage SHALL report a per-run outcome distinguishing refresh-available, refreshed, already-current, path-ambiguous, and refresh-failed, and SHALL record the outcome in the maintenance log.

#### Scenario: Outcome summary is recorded
- **WHEN** the refresh stage completes
- **THEN** the maintenance log SHALL record how many entries were refreshed, already current, skipped as path-ambiguous, and failed

#### Scenario: Drift is visible without application
- **WHEN** the refresh stage detects that upstream content differs from the local canonical store
- **THEN** it SHALL report that entries were refreshed
- **AND** the report SHALL be distinguishable from a run where no entry changed

### Requirement: Drift is observable before content is replaced

The refresh stage SHALL determine whether upstream content differs from the canonical store before it replaces any skill content, and SHALL report drift availability independently of whether that content is then applied.

#### Scenario: Drift check does not mutate
- **WHEN** the refresh stage evaluates whether any upstream content has changed
- **THEN** it SHALL report drift availability before any skill content is replaced

#### Scenario: Unchanged content is reported as already current
- **WHEN** the refresh stage runs and no upstream content differs from the canonical store
- **THEN** it SHALL report that no entry changed
- **AND** the reported outcome SHALL be distinguishable from a run that replaced content

### Requirement: Path-ambiguous upstream skills are informational

When upstream publishes the same skill at multiple paths, the refresh SHALL classify the resulting skip as an informational condition and SHALL NOT treat it as stale, broken, or failing.

#### Scenario: Multi-path upstream entry is reported as informational
- **WHEN** upstream publishes one skill at more than one path and the refresh tool declines to choose between them
- **THEN** the refresh SHALL report the entry as path-ambiguous
- **AND** the run SHALL NOT classify that entry as stale, broken, or failed

#### Scenario: Path-ambiguous entry does not fail the maintenance run
- **WHEN** the only unrefreshed entry in a run is path-ambiguous
- **THEN** the maintenance run SHALL still be able to conclude successfully

### Requirement: Refresh failures degrade without masking

An unreachable upstream or failed content refresh SHALL be reported as a degradation and SHALL NOT be reported as a silent success.

#### Scenario: Unreachable upstream is reported
- **WHEN** upstream content cannot be reached during the scheduled refresh
- **THEN** the refresh SHALL report the failure for the affected entries
- **AND** the maintenance run SHALL NOT report the refresh stage as fully successful

#### Scenario: A failed refresh does not abort unrelated stages
- **WHEN** the refresh stage fails for one or more entries
- **THEN** the remaining maintenance stages SHALL still execute

#### Scenario: Transient network failure is distinguishable from drift
- **WHEN** the refresh fails because of a network condition rather than a content difference
- **THEN** the reported outcome SHALL identify a refresh failure rather than a refreshed or already-current result

### Requirement: Refresh is time-bounded

Each refresh invocation SHALL be time-bounded, and a refresh that exceeds its bound SHALL be reported as a refresh failure rather than being allowed to run indefinitely.

#### Scenario: A hung refresh is abandoned and reported
- **WHEN** a refresh invocation exceeds its configured time bound
- **THEN** it SHALL be terminated
- **AND** its outcome SHALL be reported as a refresh failure

#### Scenario: A hung refresh does not stall the maintenance run
- **WHEN** a refresh invocation is terminated for exceeding its bound
- **THEN** the remaining maintenance stages SHALL still execute

### Requirement: Coding agent CLI coverage reflects installed agents

The coding agent CLI stage SHALL update every agent CLI in the stage's declared covered set that is installed, and SHALL report both the covered set and any installed agent CLI outside it.

#### Scenario: All installed agent CLIs are updated
- **WHEN** the coding agent CLI stage runs and more than one agent CLI from the covered set is installed
- **THEN** each installed agent CLI in the covered set SHALL be updated by the stage

#### Scenario: The covered set is declared
- **WHEN** the coding agent CLI stage runs
- **THEN** it SHALL report which agent CLIs the covered set contains
- **AND** the covered set SHALL NOT be inferred only from what happens to be installed

#### Scenario: Uncovered agents are reported
- **WHEN** an installed agent CLI is not in the covered set
- **THEN** the stage SHALL report it as uncovered

#### Scenario: Absent agents are skipped without error
- **WHEN** an agent CLI in the covered set is not installed
- **THEN** the stage SHALL skip it without reporting a failure

### Requirement: A zero-exit updater that reports an error is a failure

An agent CLI update that exits with a success status while reporting an error SHALL be reported as a failure rather than as a successful update.

#### Scenario: Error output with a zero exit is reported as failure
- **WHEN** an agent CLI updater exits zero and its output reports an error
- **THEN** the stage SHALL report that agent as failed
- **AND** the run SHALL report a degraded agent-update outcome

### Requirement: Refresh lockfile integrity is not asserted from an internal digest

The refresh stage SHALL NOT treat the lockfile lock digest as an authoritative drift signal, and SHALL determine whether content changed from the pulled content itself.

#### Scenario: Internal digest does not gate the refresh
- **WHEN** the refresh stage evaluates whether an entry needs refreshing
- **THEN** it SHALL NOT compare the lockfile lock digest against a locally computed content digest as its drift signal

#### Scenario: Content comparison uses the pulled content
- **WHEN** the refresh stage determines whether an entry changed
- **THEN** it SHALL base that determination on the content the refresh produced
