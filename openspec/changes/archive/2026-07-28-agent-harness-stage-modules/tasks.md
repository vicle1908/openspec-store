## 1. Dependency and Safety Gate

- [x] 1.1 Complete and verify `converge-agent-framework-upstream` through its typed SDK composition, configuration-composition, native LangGraph, and compatibility-matrix tasks before changing harness integration code.
- [x] 1.2 From `agent-harness/`, rerun GitNexus impact for `create_stage_agent`, `HarnessConfig`, `HarnessState`, `build_graph`, `WorkflowRunner.run`, `WorkflowRunner.astream`, and `WorkflowRunner.resume`; obtain approval before any HIGH or CRITICAL edit.
- [x] 1.3 Record the current dirty worktree and preserve all unrelated files; use a dedicated implementation branch/worktree if requested.
- [x] 1.4 Inventory public CLI/import paths, checkpoint state fields, configuration keys, stage order, gates, artifact digests, validation outcomes, and trace events.
- [x] 1.5 Record the verified baseline (`uv lock --check` pass, Ruff pass, 42 tests pass, strict mypy 27 production/74 total errors) and map every type error to tasks 2–7 or an explicit prerequisite fix; do not accept an unmapped baseline finding.
- [x] 1.6 Add focused failing tests for runtime-relevant type findings that existing tests miss, including missing `GateRequest.expiry`, invalid gateway construction, typed graph returns, and saver-backed resume.

## 2. Characterize Current Behavior and Known Defects

- [x] 2.1 Add fixture tests for all 12 stage inputs, output artifacts, digests, revisions, validation outcomes, trace events, and sequential next-node routing.
- [x] 2.2 Add a topology regression test demonstrating that the shared gate can reach unrelated gated stages; mark the current behavior as a known failure until task 6.2.
- [x] 2.3 Add tests proving `create_stage_agent` currently lacks a runnable gateway and that missing gateway resolution must fail before graph execution.
- [x] 2.4 Add reducer tests for repositories, errors, gate history, evidence, and trace; capture the incorrect message-reducer cases.
- [x] 2.5 Add durable fixtures for run, stream, status, interrupt, process restart, valid resume, invalid resume, and missing checkpoint; capture saver setup and in-memory resume gaps.
- [x] 2.6 Add CLI characterization tests for `run`, `status`, `report`, `approve`, and `reject`, including exit codes and bounded artifact paths.

## 3. Compose Configuration and Agent Dependencies

- [x] 3.1 In `agent-harness/src/agent_harness/config.py`, replace `HarnessConfig(ConsumerConfig)` with `HarnessConfig(BaseModel)` containing the converged immutable core runtime profile.
- [x] 3.2 Add one legacy config loader adapter that maps existing flat YAML/environment keys to the composed model with actionable warnings and parity tests.
- [x] 3.3 Resolve the TDT gateway at the harness composition root through the supported factory and pass it explicitly to every stage agent. (Corrective owner: `close-agent-framework-verification-gaps` 6.1.)
- [x] 3.4 Update `agent-harness/src/agent_harness/agents/factory.py` to accept a ready composition context and typed run-scoped instructions, toolsets, capabilities, and limits. (Corrective owner: `close-agent-framework-verification-gaps` 6.1–6.5.)
- [x] 3.5 Add construction tests for valid gateway/model resolution, missing credentials, invalid profile, and concurrent stages with different immutable overrides.
- [x] 3.6 In `agent-harness/src/agent_harness/config.py`, delegate dotenv loading to `tdt_core.env.load_tdt_env()`, map `HARNESS_DURABLE` and `TDT_POSTGRES_URL` into `PersistenceConfig`, reject the undocumented `HARNESS_PERSISTENCE_DURABLE` alias, keep environment-over-YAML precedence explicit, and add isolated loader tests for process env, `$TDT_HOME/.env`, YAML fallback, and workspace configuration without undeclared fields.

## 4. Replace Duplicate Tool and Capability Composition

- [x] 4.1 Adapt GitNexus, Graphify, and bounded file-read tools once to official Pydantic AI toolsets through the converged `agent-core` adapter.
- [x] 4.2 Define explicit per-stage least-privilege toolset policy with supported filtered/prepared toolsets; preserve schema, retry, metadata, ownership, budget, and audit behavior.
- [x] 4.3 Replace string capability names with typed public Pydantic AI/Harness capability instances supplied at the composition root.
- [x] 4.4 Add negative tests proving no stage gains source write, Jira/GitLab mutation, shell, code execution, unbounded filesystem, or undeclared network authority.
- [x] 4.5 Run dependency inspection and fail if the harness introduces a second tool registry/provider protocol or imports private upstream attributes.
- [x] 4.6 Resolve the Jira tool through the supported `tdt_core.clients` factory surface available in the synchronized environment; do not suppress the missing-factory type error or instantiate a raw Jira client.

## 5. Establish Static Stage Contracts and State

- [x] 5.1 Define the consumer-local frozen stage definition/protocol with native node callable, reads, writes, reducers, validators, typed toolsets/capabilities, and optional gate policy.
- [x] 5.2 Keep one statically declared `HarnessState`; document its checkpoint schema version and prohibit runtime `TypedDict` synthesis.
- [x] 5.3 Replace message reducers on `workspace_repos`, `errors`, and `gate_history` with semantic string collection reducers.
- [x] 5.4 Reconcile `HarnessState` reducer annotations with `StageDefinition.reducers` and graph validation so parallel candidates cannot share lifecycle scalars, every concurrent accumulator has one matching deterministic reducer, and validation cannot disagree with the compiled LangGraph channels. This change is the implementation owner; `close-agent-framework-verification-gaps` 7.1–7.4 supplies closure evidence only.
- [x] 5.5 Remove the unsupported `_last_value` reducer from `current_stage` and `status`; add LangGraph 1.2.9 execution tests proving `Command(update=..., goto=...)` runs the target in the following step with the update visible, while genuine parallel unreduced writes fail.
- [x] 5.6 Decide checkpoint compatibility after task 5.5: retain schema version 1 only if pending-gate and completed-run fixtures prove the persisted channel contract is unchanged; otherwise increment the version, document legacy-read behavior, and prove incompatible checkpoints remain unmodified.

## 6. Correct Native Graph and Gate Semantics

- [x] 6.1 Keep `build_graph()` as the explicit consumer composition root using native `StateGraph`, nodes, edges, `Command`, and interrupt APIs; add no `WorkflowComposer`.
- [x] 6.2 Replace the shared `gate` node with uniquely named post-stage gates having exactly one normal continuation; keep `interrupt()` out of artifact-producing stage nodes.
- [x] 6.3 Include run ID, thread ID, stage, artifact digest, expiry, and authorization identity in each gate request; recover native `Interrupt.id` and validate it on resume. (Corrective owner: `close-agent-framework-verification-gaps` 8.1–8.5.)
- [x] 6.4 Add visited-node trace tests for approval at each gate, four sequential approvals, rejection/backtrack, expired decision, cross-run decision, duplicate decision, forbidden target, and non-reexecution of completed artifact stages.
- [x] 6.5 Add graph validation tests for missing entry, invalid target, unreachable stage, unintended fan-out, and non-terminating backtrack.

## 7. Unify the Runner and Checkpointer Lifecycle

- [x] 7.1 Consume the converged `agent-core` async checkpointer boundary from `run`, `astream`, status inspection, and `resume`; do not add a harness-local saver factory.
- [x] 7.2 Verify first-use `AsyncPostgresSaver.setup()` provisioning through the core boundary and keep its opened context alive for the full harness operation.
- [x] 7.3 Preserve one `thread_id` and checkpoint backend across interrupt, process restart, status, and streaming; resume with `Command(resume={pending_interrupt.id: decision})`.
- [x] 7.4 Fail closed on unknown run, mismatched thread/interrupt, incompatible checkpoint version, saver setup error, and unauthorized resume without starting a new workflow. (Corrective owner: `close-agent-framework-verification-gaps` 9.1–9.6.)
- [x] 7.5 Finalize `agent-core/docker-entrypoint-initdb.d/20-create-harness-db.sql` for fresh local-development volumes, add non-destructive bootstrap validation, and—only after explicit database-migration approval—create the missing `agent_harness` database in the existing local volume. Use `HARNESS_DURABLE=true` and `TDT_POSTGRES_URL=postgresql://agent_core:agent_core_dev@localhost:54329/agent_harness`; do not log credentials or mutate any production database.
- [x] 7.6 Implement status/history through bounded public `aget_state`/`aget_state_history` calls and reject private saver inspection. (Corrective owner: `close-agent-framework-verification-gaps` 9.4–9.6.)
- [x] 7.7 Document the boundary between LangGraph workflow checkpoints and optional DBOS scheduled execution; do not treat them as interchangeable.
- [x] 7.8 Add real `AsyncPostgresSaver` integration tests proving setup on first use, completed artifact nodes do not rerun after runner/process recreation, only the dedicated gate may re-execute, bounded status/history and streaming observe the same pending interrupt, and authorized resume advances the original thread without private saver access.

## 8. Extract Stages Incrementally

- [x] 8.1 Extract intake, context, and clarify behind the stage contract; verify characterization parity before proceeding. (Parity evidence owner: `close-agent-framework-verification-gaps` 2.8, 7.4, 11.3.)
- [x] 8.2 Extract spec and its gate; verify artifact, validation, trace, and approval parity. (Parity evidence owner: `close-agent-framework-verification-gaps` 2.8, 8.5, 11.3.)
- [x] 8.3 Extract impact and design plus the design gate; verify GitNexus evidence and routing parity. (Parity evidence owner: `close-agent-framework-verification-gaps` 2.8, 8.5, 11.3.)
- [x] 8.4 Extract API contract and implementation plan plus its gate; verify artifact and routing parity. (Parity evidence owner: `close-agent-framework-verification-gaps` 2.8, 8.5, 11.3.)
- [x] 8.5 Extract coding plan and plan review plus its gate; verify revision and backtrack parity. (Parity evidence owner: `close-agent-framework-verification-gaps` 2.8, 8.5, 11.3.)
- [x] 8.6 Extract test plan and verification; verify final status, report, and trace parity. (Parity evidence owner: `close-agent-framework-verification-gaps` 2.8, 8.5, 11.3.)
- [x] 8.7 Keep simple stages in a single module unless independent tools or validators justify subpackages; avoid directory/file proliferation as a goal.

## 9. Evaluate Native Parallelism

- [x] 9.1 Measure each stage's read/write fields, tool side effects, authority, usage budget, and ordering assumptions.
- [x] 9.2 Keep every stage sequential unless at least one candidate branch passes the safety analysis and produces equivalent deterministic outputs.
- [x] 9.3 Record this task as not applicable: the measured dependency, scalar-write, gate-ordering, and budget analysis found no safe branch, so no fan-out/fan-in edge or dormant parallelism API is introduced.
- [x] 9.4 If no branch qualifies, document the evidence and close parallelism as a non-change rather than adding a dormant boolean/API. (Corrective owner: `close-agent-framework-verification-gaps` 7.1–7.4.)

## 10. CLI Migration and Compatibility

- [x] 10.1 Route `run`, `status`, `report`, `approve`, and `reject` through the corrected composition root and unified runner.
- [x] 10.2 Preserve existing public imports through documented delegating adapters only while fixture parity is being established.
- [x] 10.3 Publish migration examples from inherited config, string tool/capability lookup, and monolithic builder use to composed/native APIs.
- [x] 10.4 Remove old entry points only in a separate reviewable commit after the compatibility gate passes and rollback behavior is documented.

## 11. Verification and Rollback

- [x] 11.1 After completing the remaining implementation, run `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests --strict`, and `uv run pytest -x` from `agent-harness/`. (Closure evidence owner: `close-agent-framework-verification-gaps` 11.1–11.3.)
- [x] 11.2 Re-run the shared `agent-core`/`agent-docs-sync`/`agent-harness` upstream compatibility matrix and confirm only public Pydantic AI, Harness, and LangGraph contracts are used after the final state/configuration changes.
- [x] 11.3 After tasks 3.6, 5.4–5.6, 7.5, and 7.8, run end-to-end CLI plus real durable Postgres restart/resume suites under bounded read-only authority with `HARNESS_DURABLE=true` and `TDT_POSTGRES_URL`; record backend identity and prove no production database was touched.
- [x] 11.4 Run GitNexus `detect_changes` against the default branch after implementation and confirm affected symbols and execution flows match the approved impact scope. (Closure evidence owner: `close-agent-framework-verification-gaps` 11.5.)
- [x] 11.5 Re-run rollback after the final reducer/schema decision with new, completed, and pending-gate checkpoint fixtures; fail before writes when the old path cannot read a checkpoint version.
- [x] 11.6 Update harness architecture, workflow, configuration, gate, persistence, and stage-extension documentation with the final reducer, canonical environment, local bootstrap, and real Postgres composition boundary.
