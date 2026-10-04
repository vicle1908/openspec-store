# Spec Delta

## ADDED Requirements

### Requirement: Executed maintenance scripts are version controlled

Every script that a scheduled job executes from the workstation scripts directory SHALL have a copy recorded under version control in the OpenSpec store, so each script has revision history and a recovery path.

#### Scenario: A scheduled script has a recorded copy
- **WHEN** a LaunchAgent executes a script from `~/Developer/scripts/`
- **THEN** a copy of that script SHALL exist under version control in the store's `scripts/` tree
- **AND** the recorded copy SHALL be retrievable from the store's history

#### Scenario: A script executed with no recorded copy is reported
- **WHEN** a script is executed from the workstation scripts directory and no recorded copy exists in the store
- **THEN** the discrepancy SHALL be reported
- **AND** the script SHALL be named in the report

#### Scenario: History survives loss of the executed copy
- **WHEN** the executed copy of a version-controlled script is lost or corrupted
- **THEN** its content SHALL be recoverable from the recorded copy without relying on any other backup

### Requirement: Each script has one declared source of truth

For each script that exists both as an executed copy and a recorded copy, the relationship SHALL be declared explicitly, and the copies SHALL NOT be treated as independently editable.

#### Scenario: The source of truth is declared
- **WHEN** a script exists as both an executed copy and a recorded copy
- **THEN** which of the two is authoritative SHALL be stated, rather than left implicit
- **AND** the declared relationship SHALL be discoverable without inspecting file contents

#### Scenario: Copies are not left as unrelated duplicates
- **WHEN** a script is present as two separate files that are byte-identical
- **THEN** the duplication SHALL be resolved so the relationship is declared
- **AND** the two copies SHALL NOT remain independently editable with no recorded link

### Requirement: Installed-copy drift is detected and reported

The scheduled maintenance job SHALL compare the executed copy of a version-controlled script against its recorded copy and SHALL report any difference.

#### Scenario: Drift is reported
- **WHEN** the executed copy of a script differs in content from its recorded copy
- **THEN** the maintenance job SHALL report that script as drifted
- **AND** the report SHALL name the script and indicate which copy differs

#### Scenario: Drift is a reported degradation, not a silent success
- **WHEN** drift is detected during a maintenance run
- **THEN** the run SHALL report a degraded outcome
- **AND** the run SHALL NOT conclude reporting that the scripts are consistent

#### Scenario: Agreement is reported
- **WHEN** the executed and recorded copies of every checked script agree
- **THEN** the maintenance job SHALL report that no script drift was found

#### Scenario: Drift detection does not rewrite either copy
- **WHEN** drift is detected
- **THEN** the maintenance job SHALL NOT modify the executed copy or the recorded copy
- **AND** reconciling the difference SHALL require a deliberate change

### Requirement: Inventory approval digest accompanies its inventory

When a recorded inventory of repositories differs from the inventory its approval digest was computed over, the digest SHALL be regenerated in the same change, so the recorded pair remains internally consistent.

#### Scenario: A reconciled inventory carries a matching digest
- **WHEN** a recorded repository inventory is brought in line with the executed inventory
- **THEN** the recorded approval digest SHALL be recomputed over the reconciled inventory
- **AND** the recorded digest SHALL match the recorded inventory

#### Scenario: A mismatched pair is reported
- **WHEN** a recorded inventory's content does not hash to the digest recorded beside it
- **THEN** the pair SHALL be reported as inconsistent
- **AND** the affected inventory SHALL be named in the report
