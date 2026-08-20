## 1. Accept Prerequisites and Freeze Cross-Repository Ownership

- [ ] 1.1 Verify `restore-agent-pydantic-quality-gates` has accepted immutable repository SHAs and all required Ruff, strict-mypy, and pytest gates pass; record the cross-reference and leave this task incomplete if any prerequisite is missing.
- [ ] 1.2 Verify `enforce-openspec-archive-readiness-gates` has an accepted committed validator/workflow result and passes against its own SHA; record the cross-reference before any capability implementation.
- [ ] 1.3 From `/Users/androidteam/Developer`, load apply context from `/Users/androidteam/Developer/.worktrees/pydantic-ai-openspec-followups` and publish separate writer packets for agent-core, agent-docs-sync, agent-harness, and openspec-store; verify repo-local planning context is not treated as sibling-repository write authority.
- [ ] 1.4 Publish exact base SHAs, raw dirty inventories, content fingerprints, selected paths, and preservation boundaries for every writer packet; verify default-checkout dirt and active observability/JTI work are not selected.
- [ ] 1.5 Refresh GitNexus only through the reviewed single-writer workflow or record current Graphify/direct-call-site fallback evidence; verify no stale index risk count is used as acceptance evidence.
- [ ] 1.6 Create the corrective evidence ledger mapping the five reviewed archived changes to this change’s exact tasks and closure gates; verify archived files remain byte-identical to the accepted store base.

## 2. Reconcile Agent-Core Public Composition

- [ ] 2.1 Add public-boundary RED tests showing omitted optional capabilities do not install compaction, reminders, spend, planning, advisor, conversation search, or ToolGuardrail; verify the tests fail against the frozen pre-change agent-core SHA.
- [ ] 2.2 Remove implicit optional TieredCompaction, SystemReminders, and SpendLimits creation from the internal runtime while preserving instrumentation, tool preparation, hooks, and classified fallback StepPersistence; retain any necessary internal convenience kwargs only as undocumented compatibility shims unreachable through `BaseAgent`/`build_agent`, and verify omitted and explicitly supplied public capability tests pass.
- [ ] 2.3 Preserve caller-supplied capability object identity and relative order through `build_agent` → `BaseAgent` → runtime composition, and verify authority/tool visibility regression tests pass.
- [ ] 2.4 Delete the unread harness-capability dictionaries from `AgentConfig`, update its characterization tests and stale docs, and verify supported `AgentSpec` capability composition still passes without adding a second registry or generic builder layer.
- [ ] 2.5 Characterize the existing `create_conversation_search` helper as non-exported, change it to require a caller-owned snapshot store, and verify no other generic capability builders are introduced.

## 3. Share Persistence with Conversation Search

- [ ] 3.1 Verify `create_conversation_search(store=...)` uses the exact store supplied to StepPersistence and rejects a missing/unavailable declared store before model or tool execution.
- [ ] 3.2 Add a public-agent behavioral test that writes deterministic snapshots, compacts active context, and retrieves a dropped fact through ConversationSearch using the same store.
- [ ] 3.3 Verify step persistence without conversation search keeps existing same-process/restart-safe diagnostics and creates no search tool implicitly.

## 4. Wire Docs-Sync Tool Guardrails Without Forking Containment

- [ ] 4.1 Add RED production-construction tests proving generation/full-sync currently omit ToolGuardrail and check/discovery modes remain read-only; verify tests bind to the accepted agent-core worktree.
- [ ] 4.2 Change the write ToolGuardrail to require `workspace_root` and approved roots and call the existing `resolve_allowed_write_path`; add characterization coverage for all existing resolver callers and verify the shared CRITICAL resolver itself is unchanged.
- [ ] 4.3 Compose write-path, shell-command, and result-redaction ToolGuardrails into docs-sync generation/full-sync agents while preserving Input/OutputGuardrails, containment hooks, approval gates, and exactly-once ledger behavior; verify the production capability inventory.
- [ ] 4.4 Execute unsafe write, dangerous shell, and sensitive-result attempts through the public agent/tool boundary and verify no side effect occurs, raw sensitive values are absent, and the existing audit path records a redacted blocked attempt.
- [ ] 4.5 Verify check/discovery modes do not receive write-capable ToolGuardrails or broaden tool authority.

## 5. Resolve Dependency Extras and Documentation

- [ ] 5.1 Remove `[dynamic-workflow]` from agent-harness and agent-docs-sync root dependencies, run `uv sync`, and verify their direct dependency declarations omit the extra even if an accepted agent-core dependency retains it transitively.
- [ ] 5.2 Retain `[dynamic-workflow]` in agent-core only after a public DynamicWorkflow import/construct test with deterministic test agents passes against harness `0.23.0` and resolved `pydantic-monty>=0.0.19`; update the dependency baseline and fail if the lockfile disagrees.
- [ ] 5.3 Update agent-core AGENTS.md, framework/harness guides, architecture, research documents, and examples to remove obsolete `harness_config` and Monty `0.0.18` claims; verify all code snippets import and construct successfully.
- [ ] 5.4 Update agent-docs-sync configuration/framework/reference docs for production ToolGuardrail composition, explicit capability defaults, and dependency-extra ownership; verify snippets and links.
- [ ] 5.5 Update all affected SPEC_INDEX.md files after spec sync and verify index-to-source/document ownership is accurate.
- [ ] 5.6 Cross-reference `establish-agent-observability-contract` as sole telemetry-activation owner and verify this change adds no tracing-provider, trace/log correlation, evaluation-linkage, or credential work.

## 6. Replace Constructibility Evidence with Layered Behavior Tests

- [ ] 6.1 Add a public-boundary deterministic compaction functional test covering below-target and exceeded-target behavior, protected-fact preservation, and configured receipts.
- [ ] 6.2 Add a multi-request SystemReminders integration test that proves reminder insertion and absence of duplicate implicit capabilities.
- [ ] 6.3 Add SpendLimits unit/integration tests with a deterministic price function for enforcement, scoped budgets, warning thresholds, and `on_unpriced='raise'`; verify no zero-priced warning is counted as a pass.
- [ ] 6.4 Add Planning integration tests with a disposable PlanStore that create, read, update, and complete a real plan with subtasks through a public agent run.
- [ ] 6.5 Add Advisor functional tests that execute deterministic local consultation, enforce `max_uses`, and prove failure fallback without resolving a global model route.
- [ ] 6.6 Rename or replace the misleading end-to-end constructibility file and verify every archived capability claim maps to an executing unit/integration/functional test or remains an open corrective-ledger item.

## 7. Verify Each Repository and Rehearse Rollback

- [ ] 7.1 Run full pytest, full Ruff, Ruff format check, and strict mypy in agent-core with isolated caches; record exact commands, exits, passes, skips, warnings, and import origins.
- [ ] 7.2 Run full pytest, full Ruff, Ruff format check, and strict mypy in agent-docs-sync with the accepted agent-core binding; record exact commands, exits, passes, skips, warnings, and import origins.
- [ ] 7.3 Run full pytest, full Ruff, Ruff format check, and strict mypy in agent-harness with the accepted agent-core binding; record exact commands, exits, passes, skips, warnings, and import origins.
- [ ] 7.4 Run public CLI/model-free smoke checks for all three consumers plus deterministic public capability runs without credentials; verify model-free commands do not resolve LLM identity.
- [ ] 7.5 Recompute HEADs, raw dirty inventories, content fingerprints, dependency origins, and Graphify/GitNexus freshness after all gates; invalidate and rerun any evidence affected by drift.
- [ ] 7.6 Rehearse agent-core rollback in a disposable worktree, including prior explicit-capability behavior and lockfile restoration, and record focused gate results.
- [ ] 7.7 Rehearse agent-docs-sync rollback in a disposable worktree, including prior guardrail composition and lockfile restoration, and record focused gate results.
- [ ] 7.8 Rehearse agent-harness rollback in a disposable worktree, including dependency-extra restoration, and record focused gate results.

## 8. Integrate Repositories, Sync Specs, and Archive Safely

- [ ] 8.1 Run strict validation for this change and the full store before synchronization; verify all seven delta paths come only from `artifactPaths.specs.existingOutputPaths`.
- [ ] 8.2 Sync all seven delta capabilities, update the `agent-core-capabilities` Purpose from its archive placeholder, and verify removed historical requirements are absent, modified requirements are present, and unrelated main-spec scenarios are preserved.
- [ ] 8.3 Complete the corrective ledger and immutable integrated evidence manifest, verify every task has a reproducible closure artifact, and keep any failed/skipped/stale requirement open.
- [ ] 8.4 Review and commit the scoped agent-core result and record its full 40-character SHA.
- [ ] 8.5 Review and commit the scoped agent-docs-sync result and record its full 40-character SHA.
- [ ] 8.6 Review and commit the scoped agent-harness result and record its full 40-character SHA.
- [ ] 8.7 Review and commit the synchronized openspec-store result, including updated SPEC_INDEX files and corrective evidence, and record its full 40-character SHA.
- [ ] 8.8 Perform the pre-archive source-identity recapture required by `readiness-evidence`, run the committed archive-readiness validator, and archive only when every required task/gate passes against the same immutable identities.
