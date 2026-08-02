# Agent Harness Workflow Specification

## Purpose

Define the modular planning workflow, approval gates, and bounded read-only authority.
## Requirements
### Requirement: Incremental stage modularization

The existing 12-stage planning behavior SHALL be modularized incrementally behind characterization tests rather than replaced in one rewrite.

#### Scenario: Extract one stage

- **WHEN** a stage is extracted
- **THEN** its input fields, output artifact, digest, validation/revision result, trace event, and next node SHALL match the characterization fixture

#### Scenario: Compatibility entry point

- **WHEN** an existing CLI or import path is used during migration
- **THEN** it SHALL delegate to the current composition root or emit an actionable migration error

### Requirement: One-target gate interrupts

Each human approval gate SHALL be a dedicated post-stage node that interrupts for exactly one continuation. Request identity, issued-at time, and expiry SHALL be derived from checkpointed run, thread, stage, artifact identity/digest, the artifact's timezone-aware UTC creation time, and configured TTL. Allowed routing and an explicit approver allowlist SHALL be preserved with the request. Native interrupt identity SHALL be bound through public graph state and SHALL NOT be regenerated or inferred during resume. The acting principal and decision audit time SHALL be supplied by the trusted runner boundary rather than accepted from user decision data.

#### Scenario: Gate re-execution

- **WHEN** LangGraph re-executes a dedicated gate node for the same pending request
- **THEN** the gate SHALL deterministically reproduce the same request identity, issued-at time, expiry time, artifact digest, allowed routing, and approver set from checkpointed inputs
- **AND** re-execution SHALL NOT extend expiry or create a second logical decision

#### Scenario: Approval

- **WHEN** the trusted boundary resolves an authorized actor and receives an unexpired decision matching the request, run, thread, stage, artifact digest, and pending native interrupt
- **THEN** native `Command(resume={pending_interrupt.id: decision})` SHALL deliver the decision to the matching gate
- **AND** the dedicated gate MAY re-execute as required by LangGraph
- **AND** artifact generation and validation SHALL not re-execute
- **AND** only that gate's continuation SHALL run

#### Scenario: Rejection and backtrack

- **WHEN** an authorized rejection names an allowed backtrack target
- **THEN** native `Command(goto=...)` SHALL route only to the validated target
- **AND** the decision SHALL be recorded exactly once

#### Scenario: Invalid decision

- **WHEN** a decision is expired according to the runner's trusted UTC clock, replayed, submitted by an unauthorized resolved actor, contains a self-asserted actor or authorization timestamp, belongs to another request/run/thread/stage/artifact/interrupt, or targets forbidden routing
- **THEN** the workflow SHALL fail closed before advancing or modifying the checkpoint
- **AND** the rejection SHALL be observable without recording the invalid decision as approved workflow history

#### Scenario: Missing approver policy

- **WHEN** protected interrupt stages are configured without a non-empty approver allowlist
- **THEN** graph construction SHALL fail with actionable configuration guidance
- **AND** the workflow SHALL NOT begin execution

#### Scenario: Non-durable gated run

- **WHEN** a gated workflow runs without durable Postgres persistence
- **THEN** it SHALL use an in-process checkpointer retained for the runner lifetime
- **AND** same-process resume MAY be supported
- **AND** resume after process restart SHALL report that no durable checkpoint exists

### Requirement: Read-only workflow authority

Stage modularization SHALL preserve the harness read-only authority profile.

#### Scenario: Tool requests mutation

- **WHEN** a stage attempts source, Jira, GitLab, shell, code-execution, or external mutation
- **THEN** TDT policy SHALL deny it
- **AND** only bounded artifact writes under the configured harness root SHALL remain allowed

### Requirement: Evidence-grounded stage completion
A stage that declares required external or repository evidence SHALL not complete unless the evidence is present, current for the verified source identity, structurally valid, and traceable to the produced artifact.

#### Scenario: Required evidence is current
- **WHEN** a stage receives all required Jira, GitNexus, Graphify, file, or repository evidence with matching source identity
- **THEN** validation SHALL evaluate the artifact against that evidence and declared requirements
- **AND** accepted evidence references SHALL be persisted with the artifact revision

#### Scenario: Evidence is empty or stale
- **WHEN** required evidence is empty, placeholder, stale, malformed, or refers to another repository state
- **THEN** the stage SHALL fail closed or transition to `needs_input`
- **AND** workflow status SHALL not advance to completed planning

#### Scenario: Optional evidence is unavailable
- **WHEN** an explicitly optional evidence source is unavailable
- **THEN** the artifact and report SHALL identify the omission and resulting confidence limitation
- **AND** optional classification SHALL come from the stage contract rather than provider output

### Requirement: Traceability-based plan review
Plan review SHALL derive its result from declared requirements, acceptance criteria, evidence claims, repository examples, artifact dependencies, and downstream traceability. A constant or provider-authored passing boolean SHALL NOT be authoritative.

#### Scenario: Plan is fully traceable
- **WHEN** every applicable requirement and acceptance criterion maps to supported evidence, planned changes, validation, and downstream artifacts
- **THEN** plan review MAY pass with a deterministic traceability report
- **AND** the report SHALL record the evaluated identifiers and evidence references

#### Scenario: Plan lacks evidence or mapping
- **WHEN** a required claim has no supporting evidence, repository example, or downstream mapping
- **THEN** review SHALL fail or require input with explicit missing obligations
- **AND** a model-authored `passes_review=true` value SHALL not override the result

### Requirement: Immutable artifact revisions
Every artifact-producing stage SHALL persist immutable revisions with stable identity, content digest, input artifact references, evidence references, validation results, and source identity. Checkpoint state MAY reference artifact identities but SHALL not replace the artifact ledger.

#### Scenario: Artifact is revised
- **WHEN** validation or backtracking requires a new artifact version
- **THEN** the store SHALL append a new revision linked to the superseded revision
- **AND** the prior content and digest SHALL remain unchanged

#### Scenario: Workflow resumes after restart
- **WHEN** a separate process resumes a durable workflow
- **THEN** it SHALL resolve completed artifact identities and verify their digests before downstream use
- **AND** it SHALL not regenerate completed artifact-producing stages solely to reconstruct content

#### Scenario: Artifact store is unavailable
- **WHEN** a supported production run cannot persist a required artifact revision
- **THEN** the stage SHALL not advance or checkpoint a successful completion
- **AND** the failure SHALL be observable without losing the prior immutable revision
