## Context

agent-core's agent layer wraps Pydantic AI V2's `Agent` class behind `AgentRuntime` and `BaseAgent`. After installing `pydantic-ai-harness` v0.10.0 (which upgrades `pydantic-ai` to 2.16.0) and running the full test suite (398/398 pass), we confirmed that the harness provides production-grade `AbstractCapability` implementations for most remaining gaps.

**Harness 0.10.0 additions over 0.8.0:**
- `CacheStabilityMonitor` — prompt cache bust detection
- `PyaiDocs` — on-demand Pydantic AI documentation access
- `Macroscope` — CLI code review integration (future)
- `ModalSandbox` — Modal-based sandboxed execution (future)
- `LocalStack` — LocalStack emulation (future)

**Pydantic AI 2.16.0 additions over 2.9.0:**
- `SelectModel` / `ModelSelector` — dynamic model selection per run
- `RaiseContentFilterError` — content filter error handling

**Harness integration model:** Every harness capability extends `AbstractCapability` and plugs directly into `Agent(capabilities=[...])`. agent-core wires them through `AgentConfig` fields into `AgentRuntime.__init__()`.

## Goals / Non-Goals

**Goals:**
- Add `pydantic-ai-harness>=0.10.0,<1` as a first-class dependency
- Expose harness capabilities through `AgentConfig` fields (opt-in, backward-compatible)
- Wire full compaction stack: `SummarizingCompaction` + `SlidingWindow` + `ClampOversizedMessages` + `ClearToolResults` + `DeduplicateFileReads`
- Wire guardrails via `InputGuard`/`OutputGuard`
- Wire step persistence via `StepPersistence` + `SqliteStepStore`
- Wire multi-agent delegation via `SubAgents`
- Wire planning via `Planning`
- Wire repo context via `RepoContext`
- Wire output overflow via `OverflowingToolOutput`
- Wire cache monitoring via `CacheStabilityMonitor`
- Wire limit warnings via `LimitWarner`
- Wire docs access via `PyaiDocs`
- Wire YAML/JSON agent loading via `Agent.from_file()`

**Non-Goals:**
- `CodeMode`/`DynamicWorkflow` (require pydantic-monty)
- `Macroscope` (requires CLI installation)
- `ModalSandbox` (requires Modal account)
- `ExaSearch` (requires exa-py)
- `LocalStack` (requires Docker)
- Replacing agent-core's 4-tier memory (ours is richer)
- Replacing agent-core's builtins with harness `Shell`/`FileSystem` (evaluate separately)

## Decisions

### Decision 1: Harness 0.10.0 (not 0.8.0)

Use harness 0.10.0 which upgrades pydantic-ai to 2.16.0. This gives us:
- `CacheStabilityMonitor` for cache monitoring
- `PyaiDocs` for framework docs access
- Pydantic AI 2.16.0 improvements (SelectModel, etc.)

All 398 existing tests pass with the upgrade.

### Decision 2: Full compaction stack (not just SummarizingCompaction)

The compaction stack has multiple complementary strategies:
- `SummarizingCompaction` — LLM-based summarization (quality, uses tokens)
- `SlidingWindow` — message count/token sliding window (cheap, loses context)
- `ClampOversizedMessages` — clamp individual oversized messages
- `ClearToolResults` — clear old tool call results
- `DeduplicateFileReads` — deduplicate repeated file reads
- `LimitWarner` — proactive budget/limit warnings

These compose via `TieredCompaction` or can be used individually. The `AgentConfig.context_compaction` field supports strategy selection.

### Decision 3: AgentConfig as dict[str, Any] for flexibility

Each harness capability maps to an optional `dict[str, Any] | None` field on `AgentConfig`. This allows:
- Forward compatibility (new harness fields don't require AgentConfig schema changes)
- Per-delegate config (SubAgents need per-agent config)
- Validation at capability creation time (not at config parse time)

### Decision 4: StepPersistence complements LangGraph checkpointing

LangGraph `PostgresSaver` checkpoints at graph level (per node transition). `StepPersistence` + `SqliteStepStore` checkpoints at agent run level (per tool call). They operate at different granularities and are independently usable.

## Risks / Trade-offs

- **pydantic-ai version bump** (2.9.0 → 2.16.0) → All 398 tests pass; minor version but no breaking changes observed
- **Harness version pin** → `>=0.10.0,<1` — harness follows semver
- **AgentConfig field proliferation** → Many optional dict fields; mitigated by grouping
- **Compaction stack complexity** → Multiple strategies; document when to use which
- **Memory system overlap** → Keep agent-core 4-tier memory (richer than harness Memory)
