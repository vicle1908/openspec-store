## Why

After upgrading pydantic-ai-harness to 0.23.0 (see `upgrade-pydantic-ai-harness`), the workspace gains access to 13 new harness modules. Four of these provide high-value capabilities that directly address current limitations:

1. **Compaction** — The workspace has no automatic context management. Agents hit context limits on long conversations, requiring manual intervention. Harness 0.23.0 provides anchored incremental compaction with receipts, pin contracts, and keep-user-messages strategies.

2. **ToolGuard** — The workspace has custom tool validation in agent-docs-sync guardrails. Harness 0.23.0 provides structured tool argument and result validation that could simplify or enhance these guards.

3. **SystemReminders** — Agents lose instruction context over long conversations (instruction fade). Harness 0.23.0 provides cache-safe mid-run re-injection of guidance.

4. **SpendLimits** — No cost tracking exists. Harness 0.23.0 provides cross-window USD/token budgets with per-model and per-tenant tracking.

This change is needed now because:
- Context overflow is the most common agent failure mode
- Cost visibility is required for production deployment
- Instruction fade causes agents to drift from their contracts
- Custom guard implementations could be simplified with ToolGuard

## What Changes

- **ADDED**: `Compaction` capability to agent-core agent construction
- **ADDED**: `ToolGuard` capability to agent-docs-sync guardrails
- **ADDED**: `SystemReminders` capability to agent-core agent construction
- **ADDED**: `SpendLimits` capability to agent-core agent construction
- **MODIFIED**: Agent construction in `agent-core/_ai/agent.py` to include new capabilities
- **MODIFIED**: Guardrail construction in `agent-docs-sync/guardrails.py` to include ToolGuard
- Configuration files for compaction strategy, spend limits, and reminder schedules

## Non-goals

- No harness version changes (done in `upgrade-pydantic-ai-harness`)
- No changes to step_persistence or memory modules (already working)
- No adoption of Browser Use, StackOne, Coder/Researcher harnesses (not applicable)
- No adoption of Conversation Search, Advisor, PromptInjectionDefender (medium priority, later)

## Capabilities

### Added Capabilities

- `compaction-management`: Automatic context trimming using anchored incremental strategy with receipts and pin contracts
- `tool-guard-validation`: Structured validation of tool arguments and results using harness ToolGuard
- `system-reminders`: Cache-safe mid-run instruction re-injection to counter context drift
- `spend-limits`: Cross-window USD/token budgets with per-model and per-tenant cost tracking

### Modified Capabilities

- `agent-core-runtime`: Extended with Compaction, SystemReminders, and SpendLimits capabilities
- `agent-docs-sync-guardrails`: Extended with ToolGuard for structured tool validation

## Impact

- **Runtime:** New capabilities are additive — existing behavior unchanged unless explicitly enabled
- **Configuration:** New config sections for compaction strategy, spend limits, and reminder schedules
- **Testing:** New unit tests for each capability integration; existing tests must continue passing
- **Observability:** SpendLimits adds cost tracking to all agent runs
- **Blast radius:** MEDIUM — changes agent construction and guardrail patterns
- **Rollback:** Git revert per repo; capabilities can be disabled by removing from agent construction
