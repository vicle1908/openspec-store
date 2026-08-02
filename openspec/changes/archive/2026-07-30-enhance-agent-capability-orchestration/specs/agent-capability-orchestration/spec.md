## Purpose

Provide a trustworthy coordination contract that lets agents combine durable
intent, code intelligence, project knowledge, and prior-session memory without
confusing one source of truth for another or overstating runtime readiness.

## ADDED Requirements

### Requirement: Profile-scoped capability health evidence

The orchestration layer SHALL expose a schema-validated, redacted,
machine-readable health report for a named profile. Each report MUST include a
unique run identity, generation time, exact source identity, dirty-worktree
fingerprint, selected profile, overall readiness state, per-probe requirement
class, attempts, duration, status, bounded error code, and evidence reference.

Probe status SHALL be one of `healthy`, `degraded`, `unavailable`,
`blocked`, `not-configured`, or `skipped`. Overall readiness SHALL be
`ready` only when every required probe is healthy, `ready-with-warnings`
when every required probe is healthy and at least one optional probe is not,
and `not-ready` otherwise.

#### Scenario: All required probes are healthy

- **WHEN** every required probe for the selected profile passes against the
  same source identity
- **THEN** the report records `ready` or `ready-with-warnings`, identifies
  optional warnings separately, and exits successfully

#### Scenario: A required probe fails

- **WHEN** any required probe is degraded, unavailable, blocked,
  not-configured, skipped, or timed out
- **THEN** the report records `not-ready`, exits non-zero, and identifies the
  failed probe and remediation without discarding independent probe results

#### Scenario: A probe hangs

- **WHEN** a CLI, MCP, REST, filesystem, or hook probe exceeds its configured
  deadline
- **THEN** the runner terminates that probe, records a timeout with its duration
  and attempt count, and continues only with independent non-mutating probes

#### Scenario: A transient probe is retried

- **WHEN** a probe is classified as retryable
- **THEN** the runner performs only the configured bounded attempts, records
  every attempt outcome, and produces one final deterministic probe status

#### Scenario: A probe encounters credential-like output

- **WHEN** a command or endpoint returns a token, password, private key,
  authenticated URL, or environment secret
- **THEN** the report redacts the value and records only the credential class,
  owning probe, and redaction occurrence

### Requirement: Atomic and attributable evidence

Each health run SHALL write to a unique run directory and MUST bind its report
to the repository HEAD plus a deterministic fingerprint of relevant dirty
state. An incomplete, interrupted, or failed run MUST NOT overwrite a prior
successful report or become the current readiness authority.

#### Scenario: Evidence completes successfully

- **WHEN** every scheduled probe reaches a terminal status and schema
  validation passes
- **THEN** the report is finalized atomically and can be selected as the latest
  evidence for that exact source identity and profile

#### Scenario: Evidence writing fails

- **WHEN** the run directory or final manifest cannot be written or validated
- **THEN** the run stops before any later mutating action, preserves readable
  diagnostics, and does not update the latest-evidence pointer

#### Scenario: Source state changes during a run

- **WHEN** HEAD or the relevant dirty-state fingerprint changes after probes
  begin
- **THEN** the report is marked not-ready for promotion and identifies the
  source-state mismatch

### Requirement: Explicit health profiles

The orchestration layer SHALL define at least quick, exploration, and
implementation profiles. Quick SHALL be read-only and bounded to configuration,
version, source identity, and lightweight live discovery. Exploration SHALL
add live read-only query and resource probes. Implementation SHALL additionally
require strict OpenSpec validation, managed-skill parity, outer and nested
knowledge-index freshness and integrity, agentmemory health and disposable
round-trip verification, and the repository verification appropriate to the
changed tooling.

#### Scenario: Quick status is requested

- **WHEN** a developer requests the quick profile
- **THEN** no index refresh, memory write, networked ingestion, or generated
  surface mutation occurs

#### Scenario: Exploration readiness is requested

- **WHEN** a developer requests the exploration profile
- **THEN** OpenSpec context, GitNexus query/resource access, Graphify
  query/resource access, and agentmemory recall availability are probed
  read-only and independently

#### Scenario: Implementation readiness is requested

- **WHEN** a developer requests the implementation profile
- **THEN** every implementation-required probe and verification gate must pass
  for the same source identity before the report can state `ready`

### Requirement: Source-of-truth routing and fallback

The workflow SHALL route questions and evidence according to these authority
boundaries: OpenSpec for intended behavior and verification, GitNexus for
precise code symbols and impact, Graphify for documents and cross-repository
concepts, and agentmemory for prior decisions, lessons, and session history.
Agentmemory and Graphify MUST NOT override normative OpenSpec requirements or
direct source-code evidence.

#### Scenario: An agent explores an implementation area

- **WHEN** an agent starts exploration for an active change
- **THEN** it loads applicable OpenSpec context, searches prior memory, uses
  GitNexus for execution flows, uses Graphify for related documentation, and
  cites source locations for resulting claims

#### Scenario: A shared symbol is about to change

- **WHEN** an agent prepares an implementation or refactor
- **THEN** it obtains GitNexus impact evidence before editing and treats the
  selected OpenSpec tasks and scenarios as the acceptance contract

#### Scenario: An authority is unavailable

- **WHEN** a routed tool is unavailable
- **THEN** the workflow uses repository search and direct source inspection as
  the bounded fallback, records the missing specialized evidence, and does not
  claim that the unavailable probe passed

#### Scenario: Context sources disagree

- **WHEN** memory or a graph result conflicts with an OpenSpec requirement or
  source-code observation
- **THEN** the agent reports the conflict and follows the authoritative source
  rather than silently merging contradictory claims

### Requirement: Independent-root and cross-tool identity

Every cross-tool result SHALL identify its Git root, repository name, OpenSpec
change or capability when known, source location, stable symbol or concept
identifier, and evidence type. The outer repository and `mcp-router/` SHALL
remain independently indexed and independently rollbackable.

#### Scenario: A result comes from the nested repository

- **WHEN** an agent combines nested GitNexus or Graphify evidence with outer
  evidence
- **THEN** the result preserves the nested root and source path and does not
  present it as an outer-repository symbol

#### Scenario: A cross-repository contract is queried

- **WHEN** an agent uses a GitNexus group or an on-demand Graphify projection
- **THEN** every returned relationship identifies both endpoint roots, its
  confidence/evidence type, and the contract or capability identity used to
  join them

#### Scenario: First-rollout evidence is consumed

- **WHEN** the initial orchestration rollout completes
- **THEN** its health manifest remains repository-local and no
  `mcp-router/` implementation change is required unless a separately
  reviewed nested-repository change approves that consumer

### Requirement: Bounded workflow and truthful handoff

The orchestration workflow SHALL provide bounded Explore, Prepare, Verify, and
Handoff phases. Each phase MUST record its outcome and missing evidence.
Knowledge-tool failures MUST NOT block an ordinary commit or replace the
repository's required verification gates.

#### Scenario: A pre-change impact probe fails

- **WHEN** GitNexus impact analysis is unavailable before an edit
- **THEN** the workflow records the missing evidence, requires explicit manual
  dependency review for the affected scope, and does not claim impact passed

#### Scenario: A developer commits while a knowledge service is down

- **WHEN** a Graphify hook, GitNexus MCP server, or agentmemory server is
  unavailable during commit-time checks
- **THEN** the commit remains non-interactive and the health report records the
  skipped advisory check and remediation

#### Scenario: Handoff is generated

- **WHEN** verification finishes
- **THEN** handoff reports the source identity, completed and skipped phases,
  verification evidence, unresolved risks, and the applicable readiness state

### Requirement: Disposable memory verification and durable-memory discipline

The workflow SHALL derive the expected agentmemory tool surface from the
running configuration and supported version rather than assuming that any
partial tool list is complete. Implementation-profile verification SHALL use a
unique disposable record to prove save, retrieval, deletion, and auditability.
Durable saves SHALL be limited to verified decisions, lessons, risks, and
verification outcomes with stable project, change/capability, and file tags.

#### Scenario: Full memory surface is configured

- **WHEN** agentmemory is configured for its full tool profile
- **THEN** health compares live discovery with the version's documented full
  surface and reports any missing tools as degraded

#### Scenario: Core memory surface is configured

- **WHEN** agentmemory is configured for its core tool profile
- **THEN** health compares live discovery with the documented core surface and
  does not require full-profile-only tools

#### Scenario: Disposable memory round trip succeeds

- **WHEN** implementation-profile memory verification runs
- **THEN** it saves a run-tagged record, retrieves the exact record, deletes
  it through the supported governance surface, verifies deletion or audit
  evidence, and leaves no unclassified durable test memory

#### Scenario: Disposable memory cleanup fails

- **WHEN** the probe record cannot be deleted or its deletion cannot be
  verified
- **THEN** agentmemory is not healthy for the implementation profile and the
  report identifies the retained probe record without exposing its content

#### Scenario: A durable memory conflicts with source truth

- **WHEN** a recalled decision or lesson conflicts with current OpenSpec or
  source-code evidence
- **THEN** the workflow treats the memory as stale contextual evidence and does
  not persist the contradiction as a new durable fact

#### Scenario: A memory save contains a secret

- **WHEN** a proposed memory includes a credential or authenticated endpoint
- **THEN** the workflow redacts or rejects it before persistence

### Requirement: Reviewed version and scoped rollback state

The health report SHALL show approved, installed, and latest-known versions
separately for each managed CLI. A newer release MUST remain a review candidate
until compatibility evidence is accepted. Orchestration rollback SHALL remove
only its owned latest-evidence pointers while preserving historical runs,
skills, registrations, memories, indexes, hooks, guidance, credentials, and
application code. Managed-skill rollback and native-tool uninstall MUST remain
separate explicitly reviewed workflows and MUST NOT be invoked implicitly.

#### Scenario: A newer Graphify or agentmemory release is detected

- **WHEN** the update check reports a version newer than the approved pin
- **THEN** the report identifies the candidate and keeps current pins and
  generated surfaces unchanged

#### Scenario: Orchestration rollback is previewed

- **WHEN** a maintainer requests rollback
- **THEN** the owned latest-evidence pointers are the only proposed removals,
  every preserved state category is shown before mutation, and separate
  managed-skill/native-tool workflows are identified without being invoked

#### Scenario: Orchestration rollback is applied twice

- **WHEN** a maintainer applies the approved rollback more than once
- **THEN** both runs remain bounded and idempotent, only the owned latest-
  evidence pointers are absent, and historical evidence plus all separately
  owned tool, skill, hook, registration, memory, index, and source state remains
  unchanged

### Requirement: Explicit change-scope attribution

Implementation-profile evidence SHALL classify every current dirty path as
change-owned or unrelated for the selected OpenSpec change. The declared owned
scope MUST be machine-readable and MUST NOT include Go service, platform,
deployment, container, or nested-repository implementation paths for this
change. Unrelated dirty paths SHALL remain visible as contextual evidence but
MUST NOT be claimed as implementation output or mutated by the audit.

#### Scenario: Concurrent unrelated work is present

- **WHEN** the implementation profile runs in a worktree containing unrelated
  service, platform, deployment, or other OpenSpec changes
- **THEN** those paths are reported as unrelated, the audit remains read-only,
  and readiness depends on the declared change-owned scope rather than silently
  attributing the unrelated paths to this change

#### Scenario: A prohibited path is declared change-owned

- **WHEN** the selected change's owned-path policy includes a service, platform,
  deployment, container, or nested-repository implementation path
- **THEN** the scope audit is not healthy, implementation readiness is
  `not-ready`, and the conflicting path and remediation are reported

#### Scenario: Final scope evidence is retained

- **WHEN** implementation verification completes
- **THEN** the manifest references machine-readable evidence containing the
  selected change, owned paths, unrelated dirty paths, prohibited-prefix
  results, and exact source identity
