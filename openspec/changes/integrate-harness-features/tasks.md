## 1. Verify Harness Upgrade Complete

- [ ] 1.1 Confirm `upgrade-pydantic-ai-harness` change is archived and all 3 repos have harness >=0.23.0
- [ ] 1.2 Verify `uv pip show pydantic-ai-harness` shows 0.23.0+ in all 3 repos

## 2. Integrate Compaction Capability (Tier 1)

- [ ] 2.1 In `agent-core/src/agent_core/_ai/agent.py`: import `Compaction` and `AnchoredCompaction` from `pydantic_ai_harness.compaction`
- [ ] 2.2 Add `Compaction` to the capabilities list in agent construction, with `AnchoredCompaction(keep_user_messages=True, pin_last_n=5, receipt_prefix="[compacted]")`
- [ ] 2.3 Add configuration for compaction threshold (default 0.8) in agent config
- [ ] 2.4 Write unit test: verify compaction does not trigger on short conversations (<10 turns)
- [ ] 2.5 Write unit test: verify compaction triggers on long conversations (>50 turns) and preserves key facts
- [ ] 2.6 Write unit test: verify compacted sections are marked with receipt prefix

## 3. Integrate SpendLimits Capability (Tier 1)

- [ ] 3.1 In `agent-core/src/agent_core/_ai/agent.py`: import `SpendLimits` from `pydantic_ai_harness.control`
- [ ] 3.2 Add `SpendLimits` to the capabilities list with configurable per-run and per-day limits
- [ ] 3.3 Add configuration for spend limits in agent config (default: $1/run, $10/day)
- [ ] 3.4 Verify cost tracking appears in existing OTel traces (langfuse integration)
- [ ] 3.5 Write unit test: verify budget exceeded raises `SpendLimitExceeded`
- [ ] 3.6 Write unit test: verify per-model breakdown is tracked

## 4. Integrate SystemReminders Capability (Tier 1)

- [ ] 4.1 In `agent-core/src/agent_core/_ai/agent.py`: import `SystemReminders` from `pydantic_ai_harness.context`
- [ ] 4.2 Add `SystemReminders` to the capabilities list with configurable reminder text and interval
- [ ] 4.3 Add configuration for reminder schedule in agent config (default: every 5 tool calls)
- [ ] 4.4 Write unit test: verify instructions re-inject at specified intervals
- [ ] 4.5 Write unit test: verify no duplicate reminders in context
- [ ] 4.6 Write unit test: verify agent behavior consistent across long conversations

## 5. Integrate Tool Output Limits Capability (Tier 1)

- [ ] 5.1 In `agent-core/src/agent_core/_ai/agent.py`: import `ToolOutputLimits` from `pydantic_ai_harness.context`
- [ ] 5.2 Add `ToolOutputLimits` to the capabilities list with configurable max_chars and spill settings
- [ ] 5.3 Add configuration for tool output limits in agent config (default: 10K chars, spill to file)
- [ ] 5.4 Write unit test: verify large tool results truncated at threshold
- [ ] 5.5 Write unit test: verify full output saved to spill directory
- [ ] 5.6 Write unit test: verify summarized content provided to agent

## 6. Integrate ToolGuard Capability (Tier 2)

- [ ] 6.1 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: import `ToolGuard` from `pydantic_ai_harness.guardrails`
- [ ] 6.2 Add `ToolGuard` to guardrail construction for write_file tool: validate path starts with "docs/"
- [ ] 6.3 Add `ToolGuard` for shell commands: validate against dangerous command blocklist
- [ ] 6.4 Write unit test: verify invalid tool args blocked with clear message
- [ ] 6.5 Write unit test: verify valid tool args pass through unchanged
- [ ] 6.6 Write unit test: verify audit trail of blocked attempts

## 7. Integrate Warn On Cache Busts Capability (Tier 2)

- [ ] 7.1 In `agent-core/src/agent_core/_ai/agent.py`: import `WarnOnCacheBusts` from `pydantic_ai_harness.context`
- [ ] 7.2 Add `WarnOnCacheBusts` to the capabilities list with logging enabled
- [ ] 7.3 Add configuration for cache bust alerts in agent config (default: log warnings)
- [ ] 7.4 Write unit test: verify cache invalidation events logged
- [ ] 7.5 Write unit test: verify performance degradation detected

## 8. Integrate Planning Capability (Tier 2)

- [ ] 8.1 In `agent-core/src/agent_core/_ai/agent.py`: import `Planning` from `pydantic_ai_harness.reasoning`
- [ ] 8.2 Add `Planning` to the capabilities list with configurable max_tasks and reminder_interval
- [ ] 8.3 Add configuration for planning in agent config (default: max 10 tasks, remind every 3 calls)
- [ ] 8.4 Write unit test: verify model creates task plan at start
- [ ] 8.5 Write unit test: verify plan updated as tasks complete
- [ ] 8.6 Write unit test: verify plan visible in agent context

## 9. Integrate Conversation Search Capability (Tier 2)

- [ ] 9.1 In `agent-core/src/agent_core/sdk/memory.py`: import `ConversationSearch` from `pydantic_ai_harness.memory`
- [ ] 9.2 Add `ConversationSearch` to memory layer with existing memory store
- [ ] 9.3 Add configuration for search in agent config (default: max 10 results, min score 0.3)
- [ ] 9.4 Write unit test: verify search returns relevant history
- [ ] 9.5 Write unit test: verify compacted turns searchable
- [ ] 9.6 Write unit test: verify BM25 ranking works correctly

## 10. Verify All Tests Pass

- [ ] 10.1 Run `uv run pytest` in agent-core — all tests pass including new capability tests
- [ ] 10.2 Run `uv run pytest` in agent-docs-sync — all tests pass including new guardrail tests
- [ ] 10.3 Run `uv run ruff check . --select I001` in all 3 repos — no new findings
- [ ] 10.4 Run `uv run mypy src/ --strict` in all 3 repos — no type errors

## 11. Commit and Archive

- [ ] 11.1 Commit agent-core changes: `git add -A && git commit`
- [ ] 11.2 Commit agent-docs-sync changes: `git add -A && git commit`
- [ ] 11.3 Archive the OpenSpec change: `openspec archive integrate-harness-features --yes`
- [ ] 11.4 Commit openspec-store archive: `git add -A && git commit`
- [ ] 11.5 Run `openspec validate --all --strict` to confirm no regressions
