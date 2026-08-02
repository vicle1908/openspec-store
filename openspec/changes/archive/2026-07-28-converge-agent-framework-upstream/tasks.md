## 1. Confirm the Stabilized Starting Point

- [x] 1.1 Complete and verify `stabilize-agent-framework-integration`; do not begin this change while either repository still has silent capability fallback, incompatible framework versions, or skipped DynamicWorkflow imports.
- [x] 1.2 Rerun GitNexus impact for `BaseAgent.run`, `AgentRuntime.__init__`, `_build_harness_capabilities`, `WorkflowEngine.run`, and `build_full_engine`; record the CRITICAL approval checkpoints before editing.
- [x] 1.3 Inventory every `harness_config` key, custom hook event, private toolset access, `CommandResult`, dict-only state, `AgentSpec` reconstruction, and custom memory store used by `agent-core` and `agent-docs-sync`.
- [x] 1.4 Create executable characterization tests for each legacy surface so the compatibility window has measurable parity and removal criteria.

## 2. Introduce Typed SDK Composition

- [x] 2.1 In `agent-core/src/agent_core/sdk/`, define a stable composition API accepting upstream `AgentCapability` and `AgentToolset` values plus explicit TDT policy inputs; do not re-export upstream concrete capability classes.
- [x] 2.2 Define an immutable `ConsumerRuntimeProfile` value object in `agent-core/src/agent_core/sdk/`; document that consumer configuration contains it rather than subclasses it.
- [x] 2.3 Preserve capability identity, order, stable ID, description, deferred-loading behavior, and constructor policy through SDK and runtime construction.
- [x] 2.4 Add validation that rejects objects outside supported capability/toolset protocols and reports the rejected input category.
- [x] 2.5 Add authority-profile validation requiring bounded roots/allowlists, limits, and audit policy for filesystem, shell, code, network, and runtime-authoring capabilities.
- [x] 2.6 Add the legacy `ConsumerConfig`/`harness_config` adapter at one composition boundary with warnings and equivalent composed-profile examples.
- [x] 2.7 Make the SDK require an explicit gateway or explicit TDT gateway resolver; reject missing gateways before `BaseAgent` construction and add direct/resolved/missing contract tests.

## 3. Replace the Exhaustive Capability Mirror

- [x] 3.1 Refactor `AgentRuntime.__init__` to pass pre-built public capabilities and toolsets directly to Pydantic AI.
- [x] 3.2 Reduce `_build_harness_capabilities` to the temporary legacy adapter and narrow TDT-owned secure-profile factories; remove generic upstream constructor duplication.
- [x] 3.3 Add a conformance test using a public Harness capability unknown to the legacy key schema and prove it composes without an `agent-core` code change.
- [x] 3.4 Replace private `_function_toolset` access with official toolsets and `PrepareTools` filtering while preserving names, schemas, retries, metadata, and ownership.
- [x] 3.5 Add tool preparation tests for TDT allowlists, approval metadata, per-run dependencies, and denial of high-authority tools by default.

## 4. Migrate Lifecycle Ownership to Official Hooks

- [x] 4.1 Map every `HookRegistry`/`HookAdapter` lifecycle event and hook pack to the corresponding public Pydantic AI Hooks callback or supported event-stream consumer.
- [x] 4.2 Install one Hooks capability as lifecycle authority and migrate budget enforcement, structured audit, Langfuse, MLflow, and consumer callbacks without duplicate dispatch.
- [x] 4.3 Preserve upstream callback return semantics for request context, tool arguments, output, validation, and error recovery; add protocol-level tests.
- [x] 4.4 Adapt supported legacy registrations through `HookRegistry` with a migration warning and exactly-once behavior during the compatibility window.
- [x] 4.5 Add instrumentation and process-event-stream tests proving observability receives model, tool, output, deferred, error, and usage events once.

## 5. Finish Native Deferred and Stream Integration

- [x] 5.1 Expose public SDK configuration for Pydantic AI deferred call handling and event-stream processing without introducing TDT-shaped duplicate protocols.
- [x] 5.2 Remove internal reconstruction of deferred calls/results where the public upstream types can be preserved.
- [x] 5.3 Add end-to-end pause/resume tests across Pydantic AI and LangGraph that preserve tool call ID, thread ID, interrupt ID, authorization, usage, and audit correlation.
- [x] 5.4 Add streaming tests that verify event ordering, cancellation, partial-output policy, and exactly-once instrumentation.

## 6. Make Agent Specifications Round-Trip Faithfully

- [x] 6.1 Replace manual `AgentSpec.from_file` projection in `agent-core/src/agent_core/_ai/config_loader.py` with a mapping of upstream serializable fields, code-supplied tools/toolsets, registered custom capability types, and TDT policy validation.
- [x] 6.2 Construct agents through public `Agent.from_file`/`Agent.from_spec` without assigning undeclared fields or reconstructing raw agents through private attributes.
- [x] 6.3 Add JSON/YAML round-trip tests proving all supported fields retain equivalent behavior after serialization and loading.
- [x] 6.4 Reject unknown or lossy specification fields with their configuration path and add security tests preventing specs from granting undeclared high-authority capabilities.
- [x] 6.5 Add tests and guidance proving non-serializable capabilities such as Harness `DynamicWorkflow` are supplied through typed code composition rather than invented YAML fields.

## 7. Adopt Harness Memory Stores

- [x] 7.1 Define a narrow adapter between TDT-owned memory/search services and the public Harness `MemoryStore` protocol.
- [x] 7.2 Use public Harness `InMemoryStore`, `FileStore`, `SqliteMemoryStore`, or `PostgresMemoryStore` for generic memory lifecycle behavior instead of duplicating store mechanics in `agent-core`.
- [x] 7.3 Preserve TDT tenant, repository, correlation, retention, and authorization policy in the adapter and prove it with isolation tests.
- [x] 7.4 Use `StepPersistence` with public `InMemoryStepStore`, `FileStepStore`, or `SqliteStepStore` and the module-level `pydantic_ai_harness.step_persistence.continue_run(store, run_id=...)` helper for agent-step continuation; add ordering, tool-effect, persistence, and restart tests.
- [x] 7.5 Document rollback to the previous TDT memory adapter without changing persisted record identifiers or weakening tenant boundaries.
- [x] 7.6 Deprecate the custom `MemoryCapability`, dictionary-based memory wiring, and separate untyped `BaseAgent.memory` path; remove them only after the compatibility window and zero-caller census.

## 8. Thin the LangGraph Facade

- [x] 8.1 Add typed state schema support and explicit reducers to `agent-core/src/agent_core/orchestration/`; keep dict-only state behind the compatibility adapter.
- [x] 8.2 Replace new uses of custom `CommandResult` with native LangGraph `Command` for updates, routing, and resume.
- [x] 8.3 Implement an isolated `CommandResult`-to-`Command` adapter with deprecation warnings and parity tests for update, goto, and resume behavior.
- [x] 8.4 Expose native interrupt, checkpoint, async invocation, and streaming behavior through the workflow facade without translating away identifiers or errors.
- [x] 8.5 Add compile-time/runtime tests for invalid state updates, invalid targets, concurrent reducers, cancellation, and checkpoint recovery.
- [x] 8.6 Extend the existing `create_async_checkpointer` boundary to own TDT DSN resolution, explicit first-use `setup()` provisioning, and operation-scoped saver lifetime without adding a consumer-local saver factory.
- [x] 8.7 Add public `aget_state`/`aget_state_history` status examples and tests plus native `Interrupt.id` mapping tests for `Command(resume={pending_interrupt.id: decision})`.

## 9. Consolidate the Docs Consumer

- [x] 9.1 Define consumer-owned typed discovery, audit, generation, validation, and report state in `agent-docs-sync`.
- [x] 9.2 Select one canonical deterministic pipeline for check, update, discover, sync, and audit commands; route all CLI entry points through it.
- [x] 9.3 Remove overlapping manual agent construction in favor of the public typed SDK composition API and explicit docs policy inputs.
- [x] 9.4 Restrict DynamicWorkflow to bounded adaptive discovery where it demonstrates value; keep deterministic validation, write authorization, and reporting outside dynamic selection.
- [x] 9.5 Add old-versus-new fixture parity tests for CLI exit codes, discovered files, generated changes, validation results, reports, approvals, checkpoints, and audit events.
- [x] 9.6 Remove superseded builder paths only after parity tests pass and document the rollback switch to the stabilized deterministic pipeline.

## 10. Validate Additional Consumers

- [x] 10.1 Refresh the TDT workspace consumer census with GitNexus, Graphify, repository manifests, and source imports; verify that `agent-docs-sync` and `agent-harness` are active external framework consumers, `code-daily-scan` is manifest-only, and `ai-review`/`jira-epic-report` have no direct source integration.
- [x] 10.2 Classify each discovered consumer as direct typed adoption, compatibility-adapter adoption, documentation-only, or intentionally out of scope; keep `code-daily-scan` cleanup out of this implementation and create a separate OpenSpec change if removal is warranted.
- [x] 10.3 Add contract tests for each in-scope consumer before changing its integration and require a separate OpenSpec change where domain behavior or high-authority permissions would expand.
- [x] 10.4 Add a promotion checklist proving a candidate core abstraction is TDT-specific, required by two active consumers, absent upstream, free of consumer domain types, and covered by both consumer contract suites.
- [x] 10.5 Verify rebuilt deployment bundles contain the converged `agent-core` source and do not retain stale vendored copies; document the packaging check for `deployments/ai-review/deps/agent-core`.

## 11. Migrate the Harness Consumer

- [x] 11.1 In `agent-harness/src/agent_harness/config.py`, replace `HarnessConfig(ConsumerConfig)` with a domain config that contains the core runtime profile; add legacy load parity tests.
- [x] 11.2 In `agent-harness/src/agent_harness/agents/factory.py`, resolve and inject the TDT gateway explicitly and compose official toolsets, capabilities, hooks, and run-scoped instructions through the typed SDK.
- [x] 11.3 Add a construction regression test proving a stage agent reaches `BaseAgent.run` with a usable gateway and that missing gateway configuration fails before graph execution.
- [x] 11.4 Replace message reducers on `workspace_repos`, `errors`, and `gate_history` with reducers matching their actual string-list semantics; add concurrent-update tests.
- [x] 11.5 Replace the shared fan-out gate with dedicated post-stage gate nodes and assert the artifact-producing stage does not re-execute on approve, reject, backtrack, or sequential multi-gate resume.
- [x] 11.6 Refactor `WorkflowRunner.run`, `astream`, `resume`, and status inspection to consume the shared core checkpointer boundary, public state inspection, and native interrupt-ID mapping across process restart.
- [x] 11.7 Align `agent-harness-stage-modules` with native LangGraph topology and official agent-core/upstream composition; prohibit a duplicate registry, graph DSL, runtime TypedDict merger, string capabilities, and config inheritance.
- [x] 11.8 Run harness CLI fixture tests for run, stream, status, report, approve, reject, durable restart/resume, and bounded read-only authority.

## 12. Deprecate and Remove Compatibility Surfaces

- [x] 12.1 Publish the minimum one-minor-release and 30-day compatibility window plus replacement examples for `harness_config`, inherited consumer configuration, `HookRegistry`, private toolset access, `CommandResult`, dict-only state, lossy `AgentSpec` loading, and generic custom memory stores.
- [x] 12.2 Add one actionable warning per legacy surface at its public entry point and test that warnings do not duplicate within one construction/run.
- [x] 12.3 Measure manifests, imports, configuration files, examples, and deployment bundles; remove each compatibility adapter only after the minimum window passes and the census reports zero active callers.
- [x] 12.4 Add release-note and migration-guide checks that fail if a breaking removal lacks its replacement API, before/after example, and rollback guidance.

## 13. Verify Convergence and Rollback

- [x] 13.1 Run the full `agent-core`, `agent-docs-sync`, and `agent-harness` lint, strict typecheck, and test suites plus the legacy characterization and new upstream conformance suites.
- [x] 13.2 Run dependency inspection to prove only public Pydantic AI, Harness, and LangGraph imports are used for the migrated surfaces.
- [x] 13.3 Run Graphify queries over SDK composition, lifecycle, memory, orchestration, docs pipeline, and harness workflow paths, then run GitNexus `detect_changes` in each modified repository.
- [x] 13.4 Verify high-authority capabilities remain opt-in and bounded through negative filesystem, shell, network, code-execution, runtime-authoring, cross-tenant, and unauthorized-resume tests.
- [x] 13.5 Exercise rollback independently for typed composition, Hooks, native Commands, memory, docs-pipeline consolidation, and harness checkpoint/state changes; verify persisted IDs and deterministic behavior remain recoverable.
- [x] 13.6 Run the three-repository compatibility matrix against the pinned and candidate framework versions and fail on private upstream imports/attributes.
- [x] 13.7 Update architecture and consumer documentation with the final ownership boundary: upstream libraries own generic mechanics; TDT owns gateway, policy, budget, skills, tool authorization, and audit; consumers own domain state and topology.
