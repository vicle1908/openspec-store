## Purpose

Define how TDT repairs legacy OpenSpec main-spec structure while preserving
normative behavior, reviewability, and planning-root topology.

## ADDED Requirements

### Requirement: Remediation begins from an exact machine-readable baseline

The remediation SHALL record the invalid main-spec ids, error classes, file
hashes, requirement headers, and scenario headers before editing an affected
batch.

#### Scenario: Baseline is captured
- **WHEN** a remediation batch is ready to start
- **THEN** its affected files and current strict-validation findings SHALL be recorded
- **AND** requirement and scenario inventories SHALL be available for the post-edit comparison

#### Scenario: Baseline differs from the approved set
- **WHEN** a targeted file, finding, or semantic inventory differs from the approved baseline
- **THEN** that batch MUST stop before editing
- **AND** the difference SHALL be reviewed and the plan updated explicitly

### Requirement: Purpose repairs preserve normative meaning

Each added Purpose section SHALL describe the capability represented by existing
requirements and MUST NOT add normative behavior, placeholders, volatile system
details, or unsupported claims.

#### Scenario: Evidence supports Purpose text
- **WHEN** an affected spec lacks a Purpose section
- **THEN** Purpose wording SHALL be derived from its current requirements, archived OpenSpec history, or canonical repository documentation
- **AND** the evidence source SHALL be recorded for review

#### Scenario: Evidence is insufficient
- **WHEN** no authoritative source supports capability-specific Purpose text
- **THEN** the spec MUST remain unmodified
- **AND** it SHALL be escalated rather than filled with generic or speculative text

### Requirement: Structural repairs retain requirements and scenarios

The remediation SHALL preserve existing requirement names, descriptions,
scenario meaning, and ordering except for explicitly approved structural
normalization.

#### Scenario: Missing Requirements container is repaired
- **WHEN** an existing spec lacks `## Requirements` but contains requirement blocks
- **THEN** the repair SHALL place those blocks under the required container
- **AND** it MUST NOT rewrite their normative content

#### Scenario: Malformed scenarios are repaired
- **WHEN** existing scenario content does not use valid level-4 headers and WHEN/THEN bullets
- **THEN** the repair SHALL normalize only the scenario structure
- **AND** it SHALL preserve the scenario's conditions, outcomes, order, and parent requirement

#### Scenario: Unexpected semantic drift is detected
- **WHEN** a post-edit inventory loses or renames an unapproved requirement or scenario
- **THEN** the batch MUST fail and be rolled back before another batch begins

### Requirement: Remediation is bounded and independently reversible

The 66-file baseline SHALL be partitioned into explicit, non-overlapping batches,
and each batch SHALL pass its own review and validation gate before the next
batch starts.

#### Scenario: Batch completes successfully
- **WHEN** every targeted file passes strict validation and its semantic inventory matches
- **THEN** the batch MAY be marked complete
- **AND** the remaining invalid-id set SHALL equal the prior set minus only that batch's repaired ids

#### Scenario: Batch validation fails
- **WHEN** a targeted file remains invalid, a new error appears, or an inventory differs unexpectedly
- **THEN** work MUST stop before the next batch
- **AND** rollback SHALL affect only the current batch without destructive Git operations

### Requirement: Final validation establishes a green main-spec baseline

Completion SHALL require every active change and every main spec to pass strict
validation under the recorded OpenSpec version, with no remaining legacy failure
or new error class.

#### Scenario: Remediation is complete
- **WHEN** all batches have passed their local gates
- **THEN** all-spec and full-root strict validation SHALL report zero invalid main specs
- **AND** the machine-readable result SHALL be retained as the new comparison baseline

#### Scenario: A failure remains
- **WHEN** full validation reports any invalid main spec or a newly failing active change
- **THEN** the remediation MUST remain incomplete
- **AND** archive, commit, and push SHALL remain outside the completion claim

### Requirement: Planning topology remains unchanged

The remediation MUST preserve every existing capability directory and MUST NOT
introduce store, workset, default-store, nested-spec, or symlink topology changes.

#### Scenario: File placement is reviewed
- **WHEN** the final diff is inspected
- **THEN** each repaired main spec SHALL remain at its original capability path
- **AND** no planning topology metadata or symlink target SHALL have changed
