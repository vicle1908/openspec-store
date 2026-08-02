## Why

agent-core wraps Pydantic AI V2 for agent construction and LangGraph for orchestration, but only scratches the surface of what the framework ecosystem provides. After installing `pydantic-ai-harness` v0.10.0 (which upgrades `pydantic-ai` from 2.9.0 to 2.16.0) and verifying all 398 existing tests pass, we found that the harness ships **production-grade capabilities** that directly address agent-core's remaining gaps — and several more.

**Key version bump:** Harness 0.10.0 pulls `pydantic-ai==2.16.0` and `pydantic-graph==2.16.0`. All existing agent-core code remains compatible (verified via test suite).

### Harness Capabilities That Close Gaps

| Harness Capability | Agent-Core Gap | Current Agent-Core Equivalent | Action |
|---|---|---|---|
| `SummarizingCompaction` | Context Compaction | None | **Adopt** — structured LLM summarization |
| `SlidingWindow` | Context Compaction | `ContextMemory(max_messages=50)` | **Supplement** — token-aware sliding window |
| `ClampOversizedMessages` | Large Message Handling | None | **Adopt** — clamp oversized tool outputs |
| `ClearToolResults` | Memory Pressure | None | **Adopt** — clear old tool results |
| `DeduplicateFileReads` | Redundant Reads | None | **Adopt** — deduplicate repeated file reads |
| `LimitWarner` | Budget Warnings | `BudgetTracker` (partial) | **Adopt** — proactive limit warnings |
| `SubAgents` + `SubAgent` | Multi-Agent Delegation | None | **Adopt** — agent-level delegation |
| `StepPersistence` + `SqliteStepStore` | Durable Execution | LangGraph `PostgresSaver` only | **Add** — per-step persistence |
| `InputGuard` / `OutputGuard` | Guardrails | `BudgetTracker` (partial) | **Add** — structured filtering |
| `Planning` + `PlanningToolset` | Agent Planning | None | **Add** — task decomposition |
| `RepoContext` + `RepoContextToolset` | Context Loading | Manual `_build_instructions()` | **Adopt** — auto AGENTS.md loading |
| `OverflowingToolOutput` | Large Output Management | None | **Add** — auto-spill to disk |
| `CacheStabilityMonitor` | Cache Monitoring | None | **Add** — prompt cache bust detection |
| `PyaiDocs` | Framework Docs Access | None | **Add** — on-demand Pydantic AI docs |
| `Macroscope` | Code Review | None | **Future** — CLI code review integration |
| `ModalSandbox` | Sandboxed Execution | None | **Future** — Modal-based sandboxing |
| `Memory` + `FileStore` | Structured Memory | 4-tier memory (richer) | **Evaluate** — keep ours |
| `Shell` / `FileSystem` | Built-in Tools | Existing builtins | **Evaluate** — evaluate sandboxing |

### Pydantic AI 2.16.0 New Capabilities

| Capability | Description | Relevance |
|---|---|---|
| `SelectModel` / `ModelSelector` | Dynamic model selection per run | **Medium** — fallback model chains |
| `RaiseContentFilterError` | Content filter error handling | **Low** — provider-specific |

## What Changes

- **Add `pydantic-ai-harness>=0.10.0,<1`** as a dependency (upgrades pydantic-ai to 2.16.0)
- **Context Compaction**: `SummarizingCompaction` + `SlidingWindow` + `ClampOversizedMessages` + `ClearToolResults` + `DeduplicateFileReads` — full compaction stack
- **YAML/JSON Agent Definitions**: Wire `Agent.from_file()` into `AgentRuntime`
- **Step Persistence**: `StepPersistence` + `SqliteStepStore` + `ContinuableSnapshot` for resume
- **Guardrails**: `InputGuard`/`OutputGuard` for input/output filtering
- **Multi-Agent Delegation**: `SubAgents` + `SubAgent` for agent-to-agent delegation
- **Planning**: `Planning` capability for task decomposition
- **Repo Context**: `RepoContext` for automatic AGENTS.md/CLAUDE.md loading
- **Large Output Handling**: `OverflowingToolOutput` for auto-spilling large outputs
- **Cache Monitoring**: `CacheStabilityMonitor` for prompt cache bust detection
- **Limit Warnings**: `LimitWarner` for proactive budget/limit warnings
- **Framework Docs**: `PyaiDocs` for on-demand Pydantic AI documentation access

## Capabilities

### New Capabilities
- `agent-yaml-config`: YAML/JSON agent definition loading via `Agent.from_file()`
- `harness-integration`: Integration layer for `pydantic-ai-harness` capabilities
- `agent-compaction`: Context compaction stack (SummarizingCompaction + SlidingWindow + ClampOversizedMessages + ClearToolResults + DeduplicateFileReads)
- `agent-guardrails`: Input/output guardrails via `InputGuard`/`OutputGuard`
- `agent-step-persistence`: Per-step durable execution via `StepPersistence` + `SqliteStepStore`
- `agent-delegation`: Multi-agent delegation via `SubAgents` + `SubAgent`
- `agent-planning`: Task decomposition via `Planning` capability
- `agent-output-overflow`: Large output handling via `OverflowingToolOutput`
- `agent-cache-monitoring`: Prompt cache bust detection via `CacheStabilityMonitor`
- `agent-limit-warnings`: Proactive budget/limit warnings via `LimitWarner`
- `agent-docs-access`: On-demand Pydantic AI docs via `PyaiDocs`

### Modified Capabilities
- `agent-runtime` (existing): `AgentConfig` gains harness fields; `AgentRuntime.__init__` wires capabilities

## Impact

- **Code**: `pyproject.toml`, `agent_core/_ai/config.py`, `agent_core/_ai/config_loader.py` (new), `agent_core/_ai/agent.py`, `agent_core/_ai/capability.py`, `agent_core/agent_base/agent.py`
- **Tests**: New tests in `tests/test_config_loader.py`, `tests/test_harness_integration.py`
- **Dependencies**: `pydantic-ai-harness>=0.10.0,<1` (upgrades pydantic-ai to 2.16.0)
- **Backward compat**: Fully backward-compatible — all harness capabilities are opt-in
- **Non-goals**: `CodeMode`/`DynamicWorkflow` (require pydantic-monty), `Macroscope` (requires CLI), `ModalSandbox` (requires Modal account), `ExaSearch` (requires exa-py), `LocalStack` (requires Docker)
