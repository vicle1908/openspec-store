## 1. Accept Prerequisites and Freeze Cross-Repository Ownership

- [x] 1.1 Verify `restore-agent-pydantic-quality-gates` has accepted immutable repository SHAs and all required Ruff, strict-mypy, and pytest gates pass; record the cross-reference and leave this task incomplete if any prerequisite is missing.
- [x] 1.2 Verify `enforce-openspec-archive-readiness-gates` has an accepted committed validator/workflow result and passes against its own SHA; record the cross-reference before any capability implementation.
- [x] 1.3 From `/Users/androidteam/Developer`, load apply context from `/Users/androidteam/Developer/.worktrees/pydantic-ai-openspec-followups` and publish separate writer packets for agent-core, agent-docs-sync, agent-harness, and openspec-store; verify repo-local planning context is not treated as sibling-repository write authority.
- [x] 1.4 Publish exact base SHAs, raw dirty inventories, content fingerprints, selected paths, and preservation boundaries for every writer packet; verify default-checkout dirt and active observability/JTI work are not selected.
- [x] 1.5 Refresh GitNexus only through the reviewed single-writer workflow or record current Graphify/direct-call-site fallback evidence; verify no stale index risk count is used as acceptance evidence.
- [x] 1.6 Create the corrective evidence ledger mapping the five reviewed archived dependency/capability changes by exact archive path to this change’s tasks and closure gates; reconcile the proposal count with the ledger and verify archived files remain byte-identical to the accepted store base.

## 2. Reconcile Agent-Core Public Composition

- [x] 2.1 Add public-boundary RED tests showing omitted optional capabilities do not install compaction, reminders, spend, planning, advisor, conversation search, or ToolGuardrail; verify the tests fail against the frozen pre-change agent-core SHA.
- [x] 2.2 Remove implicit optional TieredCompaction, SystemReminders, and SpendLimits creation from the internal runtime while preserving instrumentation, tool preparation, hooks, and classified fallback StepPersistence; retain any necessary internal convenience kwargs only as undocumented compatibility shims unreachable through `BaseAgent`/`build_agent`, and verify omitted and explicitly supplied public capability tests pass.
- [x] 2.3 Preserve caller-supplied capability object identity and relative order through `build_agent` → `BaseAgent` → runtime composition, and verify authority/tool visibility regression tests pass.
- [x] 2.4 Delete the unread harness-capability dictionaries from `AgentConfig`, update its characterization tests and stale docs, and verify supported `AgentSpec` capability composition still passes without adding a second registry or generic builder layer.
- [x] 2.5 Characterize the existing `create_conversation_search` helper as non-exported, change it to require a caller-owned snapshot store and construct `scope="conversation"`, document that all-store search requires direct explicit upstream composition under a caller-owned single-tenant policy, and verify no other generic capability builders are introduced.

## 3. Share Persistence with Conversation Search

- [x] 3.1 Verify `create_conversation_search(store=...)` uses the exact store object supplied to StepPersistence without private upstream attribute access, constructs conversation scope, and rejects a missing/unavailable declared store before model or tool execution.
- [x] 3.2 Add a public-agent behavioral test that writes deterministic snapshots, compacts active context, and retrieves a dropped fact through ConversationSearch using the same retained store.
- [x] 3.3 Add a two-conversation shared-store regression using distinct stable correlation/conversation identities; verify each search returns only its own history and a missing identity returns no corpus rather than falling back to all runs.
- [x] 3.4 Verify step persistence without conversation search keeps existing same-process/restart-safe diagnostics and creates no search tool implicitly; add bounded-retention coverage proving pruned snapshots are not claimed as searchable.

## 4. Wire Docs-Sync Tool Guardrails Without Forking Containment

- [x] 4.1 Add RED production-construction tests proving generation/full-sync currently omit ToolGuardrail and check/discovery modes remain read-only; verify tests bind to the accepted agent-core worktree.
- [x] 4.2 Replace the prefix-only write guard with an exact-selector ToolGuardrail for `write_doc.path` and `sync_spec.main_path`; require `workspace_root` and approved roots, call the existing `resolve_allowed_write_path`, leave `sync_spec.delta_path` under read authority, add direct `ToolCallInfo` coverage plus characterization coverage for all existing resolver callers, and verify the shared CRITICAL resolver itself is unchanged.
- [x] 4.3 Compose the exact write-path, `shell_execute.command`, and result-redaction ToolGuardrails into docs-sync generation/full-sync agents while preserving Input/OutputGuardrails, containment hooks, approval gates, exactly-once ledger behavior, and mode-specific tool visibility; verify the production capability inventory and selector names.
- [x] 4.4 Execute unsafe write, dangerous shell, and sensitive-result attempts through the public agent/tool boundary; record whether the outer containment hook or innermost ToolGuardrail rejected each attempt, prove a bounded valid write reaches the ToolGuardrail before approval, verify no side effect occurs and raw values are absent, and require exactly one stable redacted audit event through the existing sink without falsely attributing an outer-hook rejection to ToolGuardrail.
- [x] 4.5 Verify check/discovery modes do not receive write-capable ToolGuardrails or broaden tool authority.

## 5. Resolve Dependency Extras and Documentation

- [x] 5.1 Remove `[dynamic-workflow]` from agent-harness and agent-docs-sync root dependencies, run `uv sync`, and verify their direct dependency declarations omit the extra even if an accepted agent-core dependency retains it transitively.
- [x] 5.2 Retain `[dynamic-workflow]` in agent-core only after `build_agent(..., capabilities=[DynamicWorkflow(...)])` executes a deterministic bounded workflow against harness `0.23.0` and resolved `pydantic-monty>=0.0.19`; verify public authority validation recognizes DynamicWorkflow as runtime authoring and fails without the bounded grant/audit policy, update the dependency baseline, and remove the extra from agent-core too if either the execution seam, authority gate, or lockfile agreement fails.
- [x] 5.3 Update agent-core AGENTS.md, framework/harness guides, architecture, research documents, and examples to remove obsolete `harness_config` and Monty `0.0.18` claims; replace deprecated aliases and invalid constructor values, require a shared-store conversation-scoped search example, and verify every representative snippet imports and constructs against the frozen tuple.
- [x] 5.4 Update agent-docs-sync configuration/framework/reference docs for exact `write_doc.path`, `sync_spec.main_path`, and conditional `shell_execute.command` ToolGuardrail composition, layered audit attribution, explicit capability defaults, and dependency-extra ownership; verify snippets and links.
- [x] 5.5 Update all affected SPEC_INDEX.md files after spec sync and verify index-to-source/document ownership is accurate.
- [x] 5.6 Cross-reference `establish-agent-observability-contract` as sole telemetry-activation owner and verify this change adds no tracing-provider, trace/log correlation, evaluation-linkage, or credential work.

## 6. Replace Constructibility Evidence with Layered Behavior Tests

- [x] 6.1 Add a public-boundary deterministic compaction functional test covering below-target and exceeded-target behavior, protected-fact preservation, configured receipts, retained-snapshot recovery, and truthful behavior when the caller's bounded retention policy has pruned an older snapshot.
- [x] 6.2 Add a multi-request SystemReminders integration test that proves reminder insertion and absence of duplicate implicit capabilities.
- [x] 6.3 Add SpendLimits unit/integration tests with a deterministic price function for enforcement, scoped budgets, warning thresholds, and `on_unpriced='raise'`; verify no zero-priced warning is counted as a pass.
- [x] 6.4 Add Planning integration tests with a disposable PlanStore that create, read, update, and complete a real plan with subtasks through a public agent run.
- [x] 6.5 Add Advisor functional tests that execute deterministic local consultation, enforce `max_uses`, and prove failure fallback without resolving a global model route.
- [x] 6.6 Rename or replace the misleading end-to-end constructibility file and verify every archived capability claim maps to an executing unit/integration/functional test or remains an open corrective-ledger item.

## 7. Verify Each Repository and Rehearse Rollback

- [x] 7.1 Run full pytest, full Ruff, Ruff format check, and strict mypy in agent-core with isolated caches; record exact commands, exits, passes, skips, warnings, and import origins.
- [x] 7.2 Run full pytest, full Ruff, Ruff format check, and strict mypy in agent-docs-sync with the accepted agent-core binding; record exact commands, exits, passes, skips, warnings, and import origins.
- [x] 7.3 Run full pytest, full Ruff, Ruff format check, and strict mypy in agent-harness with the accepted agent-core binding; record exact commands, exits, passes, skips, warnings, and import origins.
- [x] 7.4 Run public CLI/model-free smoke checks for all three consumers plus deterministic public capability runs without credentials; verify model-free commands do not resolve LLM identity.
- [x] 7.5 Recompute HEADs, raw dirty inventories, content fingerprints, dependency origins, and Graphify/GitNexus freshness after all gates; invalidate and rerun any evidence affected by drift.
- [x] 7.6 Rehearse agent-core rollback in a disposable worktree, including prior explicit-capability behavior and lockfile restoration, and record focused gate results.
- [x] 7.7 Rehearse agent-docs-sync rollback in a disposable worktree, including prior guardrail composition and lockfile restoration, and record focused gate results.
- [x] 7.8 Rehearse agent-harness rollback in a disposable worktree, including dependency-extra restoration, and record focused gate results.

## 8. Integrate Repositories, Sync Specs, and Archive Safely

- [x] 8.1 Run strict validation for this change and the full store before synchronization; verify all seven delta paths come only from `artifactPaths.specs.existingOutputPaths`.
- [x] 8.2 Sync all seven delta capabilities, update the `agent-core-capabilities` Purpose from its archive placeholder, and verify removed historical requirements are absent, modified requirements are present, and unrelated main-spec scenarios are preserved.
- [x] 8.3 Complete the corrective ledger and immutable integrated evidence manifest, verify every task has a reproducible closure artifact, and keep any failed/skipped/stale requirement open.
- [x] 8.4 Review and commit the scoped agent-core result and record its full 40-character SHA.
- [x] 8.5 Review and commit the scoped agent-docs-sync result and record its full 40-character SHA.
- [x] 8.6 Review and commit the scoped agent-harness result and record its full 40-character SHA.
- [x] 8.7 Review and commit the synchronized openspec-store result, including updated SPEC_INDEX files and corrective evidence, and record its full 40-character SHA.
- [x] 8.8 Perform the pre-archive source-identity recapture required by `readiness-evidence`, run the committed archive-readiness validator, and archive only when every required task/gate passes against the same immutable identities.
