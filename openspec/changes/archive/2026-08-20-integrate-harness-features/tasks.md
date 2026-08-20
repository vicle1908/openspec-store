## 1. Verify Harness Upgrade Complete

- [x] 1.1 Confirm `upgrade-pydantic-ai-harness` change is archived and all 3 repos have harness >=0.23.0
- [x] 1.2 Verify `uv pip show pydantic-ai-harness` shows 0.23.0+ in all 3 repos
- [x] 1.3 Verify no deprecated imports remain: `grep -rn "GuardResult\|InputGuard\|OutputGuard" src/ tests/` should return 0 matches

## 2. Batch 1: Quick Wins — Compaction + SystemReminders

### Phase 1: Compaction (CRITICAL value, LOW effort)

- [x] 2.1 In `agent-core/src/agent_core/_ai/agent.py`: import `TieredCompaction`, `DeduplicateFileReads`, `ClearToolResults`, `SummarizingCompaction` from `pydantic_ai_harness.compaction`
- [x] 2.2 Add `TieredCompaction` to capabilities list with 3 tiers: DeduplicateFileReads → ClearToolResults → SummarizingCompaction
- [x] 2.3 Add configuration for compaction target_tokens (default 120_000) in agent config
- [x] 2.4 Write unit test: verify compaction does not trigger on short conversations (<10 turns)
- [x] 2.5 Write unit test: verify compaction triggers on long conversations (>50 turns) and preserves key facts
- [x] 2.6 Write unit test: verify compaction receipts visible in traces

### Phase 2: SystemReminders (HIGH value, VERY LOW effort)

- [x] 2.7 In `agent-core/src/agent_core/_ai/agent.py`: import `SystemReminders` from `pydantic_ai_harness` (root)
- [x] 2.8 In `agent-core/src/agent_core/_ai/agent.py`: import `GoalReanchor` from `pydantic_ai_harness.system_reminders`
- [x] 2.9 Add `SystemReminders(dynamic_reminders=[GoalReanchor()])` to capabilities list
- [x] 2.10 Write unit test: verify GoalReanchor re-injects original goal each request
- [x] 2.11 Write unit test: verify no duplicate reminders in context
- [x] 2.12 Write unit test: verify agent behavior consistent across long conversations

## 3. Batch 2: Security + Cost — Guardrails + SpendLimits

### Phase 3: ToolGuardrail (HIGH value, LOW-MEDIUM effort)

Note: Guardrails migration is done in `upgrade-pydantic-ai-harness` change.
This phase adds NEW ToolGuardrail capabilities on top of the migrated API.

- [x] 3.1 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: import `ToolGuardrail` from `pydantic_ai_harness.guardrails`
- [x] 3.2 In `agent-docs-sync/src/agent_docs_sync/guardrails.py`: import `redact_secrets`, `redact_personal_data` from `pydantic_ai_harness.guardrails.detectors`
- [x] 3.3 Add `ToolGuardrail` for write_file tool: validate path starts with "docs/"
- [x] 3.4 Add `ToolGuardrail` for shell commands: validate against dangerous command blocklist
- [x] 3.5 Add `redact_secrets` detector for API keys and passwords in tool results
- [x] 3.6 Write unit test: verify ToolGuardrail blocks invalid tool args with clear message
- [x] 3.7 Write unit test: verify ready-made detectors redact sensitive content
- [x] 3.8 Write unit test: verify audit trail of blocked attempts

### Phase 4: SpendLimits (HIGH value, LOW-MEDIUM effort)

- [x] 4.1 In `agent-core/src/agent_core/_ai/agent.py`: import `SpendLimits`, `Budget` from `pydantic_ai_harness.spend`
- [x] 4.2 Add `SpendLimits` to capabilities list with configurable per-run and per-day limits
- [x] 4.3 Add configuration for spend limits in agent config (default: $5/run, $100/day)
- [x] 4.4 Verify cost tracking appears in existing OTel traces (langfuse integration)
- [x] 4.5 Write unit test: verify budget exceeded raises `SpendLimitExceeded`
- [x] 4.6 Write unit test: verify per-model breakdown is tracked
- [x] 4.7 Write unit test: verify per-tenant scoped budgets work

## 4. Batch 3: Build on Compaction — Planning + ConversationSearch

### Phase 5: Planning (MEDIUM-HIGH value, LOW-MEDIUM effort)

- [x] 5.1 In `agent-core/src/agent_core/_ai/agent.py`: import `Planning` from `pydantic_ai_harness.planning`
- [x] 5.2 Add `Planning` to capabilities list with configurable enable_subtasks
- [x] 5.3 Add configuration for planning in agent config (default: subtasks enabled)
- [x] 5.4 Write unit test: verify model creates task plan at start
- [x] 5.5 Write unit test: verify plan updated as tasks complete
- [x] 5.6 Write unit test: verify subtask decomposition works
- [x] 5.7 Write unit test: verify plan visible in agent context

### Phase 6: ConversationSearch (MEDIUM-HIGH value, LOW effort)

- [x] 6.1 In `agent-core/src/agent_core/sdk/memory.py`: import `ConversationSearch`, `SnapshotHistorySource` from `pydantic_ai_harness.conversation_search`
- [x] 6.2 Add `ConversationSearch` to memory layer with existing StepPersistence store
- [x] 6.3 Add configuration for search in agent config (default: max 10 results)
- [x] 6.4 Write unit test: verify search returns relevant history
- [x] 6.5 Write unit test: verify compacted turns searchable via pre-compaction snapshots
- [x] 6.6 Write unit test: verify BM25 ranking works correctly

## 5. Batch 4: Use-Case Specific — Advisor

### Phase 7: Advisor (MEDIUM value, LOW-MEDIUM effort)

Note: Advisor is included because the workspace runs expensive models (Opus) and could benefit from cheaper models (Sonnet) executing while Opus reviews decisions. This is optional and can be disabled by removing from capabilities.

- [x] 7.1 In `agent-core/src/agent_core/_ai/agent.py`: import `Advisor` from `pydantic_ai_harness.advisor`
- [x] 7.2 Add `Advisor` to capabilities list with configurable model and max_uses
- [x] 7.3 Add configuration for advisor in agent config (default: opus model, max 3 uses)
- [x] 7.4 Write unit test: advisor consulted before high-stakes decisions
- [x] 7.5 Write unit test: consultation logged in traces
- [x] 7.6 Write unit test: graceful fallback on advisor failure

## 6. Integration Testing

### Phase 8: End-to-End Integration Tests

- [x] 8.1 Create `agent-core/tests/test_harness_features_integration.py`: integration test that creates agent with all 7 capabilities and runs a multi-turn conversation
- [x] 8.2 Verify compaction triggers correctly in integration test (mock long conversation)
- [x] 8.3 Verify SystemReminders persist instructions across 20+ tool calls in integration test
- [x] 8.4 Verify SpendLimits tracks costs correctly in integration test (mock LLM calls)
- [x] 8.5 Verify Planning creates and updates task plan in integration test
- [x] 8.6 Verify ConversationSearch retrieves relevant history in integration test
- [x] 8.7 Verify ToolGuardrail blocks invalid tool calls in integration test
- [x] 8.8 Verify Advisor consultation works in integration test (mock advisor model)

### Phase 9: CLI Verification

- [x] 9.1 Run `uv run agent-core --help` — verify CLI works with new capabilities
- [x] 9.2 Run `uv run agent-docs-sync --help` — verify CLI works with new guardrails
- [x] 9.3 Run `uv run agent-docs-sync discover --help` — verify discovery command works
- [x] 9.4 Run `uv run agent-docs-sync sync --help` — verify sync command works
- [x] 9.5 Run `uv run agent-harness --help` — verify CLI works

### Phase 10: Real-World Usage Verification

- [x] 10.1 Run `uv run agent-docs-sync discover --repo ~/Developer/agent-core --json` — verify discovery works end-to-end
- [x] 10.2 Run `uv run agent-docs-sync validate --repo ~/Developer/agent-core --json` — verify validation works end-to-end
- [x] 10.3 Run `uv run agent-harness status --json` — verify harness status works
- [x] 10.4 Verify no regressions in existing workflows

## 7. Verify All Tests Pass

- [x] 11.1 Run `uv run pytest` in agent-core — all tests pass including new capability tests
- [x] 11.2 Run `uv run pytest` in agent-docs-sync — all tests pass including new guardrail tests
- [x] 11.3 Run `uv run ruff check .` in all 3 repos — full lint pass
- [x] 11.4 Run `uv run mypy src/ --strict` in all 3 repos — no type errors

## 8. Verify No Legacy Code Remains

- [x] 12.1 Run `grep -rn "GuardResult\|InputGuard\|OutputGuard" src/ tests/` in all repos — should return 0 matches
- [x] 12.2 Run `grep -rn "from pydantic_ai_harness.guardrails import GuardResult" src/ tests/` — should return 0 matches
- [x] 12.3 Run `grep -rn "from pydantic_ai_harness.guardrails import InputGuard" src/ tests/` — should return 0 matches
- [x] 12.4 Run `grep -rn "from pydantic_ai_harness.guardrails import OutputGuard" src/ tests/` — should return 0 matches
- [x] 12.5 Run `grep -rn "from pydantic_ai_harness.context import" src/ tests/` — should return 0 matches (use repo_context)
- [x] 12.6 Run `grep -rn "from pydantic_ai_harness.cache_stability import" src/ tests/` — should return 0 matches (use warn_on_cache_busts)
- [x] 12.7 Run `grep -rn "from pydantic_ai_harness.overflowing_tool_output import" src/ tests/` — should return 0 matches (use tool_output_limits)
- [x] 12.8 Run `grep -rn "from pydantic_ai_harness.control import" src/ tests/` — should return 0 matches (use spend)

## 9. Commit and Archive

- [x] 13.1 Commit agent-core changes: `git add -A && git commit`
- [x] 13.2 Commit agent-docs-sync changes: `git add -A && git commit`
- [x] 13.3 Archive the OpenSpec change: `openspec archive integrate-harness-features --yes`
- [x] 13.4 Commit openspec-store archive: `git add -A && git commit`
- [x] 13.5 Run `openspec validate --all --strict` to confirm no regressions
