# Agent Framework Verification Specification

## Purpose

Define evidence, compatibility, rollback, and containment gates for cross-repository framework changes.
## Requirements
### Requirement: Corrective completion ledger

The workspace SHALL maintain an evidence-backed ledger for every archived completion claim found inconsistent with active specifications or implementation, without rewriting the archived record.

#### Scenario: Archived completion mismatch

- **WHEN** verification finds an archived task whose required behavior or evidence is incomplete
- **THEN** an active corrective task SHALL identify the archived task, current evidence, owning change, and required closure evidence
- **AND** the archived artifact SHALL remain unchanged

#### Scenario: Overlapping active change

- **WHEN** a corrective item overlaps an active change
- **THEN** exactly one active task SHALL own implementation
- **AND** the other change SHALL cross-reference that task rather than duplicate ownership

### Requirement: Evidence-gated task completion

A corrective task SHALL remain incomplete until its required behavior and verification evidence are reproducible from the current source state, including complete content identity and public-boundary semantics where the task affects a CLI or production composition.

#### Scenario: Required gate passes

- **WHEN** a task requires OpenSpec validation, formatting, linting, type checking, tests, compatibility analysis, restart verification, deployment inspection, or rollback evidence
- **THEN** the evidence manifest SHALL record the command, repository, relevant environment or fixture, result, and reproducible source identity
- **AND** the task MAY be marked complete only when every required gate passes

#### Scenario: Dirty source identity

- **WHEN** verification runs with tracked or untracked worktree changes
- **THEN** source identity SHALL include the repository `HEAD`, a hash of every production-relevant tracked and untracked file, and a sorted path inventory
- **AND** a commit hash alone SHALL NOT be accepted as the verified source state

#### Scenario: Required gate is skipped or unavailable

- **WHEN** a required gate is skipped, unavailable, stale, or fails
- **THEN** the owning task SHALL remain incomplete
- **AND** the blocker SHALL be recorded without substituting unit-test success for the missing evidence

#### Scenario: Later change invalidates evidence

- **WHEN** covered source, checkpoint semantics, planning requirements, deployment artifacts, or required backend assumptions change after a gate was recorded
- **THEN** every dependent completion and archive task SHALL be reopened
- **AND** the overlapping active change SHALL remain the sole implementation owner
- **AND** the corrective change SHALL consume refreshed evidence rather than duplicate implementation

### Requirement: Cross-repository compatibility gate

`agent-core`, `agent-docs-sync`, and `agent-harness` SHALL be verified together against the declared direct Pydantic AI, Pydantic AI Harness, and LangGraph compatibility matrix. The baseline SHALL use the frozen repository lockfiles, and the candidate row SHALL be a disposable fresh resolution within the existing declared dependency bounds.

#### Scenario: Framework boundary changes

- **WHEN** implementation changes lifecycle hooks, memory composition, agent construction, workflow routing, gates, checkpointers, or native graph validation
- **THEN** all three repository contract suites SHALL run against the same declared framework versions
- **AND** private upstream imports or attributes SHALL fail the gate

#### Scenario: Candidate resolution matches baseline

- **WHEN** the disposable candidate resolution produces the same framework versions as the frozen lockfiles
- **THEN** the evidence SHALL record that the matrix collapsed to one version tuple
- **AND** the candidate gate SHALL NOT claim coverage of an unavailable version

#### Scenario: Compatibility projection removal

- **WHEN** a legacy hook, memory, builder, or workflow projection is proposed for removal
- **THEN** production-caller analysis SHALL show no remaining caller
- **AND** rollback and migration instructions SHALL be verified before removal

### Requirement: High-risk change containment

HIGH or CRITICAL workflow-root changes SHALL be implemented incrementally behind characterization and negative-path tests.

#### Scenario: Critical root modification

- **WHEN** GitNexus rates an affected symbol HIGH or CRITICAL
- **THEN** its affected processes SHALL be listed in change evidence
- **AND** characterization tests SHALL pass before and after the modification
- **AND** post-change detection SHALL confirm that only intended symbols and processes changed

### Requirement: Three-repository major-feature verification matrix

Readiness for `agent-core`, `agent-docs-sync`, and `agent-harness` SHALL be
based on a reproducible matrix covering frozen dependency installation,
formatting, lint, strict typing, full tests, coverage, security rules, CLI
entrypoints, and each repository's major deterministic feature paths.

#### Scenario: Complete verification run

- **WHEN** the three-repository readiness gate runs
- **THEN** it SHALL exercise agent configuration/skills/scaffolding,
  docs discovery/audit/validation/canonical-pipeline behavior, and harness
  run/status/gate/report behavior
- **AND** it SHALL record command, exit status, coverage, skips, environment
  classification, and dirty source identity for every repository

#### Scenario: Required environment is unavailable

- **WHEN** PostgreSQL, gateway, or another required backend is unavailable
- **THEN** the affected check SHALL be classified as unavailable with its
  prerequisite
- **AND** a required check SHALL fail while only an explicitly optional check
  MAY skip
- **AND** overall readiness SHALL remain incomplete when the missing backend
  is required for a supported feature claim

#### Scenario: Code-intelligence evidence is stale

- **WHEN** GitNexus reports that an indexed commit differs from the repository
  commit being verified
- **THEN** impact and change-detection evidence SHALL be rejected as stale
- **AND** the repository SHALL be re-indexed before risk or affected-process
  counts are recorded

### Requirement: Real PostgreSQL harness lifecycle gate

The harness durability claim SHALL be verified against a disposable real
PostgreSQL backend using the shared `agent-core` checkpointer setup contract.
The test SHALL not use a production database or replace the real backend with
an in-memory double. The gate SHALL use a pinned Testcontainers PostgreSQL
backend by default while accepting an explicit `TDT_POSTGRES_TEST_URL` override.
The finalized baseline SHALL record `langgraph==1.2.9` and
`langgraph-checkpoint-postgres==3.1.0`, or explicitly identify a later resolved
version tuple.

#### Scenario: PostgreSQL test provider selection

- **WHEN** `TDT_POSTGRES_TEST_URL` is explicitly supplied
- **THEN** the lifecycle gate SHALL use that disposable backend
- **AND** otherwise it SHALL start a Testcontainers
  `postgres:18.4-trixie` backend and obtain a driverless psycopg 3-compatible
  connection URL
- **AND** when neither an explicit backend nor Docker-daemon access is
  available, the required gate SHALL fail rather than skip or use memory

#### Scenario: Durable approval across operating-system process restart

- **WHEN** a run pauses at a protected gate, the creating operating-system
  process terminates, and a separate process opens the same configured backend
- **THEN** the shared checkpointer boundary SHALL call its public setup contract
  before graph compilation
- **AND** status SHALL recover the same run and pending native interrupt
- **AND** an authorized approval SHALL resume the same thread
- **AND** completed stages SHALL not rerun

#### Scenario: Durable rejection and report

- **WHEN** an authorized rejection selects an allowed backtrack target
- **THEN** the decision SHALL be recorded once, execution SHALL resume only at
  the allowed target, and a later report process SHALL inspect the same thread

#### Scenario: Disposable database isolation

- **WHEN** the PostgreSQL lifecycle gate runs locally or in CI
- **THEN** it SHALL use unique database/schema/run identities and pass the same
  test DSN to every lifecycle subprocess
- **AND** Testcontainers-managed resources SHALL be cleaned up on success or
  failure and SHALL not be reused across verification runs
- **AND** credentials SHALL come from test environment configuration rather
  than committed files

### Requirement: Strict checkpoint serialization compatibility gate

The real PostgreSQL harness lifecycle gate SHALL enforce LangGraph strict
MessagePack deserialization in every subprocess and SHALL reject unregistered
custom checkpoint types, compatibility warnings, or unrestricted deserialization
configuration.

#### Scenario: Strict cross-process lifecycle passes

- **WHEN** the verification gate runs `run`, `status`, an authorized gate decision, and `report` in separate operating-system processes against the same disposable PostgreSQL backend
- **THEN** every process SHALL set `LANGGRAPH_STRICT_MSGPACK=true`
- **AND** all supported harness checkpoint values SHALL deserialize without unregistered-type warnings
- **AND** exact runtime type assertions SHALL prove that checkpointed artifact models and nested enums did not degrade to raw values
- **AND** the durable run SHALL preserve thread identity, native interrupt identity, gate history, and completed-stage execution counts

#### Scenario: Allowlist coverage regresses

- **WHEN** a checkpointed harness model or enum is added or changed without a corresponding exact trusted allowlist entry
- **THEN** the required real PostgreSQL verification gate SHALL fail
- **AND** readiness and archive completion SHALL remain incomplete

#### Scenario: Compatibility evidence records serializer policy

- **WHEN** three-repository verification evidence is refreshed after a checkpoint boundary change
- **THEN** it SHALL record the frozen LangGraph tuple, strict-mode environment, PostgreSQL provider, subprocess commands, standard-error warning check, and dirty source identity

### Requirement: Verification artifact hygiene

Verification SHALL leave tracked source state unchanged except for artifacts
explicitly produced by the change under test. Generated Python bytecode,
caches, coverage data, and temporary workspaces SHALL not appear as tracked
diffs or readiness evidence.

#### Scenario: CLI import generates bytecode

- **WHEN** verification imports a CLI or module
- **THEN** tracked `.pyc` and `__pycache__` files SHALL remain absent
- **AND** repository status after verification SHALL match the pre-run source
  identity apart from explicitly expected files

### Requirement: Semantic production-path readiness gate

Three-repository readiness SHALL prove that supported major behavior is reachable from public production composition and produces meaningful fixture evidence. Executing mocks, empty providers, hard-coded outcomes, contract shapes, or test-only factories SHALL NOT satisfy readiness.

#### Scenario: Docs-sync production lifecycle is verified

- **WHEN** the readiness matrix exercises docs-sync from public CLI subprocesses
- **THEN** it SHALL prove canonical configuration and option handling, zero-authority dry-run, authenticated approval interruption, separate-process resume, exactly-once bounded write, rediscovery, validation, and truthful reporting
- **AND** it SHALL use a disposable persistent step store beneath a temporary TDT home

#### Scenario: Harness production composition is verified

- **WHEN** the readiness matrix exercises harness run, status, gate decision, resume, and report paths
- **THEN** it SHALL prove that production stage services, read-only code-intelligence adapters, factory-owned Jira access, official stage-agent composition, evidence-based review, and artifact revisions are reachable from the public boundary
- **AND** the fixture SHALL fail on empty required evidence, hard-coded review, or a test-only composition root

#### Scenario: Required backend is unavailable

- **WHEN** a supported production claim requires PostgreSQL, a persistent step store, gateway behavior, or another backend that cannot be provisioned
- **THEN** the corresponding gate SHALL fail as unavailable with its prerequisite
- **AND** readiness SHALL remain incomplete rather than substituting an in-memory or mocked backend

#### Scenario: Static quality matrix runs

- **WHEN** final readiness is evaluated
- **THEN** every repository SHALL pass `uv sync --locked`, format, lint, strict source-plus-test typing, full tests, per-repository coverage, tracked-file secret scanning, and CLI subprocess checks
- **AND** no aggregate result SHALL conceal a failed, skipped, or stale required repository gate

### Requirement: Framework corrective closure evidence

The corrective ledger SHALL explicitly associate each inaccurate archived framework completion claim with its sole active remediation owner and SHALL close only after current, dependency-complete, public-boundary semantic evidence passes against a complete source manifest.

#### Scenario: Archived convergence claim is contradicted

- **WHEN** current source contradicts an archived claim of canonical docs-sync wiring, production harness integration, strict typing, or zero legacy callers
- **THEN** the ledger SHALL identify the archived artifact, current evidence, owning remediation change, and required closure gate
- **AND** the archived artifact SHALL remain unchanged

#### Scenario: Prerequisite remediation is incomplete

- **WHEN** any named runtime, security, identity-provider, evidence, documentation, or harness remediation is incomplete or its evidence is stale
- **THEN** recertification tasks SHALL remain incomplete
- **AND** this change SHALL not duplicate the prerequisite implementation

#### Scenario: Local-history sanitation exception is evaluated

- **WHEN** recertification evaluates the owner-approved docs-sync local-only retention exception
- **THEN** it SHALL validate the redacted schema and owner-only permissions of `$TDT_HOME/state/agent-docs-sync/security/local-history-sanitization.json`
- **AND** it SHALL require proof of no remotes, remote-tracking references, tags, secondary worktrees, known clones, bundles, backups, or external distributions; absence of the original commit/object; full-history scan success; centralized credential storage; and AgentMemory runtime verification
- **AND** it SHALL NOT read `$TDT_HOME/.env`, credential values, hashes or prefixes, provider token identifiers, or request/response bodies
- **AND** discovery of any external copy SHALL invalidate the exception and require rotation before readiness closes

#### Scenario: Source identity is recertified

- **WHEN** all prerequisite changes are complete
- **THEN** final evidence SHALL record each repository HEAD, the sorted production path set with per-file content digests including untracked production files, `uv sync --locked` dependency results, commands, exit status, skips, environment classification, and coverage
- **AND** the ratified GitNexus binding plus current source/index identity and bounded post-change detection SHALL match the source being certified without setup or index refresh

#### Scenario: Verification leaves residue

- **WHEN** the complete matrix finishes or fails
- **THEN** generated bytecode, caches, coverage files, disposable databases, step stores, and temporary TDT homes SHALL be removed or remain ignored outside tracked source
- **AND** post-run repository status SHALL match the recorded expected source identity

#### Scenario: Closure evidence is current

- **WHEN** a corrective item is reviewed for closure
- **THEN** its evidence SHALL identify the exact clean source manifest, public command, fixture, provider/actor binding, and result
- **AND** all prerequisite changes SHALL be complete

#### Scenario: Closure evidence is stale

- **WHEN** source, provider, actor policy, or required backend assumptions differ from the evidence
- **THEN** the item SHALL reopen and archive readiness SHALL fail

### Requirement: Attributable code-intelligence evidence

A verification gate that relies on GitNexus SHALL require a verified GitNexus `1.6.9` CLI/source/executable plus `tdt.gitnexus-cli.v1` adapter/schema/repository/source-revision binding and SHALL reject stale, ambiguous, truncated, or unbounded evidence. MCP availability SHALL NOT determine CLI gate availability.

#### Scenario: Impact evidence is current

- **WHEN** a code-intelligence gate records an impact or source query
- **THEN** the manifest SHALL include provider package/version/source revision, transport revision, schema ID/digest, explicit repository identity, indexed revision, freshness predicate, symbol UID or verified disambiguation, all query-defining fields, bounds, truncation status, and result digest
- **AND** the evidence MAY satisfy the gate only when the indexed revision equals the intended source and all identities and limits match the approved binding

#### Scenario: Binding cannot be verified

- **WHEN** any required identity, schema digest, query field, source equality, freshness predicate, or non-truncation proof is missing or ambiguous
- **THEN** the gate SHALL remain incomplete
- **AND** no guessed alias, empty result, stale output, ambiguous symbol, mutable version, or provider annotation SHALL satisfy it

