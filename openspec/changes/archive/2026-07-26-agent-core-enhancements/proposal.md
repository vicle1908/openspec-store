## Why

After the agent-core-legacy-cleanup, the codebase is lean but has several integration gaps where built-but-unwired capabilities exist. Three areas need attention:

1. **BudgetTracker is broken** — budgets are set but never enforced. The old HTTP enforcement path was removed in the cleanup, but no replacement was built. This is a bug, not a feature gap.

2. **Memory module is isolated** — fully implemented with enhanced ABC, vector search, and recall, but not wired into the agent lifecycle. agent-docs-sync already has primitive KV state that would benefit from proper memory.

3. **cli/app.py is a 729-line monolith** — 7 commands, 16 helpers, 2 sub-apps all in one file. Extractable into focused modules.

Additionally, agent-docs-sync (the sole hard consumer) has hand-rolled retry logic that should use agent-core's resilience utilities.

## What Changes

### Phase 1: Quick Wins (BudgetTracker + CLI extraction)
- Rewire BudgetTracker into pydantic-ai hooks system (2 code changes)
- Extract cli/app.py into 6 focused modules (~50 lines remaining)
- Wire orphaned eval.py into main CLI

### Phase 2: Memory Integration
- Create MemoryCapability (pydantic-ai AbstractCapability subclass)
- Wire into agent lifecycle via harness config
- Add memory tools (store, retrieve, recall, list_keys)
- Inject context from ContextMemory into system prompt

### Phase 3: agent-docs-sync Resilience
- Replace hand-rolled on_tool_error retry with agent-core's retry_with_jitter
- Add ToolResultCache for classification results
- Pipeline checkpoint/resume via PostgresSaver

### Phase 4: Performance
- Parallel audit/validate handlers
- LLM response caching for generation
- Unified state abstraction (YAML + Memory)

## Capabilities

### New Capabilities
- `agent-core-budget-enforcement`: BudgetTracker hook rewiring for USD cost ceiling enforcement
- `agent-core-memory-lifecycle`: MemoryCapability integration into agent run loop
- `agent-core-cli-extraction`: Modular CLI architecture
- `agent-core-tool-resilience`: Tool-level retry/circuit-breaker utilities

### Modified Capabilities
- `agent-core-memory-enhancement`: Remove EXPERIMENTAL annotation after lifecycle wiring

## Impact

### Cross-Repo Compatibility (validated)
- **agent-docs-sync**: Will benefit from retry_with_jitter replacing hand-rolled hooks. Memory integration optional but valuable for caching.
- **code-daily-scan**: No impact (phantom dependency)
- **tdt-core**: No impact

### Code Changes
- **BudgetTracker**: 2 files changed (~5 lines added)
- **Memory lifecycle**: 3-4 files changed (~150 lines added)
- **CLI extraction**: 6 new files, 1 file rewritten (~700 lines reorganized, not added)
- **Tool resilience**: Available for agent-docs-sync adoption

### Non-Goals
- Changing BaseAgent's public API
- Affecting agent-docs-sync's existing behavior (enhancements are opt-in)
- Modifying orchestration module
- Adding new external dependencies
