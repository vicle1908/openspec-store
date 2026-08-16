# agent-harness-components Specification

## Purpose
Defines the core components of agent-harness: workflow runner, artifact store, checkpoint system, and gate decisions.

## Requirements

### Requirement: Workflow runner

The workflow runner SHALL execute stages, manage state, and handle interrupts.

#### Scenario: Stage execution

- **WHEN** a stage is executed
- **THEN** the runner SHALL load the current state from checkpoints
- **AND** execute the stage with the appropriate agent
- **AND** persist the artifact to the artifact store
- **AND** save the new state to checkpoints

#### Scenario: Interrupt handling

- **WHEN** a gate requires human approval
- **THEN** the runner SHALL create an interrupt
- **AND** wait for human decision
- **AND** record the decision in the gate decision store

### Requirement: Artifact store

The artifact store SHALL manage versioned artifact envelopes with integrity verification.

#### Scenario: Artifact commit

- **WHEN** an artifact is committed
- **THEN** it SHALL be written as a temporary file
- **AND** flushed to disk
- **AND** atomically renamed
- **AND** the containing directory SHALL be flushed
- **AND** the SHA-256 digest SHALL be verified

#### Scenario: Artifact verification

- **WHEN** an artifact is loaded
- **THEN** its SHA-256 digest SHALL be verified
- **AND** mismatch SHALL reject the artifact

### Requirement: Checkpoint system

The checkpoint system SHALL enable resume from any stage with full state recovery.

#### Scenario: Checkpoint save

- **WHEN** a stage completes
- **THEN** a checkpoint SHALL be saved with run_id, stage, artifact_digest, and state hash
- **AND** the checkpoint SHALL be persisted to PostgreSQL

#### Scenario: Checkpoint load

- **WHEN** a workflow is resumed
- **THEN** the latest checkpoint SHALL be loaded
- **AND** its integrity SHALL be verified
- **AND** the state SHALL be restored

### Requirement: Gate decisions

The gate system SHALL manage human approval points and decisions.

#### Scenario: Gate interrupt

- **WHEN** a gate requires human approval
- **THEN** an interrupt SHALL be created with the gate requirements
- **AND** the interrupt SHALL be sent to the configured approver

#### Scenario: Decision recording

- **WHEN** a gate decision is made
- **THEN** it SHALL be recorded with run_id, stage, decision_id, approver, decision, reason, nonce, and timestamp
- **AND** the decision SHALL be immutable

### Requirement: Symlink-safe artifact root validation

`validate_artifact_root()` SHALL scan user-supplied path components for symlinks before canonical resolution. The validation SHALL reject paths where any component is a symlink, using the expanded (not resolved) path.

#### Scenario: Symlink component rejected

- **GIVEN** an artifact root path containing a symlink component
- **WHEN** `validate_artifact_root()` is called
- **THEN** a `ValueError` SHALL be raised identifying the symlink component

#### Scenario: Direct symlink root rejected

- **GIVEN** the artifact root itself is a symlink
- **WHEN** `validate_artifact_root()` is called
- **THEN** a `ValueError` SHALL be raised

#### Scenario: Clean path accepted

- **GIVEN** an artifact root path with no symlink components
- **WHEN** `validate_artifact_root()` is called
- **THEN** the canonical resolved path SHALL be returned

### Requirement: Deny-only authority profile

AuthorityConfig fields `allowed_shell`, `allowed_code_execution`, `allowed_external_mutation`, and `allowed_source_write` SHALL accept only `False`. Construction with `True`, `1`, `"true"`, `"1"`, or any other coercion candidate SHALL raise `ValidationError`. Post-construction assignment SHALL also be rejected. Nested `HarnessConfig(authority={...})` overlays containing truthy values SHALL fail validation.

#### Scenario: Literal False is accepted

- **GIVEN** an `AuthorityConfig` instance with all deny-only fields set to `False`
- **WHEN** the instance is constructed
- **THEN** construction SHALL succeed

#### Scenario: Truthy value rejected at construction

- **GIVEN** a deny-only authority field
- **WHEN** `AuthorityConfig` is constructed with value `True`, `1`, `"true"`, or `"1"` for that field
- **THEN** a `ValidationError` SHALL be raised

#### Scenario: Truthy value rejected in nested overlay

- **GIVEN** a `HarnessConfig` with an authority overlay
- **WHEN** the overlay contains `allowed_shell: true`
- **THEN** a `ValidationError` SHALL be raised during nested construction

#### Scenario: Post-construction assignment rejected

- **GIVEN** an `AuthorityConfig` instance with all deny-only fields set to `False`
- **WHEN** post-construction assignment `allowed_shell = True` is attempted
- **THEN** a `ValidationError` SHALL be raised and the value SHALL remain `False`

#### Scenario: Structural read-only boundaries (Jira, GitLab)

- **GIVEN** the `JiraTool` class definition
- **WHEN** inspecting its public method set
- **THEN** it SHALL expose only `get_ticket`, `search`, and `get_links` — no mutation methods

- **GIVEN** the `read_only_targets` field in `AuthorityConfig`
- **WHEN** `"jira"` and `"gitlab"` are present in the list
- **THEN** structural safety is enforced by code design, not by dedicated config fields

### Requirement: Deny-only stage composition policy

`StageCompositionContext` SHALL reject caller-supplied `CapabilityAuthorityPolicy` values that contain any filesystem roots, shell commands, network hosts, runtime-authoring roots, authority grants, or disabled audit mode. The default empty policy with audit enabled SHALL remain accepted.

#### Scenario: Permissive capability policy rejected

- **GIVEN** a stage composition context with a non-empty filesystem, shell, network, runtime-authoring, or grant policy
- **WHEN** the context is constructed
- **THEN** construction SHALL raise `ValueError` identifying the deny-only boundary

#### Scenario: Disabled audit policy rejected

- **GIVEN** a stage composition context with `audit_enabled=False`
- **WHEN** the context is constructed
- **THEN** construction SHALL raise `ValueError`

#### Scenario: Default capability policy accepted

- **GIVEN** a stage composition context with the default capability policy
- **WHEN** the context is constructed
- **THEN** construction SHALL succeed
