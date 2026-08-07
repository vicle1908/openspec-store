# agent-docs-sync Specification

## Purpose

Define the supported deterministic documentation discovery, audit, generation,
validation, and reporting boundary for `agent-docs-sync`.
## Requirements
### Requirement: One canonical docs-sync pipeline

`agent-docs-sync` SHALL expose one supported deterministic pipeline for discover, audit, optional generation, validation, and reporting.

#### Scenario: Public CLI

- **WHEN** `check`, `discover`, `update`, `sync`, `audit`, or `sync-all` is invoked
- **THEN** each command SHALL route to the documented canonical pipeline or one of its explicit deterministic stages

#### Scenario: Agent participation

- **WHEN** generation or adaptive classification requires an LLM
- **THEN** the canonical pipeline SHALL invoke an agent at that bounded stage
- **AND** deterministic scanning, persistence, validation, and report formatting SHALL remain non-agent steps

#### Scenario: Deprecated pipeline

- **WHEN** a caller uses a legacy discovery, sync, full, or dynamic pipeline entry point during the migration window
- **THEN** it SHALL delegate to the canonical implementation or emit a migration error
- **AND** it SHALL not maintain independent behavior

### Requirement: One canonical agent builder

The consumer SHALL own one agent composition builder that receives the model, tools/toolsets, capabilities, hooks/policy callbacks, memory, and mode-specific instructions explicitly.

#### Scenario: Supplied registry

- **WHEN** a caller supplies a tool registry or toolset
- **THEN** the builder SHALL use it
- **AND** it SHALL not construct and silently substitute another registry

#### Scenario: Mode-specific policy

- **WHEN** check, generate, or full-sync mode is selected
- **THEN** the builder SHALL derive least-privilege tools and instructions for that mode through run-scoped composition

#### Scenario: Shared observability

- **WHEN** multiple docs-sync agents are built
- **THEN** they SHALL use the same official lifecycle and TDT observability policy
- **AND** hook packs SHALL not be registered repeatedly by every builder

### Requirement: Consumer migration verification

The migration SHALL prove behavioral parity and deletion of redundant implementation paths.

#### Scenario: End-to-end parity

- **WHEN** the canonical pipeline runs against a fixture repository
- **THEN** it SHALL produce the expected discovery, audit, generation decision, validation, and report artifacts

#### Scenario: Dead implementation paths

- **WHEN** migration is complete
- **THEN** deprecated duplicate pipeline and builder modules SHALL have no production callers
- **AND** GitNexus/Graphify analysis SHALL confirm the intended canonical path

### Requirement: Production documentation discovery boundary

By default, docs-sync discovery and audit SHALL scan production source while
deriving actionable documentation obligations from package exports, configured
console-script/CLI entrypoints, deployment and configuration artifacts, and
explicit documentation mappings. Tests, virtual environments, caches,
generated artifacts, and repository metadata SHALL be excluded unless an
explicit option requests them. Unexported production internals SHALL remain
visible in scan evidence but SHALL be informational unless explicitly mapped.
Explicit directory mappings SHALL apply to descendant files using deterministic
most-specific-prefix precedence, while an exact file mapping SHALL remain
authoritative.

#### Scenario: Default repository discovery

- **WHEN** `docs-sync discover` scans a Python repository with default options
- **THEN** scan evidence SHALL include production source modules and
  documentation files
- **AND** actionable mappings SHALL identify their public-surface provenance
  as export, CLI entrypoint, deployment/config artifact, or explicit mapping
- **AND** tests, `.venv`, `__pycache__`, `.pyc`, coverage output, and generated
  build directories SHALL not be classified as documentation needs

#### Scenario: Internal production module has no explicit mapping

- **WHEN** an unexported production module is not a CLI/deployment/config
  surface and has no explicit documentation mapping
- **THEN** its scan finding SHALL be retained as informational evidence
- **AND** absence of a one-to-one document SHALL not count as an actionable gap

#### Scenario: Explicit test-source discovery

- **WHEN** a caller explicitly enables test or internal source discovery
- **THEN** those files MAY be classified
- **AND** the report SHALL identify that non-default boundary

#### Scenario: Explicit directory mapping covers descendants

- **WHEN** a source file is a descendant of one or more configured directory mappings
- **THEN** the most-specific matching directory mapping SHALL determine its target documentation
- **AND** an exact file mapping SHALL take precedence over directory mappings

### Requirement: Truthful audit outcome contract

Docs-sync audit results SHALL distinguish successful execution from
documentation compliance. The report SHALL expose stable counts for actionable
gaps, excluded findings, broken links, and Diataxis violations. A strict mode
SHALL fail when actionable compliance findings remain or execution does not
complete successfully. A discovery failure SHALL NOT be represented as a
successful empty scan.

#### Scenario: Audit completes with gaps

- **WHEN** scanning succeeds but actionable documentation gaps or Diataxis
  violations are found
- **THEN** execution SHALL be reported as successful
- **AND** documentation compliance SHALL be reported as failed
- **AND** the result SHALL not use one ambiguous `validation_passed=true` field
  to represent both outcomes

#### Scenario: Strict audit has findings

- **WHEN** `docs-sync audit --strict` finds actionable gaps, broken local links,
  or Diataxis violations
- **THEN** the command SHALL return non-zero with deterministic finding counts

#### Scenario: Strict audit discovery fails

- **WHEN** `docs-sync audit --strict` cannot discover the requested repository
- **THEN** the report SHALL set `execution_succeeded` to false
- **AND** the command SHALL return non-zero rather than reporting an empty compliant scan

#### Scenario: Informational audit has findings

- **WHEN** audit runs without strict mode and finds actionable gaps
- **THEN** it MAY return zero to support reporting workflows
- **AND** the JSON compliance field SHALL still be false

#### Scenario: Compatibility alias during migration

- **WHEN** audit JSON is emitted during the first compatibility release
- **THEN** `validation_passed` SHALL remain present as a deprecated alias of
  `documentation_compliant`
- **AND** it SHALL NOT represent `execution_succeeded`
- **AND** the alias SHALL be removed after that one compatibility release

### Requirement: Documentation cache artifact exclusion

The docs-sync repository and scanners SHALL exclude generated Python bytecode
and cache directories from source control, discovery, audit, and generated
documentation mappings.

#### Scenario: Python CLI execution creates cache files

- **WHEN** a docs-sync CLI command imports package modules
- **THEN** `.pyc` files and `__pycache__` directories SHALL remain ignored and
  untracked
- **AND** they SHALL not alter the verification diff

### Requirement: Canonical configuration and CLI truthfulness
`agent-docs-sync` SHALL load one documented repository-root configuration schema, validate unknown or legacy keys, and ensure every public CLI option either changes canonical execution or is removed with migration guidance.

#### Scenario: Repository configuration is loaded
- **WHEN** a public docs-sync command runs for a repository
- **THEN** configuration SHALL resolve from the documented repository root and centralized TDT environment boundary
- **AND** committed configuration SHALL contain no credential literal

#### Scenario: Unsupported configuration section
- **WHEN** configuration contains an unknown or legacy section that is not supported by the canonical schema
- **THEN** validation SHALL fail before model, persistence, or write-capable tool construction
- **AND** the error SHALL identify the supported replacement without echoing protected values

#### Scenario: Public option is accepted
- **WHEN** `base-ref`, `full`, LLM classification, override review, durability, or another documented option is accepted
- **THEN** the resulting execution plan and report SHALL record the option's effective behavior
- **AND** the command SHALL NOT discard the value through a compatibility placeholder

#### Scenario: Deprecated option is removed
- **WHEN** an option cannot be supported by the canonical pipeline
- **THEN** it SHALL be removed or rejected with an actionable migration error
- **AND** help output and tests SHALL not continue to advertise ignored behavior

### Requirement: Zero-authority dry-run and bounded writes
Dry-run execution SHALL be structurally unable to write. Normal generation SHALL expose write-capable tools only for explicitly configured documentation roots, and source or OpenSpec promotion SHALL require a separate authority mode and policy review.

#### Scenario: Dry-run composition
- **WHEN** a command runs with `--dry-run`
- **THEN** `WriteDocTool`, `SyncSpecTool`, and any equivalent mutation capability SHALL be absent from the effective registry and toolsets
- **AND** the report SHALL list proposed changes without filesystem mutation

#### Scenario: Documentation write is approved
- **WHEN** an authorized approval resumes a pending documentation write
- **THEN** the normalized target SHALL remain under an allowed documentation root
- **AND** the approved path, operation, and content digest SHALL match the pending request

#### Scenario: Source or OpenSpec write is requested
- **WHEN** normal docs-sync generation targets Python source or `openspec/specs/`
- **THEN** path policy SHALL deny the write
- **AND** the diagnostic SHALL require the separate OpenSpec/code-change workflow rather than broadening normal roots

#### Scenario: Path changes before continuation
- **WHEN** symlink resolution or repository state causes an approved path to resolve outside its authorized root at resume time
- **THEN** the write SHALL fail closed before creating directories or files
- **AND** the decision SHALL remain auditable without recording a successful write

### Requirement: Restart-safe approval lifecycle

Generation approvals SHALL persist through an upstream persistent step store and SHALL be manageable through authenticated pending, list, approve, deny, and resume lifecycle commands that reconstruct the same agent and store after process restart. Caller-supplied actor text SHALL NOT be an authentication source.

#### Scenario: Approval interrupts generation

- **WHEN** a write-capable tool requests approval
- **THEN** docs-sync SHALL persist the continuable run identifier, pending request, tool arguments digest, repository identity, and expiry metadata
- **AND** the initiating command SHALL return a stable pending identifier without discarding the request

#### Scenario: Authorized approval after restart

- **WHEN** a separately started process resolves an authenticated actor authorized by policy and approves an unexpired pending request with its unique operation-bound nonce
- **THEN** it SHALL reconstruct the agent with the same persistent store and resume the same upstream run
- **AND** it SHALL revalidate authentication freshness, revocation, assurance, operation identity, and policy generation immediately before the exactly-once write transition
- **AND** completed model/tool steps SHALL not be replayed

#### Scenario: Self-asserted actor is rejected

- **WHEN** a caller supplies an allowlisted actor string without a matching authenticated subject
- **THEN** approval SHALL fail before the pending request changes
- **AND** the string SHALL not appear as an authenticated approver in audit evidence

#### Scenario: Denial after restart

- **WHEN** an authenticated authorized actor denies a pending request
- **THEN** the denial SHALL be persisted exactly once and the write SHALL not execute
- **AND** subsequent resume attempts SHALL report the terminal denial

#### Scenario: Invalid lifecycle actor or request

- **WHEN** an actor is unauthorized, a request is expired, or repository/tool/path/content identity differs from the pending request
- **THEN** lifecycle resolution SHALL fail closed before continuation
- **AND** no approval or successful write event SHALL be recorded

#### Scenario: Persistent store is unavailable

- **WHEN** durable generation is requested but its configured store is unavailable
- **THEN** preflight SHALL fail before model or write-tool execution
- **AND** the command SHALL not substitute in-memory continuation

### Requirement: Idempotent write, rediscovery, and truthful reporting
The canonical pipeline SHALL apply each approved write at most once, rediscover repository state after writes, validate the rediscovered state, and report execution, compliance, approval, and mutation outcomes separately.

#### Scenario: Approved write executes once
- **WHEN** continuation delivers the same approved tool call more than once
- **THEN** a ledger keyed by run, continuation/tool-call identity, normalized path, operation, and content digest SHALL permit at most one mutation
- **AND** later deliveries SHALL return the recorded result without rewriting content

#### Scenario: Generated file is rediscovered
- **WHEN** generation creates or updates documentation
- **THEN** discovery SHALL run against the resulting repository state before validation
- **AND** validation and report artifacts SHALL reference the post-write source identity

#### Scenario: Write succeeds but compliance fails
- **WHEN** an approved mutation succeeds but rediscovery or validation finds remaining gaps
- **THEN** execution and write status SHALL be successful while documentation compliance SHALL be false
- **AND** the command SHALL not collapse those outcomes into one passing field

#### Scenario: Legacy implementation path remains
- **WHEN** migration is declared complete
- **THEN** production-caller analysis SHALL show that legacy discovery, generation, memory, and builder paths delegate to the canonical implementation or fail with migration guidance
- **AND** no independent placeholder generation behavior SHALL remain reachable from a public CLI

### Requirement: Current documented docs-sync surface

The canonical docs-sync documentation SHALL describe only supported lifecycle, configuration, installation, and CLI behavior and SHALL identify migration paths for removed interfaces.

#### Scenario: Documentation reference is checked

- **WHEN** documentation CI scans examples and CLI references
- **THEN** every referenced option and API SHALL exist or have an explicit migration diagnostic
- **AND** installation guidance SHALL use the approved uv workflow

#### Scenario: Ignored behavior is documented

- **WHEN** a document describes an option that the canonical pipeline ignores
- **THEN** the documentation check SHALL fail until the option is implemented or removed with migration guidance

### Requirement: Consumer imports use SDK facade only

agent-docs-sync SHALL import all agent-core symbols through `agent_core.sdk`,
never from internal modules like `agent_core.agent_base`,
`agent_core.foundation.settings`, or `agent_core.lifecycle_identity`.

#### Scenario: No non-SDK imports at runtime
- **WHEN** an AST-based check scans all `agent_docs_sync` Python files for `from agent_core.*` imports
- **THEN** every import SHALL be from `agent_core.sdk` only
- **AND** no imports SHALL reference `agent_core.agent_base`, `agent_core.foundation`, or `agent_core.lifecycle_identity`

#### Scenario: Import check catches aliases and bare imports
- **WHEN** a file uses `import agent_core.lifecycle_identity as lifecycle` or `from agent_core.foundation import settings`
- **THEN** the AST-based check SHALL flag these as violations

