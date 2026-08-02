## 1. Reconcile Change Ownership and Evidence

- [x] 1.1 In `tdt-meta/openspec/changes/close-agent-framework-verification-gaps/`, add a corrective ledger mapping disputed archived tasks 4.1–4.5, 5.1–5.4, 6.1–6.5, 7.1–7.6, 9.1–9.6, 10.5, 11.1–11.8, 12.1–12.4, and 13.1–13.7 to current evidence, one owning corrective task, and required closure evidence.
- [x] 1.2 In `tdt-meta/openspec/changes/agent-harness-stage-modules/tasks.md`, reopen checked tasks whose claims are not supported, including 3.3, 3.4, 5.4, 6.3, 7.4, 7.6, affected 8.1–8.6 parity claims, 9.4, 11.1, and 11.4; cross-reference this change instead of duplicating ownership.
- [x] 1.3 Record the pre-existing dirty paths in all four repositories and define the allowed corrective file set so unrelated user changes and generated `__pycache__` files are excluded from completion evidence.
- [x] 1.4 Capture GitNexus impact output for every existing symbol before editing and record CRITICAL affected processes for docs canonical routing and harness gate/topology roots.
- [x] 1.5 Add `implementation-evidence.md` with a command/result manifest template that records repository `HEAD`, tracked binary-diff hash, sorted untracked paths, exact framework versions, and every unavailable, skipped, stale, or failed gate explicitly open.

## 2. Characterize the Verified Gaps

- [x] 2.1 In `agent-core/tests/`, add protocol tests for full supported Hooks lifecycle coverage, callback-return propagation, exactly-once dispatch, and absence of legacy deprecation paths.
- [x] 2.2 In `agent-core/tests/`, prove official Harness `Memory` composition applies bounded store behavior and that legacy `memory=` constructor paths and parallel generic store lifecycles are absent.
- [x] 2.3 In `agent-core/tests/`, complete deferred-call, stream ordering/cancellation, `AgentSpec` round-trip, unknown-field rejection, and public step-persistence characterization required by archived tasks 5.1–7.6.
- [x] 2.4 In `agent-docs-sync/tests/`, add command-by-command fixtures for `check`, `discover`, `update`, `sync`, `audit`, and `sync-all`, including exit codes, reports, generation decisions, validation, errors, and bounded writes.
- [x] 2.5 In `agent-docs-sync/tests/`, prove legacy discovery/full entry points are absent and every supported command executes through the canonical function without independent orchestration.
- [x] 2.6 In `agent-harness/tests/`, add failing gate tests for stable issuance/expiry, authorized actor, run/thread/stage/artifact/native-interrupt identity, replay, forbidden routing, and exactly-once decision recording.
- [x] 2.7 In `agent-harness/tests/`, add failing runner tests for checkpoint schema mismatch, bounded public history, unknown durable run, process restart, and preservation of checkpoints on rejected resume.
- [x] 2.8 In `agent-harness/tests/`, add failing topology tests for invalid endpoints, unreachable stages, unintended terminals/fan-out, fan-in input availability, conflicting concurrent writers, and undeclared cycles.

## 3. Complete `agent-core` Lifecycle Composition

- [x] 3.1 In `agent-core/src/agent_core/_ai/hooks.py`, compose new run, node, model, tool validation/execution, output validation/processing, error, deferred-tool, and event-stream behavior directly through the public Pydantic AI 2.18 `Hooks` callbacks.
- [x] 3.2 Remove the `HookRegistry` adaptation layer, preserve every supported callback return value through official `Hooks`, and fail stale imports at construction/import time rather than discarding or approximating them.
- [x] 3.3 Remove `HookRegistry`/`HookAdapter` from the public and consumer composition paths; compose official `Hooks` directly with no duplicate TDT audit, budget, Langfuse, or MLflow dispatch.
- [x] 3.4 Update `agent-core/src/agent_core/agent_base/agent.py` and `agent-core/src/agent_core/sdk/agents.py` so official hooks are composed explicitly and no second lifecycle authority is created.
- [x] 3.5 Run focused lifecycle, instrumentation, deferred, and stream tests and record event counts and callback-return parity in the evidence manifest.

## 4. Complete `agent-core` Memory and Specification Composition

- [x] 4.1 In `agent-core/src/agent_core/sdk/memory.py`, use public Harness 0.11 `InMemoryStore`, `FileStore`, `SqliteMemoryStore`, or `PostgresMemoryStore` directly for generic cases and retain `TDTMemoryStore` only as the structural adapter for TDT tenancy/search semantics.
- [x] 4.2 Remove legacy `memory=` construction from `agent-core/src/agent_core/sdk/agents.py`, `agent-core/src/agent_core/agent_base/agent.py`, and `agent-core/src/agent_core/_ai/agent.py`; require explicit official memory capability composition.
- [x] 4.3 Remove `agent-core/src/agent_core/_ai/capability.py::MemoryCapability`, its legacy `memory_*` tool contract, and compatibility-only tests after confirming no production callers remain.
- [x] 4.4 Verify official injection limits, memory tools, tenant/repository/session isolation, public step continuation, ordering, persistence, and restart behavior.
- [x] 4.5 Complete public `Agent.from_file`/`Agent.from_spec` round-trip support in `agent-core/src/agent_core/_ai/config_loader.py` without private attributes, lossy projection, or YAML-granted high-authority capability.
- [x] 4.6 Run `uv run pytest` for memory/spec/deferred suites and inspect imports to prove migrated mechanics use only public upstream contracts.

## 5. Collapse `agent-docs-sync` onto One Composition Root

- [x] 5.1 Refactor `agent-docs-sync/src/agent_docs_sync/workflows/canonical.py` so one mode-aware per-repository boundary owns `check`, `discover`, `update`, `sync`, and `audit` while deterministic stages remain non-agent functions.
- [x] 5.2 Keep `sync-all` in `agent-docs-sync/src/agent_docs_sync/cli.py` as a bounded aggregate coordinator whose every repository execution delegates to the canonical boundary without bypassing mode policy or report/error semantics.
- [x] 5.3 Remove `run_discovery_pipeline`, `run_full_pipeline`, `run_full_audit`, and remaining dynamic/legacy workflow entry points and route all production callers through the canonical boundary.
- [x] 5.4 Consolidate `build_doc_sync_agent` and discovery/generation/validation builders into one explicit builder receiving a resolved gateway, official toolsets/capabilities, shared lifecycle policy, and mode-scoped instructions.
- [x] 5.5 Remove silent builder-created registry, hook, gateway, and tool substitutions; use least-privilege prepared/filtered toolsets for each mode.
- [x] 5.6 Run old-versus-canonical fixtures for all commands and use GitNexus/Graphify evidence to prove one production pipeline and builder path remain.

## 6. Complete Harness Stage and Toolset Composition

- [x] 6.1 In `agent-harness/src/agent_harness/agents/factory.py`, require a ready typed composition context, resolved gateway, and inputs matching public `AgentToolset`/`AgentCapability` contracts; remove fallback registries/gateways and `list[Any]` composition.
- [x] 6.2 Adapt GitNexus, Graphify, bounded file reads, and supported Jira reads once to official toolsets, then apply explicit per-stage least-privilege visibility through public filtering/preparation.
- [x] 6.3 Wire each `StageDefinition.toolsets` and `.capabilities` value into stage-agent construction with typed immutable run-scoped profile overrides.
- [x] 6.4 Add negative authority tests denying source/Jira/GitLab mutation, shell, code execution, unbounded filesystem, undeclared network access, and string capability/tool lookup.
- [x] 6.5 Inspect imports and construction paths to prove the harness has no parallel tool registry/provider protocol and fails before execution when gateway/profile composition is invalid.

## 7. Validate Native Harness Topology

- [x] 7.1 In `agent-harness/src/agent_harness/stages/contracts.py`, define one immutable topology plan containing native node IDs, entry, edges, terminals, fan-out/fan-in, gates, and bounded retry cycles without adding execution semantics or stage inheritance.
- [x] 7.2 Make `validate_stage_topology` reject unknown endpoints, unreachable stages, unintended terminals/fan-out, missing fan-in inputs, undeclared cycles, and parallel scalar/reducer conflicts with actionable stage/field details.
- [x] 7.3 Validate the topology plan at the consumer composition root, then wire every native `StateGraph` edge/branch from that same plan; reject a second edge list or private builder inspection.
- [x] 7.4 Add strict typing and runtime coverage for valid sequential topology, any approved parallel branch, and every rejection scenario from the modified `stage-module-protocol` spec.

## 8. Make Harness Gates Fail Closed

- [x] 8.1 Extend `agent-harness/src/agent_harness/models/gates.py` with deterministic request/run/thread/stage/artifact/routing/approver/issued-at/expiry identity plus trusted resolved-actor and native-interrupt decision fields; use timezone-aware UTC datetimes.
- [x] 8.2 Update `agent-harness/src/agent_harness/workflow/graph.py` so request ID and expiry derive from checkpointed artifact identity/digest/`created_at` plus configured TTL and reproduce identically when the interrupt node restarts.
- [x] 8.3 Add explicit non-empty approvers to `GateConfig`, resolve the actor through a consumer-owned trusted CLI/service boundary, ignore self-asserted actor/time input, and match request/run/thread/stage/artifact/pending interrupt before accepting approve or reject.
- [x] 8.4 Evaluate expiry with the runner's trusted UTC clock and reject expired, unauthorized, stale, replayed, cross-thread, cross-artifact, and forbidden-route decisions before checkpoint advancement; record accepted decisions exactly once.
- [x] 8.5 Run visited-node trace tests for each gate, four sequential approvals, rejection/backtrack, and non-reexecution of completed artifact-producing stages.

## 9. Finish Harness Checkpoint and Runner Semantics

- [x] 9.1 Add an explicit static checkpoint schema version to `agent-harness/src/agent_harness/state.py` and define the supported legacy-read behavior.
- [x] 9.2 In `agent-harness/src/agent_harness/workflow/runner.py`, validate checkpoint version before stage execution, resume, or writes and preserve incompatible checkpoints unchanged.
- [x] 9.3 Bind decisions to the pending public `Interrupt.id` from `aget_state` and resume only with `Command(resume={pending_interrupt.id: decision})` on the recovered thread/backend.
- [x] 9.4 Implement bounded public history with `aget_state_history` and keep run, stream, status, history, and resume on the same operation-scoped core checkpointer boundary.
- [x] 9.5 After `agent-harness-stage-modules` tasks 3.6, 5.4–5.6, 7.5, and 7.8 complete, consume their real `AsyncPostgresSaver` evidence and verify setup, operation lifetime, process restart, non-reexecution of completed stages, and streaming/pending-interrupt identity. Do not duplicate implementation in this change.
- [x] 9.6 Retain an `InMemorySaver` for the lifetime of a non-durable gated `WorkflowRunner`, support only same-process resume there, and add CLI coverage for status/history/approve/reject errors without querying saver internals or starting an unknown run.

## 10. Compatibility, Deployment, and Rollback Evidence

- [x] 10.1 Record and test the frozen baseline tuple Pydantic AI 2.18.0, Harness 0.11.0, LangGraph 1.2.9, checkpoint 4.1.1, and Postgres saver 3.1.0 across all three repositories.
- [x] 10.2 In a disposable workspace, freshly resolve the existing dependency bounds without committing lockfile changes, rerun the cross-repository contract suites, and record explicitly when the candidate tuple collapses to the baseline.
- [x] 10.3 Add a private-upstream-import/attribute gate covering lifecycle, memory, toolsets, agent construction, interrupts, checkpointers, and graph APIs.
- [x] 10.4 Run the caller census for every compatibility projection and document warning window, replacement API, before/after example, and zero-caller removal criterion.
- [x] 10.5 Inspect rebuilt deployment bundles, including `deployments/ai-review/deps/agent-core`, and prove they contain the corrected source without stale vendored copies.
- [x] 10.6 Re-run rollback independently for hooks, memory, docs routing/builders, harness gates/topology, and the final checkpoint/reducer schema using new, completed, and pending-gate fixtures.
- [x] 10.7 Verify the refreshed rollback evidence preserves persisted IDs, tenant boundaries, deterministic reports, and checkpoints and does not re-enable an independent legacy implementation.

## 11. Strict Verification and Completion Gate

- [x] 11.1 From `agent-core/`, after finalizing the local harness-database bootstrap, pass `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests --strict`, and `uv run pytest -x`.
- [x] 11.2 From `agent-docs-sync/`, pass `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests --strict`, and `uv run pytest -x`.
- [x] 11.3 From `agent-harness/`, after the stage change completes, pass `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests --strict`, `uv run pytest -x`, and the real Postgres integration marker/suite.
- [x] 11.4 From `tdt-meta/`, pass `openspec validate --strict close-agent-framework-verification-gaps` and `openspec validate --strict agent-harness-stage-modules`.
- [x] 11.5 Run GitNexus `detect_changes` in each modified repository after the final implementation, compare with the approved impacts, and record any unexpected symbol or execution-flow change as an open blocker.
- [x] 11.6 Run Graphify queries across SDK composition, lifecycle, memory, docs routing, harness gates, runner, and topology and attach the canonical-path evidence.
- [x] 11.7 Refresh `implementation-evidence.md` with the final repository identities, canonical configuration tests, reducer/schema decision, real Postgres backend evidence, quality gates, rollback, and change detection; keep every failed, skipped, unavailable, or stale required gate unchecked.
- [x] 11.8 Review both active changes against actual code and archive only after task boxes, specs, implementation, compatibility, deployment, rollback, and real Postgres evidence agree.
