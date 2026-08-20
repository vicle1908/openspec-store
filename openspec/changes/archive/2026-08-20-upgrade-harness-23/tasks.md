# Tasks: Upgrade pydantic-ai-harness 0.11.0 → 0.23.0

## Phase 1: Dependency Upgrade ✅

- [x] Bump pydantic-ai-harness to >=0.23.0,<0.24 in agent-core/pyproject.toml
- [x] Bump pydantic-ai-harness to >=0.23.0,<0.24 in agent-harness/pyproject.toml
- [x] Bump pydantic-ai-harness to >=0.23.0,<0.24 in agent-docs-sync/pyproject.toml
- [x] Update uv.lock in all 3 repos
- [x] Update test_dependency_baseline.py assertions in all 3 repos

## Phase 2: Capability Integration ✅

- [x] Add TieredCompaction (DeduplicateFileReads → ClearToolResults → SummarizingCompaction) to AgentRuntime
- [x] Add SpendLimits + Budget (per-run $5, per-day $100) to AgentRuntime
- [x] Add Planning (enable_subtasks) to AgentRuntime
- [x] Add Advisor (model, max_uses) to AgentRuntime
- [x] Add SystemReminders + GoalReanchor to AgentRuntime
- [x] Add ConversationSearch factory to memory.py
- [x] Add AgentConfig extensions (advisor, conversation_search fields)
- [x] Fix ConsumerRuntimeProfile.max_iterations return type (int → int | None)
- [x] Export AssuranceLevel from agent_core.sdk

## Phase 3: Cross-Repo Fixes ✅

- [x] Fix agent-harness lifecycle_auth.py to import via SDK
- [x] Fix agent-harness workflow/runner.py to import via SDK
- [x] Fix agent-docs-sync architecture.md (remove HookRegistry)
- [x] Fix agent-docs-sync pyproject.toml (malformed keywords)

## Phase 4: Documentation Updates ✅

- [x] Update AGENTS.md capability table (add 6 new capabilities)
- [x] Update docs/harness-integration.md capability modules table
- [x] Update docs/framework-integration.md version constraints
- [x] Update docs/architecture.md (fix error root, hooks, remove duplicate _ai/)
- [x] Update docs/building-agents.md (remove HookRegistry)
- [x] Update docs/evaluation.md (fix EvalRecord type, evaluator count)
- [x] Add CHANGELOG v0.4.0 entry to agent-core
- [x] Add CHANGELOG.md v0.1.1 to agent-harness
- [x] Update docs/example-config.yaml (document None default)
- [x] Update docs/configuration.md (document None default)
- [x] Update wiki/entities/agent-core.md (capabilities, versions, test count)

## Phase 5: Research Docs ✅

- [x] Update docs/research/framework-comparison.md (current versions, capabilities)
- [x] Update docs/research/pydanticai-langgraph.md (current versions, capabilities)
- [x] Add staleness disclaimers to framework-comparison.md and pydanticai-langgraph.md

## Phase 6: OpenSpec Updates ✅

- [x] Mark _standalone/harness-compaction as historical
- [x] Mark _standalone/harness-runtime-authoring as historical
- [x] Mark agent-core-compose-integration-verifier as historical
- [x] Mark public-api as historical
- [x] Mark agent-compaction as partially historical
- [x] Mark builtin-hooks as historical
- [x] Update vendor-isolation (HookAdapter → create_budget_hooks)
- [x] Update harness-integration (standalone) — build_agent reference
- [x] Update integration-guide — version baseline
- [x] Update agent-docs-harness — capability list

## Phase 7: Dev Toolings ✅

- [x] Update ruff to >=0.16.3 in all 3 repos
- [x] Add pre-commit-hooks v6.0.0 to agent-harness
- [x] Add pre-commit-hooks v6.0.0 to agent-docs-sync
- [x] Update EXPECTED_SCHEDULES 18→21 in post_deploy_verify.py
- [x] Update EXPECTED_MANIFESTS 4→5 in post_deploy_verify.py
- [x] Update EXPECTED_SCHEDULES 18→21 in verify_scheduler.py
- [x] Update EXPECTED_MANIFESTS 4→5 in verify_scheduler.py

## Phase 8: Workspace Updates ✅

- [x] Update .worktree-execution-contracts-core.md versions
- [x] Update .worktree-execution-contracts-consumers.md versions

## Verification ✅

- [x] agent-core: 852 tests pass
- [x] agent-harness: 414 tests pass
- [x] agent-docs-sync: 309 tests pass
- [x] OpenSpec validate --all: 372 specs pass, 0 failed
- [x] Ruff lint: clean on all repos
- [x] Stale reference sweep: 0 findings in active code/docs
- [x] GitNexus: AgentRuntime and build_agent indexed correctly
- [x] Graphify: knowledge graph current
