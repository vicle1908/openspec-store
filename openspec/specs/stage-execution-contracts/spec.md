# stage-execution-contracts Specification

## Purpose
Define the immutable per-stage contract registry, topology bindings, evidence
preflight, capability requirements, and composition-drift checks for the
standalone 13-stage planning workflow.
## Requirements
### Requirement: Canonical version-1 contracts cover the exact standalone topology

The harness SHALL define one immutable `StageContract` for each stage in `STAGE_SEQUENCE`. Every contract SHALL use schema URI `urn:tdt:ai-harness:stage-contract:1`, contract version `1`, closed typed read/write/evidence/capability vocabularies, one stage-owned output, the canonical gate value, and the following normative policy matrix. The evidence vocabulary SHALL be exactly `file`, `symbol`, `command`, `document`, and `human_authority`. The provider-capability vocabulary SHALL map explicitly and only to these `ProviderCapabilities` boolean fields: `structured_output`, `read_only_mode`, `session_resume`, `direct_agent_selection`, `event_stream`, `cancellation`, `timeout`, `process_status`, `bounded_output`, `session_identity`, `cost_budget`, `configuration_isolation`, `mcp_isolation`, `non_persistence`, `bounded_turns`, `bare_mode_auth`, `managed_policy_isolation`, `project_config_isolation`, `token_usage`, `token_budget`, and `cost_usage`.

| Stage | Additional required reads beyond `run_metadata` and `evidence_manifest` | Owned output | Required evidence | Gate | Additional capability |
|---|---|---|---|---:|---|
| `intake` | `ticket` | `artifact_intake` | `human_authority` | false | none |
| `context` | `artifact_intake` | `artifact_context` | `file` | false | none |
| `clarify` | `artifact_context`, `clarification_answers` | `artifact_clarify` | none | false | none |
| `spec` | `artifact_clarify` | `artifact_spec` | none | true | none |
| `impact` | `artifact_spec` | `artifact_impact` | `file` | false | none |
| `design` | `artifact_impact` | `artifact_design` | none | true | none |
| `api_contract` | `artifact_design` | `artifact_api_contract` | none | false | none |
| `impl_plan` | `artifact_api_contract` | `artifact_impl_plan` | none | true | none |
| `coding_plan` | `artifact_impl_plan` | `artifact_coding_plan` | `file` | false | none |
| `plan_review` | `artifact_coding_plan` | `artifact_plan_review` | none | true | none |
| `test_cases` | `artifact_plan_review` | `artifact_test_cases` | none | false | none |
| `auto_test_plan` | `artifact_test_cases` | `artifact_auto_test_plan` | none | false | none |
| `verify` | all 12 predecessor artifacts | `artifact_verify` | none | false | none |

#### Scenario: Exact canonical coverage
- **WHEN** canonical contracts are validated
- **THEN** all 13 stages have exactly one matching contract
- **AND** every field equals the normative version-1 matrix

#### Scenario: Unknown schema or vocabulary
- **WHEN** a contract declares an unknown schema URI, version, read, write, evidence source, or capability
- **THEN** startup fails with `ConfigurationError` identifying the stage and invalid value

#### Scenario: Circular-import-safe startup
- **WHEN** topology, models, contracts, compatibility stages, workflow, and runtime are imported in any supported clean-process order
- **THEN** imports complete without a partially initialized module or circular-import error

### Requirement: Contract validation models standalone logical ownership

Contract validation SHALL model logical request inputs and stage-owned artifacts rather than LangGraph state or raw SQLite columns. `required_reads` SHALL be available from initial run inputs or accepted predecessors, and each stage SHALL own exactly the output named by the canonical matrix. `required_reads` SHALL express minimum availability, not an exclusive request projection; other bounded accepted predecessor context MAY remain present.

#### Scenario: Missing or wrong owned output
- **WHEN** a contract omits its owned output or declares another stage's output
- **THEN** initialization fails with `ConfigurationError`

#### Scenario: Unavailable predecessor read
- **WHEN** a contract requires an artifact that cannot exist before its stage
- **THEN** initialization fails and identifies the unavailable read

#### Scenario: Verify predecessor coverage
- **WHEN** the `verify` contract is validated
- **THEN** its `required_reads` contain every one of the 12 accepted predecessor artifacts

### Requirement: Canonical defaults and monotonic overrides are mandatory

`WorkflowEngine` SHALL select canonical contracts when its contract argument is `None`. Explicit controlled-composition overrides SHALL pass all canonical validation and MAY only add required evidence or provider capabilities; they SHALL NOT change or remove canonical topology, schema identity, required reads, outputs, gates, evidence, or capabilities.

#### Scenario: Canonical production default
- **WHEN** the production composition root creates an engine without an override
- **THEN** the engine stores an immutable validated copy of all canonical contracts

#### Scenario: Stronger controlled override
- **WHEN** an explicit complete override preserves canonical fields and adds an evidence or capability requirement
- **THEN** initialization succeeds and the stronger requirement is enforced

#### Scenario: Weakened or mismatched override
- **WHEN** an override removes a canonical requirement or changes a canonical stage, schema, required read, output, or gate
- **THEN** initialization fails with `ConfigurationError`

### Requirement: Active contracts own gate behavior

The engine SHALL use the active contract's `gate_required` value for gate creation. `GATED_STAGES` SHALL be derived from canonical contracts and re-exported only as a compatibility view.

#### Scenario: Canonical gated stage
- **WHEN** `spec`, `design`, `impl_plan`, or `plan_review` accepts a revision
- **THEN** the ledger atomically creates a digest-bound gate and waits for approval

#### Scenario: Canonical non-gated stage
- **WHEN** any other stage accepts a revision
- **THEN** no gate is created and normal sequential advancement continues

#### Scenario: Compatibility gate view
- **WHEN** callers import `GATED_STAGES` from the existing module
- **THEN** it equals the set derived from canonical contracts

### Requirement: Required input evidence is retryably enforced before attempt creation

The engine SHALL validate canonical required evidence against the candidate request manifest before downstream artifact reset/reconciliation, request persistence, or stage begin. Evidence SHALL match the canonical run-local repository label (the final component of resolved `run.project_root`), required source type, source-specific identity, SHA-256 digest shape, contained-path policy where applicable, and freshness policy. File/document identities SHALL be non-empty contained project-relative paths; symbol identity SHALL be a non-empty canonical UID; command identity SHALL be a non-empty bounded deterministic-collector query and SHALL NOT be executed by preflight; human authority SHALL be bound to the current run and accepted ledger input. Rejection SHALL preserve active/pending state and all attempt budgets, and its bounded validation event SHALL be the only mutation.

#### Scenario: Intake authority is present
- **WHEN** `intake` has the run-bound human-authority ticket record with the accepted ticket digest
- **THEN** evidence preflight succeeds

#### Scenario: Clarification answer cannot replace intake ticket authority
- **WHEN** `intake` has a human-authority clarification-answer record but lacks the run-bound ticket record
- **THEN** evidence preflight is rejected

#### Scenario: Required file evidence is present
- **WHEN** `context`, `impact`, or `coding_plan` has fresh current-repository file evidence with a contained path and valid digest
- **THEN** evidence preflight succeeds

#### Scenario: Required evidence is missing or invalid
- **WHEN** canonical required evidence is absent, stale, malformed, or belongs to another repository
- **THEN** one `validation` event with action `stage_preflight_rejected` is recorded using bounded reason codes
- **AND** the stage remains pending and retryable without budget consumption

#### Scenario: Human authority cannot satisfy file evidence
- **WHEN** a file requirement exists and only human-authority evidence is present
- **THEN** preflight is rejected without changing run or stage status

### Requirement: Stage readiness reuses one provider probe

Headless execution SHALL evaluate global automated-profile requirements and active-contract requirements against the same `ProviderCapabilities` value returned by one adapter probe. Native automated adapters SHALL accept that exact value through an explicit preflighted invocation extension and SHALL NOT probe again. Their existing direct `invoke(request)` compatibility entry point SHALL remain self-checking. Mutable probe caches SHALL NOT be used. Before request construction or attempt creation, the execution path SHALL compare that immutable capability snapshot with the required capability set in the selected `StageContract`. Bounded execution SHALL be satisfied by the mandatory harness-owned process timeout; a provider-native turn option MAY additionally enforce a tighter bound but SHALL NOT be required when the current provider version does not expose one.

#### Scenario: Canonical version-1 readiness
- **WHEN** the provider satisfies existing global `missing_headless()` and runtime-policy requirements
- **THEN** all canonical stage-specific readiness checks pass without another probe

#### Scenario: Direct adapter invocation remains self-checking
- **WHEN** a caller invokes a native adapter through the existing direct `invoke(request)` entry point
- **THEN** the adapter performs one probe and delegates to the same preflighted implementation

#### Scenario: Legacy-only adapter is not automated
- **WHEN** an adapter implements `probe()` and direct `invoke()` but not the preflighted invocation extension
- **THEN** workflow execution does not classify it as an automated adapter

#### Scenario: Stronger override capability is absent
- **WHEN** a valid monotonic override adds a capability requirement that is false in the probe result
- **THEN** no request is persisted and no model invocation occurs
- **AND** the run is marked unavailable using the existing provider-readiness behavior

#### Scenario: Probe failure remains distinct
- **WHEN** the single probe raises an exception
- **THEN** the run is marked unavailable with a probe-failure diagnostic rather than an unsupported-capability assertion

#### Scenario: Provider satisfies the selected stage
- **WHEN** a provider snapshot satisfies every capability required by the selected `StageContract`
- **THEN** execution may proceed to evidence preflight and request construction
- **AND** only provider options proven by that snapshot are emitted

#### Scenario: Provider lacks a required capability
- **WHEN** the selected contract requires one or more capabilities absent from the provider snapshot
- **THEN** execution stops before request or attempt creation
- **AND** the bounded validation event identifies the missing capability names without exposing provider help output or credentials

#### Scenario: Provider has extra capabilities
- **WHEN** a provider advertises capabilities beyond those required by the selected stage
- **THEN** the extra capabilities do not broaden tool access, authority, evidence requirements, or transition rights

#### Scenario: Provider omits native turn count
- **WHEN** the provider does not expose a native maximum-turn option but the harness applies a finite process timeout and cancellation boundary
- **THEN** bounded execution remains satisfied
- **AND** the adapter does not emit the unavailable turn option

#### Scenario: Override adds a capability requirement
- **WHEN** a valid monotonic override adds a provider capability requirement for one stage
- **THEN** provider preflight enforces the added requirement for that stage only
- **AND** the canonical requirements for every stage remain intact

#### Scenario: Guided execution does not invoke a provider
- **WHEN** a stage is executed in guided mode without adapter invocation
- **THEN** provider capability checks do not create provider attempts or fabricate provider readiness
- **AND** contract evidence, schema, traceability, gate, and transition requirements still apply

### Requirement: Canonical stage input continuity

A production-faithful live workflow fixture SHALL use one run identity and SHALL obtain ticket, evidence, clarification answers, and accepted predecessor artifacts through the normal runtime context resolvers. Direct adapter requests with empty upstream context are not evidence of stage continuity.

#### Scenario: Predecessor artifact is available
- **WHEN** a stage begins after a predecessor revision is accepted
- **THEN** its request includes the predecessor's verified structured result, revision identity, and digest
- **AND** superseded revisions are excluded.

#### Scenario: Evidence-required stage
- **WHEN** intake, context, impact, or coding-plan begins
- **THEN** the request contains the canonical evidence required by its stage contract
- **AND** invalid, stale, conflicting, or missing evidence prevents acceptance before provider invocation where the runtime contract requires preflight.

#### Scenario: Terminal verify receives the planning package
- **WHEN** verify begins
- **THEN** its request includes all accepted predecessor artifacts required by the canonical contract
- **AND** terminal verification can be independently recomputed from those accepted artifacts.

### Requirement: Applicability-aware semantic quality

Live workflow-quality verification SHALL validate stable identifier ownership and applicability-aware mapping obligations for every stage. It SHALL distinguish an evidence-backed `not_applicable` result from an empty or provider-prompted placeholder.

#### Scenario: Stage-owned identifiers
- **WHEN** an accepted stage emits stable identifiers
- **THEN** every identifier belongs to that stage's canonical ownership class
- **AND** duplicate, missing, malformed, or wrong-stage identifiers fail the quality check.

#### Scenario: Invalid live-provider traceability is retryable
- **WHEN** a headless provider returns a structurally valid result whose claim identifiers, evidence placement, or traceability links violate the canonical semantic policy
- **THEN** the runtime records a bounded correlated post-invocation rejection
- **AND** the current stage returns to pending while the run remains active when the configured per-stage request budget has capacity
- **AND** the next provider request contains bounded machine-readable rejection feedback without prompts, artifact bodies, session identifiers, or secret-bearing values
- **AND** exhausted or non-retryable failures terminate truthfully rather than looping.

#### Scenario: Provider schema projects canonical identifier ownership
- **WHEN** a stage result schema is supplied to a native provider
- **THEN** claim identifiers are constrained to the identifiers owned by that stage
- **AND** upstream references exclude evidence identifiers and exclude same-kind or otherwise non-downstream relationships forbidden by the traceability policy
- **AND** evidence identifiers remain confined to evidence-reference fields.

#### Scenario: API contract is not applicable
- **WHEN** the accepted design proves no interface change is required
- **THEN** only `api_contract` may return `not_applicable`
- **AND** the result contains a rationale and supporting evidence
- **AND** implementation planning maps directly from design to tasks.

#### Scenario: Incomplete real package
- **WHEN** a live provider produces an incomplete or disconnected planning package
- **THEN** the workflow remains accepted only when the stage contract permits it
- **AND** terminal verification reports partial/failed with the concrete missing obligations.

#### Scenario: Clarification interruption
- **WHEN** clarification produces unanswered stable questions
- **THEN** the run enters the clarification wait state
- **AND** restart and answer handling preserve question identity and do not advance downstream stages prematurely.

#### Scenario: Clarification retry reuses stable question identifiers
- **WHEN** answered clarification questions are followed by another `needs_input` result that reuses a prior stable question identifier
- **THEN** the ledger updates that durable question rather than violating uniqueness
- **AND** unchanged answered questions remain answered while changed or newly requested questions become pending.

#### Scenario: Semantic retry includes actionable bounded diagnostics
- **WHEN** a provider result is rejected after invocation and another attempt is allowed
- **THEN** the next stage request includes the latest sanitized validation reason for that run and stage
- **AND** the diagnostic excludes prompts, artifact bodies, credentials, provider sessions, and unbounded output
- **AND** canonical validation remains authoritative for acceptance.

#### Scenario: Long live attempts remain bounded and validated
- **WHEN** live verification configures a long finite timeout and expanded finite retry capacity
- **THEN** each provider attempt remains persisted and subject to schema, semantic, evidence, and traceability validation
- **AND** timeout or retry expansion cannot accept an invalid result or bypass run accounting.

#### Scenario: Per-stage retry capacity has an exact upper bound
- **WHEN** `requests_per_stage` is configured to a finite value
- **THEN** no more than that many provider invocations are reserved for the stage
- **AND** both structured-output rejection and post-invocation semantic rejection use the persisted attempt number rather than a stale pre-reservation count.

#### Scenario: Adapter validation diagnostics remain actionable and bounded
- **WHEN** a native provider envelope fails structured decoding or result parsing
- **THEN** the adapter returns the stable `ValidationError` category plus a bounded redacted reason
- **AND** retry classification remains based on the stable category
- **AND** protected prompt, ticket, artifact, session, and credential values are excluded.

#### Scenario: Traversal with partial authoritative verification is not certified
- **WHEN** all thirteen stages finish but authoritative verification reports missing mappings, missing stage identifiers, incomplete coverage, or unresolved assumptions
- **THEN** live workflow-quality verification fails with bounded aggregate diagnostics
- **AND** the change cannot be archived as successfully certified.

### Requirement: Runtime-backed live verification

A live workflow-quality fixture SHALL assert runtime persistence and transition evidence rather than inferring end-to-end success from provider invocation count.

#### Scenario: Accepted run evidence
- **WHEN** the fixture reaches terminal state
- **THEN** accepted revisions, provider terminal attempts, stage-finished events, materialized artifacts, gate decisions, and the verification report agree on the same run and stage sequence.
