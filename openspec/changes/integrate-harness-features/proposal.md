## Why

After upgrading pydantic-ai-harness to 0.23.0 (see `upgrade-pydantic-ai-harness`), the workspace gains access to 50+ harness capabilities. Currently only 5 modules are used (step_persistence, memory, guardrails, subagents, dynamic_workflow). This change adopts **8 high-value capabilities** that directly address current limitations:

**Tier 1 — Adopt with upgrade (high value, low effort):**
1. **Compaction** — Automatic context trimming using anchored incremental strategy. Prevents context overflow, the most common agent failure mode.
2. **SpendLimits** — Cross-window USD/token budgets with per-model and per-tenant tracking. Provides cost visibility required for production deployment.
3. **SystemReminders** — Cache-safe mid-run instruction re-injection. Prevents instruction drift in long conversations.
4. **Tool Output Limits** — Truncates oversized tool returns at the source. Prevents context overflow from large tool results.

**Tier 2 — Adopt shortly after (medium value, medium effort):**
5. **ToolGuard** — Structured validation of tool arguments and results. Simplifies custom guard implementations.
6. **Warn On Cache Busts** — Detects prompt-cache prefix collapses. Improves performance and cost.
7. **Planning** — Model-owned task plans with cache-safe live reminder. Replaces custom task decomposition.
8. **Conversation Search** — BM25 search over stored history including compaction-dropped turns. Enables history retrieval.

This change is needed now because:
- Context overflow is the most common agent failure mode (Compaction, Tool Output Limits)
- Cost visibility is required for production deployment (SpendLimits)
- Instruction fade causes agents to drift from their contracts (SystemReminders)
- Custom guard implementations could be simplified with ToolGuard
- Cache invalidation silently degrades performance (Warn On Cache Busts)
- Task planning is duplicated across agents (Planning)
- History is lost after compaction (Conversation Search)

## What Changes

- **ADDED**: `Compaction` capability to agent-core agent construction
- **ADDED**: `SpendLimits` capability to agent-core agent construction
- **ADDED**: `SystemReminders` capability to agent-core agent construction
- **ADDED**: `ToolOutputLimits` capability to agent-core agent construction
- **ADDED**: `ToolGuard` capability to agent-docs-sync guardrails
- **ADDED**: `WarnOnCacheBusts` capability to agent-core agent construction
- **ADDED**: `Planning` capability to agent-core agent construction
- **ADDED**: `ConversationSearch` capability to agent-core memory layer
- **MODIFIED**: Agent construction in `agent-core/_ai/agent.py` to include new capabilities
- **MODIFIED**: Guardrail construction in `agent-docs-sync/guardrails.py` to include ToolGuard
- **MODIFIED**: Memory layer in `agent-core/sdk/memory.py` to include ConversationSearch
- Configuration files for compaction strategy, spend limits, reminder schedules, and tool output limits

## Non-goals

- No harness version changes (done in `upgrade-pydantic-ai-harness`)
- No changes to step_persistence or memory modules (already working)
- No adoption of Browser Use, StackOne, Coder/Researcher harnesses (not applicable)
- No adoption of Advisor, PromptInjectionDefender, Tool Approval (Tier 3, later)
- No adoption of Capability Creation, Repo Context, Skills (Tier 3, later)

## Capabilities

### Added Capabilities

- `compaction-management`: Automatic context trimming using anchored incremental strategy with receipts, pin contracts, and keep-user-messages
- `spend-limits`: Cross-window USD/token budgets with per-model and per-tenant cost tracking
- `system-reminders`: Cache-safe mid-run instruction re-injection to counter context drift
- `tool-output-limits`: Truncate, spill to file, or summarize oversized tool returns at the source
- `tool-guard-validation`: Structured validation of tool arguments and results using harness ToolGuard
- `cache-bust-detection`: Detect prompt-cache prefix collapses between requests
- `planning`: Model-owned task plans with cache-safe live reminder
- `conversation-search`: BM25 search over stored history including compaction-dropped turns

### Modified Capabilities

- `agent-core-runtime`: Extended with Compaction, SpendLimits, SystemReminders, ToolOutputLimits, WarnOnCacheBusts, and Planning capabilities
- `agent-core-memory`: Extended with ConversationSearch for history retrieval
- `agent-docs-sync-guardrails`: Extended with ToolGuard for structured tool validation

## Impact

- **Runtime:** New capabilities are additive — existing behavior unchanged unless explicitly enabled
- **Configuration:** New config sections for compaction strategy, spend limits, reminder schedules, tool output limits, and planning
- **Testing:** New unit tests for each capability integration; existing tests must continue passing
- **Observability:** SpendLimits adds cost tracking; WarnOnCacheBusts adds cache metrics
- **Performance:** Compaction and ToolOutputLimits reduce context size; Planning improves task completion
- **Blast radius:** MEDIUM — changes agent construction, memory layer, and guardrail patterns
- **Rollback:** Git revert per repo; capabilities can be disabled by removing from agent construction
