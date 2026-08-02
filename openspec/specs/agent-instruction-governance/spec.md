# Agent Instruction Governance Specification

## Purpose

Define deterministic, scoped, safe, and verifiable repository guidance for
agents working across the outer microservices workspace and the independent MCP
Router repository.

## Requirements

### Requirement: Layered repository guidance
The repository SHALL provide a non-empty root `AGENTS.md` and scoped
`AGENTS.md` files for `services/`, `platform/`, `deploy/`, `openspec/`, and
`scripts/`. The independent `mcp-router/` Git repository MUST provide its own
non-empty root `AGENTS.md`.

#### Scenario: Required guidance is present
- **WHEN** agent-instruction validation enumerates the workspace
- **THEN** it finds exactly one required guide at each governed scope
- **AND** every required guide contains a Markdown H1 and at least one scoped instruction section

#### Scenario: A scoped guide is missing
- **WHEN** any required guide is absent, empty, or unreadable
- **THEN** validation exits non-zero and identifies the missing scope without modifying the workspace

### Requirement: Deterministic instruction precedence
The guidance model SHALL apply broad repository instructions before the closest
applicable scoped instructions. A direct user instruction MUST take precedence
over project guidance, and scoped guidance MUST refine only the subtree it
governs.

#### Scenario: Service work receives layered guidance
- **WHEN** an agent starts work under `services/<service>/`
- **THEN** the effective project chain contains the outer root guide followed by `services/AGENTS.md`
- **AND** unrelated deployment, script, and platform guides are excluded

#### Scenario: Independent repository work receives local guidance
- **WHEN** an agent opens `mcp-router/` as its Git project
- **THEN** `mcp-router/AGENTS.md` is available as the repository-local guide
- **AND** its pnpm, Electron, MCP, and worktree rules do not depend on an outer scoped guide being loaded

#### Scenario: User direction conflicts with a guide
- **WHEN** an explicit user instruction conflicts with a project guide without violating a higher-level safety policy
- **THEN** the agent follows the user instruction and reports any resulting skipped repository check

### Requirement: Scope-owned operational content
Each guide SHALL state the scope it governs and MUST document the authoritative
commands, architecture or operational constraints, and focused verification
needed for that scope. The root guide SHALL remain a concise entry point rather
than duplicate every scoped rule.

#### Scenario: A contributor selects a focused check
- **WHEN** a contributor changes one service, the shared platform, deployment assets, an OpenSpec artifact, a script, or MCP Router
- **THEN** the nearest guide identifies a valid focused verification command for that scope
- **AND** it identifies the broader handoff gate when the change crosses scope boundaries

#### Scenario: A documented command drifts
- **WHEN** a guide references a missing Make target, package script, or repository path
- **THEN** validation exits non-zero and reports the guide, reference category, and unresolved name

### Requirement: Architecture and safety constraints remain local
Scoped guidance SHALL preserve the enforced boundaries of its subtree. Service
guidance MUST protect hexagonal layering, service-owned schemas, idempotency,
Temporal determinism, and schema-first generated contracts. Deployment and
script guidance MUST protect project-scoped cleanup, diagnostics-before-
teardown, GitOps ownership, non-local secret handling, bounded execution, and
redacted output.

#### Scenario: Service guidance is evaluated
- **WHEN** validation reads `services/AGENTS.md`
- **THEN** it confirms the guide covers service ownership, prohibited peer-internal imports, retry-safe side effects, generated contracts, and service-local verification

#### Scenario: Destructive operational guidance is evaluated
- **WHEN** validation reads `deploy/AGENTS.md` or `scripts/AGENTS.md`
- **THEN** it confirms destructive actions require explicit scope and validated targets
- **AND** failure investigation requires diagnostics before teardown where applicable

### Requirement: Generated instruction surfaces have one owner
The root and scoped guides SHALL distinguish hand-authored repository guidance
from bootstrap-created agentmemory wiring, mirrored OpenSpec skills and
commands, validation evidence, coverage output, and files declaring
`generatedBy`. Agents MUST change the canonical source or generator instead of
editing every generated copy.

#### Scenario: Generated copies are encountered
- **WHEN** an agent finds equivalent generated instructions under multiple client-specific directories
- **THEN** project guidance directs the agent to locate the canonical source or generator
- **AND** the agent does not independently patch the mirrored copies

#### Scenario: Generated ownership language is removed
- **WHEN** the root guide no longer distinguishes generated surfaces from hand-authored guidance
- **THEN** validation exits non-zero and reports a generated-ownership violation

### Requirement: Agent guidance validation is a PR gate
The repository SHALL expose a non-mutating `make validate-agent-guidance`
command and `make verify-pr` MUST run it. The validator SHALL enumerate all
required guides, evaluate expected discovery chains, validate owned references
and safety markers, and support deterministic machine-readable output.

#### Scenario: Guidance passes validation
- **WHEN** all required guides, discovery chains, references, content contracts, and safety rules are valid
- **THEN** `make validate-agent-guidance` exits zero
- **AND** its report identifies every evaluated guide and check

#### Scenario: Multiple guidance violations exist
- **WHEN** validation detects more than one missing, malformed, stale, unsafe, or contradictory guide condition
- **THEN** it reports all detected violations in one run
- **AND** each violation includes the guide or scope, category, and remediation
- **AND** no repository file or external system is changed

### Requirement: Credentials remain undisclosed
Agent guidance and its validation output MUST NOT contain or echo live tokens,
passwords, private keys, authenticated connection strings, or complete secret
values. Examples SHALL use placeholders or documented non-sensitive local
values.

#### Scenario: Credential-like text is detected
- **WHEN** validation finds a credential-like literal in a guide
- **THEN** it exits non-zero and reports only the file, line, and secret category
- **AND** it does not print the matched value

### Requirement: MCP health claims require live evidence
The MCP Router guide SHALL require end-to-end verification before an agent
reports MCP availability, authentication repair, or installed-app success.
Verification MUST cover tool and resource discovery, configured server
identity, process and listener state, authentication, and an MCP endpoint
handshake. A restart or configuration file alone MUST NOT establish success.

#### Scenario: MCP availability is confirmed
- **WHEN** an agent reports that MCP Router is usable
- **THEN** the report is based on a successful live handshake and tool or resource discovery in addition to process and configuration checks
- **AND** no credential value is exposed

#### Scenario: Only the process restarts
- **WHEN** MCP Router restarts but authenticated initialization or discovery has not succeeded
- **THEN** the agent reports verification as incomplete or failed rather than declaring the router usable

### Requirement: Existing worktree changes remain user-owned
Agents applying or validating repository guidance MUST preserve pre-existing
worktree changes in both the outer repository and the nested MCP Router
repository.

#### Scenario: Guidance is changed in a dirty worktree
- **WHEN** unrelated files are already modified or untracked
- **THEN** the agent limits edits, formatting, staging, and diff review to the requested guidance and validation files
- **AND** unrelated changes remain byte-for-byte untouched
