# Harness Workflow Specification

## Purpose

Define the standalone AI planning harness product boundary, workflow, providers, persistence, safety, traceability, installation, and verification contracts.
## Requirements
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

The Claude provider adapter SHALL use Claude Code non-interactive execution with schema-validated output, a customization-isolated automated profile, bounded permissions, explicit working-directory scope, timeouts, finite turns, non-persistent sessions, and provider session identity.

#### Scenario: Claude headless stage succeeds
- **WHEN** Claude Code passes its structured-output, isolation, read-only, bounded-turn, non-persistence, and process-control probes and returns schema-valid output within limits
- **THEN** the adapter returns a typed stage result and provider session identity to the CLI
- **AND** doctor identifies the effective automated isolation capabilities

#### Scenario: Claude planning authority
- **WHEN** Claude executes an automated planning stage
- **THEN** bare and safe modes make source editing, unrestricted shell authority, MCP tools, plugins, hooks, custom skills, custom agents, and unapproved ordinary settings unavailable
- **AND** the provider returns its result through structured output instead of writing the current artifact

#### Scenario: Claude managed policy or authentication is incompatible
- **WHEN** bare-mode-compatible authentication is unavailable or an effective provider-managed policy cannot be shown to preserve the explicit read-only tool and permission boundary
- **THEN** the provider is not classified under the automated profile
- **AND** doctor reports the missing capability or residual managed-policy authority without invoking a model

#### Scenario: Claude session persistence
- **WHEN** an automated Claude stage terminates successfully, fails, times out, or is cancelled
- **THEN** the invocation does not persist a resumable provider session outside harness-owned metadata
- **AND** a later stage starts a fresh isolated invocation

#### Scenario: Claude custom agent requested
- **WHEN** configuration requests direct custom-agent selection for headless execution
- **THEN** the provider is not classified under the customization-isolated automated profile
- **AND** the CLI rejects the setting or requires an explicitly experimental profile

#### Scenario: Direct Claude agent selection
- **WHEN** a configured managed Claude agent exists or direct agent selection is requested
- **THEN** the automated profile does not select that agent and preserves the canonical stage request
- **AND** the CLI rejects the setting or requires an explicitly experimental or guided profile

#### Scenario: Claude output validation fails
- **WHEN** Claude exits successfully but its final response does not satisfy the stage schema
- **THEN** the stage remains incomplete
- **AND** the adapter records bounded diagnostics without accepting an artifact

### Requirement: Codex provider adapter

The Codex provider adapter SHALL use `codex exec` with a read-only sandbox, explicit working directory, output schema, ephemeral session, ignored user configuration and execution rules, a fail-closed project-configuration guard, timeout, and provider session identity.

#### Scenario: Codex headless stage succeeds
- **WHEN** Codex passes its structured-output, read-only, ephemeral, configuration-isolation, and process-control probes and returns schema-valid output within limits
- **THEN** the adapter returns a typed stage result and provider session identity to the CLI
- **AND** doctor identifies the effective automated isolation capabilities

#### Scenario: Codex planning sandbox
- **WHEN** Codex executes an automated planning stage
- **THEN** the process uses read-only sandboxing, ephemeral session storage, ignored user configuration, ignored execution rules, and no active project `.codex/config.toml`
- **AND** the provider cannot write the current OpenSpec artifact

#### Scenario: Codex project configuration is active
- **WHEN** the project configuration chain contains an active `.codex/config.toml` that the installed CLI cannot ignore
- **THEN** the provider is not classified under the automated profile and no model process is spawned
- **AND** doctor identifies the configuration path and requires guided or explicit experimental execution

#### Scenario: Codex project instructions remain visible
- **WHEN** the installed Codex CLI loads project instructions that it cannot disable independently of source access
- **THEN** the harness treats those instructions as untrusted project context within the read-only process
- **AND** local schema, evidence, traceability, and artifact-integrity validation remain authoritative

#### Scenario: Custom Codex agent is unavailable
- **WHEN** direct named-agent selection is unavailable or prohibited by the automated profile
- **THEN** headless execution uses the canonical stage request without custom-agent authority
- **AND** the stage does not fail solely because a custom subagent was not selected

#### Scenario: Codex event stream fails
- **WHEN** the Codex event stream terminates without a valid final result or with a non-zero process exit
- **THEN** the stage remains incomplete
- **AND** bounded process diagnostics are recorded

### Requirement: Provider support tiers

The harness SHALL classify provider and host support as `automated`, `guided`, `experimental`, or `unsupported` based on verified runtime capabilities, including the isolation capabilities required by the selected execution profile. Before creating a provider request or provider-attempt record, the engine SHALL probe the selected adapter exactly once, classify readiness against the current stage contract, and retain one immutable complete capability snapshot. The engine SHALL pass that same snapshot through request construction, reservation, invocation, and terminal audit persistence without re-probing or consulting a mutable global cache.

#### Scenario: Doctor reports automated provider
- **WHEN** a provider passes every required structured-output, read-only, isolation, non-persistence, timeout, cancellation, bounded-output, process-status, and session-identity conformance probe
- **THEN** `harness doctor` reports it as `automated`
- **AND** it lists the verified capabilities and provider version used for diagnostics

#### Scenario: Isolation capability is missing
- **WHEN** a provider supports structured output and read-only execution but lacks a required configuration-isolation or non-persistence capability
- **THEN** it is not reported as `automated`
- **AND** headless use is rejected or requires an explicit experimental opt-in

#### Scenario: Skills-only host
- **WHEN** a host can load the portable skills but lacks a conforming headless adapter
- **THEN** the host is reported as `guided`
- **AND** documentation does not claim automated execution for that host

#### Scenario: Experimental adapter
- **WHEN** an adapter exists but lacks one or more required guarantees or enables provider customizations outside the approved isolated profile
- **THEN** the host is reported as `experimental`
- **AND** headless use requires an explicit opt-in

#### Scenario: Current provider option surface
- **WHEN** capability probing reads the selected provider's bounded help output
- **THEN** readiness reflects the options and security guarantees actually exposed by that provider version
- **AND** removed historical options are not required or emitted

#### Scenario: Provider structured-output subset
- **WHEN** an immutable stage result schema contains metadata or validation keywords unsupported by a selected provider
- **THEN** the adapter derives a provider-facing schema using only the provider's strict structured-output subset
- **AND** enum and const properties carry explicit primitive types and exposed object properties are provider-required
- **AND** the original immutable stage result schema remains the sole acceptance authority after invocation

#### Scenario: Provider saved authentication in headless mode
- **WHEN** Claude or Codex has a valid saved CLI login
- **THEN** the headless adapter MAY reuse that authenticated provider endpoint
- **AND** Claude disables customizations with safe mode and explicit MCP/skill/session/tool controls
- **AND** Codex disables MCP, plugins, hooks, memories, rules, persistence, and project configuration through explicit invocation controls
- **AND** credential values are never read into diagnostics or persisted state

#### Scenario: Repeated capability read
- **WHEN** readiness, request construction, attempt reservation, and audit persistence inspect capabilities for one attempt
- **THEN** they use the exact same immutable snapshot and digest
- **AND** the provider probe runs once for that attempt

#### Scenario: Required capability is absent
- **WHEN** the selected provider lacks a capability required by the current stage contract
- **THEN** the workflow records one bounded unavailable/rejection event and stops before request persistence, reservation, or provider invocation
- **AND** no request or attempt budget is consumed

#### Scenario: Provider help is malformed or unavailable
- **WHEN** bounded probing fails, times out, exceeds limits, or cannot classify the provider contract
- **THEN** readiness fails closed without persisting a request or attempt
- **AND** diagnostics do not expose credentials, full help output, or protected configuration

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

The harness SHALL persist runtime metadata and authoritative provider-attempt usage in a versioned SQLite ledger under `$TDT_HOME/ai-harness/` and SHALL use transactions for state transitions, request reservations, and usage reconciliation.

#### Scenario: Atomic stage transition
- **WHEN** a stage result is accepted
- **THEN** the revision, validation outcome, event, authoritative usage reference, and next state commit atomically
- **AND** a crash cannot expose a completed stage without its accepted revision metadata

#### Scenario: Attempt reservation and reconciliation
- **WHEN** a provider attempt starts and later succeeds, fails, times out, is cancelled, or returns invalid output
- **THEN** its request reservation and final authoritative usage are recorded exactly once
- **AND** recovery can distinguish an unreconciled interrupted attempt from a free retry

#### Scenario: Restart recovery
- **WHEN** the process restarts after a committed transition, clarification request, pending gate, or reconciled provider attempt
- **THEN** the CLI resumes from the last committed state and authoritative usage totals
- **AND** completed provider work or consumed budget is not repeated or discarded automatically

#### Scenario: Concurrent advancement
- **WHEN** two processes attempt to advance the same run
- **THEN** at most one process holds the valid run lease and request reservation
- **AND** the other process exits without changing state or exceeding the configured request limit

#### Scenario: Stale lease recovery
- **WHEN** a lease expires after an interrupted process
- **THEN** the CLI verifies owner, expiry, and provider-attempt reconciliation metadata before acquiring a replacement lease
- **AND** it records the recovery event without erasing any authoritative usage already reported

#### Scenario: Secret persistence is prohibited
- **WHEN** configuration, provider output, usage telemetry, or diagnostics contain credential-like values
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

The harness SHALL use stage-owned stable identifiers rather than mutable Markdown line numbers to trace requirements through every applicable downstream planning layer. Terminal `complete` SHALL require a valid accepted graph and zero missing applicability-aware mapping obligations; coverage percentages alone SHALL NOT grant completion.

#### Scenario: Stable upstream mapping
- **WHEN** a downstream artifact is accepted
- **THEN** it references applicable upstream IDs such as `REQ-001`, `DES-001`, `API-001`, `TASK-001`, or `TC-001`
- **AND** every newly created stable ID belongs to a kind permitted for the artifact's stage

#### Scenario: Stage-owned identifier kind
- **WHEN** an accepted result creates a stable identifier in a stage that does not own that identifier kind
- **THEN** validation rejects the result before materializing or advancing the stage
- **AND** the error identifies the identifier, actual stage, and permitted owning stage

#### Scenario: Downstream matrix generation
- **WHEN** `verify` executes
- **THEN** it generates a downstream traceability matrix from accepted ledger references and accepted artifact applicability
- **AND** earlier artifacts are not required to predict future downstream links

#### Scenario: Applicable full-chain obligations
- **WHEN** verification evaluates applicable planning artifacts
- **THEN** every requirement reaches design and test-case coverage, every acceptance criterion reaches a test case, every applicable design reaches an API or an approved API bypass to a task, every API reaches a task, every task reaches a test case, every test case reaches an automated-test plan, and every automated-test plan reaches verification
- **AND** at least one stage-owned verification identifier exists

#### Scenario: Non-applicable API bypass
- **WHEN** the accepted `api_contract` artifact is `not_applicable` with its required rationale and evidence
- **THEN** the policy permits a design-to-task mapping without fabricating an API identifier
- **AND** all remaining required mapping obligations still apply

#### Scenario: Applicable stage omits its required identifiers
- **WHEN** an applicable design, API-contract, implementation-plan, test-case, automated-test-plan, or verification stage has no required stage-owned identifier
- **THEN** terminal verification lists the missing obligation
- **AND** overall status is not `complete`

#### Scenario: Coverage report
- **WHEN** verification completes
- **THEN** it reports requirement, acceptance-criterion, test-case, and automated-test-plan coverage percentages
- **AND** it lists every missing required edge obligation in deterministic categories with the affected stable IDs

#### Scenario: Incomplete intermediate chain cannot pass
- **WHEN** a graph reaches test and verification identifiers but omits an applicable design, API, or task layer
- **THEN** verification reports the relevant missing obligations
- **AND** overall status is `partial`, never `complete`

#### Scenario: Broken reference
- **WHEN** an artifact references an unknown, duplicate, reverse, superseded-only, wrong-stage, or inapplicable ID without an accepted policy mapping
- **THEN** validation reports the broken reference and blocks acceptance or verification according to the graph-validity policy
- **AND** it does not record a misleading complete outcome

### Requirement: Security and path containment

The harness SHALL enforce read-only provider execution, provider-configuration isolation, safe subprocess invocation, approved paths, bounded resources, and secret-safe diagnostics independently of skill metadata and provider-owned customizations.

#### Scenario: Safe provider invocation
- **WHEN** the CLI invokes a provider
- **THEN** it uses an argument array without `shell=True`
- **AND** ticket or prompt content is supplied through bounded files or stdin rather than shell interpolation

#### Scenario: Read-only isolated planning provider
- **WHEN** any automated initial-release stage executes
- **THEN** the provider receives read-only authority and the approved isolated provider profile
- **AND** only the harness CLI can write inside approved artifact and run-store roots

#### Scenario: Read-only planning provider
- **WHEN** any initial-release stage executes
- **THEN** the provider receives read-only authority
- **AND** only the harness CLI can write inside approved artifact and run-store roots

#### Scenario: Path escape attempt
- **WHEN** a configured or provider-supplied path resolves outside an approved root or traverses a disallowed symlink
- **THEN** the operation is rejected before file access or mutation

#### Scenario: Shared output limit reached
- **WHEN** the combined provider stdout and stderr bytes exceed the configured output limit
- **THEN** the provider process is terminated and output beyond the shared bound is discarded
- **AND** neither stream receives a separate full allowance

#### Scenario: Resource limit reached
- **WHEN** a provider exceeds its timeout, combined output-size, request, token, or configured cost limit
- **THEN** the process is cancelled or rejected according to the enforceable provider capability
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

The implementation SHALL include deterministic unit, adapter-contract, and workflow integration tests plus opt-in read-only real-provider smoke tests. The live smoke suite SHALL exercise each supported native provider against the complete ordered 13-stage topology and SHALL emit bounded, secret-safe details for every accepted stage output. Live smoke SHALL use the harness default runtime policy unless the operator explicitly configures token or cost limits. Deterministic tests remain the CI authority and live tests remain explicitly opted in. The deterministic fake-provider end-to-end journey test SHALL exercise the complete 13-stage workflow with a recording fake provider and assert per-stage claim ownership, gate lifecycle, artifact materialization, verification report correctness, ledger audit completeness, and provider input isolation.

#### Scenario: Unit verification
- **WHEN** deterministic tests run
- **THEN** they cover transitions, SQLite transactions, leases, gates, revisions, rendering, evidence IDs, traceability, and path containment

#### Scenario: Fake-provider contract verification
- **WHEN** adapter tests run in deterministic CI
- **THEN** fake provider executables cover success, invalid output, timeout, cancellation, missing capability, stale session, non-zero exit, current CLI option compatibility, and explicit-versus-absent budget behavior

#### Scenario: Full workflow integration
- **WHEN** integration tests execute the workflow
- **THEN** they cover all 13 stages, guided and headless modes, clarification, approvals, rejection, restart, backtrack, supersession, and report generation

#### Scenario: Fake-provider end-to-end journey verification
- **WHEN** the deterministic fake-provider journey test runs
- **THEN** a `StageRecordingProvider` exercises all 13 canonical stages from `intake` through `verify` in headless mode
- **AND** each stage receives a `StageRequest` containing the run identity, stage identity, canonical instruction, upstream artifacts from all applicable predecessors, and stage-appropriate evidence
- **AND** the assertion confirms exactly 13 provider invocations in canonical stage order

#### Scenario: Per-stage claim ownership
- **WHEN** the fake-provider journey test validates claim outputs
- **THEN** each owning stage produces exactly the claims it is permitted to own: `REQ-*` for intake, `AC-*` for spec, `DEC-*` and `DES-*` for design, `API-*` for api_contract, `TASK-*` for impl_plan, `TC-*` for test_cases, `ATP-*` for auto_test_plan, and `VER-*` for verify
- **AND** non-owning stages (context, clarify, impact, coding_plan, plan_review) produce zero claims
- **AND** every claim references valid upstream identifiers at the correct traceability level

#### Scenario: Gate lifecycle verification
- **WHEN** the fake-provider journey test validates gate behavior
- **THEN** exactly four gate approvals are required after `spec`, `design`, `impl_plan`, and `plan_review`
- **AND** each gated stage produces a WAITING status with APPROVAL reason before advancing
- **AND** approving a gate with matching identity and artifact digest advances the workflow to the next stage

#### Scenario: Artifact materialization verification
- **WHEN** the fake-provider journey test validates artifact output
- **THEN** exactly 13 markdown artifact files are written to the project artifacts directory, one per stage
- **AND** each artifact is non-empty and contains its stage name

#### Scenario: Verification report correctness
- **WHEN** the fake-provider journey test validates the terminal verification report
- **THEN** the report records `verification_outcome: complete` with 100% coverage across requirements, acceptance criteria, test cases, and automated test plans
- **AND** the traceability chain contains valid links from requirements through verification identifiers
- **AND** the final run status is COMPLETED

#### Scenario: Ledger audit trail completeness
- **WHEN** the fake-provider journey test validates the SQLite ledger
- **THEN** exactly 13 `provider_attempt_terminal` events and 13 `stage_finished` events are recorded
- **AND** every terminal event includes non-negative timing duration
- **AND** every stage_finished event includes an artifact digest
- **AND** all 13 terminal events carry globally unique attempt identifiers

#### Scenario: Provider input isolation verification
- **WHEN** the fake-provider journey test validates provider inputs
- **THEN** upstream artifacts grow monotonically from intake through verify
- **AND** the ticket resolver provides the ticket text to every stage request
- **AND** evidence types match stage contracts: human_authority for intake, file for context and impact, none for clarify and spec

#### Scenario: Real-provider smoke test
- **WHEN** an authorized developer opts into a real Claude or Codex smoke test
- **THEN** the test uses read-only authority plus finite timeout and output bounds
- **AND** it applies token or cost limits only when the operator explicitly configured them
- **AND** deterministic CI does not depend on the live provider result

#### Scenario: Artifact and skill validation
- **WHEN** release verification runs
- **THEN** the harness OpenSpec schema, current OpenSpec change, and portable skills pass their respective strict validators

#### Scenario: Deterministic default run
- **WHEN** the test suite runs without live-provider opt-in
- **THEN** no external provider request is made
- **AND** one intentional start-to-end journey skip is reported for each provider

#### Scenario: Complete ordered live stage matrix
- **WHEN** `AI_HARNESS_LIVE_SMOKE=1` is set and both supported provider CLIs are authenticated
- **THEN** Claude and Codex each execute all 13 canonical stages from `intake` through `verify` through the actual adapter boundary
- **AND** all twenty-six results pass canonical local validation for the requested stage
- **AND** each provider's observed journey order equals the canonical stage sequence

#### Scenario: Detailed stage output transcript
- **WHEN** an opted-in live stage case succeeds
- **THEN** pytest can display a JSON transcript containing provider, one-based sequence position, stage, status, applicability, artifact body, stage-extension data, and normalized usage
- **AND** the transcript omits provider session identifiers, attempt identifiers, prompts, environment values, and credential material

#### Scenario: Stage-specific fields are exercised
- **WHEN** the live smoke invokes `clarify` or `verify`
- **THEN** clarification includes a valid `clarification_outcome`
- **AND** verification includes a valid outcome, policy version, graph status, and missing-stage identifier collection

#### Scenario: Live matrix remains read-only and default-unlimited
- **WHEN** any live smoke invocation is constructed
- **THEN** it retains finite timeout and output bounds and read-only provider authority
- **AND** it does not configure token or cost limits unless explicitly requested by the caller

#### Scenario: Live provider validation fails
- **WHEN** a provider exits non-zero, times out, or returns output invalid under the requested canonical stage schema
- **THEN** the corresponding matrix case fails with bounded diagnostics
- **AND** success from another provider or stage does not mask the failure

### Requirement: Version-pinned planning and verification policy

The harness SHALL bind each run to the actual installed planning-schema version and verification-policy version resolved when the run is created. It SHALL NOT silently advance or reinterpret a run using an incompatible schema or verification policy.

#### Scenario: Run captures installed versions
- **WHEN** the CLI creates a run from an installed `harness-13` schema
- **THEN** it records the resolved schema name, schema version, and verification-policy version rather than repository defaults
- **AND** the authoritative stage request and terminal report expose those versions

#### Scenario: Active run encounters incompatible installed policy
- **WHEN** a run resumes after the installed schema or verification policy changes incompatibly
- **THEN** runtime composition fails before beginning another stage
- **AND** the diagnostic identifies the pinned and installed versions without modifying run state

#### Scenario: Legacy verification is reported
- **WHEN** a terminal revision was accepted under an older verification policy
- **THEN** the report preserves the recorded historical outcome and labels its policy version
- **AND** it does not present the revision as having passed the current policy without an explicit new verification revision or run

### Requirement: Harness-owned provider option authority

The harness SHALL expose only typed, provider-specific safe configuration and SHALL retain exclusive authority over options that affect tools, permissions, sandboxing, working directories, provider configuration, MCP servers, plugins, agents, sessions, schemas, event formats, output destinations, execution bounds, and explicit provider budgets. It SHALL emit only options proven available by the immutable capability snapshot used for that invocation.

#### Scenario: Safe typed provider setting
- **WHEN** configuration supplies a supported typed model, effort, or bounded-turn setting with a valid value
- **THEN** the adapter translates it only when the selected provider exposes the corresponding option
- **AND** harness-owned isolation and output arguments remain unchanged

#### Scenario: Current CLI omits a former turn option
- **WHEN** provider help no longer exposes the configured native turn option
- **THEN** the adapter omits that option and relies on the mandatory harness process timeout as the hard execution bound
- **AND** capability preflight does not reject the provider solely because the former option is absent

#### Scenario: Legacy arbitrary argument
- **WHEN** configuration supplies legacy arbitrary `extra_args` or an unknown provider option
- **THEN** validation fails before run creation or provider probing
- **AND** the diagnostic identifies the supported typed replacement when one exists

#### Scenario: Authority-changing option
- **WHEN** configuration attempts to supply an MCP, plugin, settings, profile, custom-agent, tool, permission-bypass, sandbox, working-directory, session, schema, or output-control option
- **THEN** validation rejects the configuration before spawning a provider process
- **AND** the prohibited value is not copied into routine diagnostics when it is credential-like

### Requirement: Authoritative provider usage provenance

The harness SHALL derive enforceable provider usage from provider-native envelopes, events, or hard-control outcomes and SHALL NOT trust model-authored planning content as authoritative usage.

#### Scenario: Provider-native usage is available
- **WHEN** a provider invocation emits supported native request, token, or cost telemetry
- **THEN** the adapter normalizes it with provider identity, session identity, attempt identity, and provenance
- **AND** the ledger validates and records finite non-negative values exactly once

#### Scenario: Model-authored usage conflicts
- **WHEN** structured planning output contains usage values that differ from or exist without provider-native telemetry
- **THEN** those values do not affect enforcement or authoritative totals
- **AND** the discrepancy is excluded from accepted policy state or reported as advisory diagnostics

#### Scenario: Usage is unavailable
- **WHEN** a provider or guided host does not expose authoritative token or cost telemetry
- **THEN** the corresponding usage values and enforcement quality are recorded as unavailable rather than zero
- **AND** the harness does not claim that the missing policy was enforced

#### Scenario: Failed invocation reports usage
- **WHEN** an invocation returns authoritative usage but its process, schema, evidence, or traceability result fails
- **THEN** the usage is reconciled into the run totals even though no artifact is accepted
- **AND** retrying cannot erase or bypass the consumed budget

### Requirement: Cumulative run policy enforcement

The harness SHALL evaluate request, token, and cost policies cumulatively across all provider attempts in a run and SHALL expose whether each configured policy is enforced, observed, or unavailable. An absent token or cost limit SHALL mean that policy is not configured and SHALL NOT cause the adapter to invent an implicit ceiling.

#### Scenario: Request slot reservation
- **WHEN** a stage is ready to invoke a provider
- **THEN** the ledger atomically reserves a request attempt before process start
- **AND** concurrent commands cannot reserve attempts beyond the run limit

#### Scenario: Run budget exhausted before invocation
- **WHEN** an authoritative run total has exhausted an enforced request, token, or cost limit
- **THEN** the workflow fails before spawning another provider process
- **AND** it records a bounded policy failure without advancing the stage

#### Scenario: Remaining provider budget
- **WHEN** a provider exposes a native hard budget control and a run has an explicit remaining budget
- **THEN** the adapter receives no more than the authoritative remaining run budget for that invocation
- **AND** it does not receive the original full run cap again for each stage

#### Scenario: No configured token or cost limit
- **WHEN** a run has no configured token or cost limit
- **THEN** the adapter SHALL NOT invent or pass an implicit token or cost ceiling
- **AND** reporting SHALL preserve the corresponding limit and remaining value as null

#### Scenario: Hard policy cannot be enforced
- **WHEN** configuration requires a hard token or cost limit that the selected provider can only observe or cannot report
- **THEN** the execution profile is not classified as automated for that configuration
- **AND** execution is rejected or requires explicit experimental opt-in without claiming hard enforcement

#### Scenario: Authoritative totals are reported
- **WHEN** status or report output includes usage
- **THEN** it reports cumulative authoritative totals, remaining limits, telemetry provenance, and enforcement quality
- **AND** unknown values remain null rather than being treated as zero

### Requirement: Active runtime policy configuration

Every accepted runtime-policy setting SHALL have an implemented enforcement or reporting consumer. Settings reserved for future fan-out or cleanup SHALL be rejected before run creation rather than accepted as unavailable or non-enforcing metadata.

#### Scenario: Dormant concurrency setting
- **WHEN** configuration supplies a concurrency value but the selected workflow has no declared in-stage fan-out controller
- **THEN** configuration rejects the unsupported setting before run creation with actionable migration guidance
- **AND** documentation does not claim a global or internal concurrency guarantee

#### Scenario: Dormant retention setting
- **WHEN** configuration supplies provider-event or completed-run retention values without an installed cleanup mechanism
- **THEN** configuration rejects the unsupported setting before run creation with actionable migration guidance
- **AND** documentation states that no automatic deletion occurs

#### Scenario: Immutable revision retention
- **WHEN** a run completes or policy configuration changes
- **THEN** immutable artifact revisions are not automatically deleted
- **AND** any future removal requires a separately specified export-and-prune operation

### Requirement: Contract upgrade preserves workflow compatibility and isolation

The harness SHALL operate as a standalone product without a runtime dependency on `agent-harness`, agent-core, LangGraph, Pydantic AI, DBOS, or PostgreSQL. It SHALL NOT modify or share runtime state with `agent-harness`. Canonical stage contracts and preflight behavior SHALL be implemented entirely within `ai_harness` using the standalone topology, evidence records, ledger, and provider capabilities.

#### Scenario: Standalone startup
- **WHEN** the harness starts with valid configuration and canonical contracts
- **THEN** it initializes without importing or connecting to `agent-harness` or agent-core
- **AND** it uses only its own configuration, contracts, ledger, evidence, and artifact paths

#### Scenario: Shared-state configuration is rejected
- **WHEN** configuration points the harness at an `agent-harness` checkpoint or runtime state store
- **THEN** startup fails before creating or advancing a run
- **AND** the error identifies the unsupported shared-state boundary

#### Scenario: Existing product remains unchanged
- **WHEN** a standalone workflow runs to completion with contract enforcement
- **THEN** no file, database record, configuration, or public API owned by `agent-harness` or agent-core is modified

#### Scenario: Existing public snapshot remains stable
- **WHEN** callers import `WorkflowSnapshot` from `ai_harness.workflow` or call `WorkflowEngine.snapshot()`
- **THEN** the existing typed public snapshot remains available without relocation or replacement

#### Scenario: Existing validation remains authoritative
- **WHEN** a guided host or provider submits a result after successful preflight
- **THEN** the result still undergoes all existing mandatory structural, evidence, claim-policy, integrity, and traceability validation

### Requirement: Contract-driven stage preflight

Every guided and headless stage SHALL evaluate the same active contract before request persistence or attempt creation. Headless stages SHALL additionally evaluate global and stage-specific provider readiness using exactly one probe result.

#### Scenario: Guided preflight succeeds
- **WHEN** a guided stage has all contract-required input evidence
- **THEN** the CLI persists and returns the existing bounded `StageRequest`
- **AND** no provider capability probe is performed

#### Scenario: Headless preflight succeeds
- **WHEN** a headless stage begins with required evidence and a conforming provider
- **THEN** the engine performs one provider probe
- **AND** evaluates global and stage-specific readiness against that same result before invocation

#### Scenario: Evidence preflight is rejected
- **WHEN** required input evidence is absent, stale, malformed, or for another repository
- **THEN** the engine records one bounded validation rejection event
- **AND** leaves the run active and stage pending
- **AND** does not persist a request, increment the attempt, reserve a provider attempt, or consume request budget

#### Scenario: Retry after evidence correction
- **WHEN** an operator corrects the evidence condition after a preflight rejection
- **THEN** the same pending stage can begin normally without an administrative state repair

### Requirement: Provider-attempt audit is transactionally integrated

The harness SHALL persist runtime metadata and authoritative provider-attempt usage in a versioned SQLite ledger under `$TDT_HOME/ai-harness/`. Version-4 provider-attempt intent SHALL be durable before invocation, and authoritative terminal reconciliation plus its unique `provider_attempt_terminal` event SHALL commit atomically and idempotently.

#### Scenario: Atomic stage transition
- **WHEN** a stage result is accepted
- **THEN** revision metadata, validation summary, transition event, gate or next state, and authoritative attempt reference commit atomically
- **AND** a crash cannot expose a completed stage without its accepted revision metadata

#### Scenario: Durable attempt lifecycle
- **WHEN** a provider attempt is reserved and invoked
- **THEN** request identity and `not_started` intent commit before invocation-start state
- **AND** `in_flight` commits immediately before the adapter call

#### Scenario: Atomic terminal reconciliation
- **WHEN** a provider attempt reaches one of the six closed terminal outcomes
- **THEN** authoritative usage/outcome reconciliation and one `provider_attempt_terminal` event commit in the same transaction

#### Scenario: Restart recovery
- **WHEN** recovery finds a reconciled attempt
- **THEN** equivalent replay returns the existing terminal record and conflicting replay fails closed
- **AND** usage is not double-counted

#### Scenario: Unknown invocation recovery
- **WHEN** recovery finds an `in_flight` attempt without committed reconciliation
- **THEN** it records or interprets the intent as non-terminal `unknown`
- **AND** does not repeat the external invocation; only a valid late result or trusted terminal recovery classification may close the same attempt

#### Scenario: Concurrent reconciliation
- **WHEN** two processes reconcile the same attempt
- **THEN** SQLite transaction serialization and terminal-row uniqueness allow at most one authoritative terminal record

#### Scenario: Secret persistence is prohibited
- **WHEN** configuration, output, telemetry, or diagnostics contain protected content
- **THEN** terminal metadata excludes prompts, instructions, model output, artifact bodies, and credential-like values

### Requirement: Provider-attempt audit remains local and migration-safe

The harness SHALL implement provider-attempt audit behavior within its local SQLite ledger and `ai_harness` modules without a runtime dependency on `agent-harness`, agent-core, LangGraph, Pydantic AI, DBOS, PostgreSQL, OpenTelemetry, or an external event service. It SHALL NOT modify or share runtime state with `agent-harness`.

#### Scenario: Standalone startup
- **WHEN** the harness opens a supported ledger
- **THEN** it initializes without connecting to an external orchestration or telemetry runtime

#### Scenario: Existing product remains isolated
- **WHEN** terminal audit data is committed
- **THEN** no external harness-owned state or API is modified

#### Scenario: Supported migration chain
- **WHEN** a supported schema-1, schema-2, or schema-3 ledger is opened by version-4 code
- **THEN** initialization reaches schema 3 through the existing validated path where necessary, creates the verified schema-3 rollback backup, and completes the transactional 3 -> 4 migration before writes
- **AND** existing attempts, events, revisions, usage, and triggers remain intact

### Requirement: Structured subjects remain advisory to mandatory evidence validation

Every material claim SHALL be classified as `observed`, `proposed`, `assumption`, or `decision` and validated according to its type. Under result schema `urn:tdt:ai-harness:stage-result:2`, a claim MAY declare a structured subject for accepted-revision advisory diagnostics. Existing evidence IDs, repository/source identity, digests, freshness, authority limits, and traceability SHALL remain mandatory and authoritative.

#### Scenario: Observed claim
- **WHEN** an artifact states a current fact
- **THEN** it is classified `observed` and cites accepted evidence with source identity and digest

#### Scenario: Structured observed subject
- **WHEN** an observed claim declares a valid symbol, file, or document subject
- **THEN** diagnostics compare it only with cited accepted evidence using exact identity rules

#### Scenario: Proposed behavior
- **WHEN** an artifact defines new behavior
- **THEN** it is classified `proposed` and validated through requirement/decision references, not current-source existence

#### Scenario: Unresolved assumption
- **WHEN** progress depends on an unverified premise
- **THEN** it is classified `assumption` and surfaced for review or clarification

#### Scenario: Design decision
- **WHEN** the workflow selects among alternatives
- **THEN** it is classified `decision` and records rationale and inputs

#### Scenario: Human authority for current source
- **WHEN** human-authority evidence is used to prove an observed current-code subject
- **THEN** mandatory validation rejects before advisory persistence

#### Scenario: Fabricated or stale evidence
- **WHEN** cited evidence is unknown, stale, malformed, or digest-invalid
- **THEN** mandatory validation rejects and advisory diagnostics cannot downgrade the failure

### Requirement: Structured diagnostic persistence is atomic

The harness SHALL use ledger schema version 4 and SHALL commit one bounded structured-claim diagnostic event in the same transaction as every accepted revision, transition, and gate/next state. Diagnostic schemas SHALL be locally versioned and secret-safe.

#### Scenario: Atomic accepted revision
- **WHEN** a stage result passes mandatory validation and diagnostic serialization
- **THEN** revision, diagnostic event, transition, and gate/next state commit atomically

#### Scenario: Legacy claims
- **WHEN** an accepted result contains no structured observed subject
- **THEN** a versioned `not_applicable` summary commits without changing existing acceptance behavior

#### Scenario: Diagnostic failure
- **WHEN** diagnostic schema, bounds, or security checks fail
- **THEN** no accepted revision or transition is visible

#### Scenario: Secret persistence is prohibited
- **WHEN** claim prose, evidence content, or diagnostics contain sensitive values
- **THEN** routine diagnostic events retain only bounded stable IDs, compact subject fields, reason codes, and digest/reference metadata

### Requirement: Structured diagnostics remain local and isolated

The harness SHALL implement structured subjects, result-schema registries, and claim diagnostics within local `ai_harness` models, artifact validation, and the standalone ledger. It SHALL NOT depend at runtime on `agent-harness`, agent-core, LangGraph, Pydantic AI, DBOS, PostgreSQL, in-toto, SLSA services, or W3C PROV tooling, and SHALL NOT modify another harness's state.

#### Scenario: Standalone startup
- **WHEN** result schema 2 and diagnostic schema 1 are enabled
- **THEN** the harness initializes without connecting to an external orchestration or attestation runtime

#### Scenario: Existing product remains isolated
- **WHEN** diagnostics are computed and persisted
- **THEN** no external harness-owned file, database record, configuration, or API is modified

### Requirement: Live provider workflow quality evidence

The harness SHALL distinguish direct provider-adapter traversal from a live workflow run. An opt-in real-provider workflow-quality fixture SHALL execute each supported native provider through the actual `WorkflowEngine`, ledger, artifact store, evidence resolver, upstream artifact resolver, approval gates, and terminal verification report using a non-sensitive realistic ticket and fixture repository. Deterministic CI SHALL remain independent of external provider calls.

#### Scenario: Live workflow uses the runtime composition
- **WHEN** the real-provider workflow fixture is explicitly opted in
- **THEN** the provider is invoked through `WorkflowEngine.execute_headless`
- **AND** accepted revisions, stage transitions, provider attempts, artifacts, gates, and the terminal report are persisted by the normal runtime
- **AND** the fixture does not call an adapter directly as a substitute for workflow execution

#### Scenario: Live fixture is isolated from workspace provider configuration
- **WHEN** a live Claude or Codex workflow fixture is prepared
- **THEN** the checked-in synthetic fixture is copied byte-for-byte into a temporary execution root outside workspace ancestors
- **AND** provider capability probing and invocation use that isolated root
- **AND** ancestor user/workspace provider configuration cannot cause a false project-isolation failure or alter fixture instructions.

#### Scenario: Headless health is diagnosed before workflow execution
- **WHEN** a runtime-backed live journey is requested
- **THEN** representative common, clarification, and verification adapter operations are checked independently for both providers
- **AND** a later workflow failure records bounded stage/attempt/timing/request-size context without prompts, artifact bodies, sessions, or credentials.

#### Scenario: Connected stage inputs
- **WHEN** a live stage begins after its predecessor is accepted
- **THEN** the provider request contains the realistic ticket where applicable, current fixture evidence where required, and every accepted non-superseded predecessor artifact required by the canonical contract
- **AND** each stage uses the same run identity rather than an isolated stage-only run

#### Scenario: Semantic stage quality
- **WHEN** a live provider stage result is accepted
- **THEN** assertions validate stage-owned stable identifiers, applicable upstream references, evidence references, applicability, and required stage-purpose fields from the installed schema
- **AND** assertions do not require provider-specific prose or exact wording

#### Scenario: Semantic repair stays in the production workflow
- **WHEN** a live provider result fails canonical semantic validation after invocation
- **THEN** repair uses the normal persisted attempt/retry lifecycle and the same run identity
- **AND** no test-only normalization rewrites identifiers, evidence, applicability, or traceability into an acceptable result
- **AND** each rejected and accepted attempt remains auditable in the ledger.

#### Scenario: Complete real workflow
- **WHEN** the opted-in fixture completes successfully
- **THEN** all 13 canonical stages are accepted in order
- **AND** four digest-bound approval gates are recorded and approved
- **AND** 13 artifact files, 13 terminal provider attempts, 13 stage-finished transitions, and one terminal verification report exist
- **AND** the final report is derived from accepted artifacts and traceability rather than provider-declared coverage fields

#### Scenario: Truthful verification
- **WHEN** accepted artifacts contain no valid requirement-to-downstream traceability
- **THEN** terminal verification is `partial` or `failed` with non-empty missing mappings or missing stage identifiers
- **AND** a provider cannot force `complete` by declaring completion, 100-percent coverage, or an empty missing-stage collection

#### Scenario: Live clarification branch
- **WHEN** the realistic fixture contains a material ambiguity
- **THEN** clarification returns `needs_input` with stable question identifiers or a bounded blocked outcome
- **AND** the workflow pauses and resumes only after recorded answers or explicit terminal handling

#### Scenario: Default deterministic run
- **WHEN** live-provider opt-in is absent
- **THEN** the direct adapter traversal and workflow-quality tests make no external provider request
- **AND** deterministic fake-provider workflow tests continue to verify runtime invariants.

### Requirement: Adapter traversal is accurately scoped

The existing direct Claude/Codex 13-stage smoke SHALL be documented and reported as adapter traversal. It SHALL retain structured schema, identity, timeout/output, and transcript assertions but SHALL NOT be presented as evidence of live workflow-engine execution or semantic planning quality.

#### Scenario: Adapter-only report boundary
- **WHEN** only the direct adapter smoke has run
- **THEN** validation evidence labels it as adapter-level traversal
- **AND** it explicitly reports live runtime chaining and semantic quality as unverified.
