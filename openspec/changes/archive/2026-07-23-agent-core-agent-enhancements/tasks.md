## 1. Dependency & Config

- [x] 1.1 Add `pydantic-ai-harness>=0.10.0,<1` to `pyproject.toml` dependencies
- [x] 1.2 Run `uv sync` and verify all 398 existing tests still pass
- [x] 1.3 Add harness config fields to `AgentConfig`: `source_file`, `context_compaction`, `guardrails`, `step_persistence`, `subagents`, `planning`, `repo_context`, `output_overflow`, `cache_monitoring`, `limit_warnings`, `docs_access` (all `dict[str, Any] | None = None`)

## 2. YAML/JSON Agent Loading

- [x] 2.1 Create `agent_core/_ai/config_loader.py` with `load_agent_config(path, registry)` using `AgentSpec.from_file()`
- [x] 2.2 Implement tool name resolution: iterate spec tools, look up in `ToolRegistry`, raise `ValueError` for unknowns
- [x] 2.3 Implement capability resolution: map spec capabilities to Pydantic AI instances (`Thinking`, `MCP`, etc.)
- [x] 2.4 Create example YAML agent at `examples/agents/review-agent.yaml`

## 3. AgentRuntime Harness Wiring — Core Capabilities

- [x] 3.1 Add `_build_harness_capabilities(config)` private method to `AgentRuntime`
- [x] 3.2 Wire `SummarizingCompaction` / `SlidingWindow` / `TieredCompaction` from `context_compaction` config (strategy selection)
- [x] 3.3 Wire `ClampOversizedMessages` from `context_compaction.clamp_oversized` flag
- [x] 3.4 Wire `ClearToolResults` from `context_compaction.clear_tool_results` flag
- [x] 3.5 Wire `DeduplicateFileReads` from `context_compaction.deduplicate_reads` flag
- [x] 3.6 Wire `InputGuard`/`OutputGuard` from `guardrails` config
- [x] 3.7 Wire `StepPersistence` + `SqliteStepStore` from `step_persistence` config
- [x] 3.8 Wire `SubAgents` + `SubAgent` from `subagents` config
- [x] 3.9 Wire `Planning` from `planning` config
- [x] 3.10 Wire `RepoContext` from `repo_context` config

## 4. AgentRuntime Harness Wiring — Monitoring & Output

- [x] 4.1 Wire `OverflowingToolOutput` from `output_overflow` config
- [x] 4.2 Wire `CacheStabilityMonitor` from `cache_monitoring` config
- [x] 4.3 Wire `LimitWarner` from `limit_warnings` config
- [x] 4.4 Wire `PyaiDocs` from `docs_access` config
- [x] 4.5 Update `AgentRuntime.__init__()` to call `_build_harness_capabilities()` and extend capabilities list
- [x] 4.6 Update `BaseAgent.__init__()` to accept `source_file` parameter

## 5. AgentRuntime Resume (Step Persistence)

- [x] 5.1 Add `run_resume(snapshot: ContinuableSnapshot)` method to `AgentRuntime`
- [x] 5.2 Pass `message_history=snapshot.messages` to the underlying `pydantic_ai.Agent.run()`

## 6. Tests

- [x] 6.1 Create `tests/test_config_loader.py` — YAML loading, JSON loading, tool resolution, unknown tool error, invalid spec error
- [x] 6.2 Test `AgentConfig` harness fields default to `None`
- [x] 6.3 Test `AgentRuntime` creates `SummarizingCompaction` when `context_compaction` is set
- [x] 6.4 Test `AgentRuntime` creates `InputGuard`/`OutputGuard` when `guardrails` is set
- [x] 6.5 Test `AgentRuntime` creates `StepPersistence` when `step_persistence` is set
- [x] 6.6 Test `AgentRuntime` creates `SubAgents` when `subagents` is set
- [x] 6.7 Test `AgentRuntime` creates `Planning` when `planning` is set
- [x] 6.8 Test `AgentRuntime` creates `RepoContext` when `repo_context` is set
- [x] 6.9 Test `AgentRuntime` creates `OverflowingToolOutput` when `output_overflow` is set
- [x] 6.10 Test `AgentRuntime` creates `CacheStabilityMonitor` when `cache_monitoring` is set
- [x] 6.11 Test `AgentRuntime` creates `LimitWarner` when `limit_warnings` is set
- [x] 6.12 Test `AgentRuntime` creates `PyaiDocs` when `docs_access` is set
- [x] 6.13 Test backward compat: `AgentConfig(model=...)` without harness fields works unchanged
- [x] 6.14 Test `load_agent_config()` with example YAML file
- [x] 6.15 Test `AgentRuntime.run_resume()` with mock `ContinuableSnapshot`

## 7. Validation

- [x] 7.1 Run `ruff check . --fix && ruff format .` from agent-core root
- [x] 7.2 Run `mypy src/agent_core/ --strict` — zero errors
- [x] 7.3 Run `pytest tests/ -x` — all tests pass (no regressions)
