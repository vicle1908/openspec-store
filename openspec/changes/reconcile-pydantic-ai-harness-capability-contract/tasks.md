## 1. Accept the Quality Prerequisite and Freeze Ownership

- [ ] 1.1 Verify `restore-agent-pydantic-quality-gates` has accepted immutable result SHAs and all required Ruff, strict-mypy, and pytest gates pass; record the cross-reference and leave this task incomplete if any prerequisite is missing.
- [ ] 1.2 Publish one writer/worktree per agent-core, agent-docs-sync, agent-harness, and openspec-store with exact base SHA, raw dirty inventory, content fingerprint, and preservation boundary; verify current default-checkout dirt and active observability/JTI changes are not selected for mutation.
- [ ] 1.3 Refresh GitNexus only through the reviewed single-writer workflow or record current direct-call-site fallback evidence; verify no stale index risk count is used as acceptance evidence.
- [ ] 1.4 Create the corrective evidence ledger mapping the four reviewed archived changes to this change’s exact tasks and closure gates; verify archived files remain byte-identical to the accepted store base.

## 2. Reconcile Agent-Core Public Composition

- [ ] 2.1 Add public-boundary RED tests showing omitted optional capabilities do not install compaction, reminders, spend, planning, advisor, conversation search, or ToolGuardrail; verify the tests fail against the frozen pre-change agent-core SHA.
- [ ] 2.2 Remove implicit optional TieredCompaction, SystemReminders, and SpendLimits creation from the internal runtime while preserving instrumentation, tool preparation, hooks, and classified fallback StepPersistence; verify omitted and explicitly supplied capability tests pass.
- [ ] 2.3 Preserve caller-supplied capability object identity and relative order through `build_agent` → `BaseAgent` → runtime composition, and verify authority/tool visibility regression tests pass.
- [ ] 2.4 Remove unread capability dictionaries from `AgentConfig` or materialize them before public construction with typed fail-closed validation; verify no accepted configuration key is silently ignored.
- [ ] 2.5 Add explicit typed capability builders/examples for compaction, reminders, priced spend limits, planning, advisor, and conversation search, and verify each returns public upstream types without private imports.

## 3. Share Persistence with Conversation Search

- [ ] 3.1 Change ConversationSearch construction to require a caller-owned snapshot source/store instead of allocating a private fresh store, and verify object identity with the supplied StepPersistence source.
- [ ] 3.2 Add a public-agent behavioral test that writes deterministic snapshots, compacts active context, and retrieves a dropped fact through ConversationSearch using the same store; verify an unavailable declared store fails before model/tool execution.
- [ ] 3.3 Verify step persistence without conversation search keeps existing same-process/restart-safe diagnostics and creates no search tool implicitly.

## 4. Wire Docs-Sync Tool Guardrails

- [ ] 4.1 Add RED production-construction tests proving generation/full-sync currently omit ToolGuardrail and check/discovery modes remain read-only; verify the tests bind to the accepted agent-core worktree.
- [ ] 4.2 Compose write-path, shell-command, and result-redaction ToolGuardrails into docs-sync generation/full-sync agents while preserving Input/OutputGuardrails, containment hooks, approval gates, and exactly-once ledger behavior; verify the production capability inventory.
- [ ] 4.3 Execute unsafe write, dangerous shell, and sensitive-result attempts through the public agent/tool boundary and verify no tool side effect occurs, raw sensitive values are absent, and the existing audit path records a redacted blocked attempt.
- [ ] 4.4 Verify check/discovery modes do not receive write-capable ToolGuardrails or broaden tool authority.

## 5. Resolve Dependency Extras and Documentation

- [ ] 5.1 Remove `[dynamic-workflow]` from agent-harness and agent-docs-sync, retain it only in agent-core, run `uv sync`, and verify all three lockfiles and dependency-baseline tests resolve `pydantic-ai==2.32.0` and `pydantic-ai-harness==0.23.0` with the intended extras.
- [ ] 5.2 Verify no agent-harness or docs-sync production/test import requires DynamicWorkflow; if a direct consumer is found, stop and update the proposal/specs instead of silently retaining the extra.
- [ ] 5.3 Update agent-core and docs-sync guides, AGENTS.md capability tables, examples, and spec indexes to describe explicit typed defaults, shared persistence, guardrail authority, dependency-extra ownership, and failure conditions; verify all documented code snippets import and construct successfully.
- [ ] 5.4 Cross-reference `establish-agent-observability-contract` as sole telemetry-activation owner and verify this change adds no tracing-provider, trace/log correlation, evaluation-linkage, or credential work.

## 6. Replace Constructibility Evidence with Behavior

- [ ] 6.1 Add a public-boundary deterministic compaction test covering below-target and exceeded-target behavior, protected-fact preservation, and configured receipts.
- [ ] 6.2 Add a multi-request SystemReminders test that proves reminder insertion and absence of duplicate implicit capabilities.
- [ ] 6.3 Add priced SpendLimits tests for threshold warning/enforcement, per-model accounting, scoped budgets, and `on_unpriced='raise'`; verify no zero-priced warning is counted as a pass.
- [ ] 6.4 Add Planning tests that create, read, update, and complete a real plan with subtasks through a public agent run.
- [ ] 6.5 Add Advisor tests that execute deterministic consultation, enforce `max_uses`, record the capability result, and prove graceful local failure behavior without resolving a global model route.
- [ ] 6.6 Replace or rename the misleading end-to-end constructibility test file and verify every archived capability claim maps to an executing behavioral test or remains an open corrective-ledger item.

## 7. Cross-Repository Verification and Rollback

- [ ] 7.1 Run full pytest, full Ruff, Ruff format check, and strict mypy in agent-core, agent-docs-sync, and agent-harness with isolated caches and accepted editable import origins; record exact commands, exits, passes, skips, and warnings.
- [ ] 7.2 Run public CLI/model-free smoke checks for all three consumers and deterministic public capability runs without credentials; verify model-free commands do not resolve LLM identity.
- [ ] 7.3 Recompute HEADs, raw dirty inventories, content fingerprints, dependency origins, and Graphify/GitNexus freshness after all gates; invalidate and rerun any evidence affected by drift.
- [ ] 7.4 Rehearse per-repository rollback in disposable worktrees, including prior explicit-capability behavior and lockfile restoration, and record evidence that default checkouts and active changes remain unchanged.

## 8. Spec Sync and Archive Readiness

- [ ] 8.1 Run strict validation for this change and the full store, then use `artifactPaths.specs.existingOutputPaths` to sync all seven delta capabilities; verify removed historical requirements are absent and unrelated scenarios are preserved.
- [ ] 8.2 Update each repository SPEC_INDEX.md for the synchronized capability paths and verify index-to-source/document ownership is accurate.
- [ ] 8.3 Complete the corrective ledger and immutable integrated evidence manifest, verify every checkbox has a reproducible closure artifact, and leave archive tasks incomplete if a required gate is failed, skipped, stale, or unavailable.
- [ ] 8.4 Commit each repository and store result with full 40-character SHAs, perform the pre-archive source-identity recapture required by `readiness-evidence`, and archive only after `enforce-openspec-archive-readiness-gates` passes.
