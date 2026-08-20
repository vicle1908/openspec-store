## Why

After upgrading pydantic-ai-harness to 0.23.0 (see `upgrade-pydantic-ai-harness`), the workspace gains access to 50+ harness capabilities. Currently only 5 modules are used (step_persistence, memory, guardrails, subagents, dynamic_workflow). This change adopts **7 high-value capabilities** that directly address current limitations:

**Batch 1 — Quick wins (same commit, biggest bang):**
1. **Compaction** — Automatic context trimming using TieredCompaction strategy. Prevents context overflow, the most common agent failure mode.
2. **SystemReminders** — Cache-safe mid-run instruction re-injection using GoalReanchor. Prevents instruction drift in long conversations.

**Batch 2 — Security + Cost (independent, can parallel):**
3. **ToolGuardrail** — Structured validation of tool arguments and results with hidden tools and ready-made detectors. Simplifies custom guard implementations.
4. **SpendLimits** — Cross-window USD/token budgets with per-model and per-tenant tracking. Provides cost visibility required for production deployment.

**Batch 3 — Build on compaction:**
5. **Planning** — Model-owned task plans with subtask support. Replaces test-only dynamic_workflow with production planner.
6. **ConversationSearch** — BM25 search over stored history including compaction-dropped turns. Enables history retrieval.

**Batch 4 — Use-case specific:**
7. **Advisor** — Multi-model consultation where cheaper model executes and expensive model reviews decisions. Best for high-stakes decision agents.

This change is needed now because:
- Context overflow is the most common agent failure mode (Compaction)
- Instruction fade causes agents to drift from their contracts (SystemReminders)
- Cost visibility is required for production deployment (SpendLimits)
- Custom guard implementations could be simplified with ToolGuardrail
- Task planning is duplicated across agents (Planning)
- History is lost after compaction (ConversationSearch)
- High-stakes decisions need expert review (Advisor)

## What Changes

- **ADDED**: `Compaction` capability to agent-core agent construction
- **ADDED**: `SystemReminders` capability to agent-core agent construction
- **ADDED**: `ToolGuardrail` capability to agent-docs-sync guardrails
- **ADDED**: `SpendLimits` capability to agent-core agent construction
- **ADDED**: `Planning` capability to agent-core agent construction
- **ADDED**: `ConversationSearch` capability to agent-core memory layer
- **ADDED**: `Advisor` capability to agent-core agent construction
- **MODIFIED**: Agent construction in `agent-core/_ai/agent.py` to include new capabilities
- **MODIFIED**: Guardrail construction in `agent-docs-sync/guardrails.py` to include ToolGuardrail
- **MODIFIED**: Memory layer in `agent-core/sdk/memory.py` to include ConversationSearch
- Configuration files for compaction strategy, spend limits, planning, and advisor

## Non-goals

- No harness version changes (done in `upgrade-pydantic-ai-harness`)
- No changes to step_persistence or memory modules (already working)
- No adoption of Browser Use, StackOne, Coder/Researcher harnesses (not applicable)
- No adoption of ToolOutputLimits, WarnOnCacheBusts (lower priority, later)

## Capabilities

### Added Capabilities

- `compaction-management`: Automatic context trimming using TieredCompaction with DeduplicateFileReads → ClearToolResults → SummarizingCompaction
- `system-reminders`: Cache-safe mid-run instruction re-injection using GoalReanchor
- `tool-guardrail`: Structured validation of tool arguments and results with hidden tools and ready-made detectors
- `spend-limits`: Cross-window USD/token budgets with per-model and per-tenant cost tracking
- `planning`: Model-owned task plans with subtask support and persistence
- `conversation-search`: BM25 search over stored history including compaction-dropped turns
- `advisor`: Multi-model consultation for high-stakes decision agents

### Modified Capabilities

- `agent-core-runtime`: Extended with Compaction, SystemReminders, SpendLimits, Planning, and Advisor capabilities
- `agent-core-memory`: Extended with ConversationSearch for history retrieval
- `agent-docs-sync-guardrails`: Extended with ToolGuardrail for structured tool validation

## Impact

- **Runtime:** New capabilities are additive — existing behavior unchanged unless explicitly enabled
- **Configuration:** New config sections for compaction strategy, spend limits, planning, and advisor
- **Testing:** New unit tests for each capability integration; existing tests must continue passing
- **Observability:** SpendLimits adds cost tracking; Advisor adds consultation traces
- **Performance:** Compaction reduces context size; Planning improves task completion
- **Blast radius:** MEDIUM — changes agent construction, memory layer, and guardrail patterns
- **Rollback:** Git revert per repo; capabilities can be disabled by removing from agent construction
