## Why

TDT already has `agent-harness`, a production-oriented planning runtime built on
agent-core, LangGraph, typed checkpoints, and PostgreSQL. Some teams and interview
or evaluation environments need a separate, dependency-light alternative that can
run locally through native coding-agent CLIs and expose the same workflow through
portable Agent Skills.

This change creates that alternative. It does not replace, extend, or share runtime
state with `agent-harness`.

## What Changes

### New: Standalone 13-Stage Planning Workflow

Create a standalone workflow that turns a vague engineering ticket into grounded,
traceable planning artifacts:

1. INTAKE
2. CONTEXT
3. CLARIFY
4. SPEC
5. IMPACT
6. DESIGN
7. API_CONTRACT
8. IMPL_PLAN
9. CODING_PLAN
10. PLAN_REVIEW
11. TEST_CASES
12. AUTO_TEST_PLAN
13. VERIFY

The workflow is planning-only. `PLAN_REVIEW` reviews the proposed delivery plan;
`VERIFY` verifies artifact completeness, evidence, and traceability. Neither stage
claims to review or verify implemented source code.

### New: Two Execution Modes

- **Guided mode** — a user invokes portable Agent Skills inside a supported coding
  agent. The host agent performs the stage while the harness CLI controls state,
  validation, and artifact persistence.
- **Headless mode** — the harness CLI invokes a supported native coding-agent CLI
  through a provider adapter and requires schema-validated structured output.

Initial automated provider support is limited to Claude Code and Codex. Other Agent
Skills hosts, including Cursor and Gemini CLI, are guided or experimental until
their headless output and permission contracts pass adapter conformance tests.

### New: Portable Skill Interface

Provide three portable, feature-based skills following the Agent Skills
specification:

- `harness-workflow` for starting, inspecting, and running the 13-stage workflow;
- `harness-gates` for approval, rejection, and backtracking procedures;
- `harness-traceability` for evidence links, stable identifiers, and coverage.

The portable skills contain standard Agent Skills metadata and explicit CLI
instructions. Platform-specific behavior such as Claude subagent context, argument
substitution, dynamic context injection, model selection, or invocation policy
lives only in platform adapters or overrides.

### New: Native CLI Provider Adapters

Provide a typed provider boundary for native agent execution:

- Claude Code adapter using headless mode, direct agent selection, permission
  controls, and JSON Schema output validation.
- Codex adapter using `codex exec`, sandbox controls, JSON Schema output
  validation, and session identifiers. Codex custom agent files are optional
  guided-mode enhancements rather than a required headless execution mechanism.
- Capability discovery that fails closed when a provider lacks required structured
  output or permission controls.

### New: OpenSpec Artifact Workflow

Provide a project-local `harness-13` OpenSpec schema containing the 13 artifact
definitions, dependency graph, templates, and stage instructions.

OpenSpec owns artifact readiness and schema metadata. Harness runtime state is kept
in a separate versioned run ledger and is not embedded in `.openspec.yaml`.

### New: Versioned Run Ledger and Human Gates

Persist run state, provider session identifiers, stage revisions, artifact digests,
gate decisions, clarification requests, and backtrack history in a harness-owned
run ledger.

- Writes are atomic and recoverable.
- Backtracking creates new revisions and marks downstream artifacts superseded
  instead of deleting audit history.
- `CLARIFY` can enter `needs-input` and wait for human answers.
- Gate commands are resumable and do not require a long-running interactive
  process.

### New: Evidence and Traceability Contract

Provider outputs use schema-validated claim types:

- `observed`
- `proposed`
- `assumption`
- `decision`

Observed claims reference immutable evidence identifiers. Requirements, decisions,
API changes, tasks, and tests use stable identifiers such as `REQ-001`, `DES-001`,
`API-001`, `TASK-001`, and `TC-001`. Verification builds a traceability matrix from
these identifiers rather than mutable Markdown line numbers.

### New: Explicit Installation Channels

Installation is split by responsibility:

- Python/CLI installation through `uv`.
- Portable skill installation through `npx skills`.
- OpenSpec schema and platform-specific agent installation through an explicit,
  idempotent `harness init` command with dry-run and conflict detection.

`npx skills` is not expected to install the Python CLI, OpenSpec schemas, or native
agent definitions.

## Capabilities

### New Capabilities

- `harness-workflow`: Standalone skill-first and native-CLI-agent planning workflow,
  including provider adapters, execution modes, state, gates, artifact revisions,
  evidence, traceability, packaging, and installation.

### Modified Capabilities

None. This alternative does not modify the requirements or runtime behavior of
`agent-harness`, `agent-core`, or existing OpenSpec workflows.

## Impact

- **New repository:** `ai-harness-skills/`, developed locally before internal
  distribution.
- **Existing repositories:** No runtime or source-code changes to `agent-harness`
  or `agent-core`.
- **Python:** Python 3.14 package managed exclusively with `uv`.
- **Dependencies:** Typer, PyYAML, and jsonschema are approved runtime dependencies.
- **External tools:** OpenSpec plus at least one supported native provider CLI.
- **Project initialization:** May create a project-local OpenSpec schema and
  platform agent definitions only through explicit `harness init`.
- **Public interfaces:** Harness CLI commands, portable skills, provider adapter
  contract, run-ledger schema, and artifact schemas.
- **Mobile applications:** No direct impact.

## Non-goals

- Replacing, migrating, or extending `agent-harness`
- Depending on agent-core, LangGraph, Pydantic AI, DBOS, or PostgreSQL
- Sharing runtime state or checkpoints with `agent-harness`
- Editing application source code or executing an implementation
- Claiming automated support for every host supported by `npx skills`
- Treating Agent Skills metadata as a cross-platform security boundary
- Installing arbitrary project configuration implicitly through `npx skills`
- Remote/public marketplace distribution in the initial phase
