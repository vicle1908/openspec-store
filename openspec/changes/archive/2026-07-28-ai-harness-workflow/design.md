## Context

TDT has an existing `agent-harness` repository for production-oriented planning
workflows. It uses agent-core, Pydantic AI, LangGraph, typed checkpoints, and
PostgreSQL. That system is intentionally durable, policy-rich, and TDT-specific.

This change provides a separate alternative for local development, interviews,
evaluations, and teams that want a smaller operational footprint. The alternative
uses portable Agent Skills for its user-facing workflow and delegates model work to
native coding-agent CLIs such as Claude Code and Codex. A Python CLI owns the stage
machine, validation, artifacts, gates, and run history.

The two products share a problem domain but do not share implementation, runtime
state, checkpoints, or public APIs:

| Concern | `agent-harness` | `ai-harness-workflow` |
|---|---|---|
| Runtime | Embedded agent frameworks and LangGraph | Native coding-agent CLI subprocesses |
| Persistence | Typed checkpoints and PostgreSQL | Local SQLite run ledger |
| Interface | TDT-specific CLI and runtime | Portable skills plus standalone CLI |
| Policy | agent-core gateway and typed toolsets | Process, sandbox, path, and output controls |
| Target | Durable TDT orchestration | Local-first portable planning workflow |

The workflow is planning-only. It produces requirements, context, design, API,
implementation-plan, review, test, and verification artifacts, but does not edit
application source or execute the proposed implementation.

### Validated external constraints

- Agent Skills standardizes skill metadata and Markdown instructions. Host-specific
  fields and dynamic command syntax are not portable policy controls.
- `npx skills` installs discovered skill directories. It does not install the Python
  CLI, an OpenSpec schema, or repository-root native agent definitions.
- Claude Code supports non-interactive execution, direct custom-agent selection,
  permission controls, sessions, and JSON Schema output validation.
- Codex supports non-interactive execution, read-only sandboxing, sessions, project
  custom subagents, and JSON Schema output validation. `codex exec` does not expose
  a direct named-agent selector, so headless execution cannot depend on one.
- Cursor supports Agent Skills and headless JSON output, but its structured-output
  validation and write-authority guarantees differ from Claude and Codex.
- OpenSpec owns `.openspec.yaml`. OpenSpec 1.6 parses a closed metadata shape and
  strips unknown fields when it rewrites change metadata.

### Repositories and ownership

- Planning artifacts for this change remain in `tdt-meta`.
- Implementation will create a new standalone repository, initially named
  `ai-harness-skills/`.
- `agent-harness/` and `agent-core/` are reference systems only and SHALL NOT be
  modified by this change.
- The new repository SHALL use Python 3.14 and `uv` exclusively.

## Goals / Non-Goals

**Goals:**

- Implement an exact 13-stage planning workflow backed by OpenSpec artifacts.
- Offer guided execution through portable Agent Skills.
- Offer headless execution through capability-tested Claude Code and Codex adapters.
- Keep the Python CLI authoritative for transitions, gates, revisions, and writes.
- Ground observed claims in immutable evidence and provide stable traceability IDs.
- Support human clarification, approval, rejection, resume, and backtracking without
  requiring a long-running process.
- Remain dependency-light and usable without agent-core, LangGraph, or PostgreSQL.
- Fail closed when a provider lacks required structured output or permission controls.
- Install skills, the CLI, OpenSpec schemas, and native agents through explicit,
  separately testable channels.

**Non-Goals:**

- Replacing, extending, or migrating `agent-harness`.
- Sharing state, artifacts, checkpoints, or compatibility contracts with
  `agent-harness`.
- Editing application source, creating branches or commits, or running an
  implementation.
- Treating skill metadata or natural-language instructions as a security boundary.
- Automated headless support for every host recognized by `npx skills`.
- A daemon, scheduler, Docker service, launchd service, or remote orchestration API.
- Public marketplace distribution in the initial release.
- Automatic provider installation, authentication, or credential management.

## Architecture

```text
User or coding-agent host
          |
          v
Portable feature-based skill
          |
          v
Standalone harness CLI ---------------- OpenSpec harness-13 schema
  |          |             |             templates + artifact DAG
  |          |             |
  |          |             +---------- Evidence/trace validator
  |          +------------------------ SQLite run ledger
  +----------------------------------- Provider adapter
                                          |-- Claude Code CLI
                                          |-- Codex CLI
                                          `-- Guided/experimental hosts
```

### Component boundaries

| Component | Responsibility | Must not do |
|---|---|---|
| Portable skills | Discoverability, user guidance, feature-scoped CLI invocation | Own state, validation, artifact templates, or provider-specific policy |
| Harness CLI | State machine, gates, provider calls, validation, rendering, writes | Perform model reasoning itself |
| OpenSpec adapter | Schema installation, change creation, artifact readiness | Store volatile run state |
| Provider adapter | Capability probe, safe process invocation, structured response parsing | Advance workflow state or write artifacts |
| Run ledger | Transactional run, stage, gate, session, revision, and event records | Store secrets or full prompts |
| Artifact store | Immutable revisions and current OpenSpec materialization | Accept unvalidated provider output |
| Evidence validator | Resolve evidence IDs, digests, freshness, and traceability | Decide business requirements autonomously |

## Decisions

### 1. The CLI Owns Orchestration

**Decision:** The Python CLI is the only authority allowed to advance a run, record
a gate decision, create a revision, or materialize a current artifact.

**Rationale:** Agent Skills are reusable instructions loaded by a host agent; they
are not stable executable workflow nodes. Giving skills or provider agents direct
state ownership would make transitions depend on host-specific behavior.

**Alternatives considered:**

- **Skill-owned orchestration:** Rejected because it cannot guarantee atomic state,
  restart recovery, or consistent gates across hosts.
- **Embedded LLM SDK:** Rejected because this alternative intentionally delegates to
  already-installed native coding-agent CLIs.

The core command surface is:

```text
harness init
harness doctor
harness start
harness run
harness next
harness status
harness stage begin
harness stage complete
harness answer
harness approve
harness reject
harness backtrack
harness report
```

Commands SHALL support human-readable output and a JSON mode with stable exit codes.

### 2. Guided and Headless Execution Are Separate Modes

**Decision:** The same workflow supports two execution modes with the same stage
result schema and validation boundary.

#### Guided mode

1. A user invokes a portable feature-based skill in a host agent.
2. The skill calls `harness stage begin --json`.
3. The CLI returns the current stage instruction, bounded evidence bundle, output
   schema, and run identity.
4. The host agent produces a structured result.
5. The skill submits the result through `harness stage complete`.
6. The CLI validates and persists the result before advancing.

Guided host output is untrusted. The CLI applies the same structural, evidence, and
traceability validation as headless mode.

#### Headless mode

1. The CLI resolves the configured provider adapter.
2. The adapter probes the installed CLI for required capabilities.
3. The CLI builds a stage request from the OpenSpec instruction, evidence manifest,
   upstream artifact IDs, and output schema.
4. The adapter invokes the provider process with bounded permissions and budgets.
5. The CLI validates the structured response and persists a revision.

Headless runs SHALL exit when waiting for clarification or approval. They SHALL NOT
block indefinitely for terminal input.

### 3. Providers Implement a Capability Contract

**Decision:** Provider support is based on runtime capability probes and adapter
conformance, not marketing support lists or version-string comparisons alone.

Conceptual provider types:

```text
ProviderCapabilities
  structured_output: bool
  read_only_mode: bool
  session_resume: bool
  direct_agent_selection: bool
  event_stream: bool
  cost_budget: bool

StageRequest
  run_id
  stage_id
  working_directory
  instruction
  evidence_manifest
  upstream_artifacts
  output_schema
  limits

StageResult
  provider
  provider_session_id
  stage_id
  status
  structured_output
  usage
  diagnostics
```

The adapter SHALL reject a stage before model execution when a required capability
is missing.

#### Claude Code adapter

The adapter uses non-interactive execution with:

- direct agent selection when a generated Claude agent is configured;
- JSON Schema output validation;
- JSON or streaming JSON output;
- explicit permission mode and allowed/disallowed tools;
- session identifiers and bounded resume;
- a provider-supported cost limit when configured.

Planning roles SHALL not receive Edit or unrestricted Bash authority. The CLI, not
the provider agent, writes artifacts.

#### Codex adapter

The adapter uses `codex exec` with:

- `--sandbox read-only` for every planning stage;
- `--output-schema` for the final structured response;
- JSONL events when diagnostics or progress are requested;
- an explicit working directory;
- session identifiers and bounded resume.

Codex project agents are subagent configuration layers. Because `codex exec` has no
direct named-agent selector, the adapter SHALL NOT require a custom Codex agent for
headless execution. Stage instructions and CLI configuration define the root
session. Generated `.codex/agents/*.toml` files are optional guided-mode helpers.

#### Other hosts

Cursor, Gemini CLI, Copilot, and other Agent Skills hosts begin in guided mode.
Headless support requires a provider adapter proving:

- deterministic success/failure signaling;
- parseable final output;
- schema enforcement or equivalent local validation;
- enforceable read-only behavior;
- bounded sessions, timeouts, and cancellation.

Support tiers are reported by `harness doctor`:

| Tier | Meaning |
|---|---|
| Automated | Headless adapter passes all required conformance checks |
| Guided | Portable skills work; host performs stage reasoning interactively |
| Experimental | Adapter exists but lacks one or more production guarantees |
| Unsupported | Required skill or CLI behavior is unavailable |

### 4. Portable Skills Contain Only Portable Behavior

**Decision:** The source repository exposes a feature-based skill set:

```text
skills/
  harness-workflow/    # Workflow guidance and lifecycle command mapping
  harness-gates/       # Gate management (approval, rejection, backtrack)
  harness-traceability/ # Traceability system (links, matrix, validation)
```

**Why feature-based (not function-based):**
- Follows agentskills.io principle: "One skill, one procedure"
- Follows agentskills.io principle: "Skills are passive, not agentic"
- Follows agentskills.io finding: "Focused skills outperform comprehensive ones"
- Gates and traceability are reusable across different workflows
- Distinct trigger boundaries for workflow use, gate decisions, and traceability
- Independent installation and validation for each reusable procedure
- Smaller host context than duplicating the full CLI and OpenSpec contracts

**Skill architecture:**

```text
skills/
  harness-workflow/
    SKILL.md                    # Orchestrator instructions
    references/
      stages.md                 # Non-authoritative stage purpose map
      anti-hallucination.md     # Anti-hallucination guide
      gotchas.md                # Common mistakes to avoid
      commands.md               # CLI lifecycle command mapping

  harness-gates/
    SKILL.md                    # Gate management instructions
    references/
      gate-policies.md          # Gate configuration
      approval-patterns.md      # How to review artifacts

  harness-traceability/
    SKILL.md                    # Traceability instructions
    references/
      traceability-format.md    # Link format
      traceability-matrix.md    # Matrix examples
```

The core `SKILL.md` files use standard Agent Skills metadata and explicit CLI
instructions. They SHALL NOT require:

- Claude-only `context`, `agent`, invocation, or argument behavior;
- dynamic shell injection syntax;
- model names;
- host-specific tool names as a security control.

**Knowledge vs Orchestration separation:**
- Skills provide KNOWLEDGE (how to do things correctly)
- CLI provides ORCHESTRATION (when to do things, state management)
- Skills are passive; CLI is active
- OpenSpec resources provide the authoritative stage instructions, schemas, and
  templates; skill references are explanatory and MUST NOT duplicate them.

Optional platform layers may add:

```text
adapters/claude/agents/*.md
adapters/claude/skill-overrides/*
adapters/codex/agents/*.toml
```

Native agent roles are intentionally small:

| Role | Purpose | Authority |
|---|---|---|
| researcher | Context and impact evidence | Read-only |
| writer | Spec, design, API, and planning synthesis | Read-only; result via stdout |
| verifier | Review, test, and traceability validation | Read-only |

### 5. The Workflow Uses an Exact 13-Stage Sequential DAG

**Decision:** The initial topology is sequential:

```text
INTAKE
  -> CONTEXT
  -> CLARIFY
  -> SPEC [gate]
  -> IMPACT
  -> DESIGN [gate]
  -> API_CONTRACT
  -> IMPL_PLAN [gate]
  -> CODING_PLAN
  -> PLAN_REVIEW [gate]
  -> TEST_CASES
  -> AUTO_TEST_PLAN
  -> VERIFY
```

Stage identifiers, not ordinal numbers, are authoritative.

`PLAN_REVIEW` reviews consistency, feasibility, risk, and testability of the
planning artifacts. `VERIFY` verifies evidence, schema, and traceability coverage.
Neither claims that implementation code exists.

If a stage is irrelevant, it produces a validated artifact with
`applicability: not_applicable`, a rationale, and evidence. Skipping a file entirely
would make dependency and traceability behavior ambiguous.

#### Clarification interrupt

`CLARIFY` returns one of:

- `resolved` — all material ambiguities are resolved by existing evidence;
- `needs_input` — human answers are required;
- `blocked` — the required authority or source is unavailable.

For `needs_input`, the CLI records questions, exits with a stable waiting status,
and resumes only after `harness answer` records a response. The provider SHALL NOT
invent answers to unresolved business questions.

### 6. Parallelism Is Bounded Within a Stage

**Decision:** `IMPACT` and `DESIGN` are sequential because design consumes impact.
The initial workflow exposes no stage-level fan-out.

Bounded parallel work is permitted inside selected stages:

- independent repository evidence queries in `CONTEXT`;
- independent blast-radius queries in `IMPACT`;
- independent critic passes in `PLAN_REVIEW`.

Each fan-out declares a concurrency limit, timeout, cancellation policy, isolated
result files, and deterministic merge order. Partial failure either produces an
explicit partial result or fails the stage; it never silently advances.

**Alternative considered:** Configuration-only stage parallelism was rejected
because it does not prove input independence, concurrent-write safety, or
deterministic recovery.

### 7. OpenSpec Owns Artifacts, Not Runtime State

**Decision:** `harness-13` is installed as a project-local OpenSpec schema and
defines:

- thirteen artifact IDs and current materialized Markdown paths;
- dependency ordering;
- templates and instructions;
- apply readiness for the completed planning package.

OpenSpec 1.6 stores each stage instruction inline in `schema.yaml` and loads each
template only from `templates/`. The `apply.requires` list contains all thirteen
artifact IDs because readiness checks direct file existence rather than transitive
dependency closure. Its instruction labels the result as a planning-only handoff.

`.openspec.yaml` retains only OpenSpec-supported metadata. Harness fields SHALL NOT
be added to it.

`harness init` preserves both the logical project root and the canonical OpenSpec
root, including the TDT symlinked root,
and installs `openspec/schemas/harness-13/` only after a dry-run reports:

- destination path;
- existing managed or unmanaged files;
- source and destination versions;
- files to create, replace, or preserve.

Unmanaged files are never overwritten without explicit confirmation.

The initializer invokes `openspec schema validate harness-13` with the logical
project root as its working directory. Harness-side contract tests additionally
enforce the exact stage set and order, contained output paths, complete apply list,
and instruction semantics because the OpenSpec validator checks structure,
dependencies, cycles, and template existence but not those product constraints.

### 8. Runtime State Uses a Transactional SQLite Ledger

**Decision:** Runtime state uses the Python standard-library SQLite module under:

```text
$TDT_HOME/ai-harness/
  config.yaml
  state.sqlite
  runs/<run-id>/
    provider-events/
    artifacts/<stage>/<revision>.json
    artifacts/<stage>/<revision>.md
```

The loader honors `TDT_HOME`, expands `~`, and defaults to `~/.tdt`. Provider
credentials are not stored in this database or YAML configuration.

Conceptual tables:

| Table | Purpose |
|---|---|
| runs | Run identity, ticket, change root, schema version, mode, provider, status |
| stages | Current stage status, attempt, latest accepted revision, timestamps |
| artifact_revisions | Immutable revision metadata, paths, digests, supersession |
| gates | Request identity, stage, artifact digest, status, actor, reason, expiry |
| clarifications | Question/answer records and resolution status |
| provider_sessions | Provider session IDs, stage, attempt, resume eligibility |
| events | Append-only transition, validation, and failure events |

Every transition occurs in a transaction. A per-run lease prevents two CLI
processes from advancing the same run concurrently. Stale leases are recovered
only after checking owner identity and expiry.

SQLite contains metadata and references, not full prompts, secrets, or unrestricted
artifact content.

### 9. Artifacts Have Immutable Revisions and a Current Materialization

**Decision:** Provider output first becomes an immutable run-ledger revision. After
validation, the CLI atomically materializes the accepted Markdown revision at the
OpenSpec artifact path, for example `artifacts/spec.md`.

Each immutable revision records:

- run, stage, and revision identity;
- provider and provider session ID;
- input artifact and evidence digests;
- structured result digest;
- rendered Markdown digest;
- validation results;
- creation and supersession timestamps.

On backtrack:

1. The CLI records the decision and target stage.
2. Accepted downstream revisions are marked superseded but remain addressable.
3. Downstream current OpenSpec materializations are removed only after their
   immutable copies and digests are verified in the run store.
4. The target stage becomes pending for a new revision.
5. A fresh provider session is used unless an adapter proves that same-stage resume
   is safe and requested.

This restores OpenSpec readiness without deleting audit history.

### 10. Gates Are Digest-Bound, Audited, and Resumable

**Decision:** Gates exist after `SPEC`, `DESIGN`, `IMPL_PLAN`, and `PLAN_REVIEW`.

A gate request contains:

- decision ID;
- run ID and stage ID;
- artifact revision and digest;
- allowed decisions and backtrack targets;
- issued and expiry timestamps;
- configured approvers or local actor policy.

Approval and rejection commands validate the pending request and artifact digest.
Replayed, expired, stale, or mismatched decisions fail closed.

Initial local actor identity comes from the trusted operating-system boundary. A
self-asserted `--actor` value is not authoritative. Gate events are append-only.

An explicit `harness backtrack` command is a trusted local administrative action.
It requires a reason and an allowed target, binds its authorization to the current
accepted revision and digest, and atomically records and consumes that authorization
before superseding revisions. It cannot bypass an unresolved or stale gate request.

Interactive prompting may be provided as a convenience wrapper, but the durable
contract is command-based:

```text
harness approve --run <id> --decision <id>
harness reject --run <id> --decision <id> --reason <text> --backtrack <stage>
harness run --run <id>
```

### 11. Structured Output Is the Provider Boundary

**Decision:** Every provider returns a JSON document validated against a stage JSON
Schema. Providers never write current OpenSpec artifacts directly.

Common result fields include:

```text
stage_id
status
applicability
claims[]
artifact_body
evidence_refs[]
upstream_refs[]
assumptions[]
unresolved_questions[]
diagnostics[]
```

The CLI rejects:

- malformed or schema-invalid output;
- a stage ID different from the request;
- unknown evidence or upstream IDs;
- observed claims without evidence;
- output exceeding configured limits;
- provider-reported success after timeout or cancellation.

The CLI renders accepted structured output into Markdown using deterministic
templates and records both JSON and Markdown digests.

### 12. Evidence Distinguishes Observation From Proposal

**Decision:** Claims are explicitly classified:

| Claim type | Meaning | Evidence rule |
|---|---|---|
| observed | Statement about current code, API, configuration, or documentation | MUST cite verified evidence |
| proposed | New behavior or interface being designed | MUST cite the requirement or decision it implements |
| assumption | Unverified premise needed to proceed | MUST be surfaced for human review |
| decision | Chosen design with rationale | MUST cite inputs and alternatives |

Evidence records use stable IDs such as `EVD-001` and include source type,
repository, path or symbol UID, indexed revision or freshness information, query,
digest, and collection time.

Recorded human clarification answers may support requirements, decisions, and the
resolution of assumptions. They do not prove observed facts about current code,
configuration, or APIs; those claims still require deterministic collected evidence.

Validation scripts do not attempt to prove every natural-language sentence. They
verify evidence existence, digest integrity, claim classification, ID resolution,
and required coverage. A proposed endpoint does not fail merely because it is not
present in the current source.

### 13. Traceability Uses Stable IDs

**Decision:** Traceability identifiers, not mutable Markdown line numbers, connect
artifacts:

```text
REQ-001 -> DES-001 -> API-001 -> TASK-001 -> TC-001 -> ATP-001 -> VER-001
```

Artifacts contain upstream references known at creation time. Downstream mappings
are built incrementally in the run ledger and emitted by `VERIFY` as a terminal
traceability matrix. Earlier artifact bodies do not need speculative downstream
links.

Verification reports:

- requirement coverage;
- acceptance-criterion to test-case coverage;
- automated-test-plan coverage;
- unresolved assumptions;
- missing or stale evidence;
- superseded revisions and gate decisions;
- overall `complete`, `partial`, or `failed` status.

### 14. Security Is Enforced Outside Skill Metadata

**Decision:** All initial stages run with read-only provider authority. Only the
harness CLI writes inside approved artifact and run-store roots.

Controls include:

- subprocess argument arrays; never `shell=True`;
- ticket and large prompt input through files or stdin rather than shell
  interpolation;
- executable resolution through configured allowlisted provider names;
- resolved-path containment and symlink checks;
- minimal environment inheritance and secret redaction;
- explicit working directory and approved additional roots;
- process timeout, cancellation, output-size, request, token, and cost limits;
- bounded provider event capture with prompts and artifact bodies excluded from
  routine logs;
- output treated as untrusted until schema and evidence validation complete.

Agent Skills `allowed-tools` is experimental and host-dependent. It may improve user
experience but is not used as an enforcement mechanism.

### 15. Installation Has Separate Explicit Channels

**Decision:** Installation is intentionally split:

```text
CLI package        -> uv tool install <source>
Portable skills    -> npx skills add <source>
Schema and agents  -> harness init --platform claude --platform codex
```

`harness init` is idempotent and supports:

- `--dry-run`;
- explicit project and OpenSpec roots;
- selected platforms;
- version and ownership markers;
- conflict reporting;
- managed-file upgrade;
- rollback of managed files only.

The command may install:

```text
openspec/schemas/harness-13/
.claude/agents/harness-*.md
.codex/agents/harness-*.toml
```

It SHALL NOT install skills implicitly; `npx skills` remains authoritative for
skill installation. It SHALL NOT overwrite unmanaged platform configuration.

The internal repository is distributed through the approved internal Git service.
Public GitHub, skills.sh, and public plugin marketplaces remain out of scope.

### 16. Configuration Is Typed and Secret-Free

**Decision:** `$TDT_HOME/ai-harness/config.yaml` contains non-secret configuration:

- default provider and execution mode;
- provider executable names and permitted arguments;
- workspace roots;
- gate policy;
- stage and provider budgets;
- concurrency, timeout, revision, and output-size limits;
- retention policy;
- optional model aliases.

Provider authentication remains owned by each native CLI. Secrets SHALL NOT be
copied into harness YAML, SQLite, prompts, artifacts, reports, or logs.

Configuration validation runs before a workflow starts. Unlimited budgets or
unbounded retries are rejected in the initial release.

### 17. Error Handling and Observability Use Stable Contracts

**Decision:** The domain separates `RunStatus`, `StageStatus`, `WaitReason`, and
`VerificationOutcome`. Waiting is a resumable run status with a typed reason, while
`complete`, `partial`, and `failed` are verification outcomes. The CLI distinguishes
at least:

- success;
- waiting for clarification;
- waiting for approval;
- invalid input or configuration;
- provider unavailable or capability mismatch;
- provider execution failure or timeout;
- structured-output validation failure;
- evidence or traceability blocked;
- run not found or stale decision;
- internal failure.

JSON mode writes machine-readable results to stdout and diagnostics to stderr.
Events include run ID, stage, attempt, provider, duration, outcome, revision, and
artifact digest. They exclude credentials, full prompts, and protected artifact
contents.

`harness doctor` reports:

- Python and `uv` compatibility;
- OpenSpec availability and schema resolution;
- run-store health;
- provider executable and capability status;
- installed portable skills and native agent files;
- unmanaged-file conflicts;
- configured path containment.

### 18. Testing Uses Deterministic Adapter Boundaries

**Decision:** Testing has four layers:

1. **Deterministic unit tests**
   - state transitions, SQLite transactions, leases, gates, revisions, rendering,
     ID generation, path containment, and validation;
2. **Adapter contract tests**
   - fake Claude/Codex executables covering success, invalid JSON, timeout,
     cancellation, missing capability, stale session, and non-zero exit;
3. **Workflow integration tests**
   - full 13-stage guided and headless flows, clarification, approvals, rejection,
     restart, backtrack, supersession, and report generation;
4. **Opt-in provider smoke/evaluation tests**
   - installed real CLIs with bounded budgets, never required for deterministic CI.

Additional checks include:

- `openspec schema validate harness-13`;
- strict validation of the planning change;
- Agent Skills validation with `skills-ref`;
- installation dry-run and conflict fixtures;
- platform generation golden files;
- lint, format, strict typing, tests, and coverage.

Skill evaluation measures correct triggering, CLI invocation, gate behavior, and
artifact quality. Exact natural-language output is not asserted.

## Risks / Trade-offs

- **Native CLI behavior can change** -> Probe capabilities at runtime, keep adapters
  isolated, and run opt-in smoke tests against supported provider versions.
- **Guided hosts can ignore instructions** -> Treat guided results as untrusted and
  require the same local schema/evidence validation as headless results.
- **Cross-platform skills have a small common contract** -> Keep the portable core
  minimal and move enhancements into explicit platform adapters.
- **OpenSpec schemas are experimental** -> Version the installed schema, validate it
  during initialization, and refuse silent incompatible upgrades.
- **Local SQLite is not distributed orchestration** -> Enforce a per-run lease and
  document that multi-host execution is out of scope.
- **Provider sessions can retain stale assumptions** -> Default to fresh sessions per
  stage/revision and allow resume only for bounded same-attempt recovery.
- **Agent-generated evidence can be fabricated** -> Accept only evidence IDs created
  by deterministic collectors and verified against current sources.
- **Installation spans multiple tools** -> Provide `harness doctor`, explicit dry-run,
  ownership markers, and a single documented setup sequence.
- **Planning-only verification may be mistaken for implementation verification** ->
  Use `PLAN_REVIEW`, label reports as planning verification, and state non-goals in
  CLI help and artifacts.
- **Model and token costs vary** -> Require finite per-stage and per-run budgets and
  record usage when providers expose it.
- **New Python dependencies require approval** -> Use only the approved Typer,
  PyYAML, jsonschema, Hatchling, pytest, pytest-cov, pytest-asyncio, ruff, mypy,
  and types-PyYAML distributions, managed exclusively with `uv`.

## Migration Plan

There is no migration from `agent-harness`; this is a new standalone product.

1. Create the new repository and Python package after dependency approval.
2. Implement the run ledger, state machine, artifact renderer, and fake provider
   adapter before invoking a real model.
3. Implement and validate the `harness-13` schema and explicit initializer.
4. Add the Claude adapter and pass deterministic plus bounded smoke tests.
5. Add the Codex adapter without depending on direct custom-agent selection.
6. Add feature-based portable skills and validate them against the Agent Skills spec.
7. Add optional Claude and Codex native-agent templates.
8. Run a full local pilot on both automated providers.
9. Document guided mode for other Agent Skills hosts.
10. Package for the approved internal repository only after local acceptance.

### Rollback

- Stop invoking the standalone CLI; no service shutdown is required.
- Use the initializer rollback command to remove only files carrying matching
  harness ownership/version markers.
- Remove installed portable skills through `npx skills remove`.
- Remove the `uv` tool installation.
- Preserve or explicitly export the SQLite ledger and immutable artifact revisions
  before deletion.
- No `agent-harness` rollback is involved.

## Open Questions

The implementation decisions are resolved for version 1:

1. The repository name is `ai-harness-skills`; the Python import package is
   `ai_harness`, and the installed command is `harness`.
2. Typer, PyYAML, and jsonschema are approved runtime dependencies. Hatchling,
   pytest, pytest-cov, pytest-asyncio, ruff, and mypy are approved development and
   build dependencies, all managed exclusively through `uv`.
3. Gate authorization trusts the effective operating-system user. A configured
   local approver allowlist may further restrict accepted OS identities; a CLI
   `--actor` assertion never grants authority.
4. Provider event files default to 30-day retention and completed-run ledger
   metadata defaults to 365-day retention. Immutable artifact revisions and their
   digest/audit metadata are never deleted automatically; removal requires an
   explicit export-and-delete operation that is outside the initial command set.
5. Required automated-provider capabilities are structured final output, locally
   enforceable schema validation, read-only execution, explicit working-directory
   containment, deterministic process status, timeout, cancellation, bounded
   output, and session identity. Capability probes, not version strings alone,
   determine the support tier.

Deferred product questions:

1. Should Cursor become an automated provider after a dedicated read-only and
   structured-output conformance spike?
2. Should internal distribution use a GitLab URL directly with `npx skills`, or a
   mirrored internal package source?
