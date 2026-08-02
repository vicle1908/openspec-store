## 1. Verify Prerequisites and Authority

- [x] 1.1 In `tdt-meta`, confirm `stabilize-agent-framework-integration` is complete, strictly valid, and its full `agent-core`/`agent-docs-sync` contract suites pass.
- [x] 1.2 In `tdt-meta`, confirm `converge-agent-framework-upstream` is complete, strictly valid, and typed SDK, Hooks, deferred, memory, and LangGraph conformance tests pass.
- [x] 1.3 Obtain explicit approval to add the new `agent-harness` repository dependencies, including workspace `agent-core`/`tdt-core` and the reviewed Pydantic AI/Harness/LangGraph family; stop setup if approval is not granted.
- [x] 1.4 Record the initial authority profile: read-only target repositories/Jira, artifact writes only beneath `$TDT_HOME/agent-harness/`, local authenticated gate decisions, and no external mutation.

## 2. Create the Repository and Reproducible Environment

- [x] 2.1 Create `agent-harness/pyproject.toml` with Python 3.14, hatchling, public CLI entry point, direct imported dependencies, `[tool.uv] required-version >=0.11.15`, ruff, strict mypy, and pytest configuration.
- [x] 2.2 Declare the reviewed direct framework ranges and workspace sources; generate `agent-harness/uv.lock` with `uv` and verify the exact `(2.18.0, 0.11.0, 0.0.19, 1.2.9)` tuple.
- [x] 2.3 Create `agent-harness/src/agent_harness/` and `agent-harness/tests/` package structure without adding source-write, shell, code-execution, GitLab mutation, or OpenSpec mutation modules.
- [x] 2.4 Add `agent-harness/.python-version`, README, example configuration, and repository-local developer commands consistent with TDT workspace rules.
- [x] 2.5 Run `uv sync --frozen`, an import smoke test, `uv run ruff check .`, and `uv run mypy src tests --strict`.

## 3. Implement Typed Configuration and Workspace Policy

- [x] 3.1 Implement `agent-harness/src/agent_harness/config.py` with typed harness, gate, validation, persistence, budget, retention, and authority settings composed with the public agent-core consumer configuration.
- [x] 3.2 Implement TDT_HOME-aware loading for `$TDT_HOME/harness/config.yaml`, `$TDT_HOME/harness/workspace.yaml`, and `$TDT_HOME/.env` using supported shared loaders.
- [x] 3.3 Implement `agent-harness/src/agent_harness/workspace.py` to resolve unique canonical repository roots inside administrator-approved workspace roots.
- [x] 3.4 Add startup validation rejecting unsafe artifact roots, unlimited budgets, model-authored gate rules, source-write/shell/code/external-mutation authority, and unbounded repository paths.
- [x] 3.5 Add configuration precedence, environment override, secret-redaction, path-expansion, and invalid-authority tests.

## 4. Implement Artifacts, State, Gates, and Evidence Models

- [x] 4.1 Implement `agent-harness/src/agent_harness/models/artifacts.py` with the common artifact envelope and distinct typed models for all 12 stages.
- [x] 4.2 Implement `agent-harness/src/agent_harness/models/evidence.py` for GitNexus, Graphify, file, index-freshness, validation, and confidence evidence.
- [x] 4.3 Implement `agent-harness/src/agent_harness/models/gates.py` for gate requests, decisions, expiry, actor, backtrack targets, and audit projection.
- [x] 4.4 Implement `agent-harness/src/agent_harness/models/trace.py` with append-only revision/digest lineage and requirement mappings.
- [x] 4.5 Implement `agent-harness/src/agent_harness/state.py` as a typed LangGraph state schema with explicit artifact fields and reducers for trace, evidence, and revisions.
- [x] 4.6 Add strict serialization, unknown-field, invalid-transition, reducer, and checkpoint round-trip tests.

## 5. Implement Read-Only Integration Toolsets

- [x] 5.1 Implement `agent-harness/src/agent_harness/tools/gitnexus.py` using GitNexus MCP `query`, `context`, and `impact` contracts with explicit repository targeting and evidence capture.
- [x] 5.2 Add a bounded host-only GitNexus CLI fallback for operational environments without MCP; allow only query/context/impact/status operations and prohibit analyze/delete/rename from agent authority.
- [x] 5.3 Implement `agent-harness/src/agent_harness/tools/graphify.py` with validated graph paths and only query/path/freshness operations; do not expose a general shell command.
- [x] 5.4 Implement `agent-harness/src/agent_harness/tools/files.py` with bounded read/search operations that cannot escape configured repository roots.
- [x] 5.5 Implement `agent-harness/src/agent_harness/tools/jira.py` with `tdt_core.clients.JiraClientFactory` read operations only.
- [x] 5.6 Compose the integrations as official Pydantic AI toolsets through `agent_core.sdk`, preserving schemas, metadata, retries, timeouts, and authority.
- [x] 5.7 Add tests for repository disambiguation, stale indexes, missing graphs, path/symlink escape, transient retry, deterministic invalid-input failure, and absence of mutation tools.

## 6. Compose Stage Agents and Memory

- [x] 6.1 Implement `agent-harness/src/agent_harness/agents/factory.py` using typed public agent-core SDK composition and upstream capabilities/toolsets; do not use `harness_config` or internal imports.
- [x] 6.2 Configure official Pydantic AI `Instrumentation`/`Hooks` composition plus TDT budget, audit, correlation, and tool-authorization policy.
- [x] 6.3 Implement a tenant/workspace/ticket-scoped adapter to public Harness `MemoryStore` only where TDT backend semantics are required.
- [x] 6.4 Use the official Harness `Memory` capability with finite injection/search limits and add cross-tenant/workspace isolation tests.
- [x] 6.5 Use Harness `StepPersistence` with a public step store for agent-step continuation and add process-local versus durable behavior tests.
- [x] 6.6 Add concurrent-run tests proving instructions, tools, memory namespace, evidence, and correlation data do not leak.

## 7. Implement the Three Validation Tiers

- [x] 7.1 Implement `agent-harness/src/agent_harness/validation/existence.py` for typed GitNexus/Graphify/file evidence and freshness-aware confidence.
- [x] 7.2 Implement `agent-harness/src/agent_harness/validation/semantic.py` using evidenced repository examples and structured model output.
- [x] 7.3 Implement `agent-harness/src/agent_harness/validation/structural.py` for requirement-to-design/API/plan/test mappings.
- [x] 7.4 Implement `agent-harness/src/agent_harness/validation/pipeline.py` with finite revision counts and native `Command` backtrack outcomes.
- [x] 7.5 Add tests proving missing/stale evidence cannot become “verified”, HIGH/CRITICAL impact requires human disposition, and exhausted revisions become blocked/needs-human.

## 8. Implement the Twelve Planning Stages

- [x] 8.1 Implement `stages/intake.py` to read and normalize the Jira ticket without mutating it.
- [x] 8.2 Implement `stages/context.py` to gather bounded multi-repository GitNexus, Graphify, file, and approved memory evidence.
- [x] 8.3 Implement `stages/clarify.py` to produce grounded requirements, acceptance criteria, constraints, assumptions, and unresolved questions.
- [x] 8.4 Implement `stages/spec.py` to produce draft proposal/spec content inside the harness artifact root without touching the canonical OpenSpec store.
- [x] 8.5 Implement `stages/impact.py` to capture upstream GitNexus impact, affected processes/modules, confidence, and human-review flags.
- [x] 8.6 Implement `stages/design.py` to produce decisions tied to accepted requirements and current repository patterns.
- [x] 8.7 Implement `stages/api_contract.py` to describe API/schema compatibility without claiming deployment or implementation.
- [x] 8.8 Implement `stages/implementation_plan.py` to order repository/symbol changes and dependencies.
- [x] 8.9 Implement `stages/coding_plan.py` to describe proposed files, symbols, tests, checks, and rollback without editing code.
- [x] 8.10 Implement `stages/plan_review.py` to review the planning artifacts and evidence, not nonexistent code.
- [x] 8.11 Implement `stages/test_plan.py` to map every acceptance criterion to planned unit/integration/e2e/rollback tests.
- [x] 8.12 Implement `stages/verification.py` to compute typed coverage, flags, blocked items, and final status.
- [x] 8.13 Add focused schema/evidence tests for every stage and a test that no stage exposes source or external mutation tools.

## 9. Assemble Native LangGraph Workflow and Gates

- [x] 9.1 Implement `agent-harness/src/agent_harness/workflow/graph.py` with public `StateGraph`, the typed state schema, exact 12 stages, and validated edges.
- [x] 9.2 Implement native `Command` routing for revision, skip, blocked, abort, and terminal outcomes.
- [x] 9.3 Implement native `interrupt` gate nodes with typed requests at configured stages.
- [x] 9.4 Implement host authorization and typed `Command(resume=GateDecision(...))` handling for approve/reject/backtrack.
- [x] 9.5 Add tests for unauthorized, stale, expired, wrong-stage, replayed, deterministic auto-approved, rejected/backtracked, and escalated decisions.
- [x] 9.6 Add a separation test proving workflow-stage approval never authorizes an unrelated deferred agent tool call.

## 10. Implement Async Durability and Artifact Storage

- [x] 10.1 Implement `agent-harness/src/agent_harness/workflow/runner.py` with `ainvoke`/`astream` and run-specific `thread_id`.
- [x] 10.2 Implement durable runner ownership of `AsyncPostgresSaver.from_conn_string()` from enter through graph compile, run/resume, and exit.
- [x] 10.3 Implement `agent-harness/src/agent_harness/artifacts/store.py` with TDT_HOME-bounded immutable revisions, digests, atomic writes, and symlink/traversal defense.
- [x] 10.4 Implement append-only JSONL trace and Markdown/JSON verification report generation under the run artifact root.
- [x] 10.5 Add crash/restart tests at completed-stage and pending-interrupt boundaries and prove completed work is not repeated.
- [x] 10.6 Add no-Postgres tests that report non-durable behavior without claiming recovery.
- [x] 10.7 Add filesystem tests proving all target repository trees are byte-for-byte unchanged after a full workflow.

## 11. Implement the CLI

- [x] 11.1 Implement `agent-harness/src/agent_harness/cli.py` with `run`, `status`, and `report` commands and stable human/JSON output.
- [x] 11.2 Implement `approve` and `reject` commands using authenticated OS/session identity, current checkpoint validation, and typed resume decisions.
- [x] 11.3 Publish and test distinct exit codes for success, invalid config/input, not found, unauthorized/stale decision, blocked evidence, and internal failure.
- [x] 11.4 Add CLI tests for stdout/stderr separation, JSON schema, secret-safe errors, safe output paths, and unsupported transports.

## 12. Verify Observability and Budgets

- [x] 12.1 Add workflow/stage spans with run, ticket, stage, artifact digest, repository/index commit, decision, and correlation identifiers.
- [x] 12.2 Add exactly-once assertions for Pydantic AI lifecycle instrumentation, TDT audit events, model/tool usage, and gate lifecycle events.
- [x] 12.3 Add finite model request/token, stage timeout, query fan-out, revision, artifact-size, and gate-expiry tests.
- [x] 12.4 Add telemetry redaction tests proving secrets, full prompts, and protected artifact bodies are not attributes or log fields.

## 13. Run Full Verification and Safety Analysis

- [x] 13.1 Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests --strict`, and `uv run pytest -x` in `agent-harness`.
- [x] 13.2 Run the full mocked 12-stage workflow, validation failure/backtrack flow, authorized approval flow, durable restart flow, and no-mutation flow.
- [x] 13.3 Index `agent-harness` with GitNexus, query its principal execution flows, and run upstream impact before changing any shared symbol discovered during implementation.
- [x] 13.4 Build/query its Graphify graph and verify paths from CLI to runner, graph stages, agent composition, evidence adapters, gates, persistence, and report.
- [x] 13.5 Run GitNexus `detect_changes` before commit and verify only the new consumer and its planned OpenSpec artifacts are affected.
- [x] 13.6 Run `openspec validate --strict agent-harness-c4-design` and record dependency versions, test counts, skipped tests, and any pre-existing failures.

## 14. Document and Release the Planning Consumer

- [x] 14.1 Create `agent-harness/docs/architecture.md` with C4 context/container/component diagrams and ownership boundaries.
- [x] 14.2 Create `agent-harness/docs/workflow.md` covering the exact 12 stages, state, revisions, validation tiers, gates, and terminal outcomes.
- [x] 14.3 Create `agent-harness/docs/configuration.md` covering TDT_HOME, workspace roots, authority, budgets, gate policy, and examples.
- [x] 14.4 Create `agent-harness/docs/operations.md` covering index freshness, Postgres durability, restart, backup, artifact retention, observability, and rollback.
- [x] 14.5 Create `agent-harness/docs/integrations.md` documenting GitNexus MCP, Graphify, Jira factory, official capabilities/toolsets, memory stores, and unsupported mutation transports.
- [x] 14.6 Publish the initial scope prominently: planning/evidence only, read-only targets, artifact-root writes only, and separate reviewed changes required for implementation automation.
