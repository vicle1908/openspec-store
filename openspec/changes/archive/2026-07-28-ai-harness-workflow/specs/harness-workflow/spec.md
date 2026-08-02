## ADDED Requirements

### Requirement: Standalone product boundary

The harness SHALL operate as a standalone product without a runtime dependency on
`agent-harness`, agent-core, LangGraph, Pydantic AI, DBOS, or PostgreSQL. It SHALL
NOT modify or share runtime state with `agent-harness`.

#### Scenario: Standalone startup
- **WHEN** the harness starts with valid standalone configuration
- **THEN** it initializes without importing or connecting to `agent-harness` or agent-core
- **AND** it uses only its own configuration, run ledger, and artifact paths

#### Scenario: Shared-state configuration is rejected
- **WHEN** configuration points the harness at an `agent-harness` checkpoint or runtime state store
- **THEN** startup fails before creating or advancing a run
- **AND** the error identifies the unsupported shared-state boundary

#### Scenario: Existing product remains unchanged
- **WHEN** a standalone harness workflow runs to completion
- **THEN** no file, database record, configuration, or public API owned by `agent-harness` or agent-core is modified

### Requirement: Exact 13-stage planning workflow

The harness SHALL process planning work through exactly these named stages in order:
`intake`, `context`, `clarify`, `spec`, `impact`, `design`, `api_contract`,
`impl_plan`, `coding_plan`, `plan_review`, `test_cases`, `auto_test_plan`, and
`verify`.

#### Scenario: Normal progression
- **WHEN** every stage completes without a clarification interrupt, gate pause, validation failure, or blocked dependency
- **THEN** the harness advances through all 13 named stages in order
- **AND** `verify` produces the terminal planning-verification result

#### Scenario: Planning-only review
- **WHEN** `plan_review` executes
- **THEN** it reviews the consistency, feasibility, risk, and testability of the planning artifacts
- **AND** it does not claim that implementation source code was reviewed

#### Scenario: Planning-only verification
- **WHEN** `verify` executes
- **THEN** it verifies artifact structure, evidence, assumptions, gates, and traceability
- **AND** it does not claim that application code was implemented or that proposed tests were executed

#### Scenario: Non-applicable stage
- **WHEN** a stage such as `api_contract` does not apply to the ticket
- **THEN** the stage produces a schema-valid `not_applicable` artifact
- **AND** the artifact contains a rationale and supporting evidence

#### Scenario: Unknown stage identifier
- **WHEN** configuration, a provider result, or a command references an unknown stage identifier
- **THEN** the harness rejects the operation before changing run state

### Requirement: CLI-owned workflow transitions

The harness CLI SHALL be the only authority that advances stages, records gate or
clarification decisions, accepts revisions, and materializes current OpenSpec
artifacts.

#### Scenario: Accepted transition
- **WHEN** the CLI validates a stage result and all dependencies are satisfied
- **THEN** it commits the artifact revision and stage transition in one controlled operation

#### Scenario: Provider attempts to advance state
- **WHEN** provider output claims that a later stage is complete or requests a direct state mutation
- **THEN** the CLI ignores the requested mutation
- **AND** it evaluates only the result for the requested current stage

#### Scenario: Direct artifact modification
- **WHEN** a current artifact changes without a matching accepted revision in the run ledger
- **THEN** the harness reports an integrity mismatch
- **AND** it does not advance until the mismatch is explicitly reconciled

### Requirement: Guided execution mode

The harness SHALL support guided execution in which a host coding agent performs
stage reasoning while the CLI owns state and validation.

#### Scenario: Begin guided stage
- **WHEN** a guided host calls `harness stage begin` for the current run
- **THEN** the CLI returns the run and stage identity, stage instruction, bounded evidence manifest, upstream references, limits, and output schema

#### Scenario: Complete guided stage
- **WHEN** the host submits a structured result through `harness stage complete`
- **THEN** the CLI treats the result as untrusted input
- **AND** it advances only after structural, evidence, and traceability validation succeeds

#### Scenario: Guided result is invalid
- **WHEN** a host submits malformed, mismatched, oversized, or unsupported output
- **THEN** the current stage remains unchanged
- **AND** the CLI returns actionable validation errors

### Requirement: Headless execution mode

The harness SHALL support headless execution through native coding-agent CLI
provider adapters.

#### Scenario: Supported headless provider
- **WHEN** the configured provider proves structured-output, read-only, timeout, cancellation, and process-result capabilities
- **THEN** the CLI invokes the provider for the current stage with bounded inputs and limits

#### Scenario: Missing required capability
- **WHEN** a provider lacks a required headless capability
- **THEN** the run fails before model execution
- **AND** the diagnostic lists the missing capabilities and the provider's supported tier

#### Scenario: Headless clarification boundary
- **WHEN** a headless run reaches `needs_input`
- **THEN** the CLI commits the clarification request and exits with the documented waiting outcome
- **AND** it does not wait indefinitely for terminal input

#### Scenario: Headless approval boundary
- **WHEN** a headless run reaches a required gate
- **THEN** the CLI commits the pending gate and exits with the documented waiting outcome
- **AND** a later command can inspect and resume the same run

### Requirement: Portable feature-based skills

The harness SHALL provide portable Agent Skills for `harness-workflow`,
`harness-gates`, and `harness-traceability`. The skills SHALL remain passive
knowledge and command interfaces while the harness CLI retains orchestration,
state, validation, and artifact-write authority.

#### Scenario: Portable skill validation
- **WHEN** a feature-based skill is validated against the Agent Skills specification
- **THEN** its portable definition passes naming, description, structure, and file-reference validation

#### Scenario: Portable core excludes host-only behavior
- **WHEN** a portable feature-based skill is installed for a non-Claude host
- **THEN** it does not require Claude-only context, agent selection, argument substitution, invocation policy, or dynamic command injection

#### Scenario: Independent feature boundaries
- **WHEN** the three skills are installed or validated independently
- **THEN** `harness-workflow` covers workflow lifecycle guidance, `harness-gates` covers gate decisions and backtracking, and `harness-traceability` covers evidence and traceability interpretation
- **AND** each skill invokes CLI commands instead of implementing state changes, validation, rendering, or provider execution

#### Scenario: Stage instruction resolution
- **WHEN** `harness-workflow` guides a host through a stage
- **THEN** it obtains the current instruction and output schema from the harness CLI
- **AND** no duplicate stage instruction embedded in another skill is authoritative

#### Scenario: Authoritative templates remain outside skills
- **WHEN** a host follows a skill reference
- **THEN** authoritative schemas, stage instructions, and artifact templates resolve through the CLI and installed OpenSpec schema
- **AND** the skill does not carry a second authoritative copy

#### Scenario: Skill metadata is not enforcement
- **WHEN** a host ignores or does not support an optional skill tool field
- **THEN** CLI-side sandbox, path, state, and validation controls remain effective

### Requirement: Claude provider adapter

The Claude provider adapter SHALL use Claude Code non-interactive execution with
schema-validated output, bounded permissions, explicit working-directory scope,
timeouts, and provider session identity.

#### Scenario: Claude headless stage succeeds
- **WHEN** Claude Code passes its capability probe and returns schema-valid output within limits
- **THEN** the adapter returns a typed stage result and provider session identity to the CLI

#### Scenario: Claude planning authority
- **WHEN** a Claude planning role executes a stage
- **THEN** source editing and unrestricted shell authority are unavailable
- **AND** the provider returns its result through structured output instead of writing the current artifact

#### Scenario: Direct Claude agent selection
- **WHEN** a configured managed Claude agent exists and direct agent selection is supported
- **THEN** the adapter can select that agent for the stage
- **AND** the selected agent's effective authority cannot exceed the stage policy

#### Scenario: Claude output validation fails
- **WHEN** Claude exits successfully but its final response does not satisfy the stage schema
- **THEN** the stage remains incomplete
- **AND** the adapter records bounded diagnostics without accepting an artifact

### Requirement: Codex provider adapter

The Codex provider adapter SHALL use `codex exec` with a read-only sandbox, explicit
working directory, output schema, timeout, and provider session identity.

#### Scenario: Codex headless stage succeeds
- **WHEN** Codex passes its capability probe and returns schema-valid output within limits
- **THEN** the adapter returns a typed stage result and provider session identity to the CLI

#### Scenario: Codex planning sandbox
- **WHEN** Codex executes a planning stage
- **THEN** the process uses read-only sandboxing
- **AND** the provider cannot write the current OpenSpec artifact

#### Scenario: Custom Codex agent is unavailable
- **WHEN** no compatible project custom agent exists or direct named-agent selection is unavailable
- **THEN** headless execution uses the stage request and root-session configuration
- **AND** the stage does not fail solely because a custom subagent was not selected

#### Scenario: Codex event stream fails
- **WHEN** the Codex event stream terminates without a valid final result or with a non-zero process exit
- **THEN** the stage remains incomplete
- **AND** bounded process diagnostics are recorded

### Requirement: Provider support tiers

The harness SHALL classify provider and host support as `automated`, `guided`,
`experimental`, or `unsupported` based on verified runtime capabilities.

#### Scenario: Doctor reports automated provider
- **WHEN** a provider passes every required headless conformance probe
- **THEN** `harness doctor` reports it as `automated`
- **AND** it lists the verified capabilities

#### Scenario: Skills-only host
- **WHEN** a host can load the portable skills but lacks a conforming headless adapter
- **THEN** the host is reported as `guided`
- **AND** documentation does not claim automated execution for that host

#### Scenario: Experimental adapter
- **WHEN** an adapter exists but lacks one or more required guarantees
- **THEN** the host is reported as `experimental`
- **AND** headless use requires an explicit opt-in

### Requirement: Structured provider-output boundary

Every provider or guided-host stage result SHALL validate against the current
stage's JSON Schema before the CLI renders or accepts an artifact.

#### Scenario: Valid structured result
- **WHEN** a result matches the requested run, stage, schema, limits, evidence IDs, and upstream IDs
- **THEN** the CLI renders deterministic Markdown and records JSON and Markdown digests

#### Scenario: Run or stage mismatch
- **WHEN** a result names a different run or stage than the request
- **THEN** the CLI rejects the result
- **AND** no revision or transition is committed

#### Scenario: Unknown evidence reference
- **WHEN** a result references an evidence ID that is absent from the accepted evidence manifest
- **THEN** the CLI rejects or blocks the affected observed claim according to validation policy

#### Scenario: Output exceeds limit
- **WHEN** provider output exceeds the configured byte, item, or field limit
- **THEN** the provider process is stopped or the result is rejected
- **AND** the complete oversized output is not written to routine logs

#### Scenario: Provider writes artifact directly
- **WHEN** the provider process creates or changes a current artifact outside the CLI acceptance path
- **THEN** the CLI reports an integrity violation
- **AND** the unauthorized materialization is not accepted as a stage revision

### Requirement: OpenSpec artifact ownership

The harness SHALL use a project-local `harness-13` OpenSpec schema for artifact
definitions, dependencies, templates, and instructions while preserving
OpenSpec's ownership of `.openspec.yaml`.

#### Scenario: Schema contains exact artifacts
- **WHEN** `harness-13` is validated
- **THEN** it contains exactly one artifact definition for each of the 13 named stages
- **AND** its dependency graph matches the approved sequential topology

#### Scenario: Runtime metadata remains separate
- **WHEN** run state, provider session data, gates, or revision history changes
- **THEN** `.openspec.yaml` remains unchanged except through supported OpenSpec metadata operations

#### Scenario: Schema initialization dry-run
- **WHEN** a user runs `harness init --dry-run`
- **THEN** the CLI reports the resolved OpenSpec root, schema destination, versions, and every planned file action
- **AND** no file is changed

#### Scenario: Unmanaged schema conflict
- **WHEN** schema initialization encounters an unmanaged destination file
- **THEN** initialization fails without overwriting the file
- **AND** the conflict identifies the destination and remediation options

### Requirement: Transactional runtime persistence

The harness SHALL persist runtime metadata in a versioned SQLite ledger under
`$TDT_HOME/ai-harness/` and SHALL use transactions for state transitions.

#### Scenario: Atomic stage transition
- **WHEN** a stage result is accepted
- **THEN** the revision, validation outcome, event, and next state commit atomically
- **AND** a crash cannot expose a completed stage without its accepted revision metadata

#### Scenario: Restart recovery
- **WHEN** the process restarts after a committed transition, clarification request, or pending gate
- **THEN** the CLI resumes from the last committed state
- **AND** completed provider work is not repeated automatically

#### Scenario: Concurrent advancement
- **WHEN** two processes attempt to advance the same run
- **THEN** at most one process holds the valid run lease
- **AND** the other process exits without changing state

#### Scenario: Stale lease recovery
- **WHEN** a lease expires after an interrupted process
- **THEN** the CLI verifies owner and expiry metadata before acquiring a replacement lease
- **AND** it records the recovery event

#### Scenario: Secret persistence is prohibited
- **WHEN** configuration, provider output, or diagnostics contain credential-like values
- **THEN** the ledger and logs exclude or redact those values
- **AND** full prompts are not stored as routine run metadata

### Requirement: Clarification interrupt

The `clarify` stage SHALL produce `resolved`, `needs_input`, or `blocked` and SHALL
not fabricate answers to unresolved business questions.

#### Scenario: Clarification resolved by evidence
- **WHEN** every material ambiguity is answered by accepted evidence
- **THEN** `clarify` records `resolved`
- **AND** the workflow can proceed to `spec`

#### Scenario: Human input required
- **WHEN** at least one material ambiguity lacks authoritative evidence
- **THEN** `clarify` records `needs_input` with stable question IDs
- **AND** the workflow stops before `spec`

#### Scenario: Answers resume clarification
- **WHEN** an authorized user submits answers through `harness answer`
- **THEN** the answers are bound to the pending question IDs and recorded in the run ledger
- **AND** `clarify` is eligible for a new validated revision

#### Scenario: Provider invents an answer
- **WHEN** provider output resolves an unanswered human question without evidence or a recorded answer
- **THEN** validation rejects the resolution
- **AND** the run remains `needs_input`

### Requirement: Digest-bound human gates

The harness SHALL enforce human gates after `spec`, `design`, `impl_plan`, and
`plan_review`. Each decision SHALL bind to the run, stage, artifact revision,
artifact digest, decision identity, allowed action, and expiry.

#### Scenario: Gate pause
- **WHEN** a gated artifact revision is accepted
- **THEN** the CLI records one pending gate request bound to that revision and digest
- **AND** downstream execution remains blocked

#### Scenario: Valid approval
- **WHEN** the trusted local actor approves the current unexpired gate with matching identity and digest
- **THEN** the decision is recorded once
- **AND** the next stage becomes eligible without rerunning the approved stage

#### Scenario: Valid rejection and backtrack
- **WHEN** the trusted local actor rejects the current gate with a reason and allowed earlier target
- **THEN** the rejection is recorded once
- **AND** revision-safe backtracking begins at the approved target

#### Scenario: Explicit administrative backtrack
- **WHEN** the trusted local actor invokes `harness backtrack` with a reason and an allowed target for the current accepted revision
- **THEN** the CLI creates and atomically consumes a digest-bound backtrack authorization
- **AND** it refuses to bypass an unresolved, stale, or mismatched gate decision

#### Scenario: Invalid gate decision
- **WHEN** a decision is stale, replayed, expired, unauthorized, mismatched, or targets a forbidden stage
- **THEN** the CLI fails closed before advancing or superseding artifacts
- **AND** the invalid attempt is observable without recording it as an accepted decision

#### Scenario: Self-asserted actor
- **WHEN** a command supplies an arbitrary actor value that differs from the trusted operating-system identity
- **THEN** the arbitrary value is not accepted as authoritative identity

### Requirement: Revision-safe backtracking

Backtracking SHALL preserve immutable artifact history, mark invalidated downstream
revisions superseded, and rerun the target stage as a new revision.

#### Scenario: Backtrack accepted
- **WHEN** a valid decision backtracks from a later stage to an earlier target
- **THEN** every accepted downstream revision is marked superseded
- **AND** the target stage becomes pending for a new revision

#### Scenario: Historical revision remains addressable
- **WHEN** a revision is superseded
- **THEN** its structured output, rendered artifact, digest, evidence references, and decision history remain addressable in the run store

#### Scenario: Current materialization reset
- **WHEN** downstream OpenSpec materializations must be removed to restore readiness
- **THEN** the CLI verifies their immutable historical copies and digests before removal
- **AND** audit history remains intact

#### Scenario: Provider session after backtrack
- **WHEN** the target stage reruns after backtracking
- **THEN** the harness starts a fresh provider session by default
- **AND** any session reuse requires an adapter-supported, explicitly requested same-stage recovery

### Requirement: Bounded internal parallelism

The initial workflow SHALL keep stage transitions sequential. Parallel work SHALL be
limited to declared independent operations inside a stage.

#### Scenario: Impact precedes design
- **WHEN** `impact` completes successfully
- **THEN** `design` consumes the accepted impact artifact
- **AND** `impact` and `design` are not executed as sibling parallel stages

#### Scenario: Independent evidence fan-out
- **WHEN** a stage declares independent evidence queries
- **THEN** each query has an isolated result, timeout, cancellation policy, and concurrency limit
- **AND** results are merged in a deterministic order

#### Scenario: Parallel partial failure
- **WHEN** one internal parallel operation fails or times out
- **THEN** the stage fails or records an explicit partial result according to policy
- **AND** the workflow does not silently advance as complete

### Requirement: Evidence classification and validation

Every material claim SHALL be classified as `observed`, `proposed`, `assumption`,
or `decision` and validated according to its type.

#### Scenario: Observed claim
- **WHEN** an artifact states a fact about current code, APIs, configuration, or documentation
- **THEN** the claim is classified `observed`
- **AND** it references accepted evidence with source identity and digest

#### Scenario: Proposed behavior
- **WHEN** an artifact defines a new endpoint, component, or behavior
- **THEN** the claim is classified `proposed`
- **AND** validation checks its requirement or decision references rather than requiring current-source existence

#### Scenario: Unresolved assumption
- **WHEN** progress depends on a premise that cannot be verified
- **THEN** the claim is classified `assumption`
- **AND** the assumption is surfaced for human review or clarification

#### Scenario: Design decision
- **WHEN** the workflow chooses among alternatives
- **THEN** the claim is classified `decision`
- **AND** it records rationale, inputs, and considered alternatives

#### Scenario: Clarification answer evidence
- **WHEN** an authorized human answer resolves a requirement, decision, or assumption
- **THEN** the ledger records it as human-authority evidence
- **AND** it is not accepted as proof of an observed current-code fact without deterministic collected evidence

#### Scenario: Fabricated evidence ID
- **WHEN** a provider cites an evidence ID that was not created by an accepted collector or recorded authorized input
- **THEN** the claim fails evidence validation

### Requirement: Stable end-to-end traceability

The harness SHALL use stable identifiers rather than mutable Markdown line numbers
to trace requirements through downstream planning artifacts.

#### Scenario: Stable upstream mapping
- **WHEN** a downstream artifact is accepted
- **THEN** it references applicable upstream IDs such as `REQ-001`, `DES-001`, `API-001`, `TASK-001`, or `TC-001`

#### Scenario: Downstream matrix generation
- **WHEN** `verify` executes
- **THEN** it generates a downstream traceability matrix from accepted ledger references
- **AND** earlier artifacts are not required to predict future downstream links

#### Scenario: Coverage report
- **WHEN** verification completes
- **THEN** it reports requirement, acceptance-criterion, test-case, and automated-test-plan coverage percentages
- **AND** it lists every missing required mapping

#### Scenario: Broken reference
- **WHEN** an artifact references an unknown, superseded-only, or inapplicable ID without an accepted mapping
- **THEN** verification reports the broken reference
- **AND** overall status is `partial` or `failed` according to required coverage policy

### Requirement: Security and path containment

The harness SHALL enforce read-only provider execution, safe subprocess invocation,
approved paths, bounded resources, and secret-safe diagnostics independently of
skill metadata.

#### Scenario: Safe provider invocation
- **WHEN** the CLI invokes a provider
- **THEN** it uses an argument array without `shell=True`
- **AND** ticket or prompt content is supplied through bounded files or stdin rather than shell interpolation

#### Scenario: Read-only planning provider
- **WHEN** any initial-release stage executes
- **THEN** the provider receives read-only authority
- **AND** only the harness CLI can write inside approved artifact and run-store roots

#### Scenario: Path escape attempt
- **WHEN** a configured or provider-supplied path resolves outside an approved root or traverses a disallowed symlink
- **THEN** the operation is rejected before file access or mutation

#### Scenario: Resource limit reached
- **WHEN** a provider exceeds its timeout, output-size, request, token, or configured cost limit
- **THEN** the process is cancelled or rejected
- **AND** the run records a bounded failure outcome

#### Scenario: Secret-safe diagnostics
- **WHEN** an error, event, or provider stream is persisted or displayed
- **THEN** credentials and protected environment values are redacted
- **AND** routine telemetry excludes full prompts and protected artifact bodies

### Requirement: Explicit installation channels

The harness SHALL install the CLI, portable skills, OpenSpec schema, and native
agent files through separate explicit channels.

#### Scenario: CLI installation
- **WHEN** the Python CLI is installed
- **THEN** installation uses `uv`
- **AND** no pip-based installation instruction is required

#### Scenario: Skill installation
- **WHEN** portable skills are installed
- **THEN** `npx skills` installs only the selected skill directories for selected hosts
- **AND** documentation does not claim that this installs the Python CLI, schema, or native agents

#### Scenario: Project initialization
- **WHEN** a user applies `harness init` after reviewing its dry-run
- **THEN** only selected managed schema and platform-agent files are created or upgraded
- **AND** each generated file contains ownership and version metadata

#### Scenario: Unmanaged file protection
- **WHEN** initialization encounters an unmanaged destination file
- **THEN** it refuses to overwrite the file
- **AND** it reports the conflict and available explicit remediation

#### Scenario: Managed rollback
- **WHEN** a user requests initializer rollback
- **THEN** only files with matching harness ownership metadata are removed
- **AND** unrelated project configuration is preserved

#### Scenario: Provider authentication
- **WHEN** a provider requires authentication
- **THEN** authentication remains owned by the provider CLI or approved execution environment
- **AND** the harness does not copy credentials into its configuration or ledger

### Requirement: Stable errors and secret-safe observability

The CLI SHALL provide stable machine-readable outcomes and bounded, secret-safe
events for workflow operations.

Run status, stage status, waiting reason, and planning-verification outcome SHALL
be separate typed values. A waiting run is resumable and SHALL NOT be represented
as a terminal planning-verification outcome.

#### Scenario: JSON command output
- **WHEN** a command runs in JSON mode
- **THEN** stdout contains only schema-valid command output
- **AND** diagnostics are written to stderr

#### Scenario: Distinct operational outcomes
- **WHEN** a command finishes
- **THEN** success, waiting for clarification, waiting for approval, invalid input, provider unavailable, provider failure, validation blocked, stale decision, not found, and internal failure have distinct documented outcomes

#### Scenario: Stage event
- **WHEN** a stage attempt starts or finishes
- **THEN** the event records run ID, stage, attempt, provider, duration, outcome, revision, and artifact digest when available
- **AND** it excludes credentials, full prompts, and protected artifact content

#### Scenario: Doctor report
- **WHEN** `harness doctor` runs
- **THEN** it reports OpenSpec schema resolution, run-store health, provider capabilities, skill and native-agent installation, path containment, and conflicts
- **AND** the report does not expose secrets

### Requirement: Deterministic verification strategy

The implementation SHALL include deterministic unit, adapter-contract, and workflow
integration tests plus opt-in bounded real-provider smoke tests.

#### Scenario: Unit verification
- **WHEN** deterministic tests run
- **THEN** they cover transitions, SQLite transactions, leases, gates, revisions, rendering, evidence IDs, traceability, and path containment

#### Scenario: Fake-provider contract verification
- **WHEN** adapter tests run in deterministic CI
- **THEN** fake provider executables cover success, invalid output, timeout, cancellation, missing capability, stale session, and non-zero exit

#### Scenario: Full workflow integration
- **WHEN** integration tests execute the workflow
- **THEN** they cover all 13 stages, guided and headless modes, clarification, approvals, rejection, restart, backtrack, supersession, and report generation

#### Scenario: Real-provider smoke test
- **WHEN** an authorized developer opts into a real Claude or Codex smoke test
- **THEN** the test uses explicit finite budgets and read-only authority
- **AND** deterministic CI does not depend on the live provider result

#### Scenario: Artifact and skill validation
- **WHEN** release verification runs
- **THEN** the harness OpenSpec schema, current OpenSpec change, and portable skills pass their respective strict validators
