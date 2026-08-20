## Design: Harness Feature Integration (Maximized)

### Verified Import Paths (Smoke-Tested Against 0.23.0)

All import paths verified via `uv run --with pydantic-ai-harness==0.23.0 python -c "import ..."`:

| Module | Import Path | Status |
|---|---|---|
| Compaction | `pydantic_ai_harness.compaction` | ✅ Verified |
| SystemReminders | `pydantic_ai_harness` (root) | ✅ Verified |
| GoalReanchor | `pydantic_ai_harness.system_reminders` | ✅ Verified |
| ToolOutputLimits | `pydantic_ai_harness.tool_output_limits` | ✅ Verified |
| WarnOnCacheBusts | `pydantic_ai_harness.warn_on_cache_busts` | ✅ Verified |
| SpendLimits | `pydantic_ai_harness.spend` | ✅ Verified |
| Planning | `pydantic_ai_harness.planning` | ✅ Verified |
| ConversationSearch | `pydantic_ai_harness.conversation_search` | ✅ Verified |
| Advisor | `pydantic_ai_harness.advisor` | ✅ Verified |
| GuardrailResult | `pydantic_ai_harness.guardrails` | ✅ Verified |
| ToolGuardrail | `pydantic_ai_harness.guardrails` | ✅ Verified |
| redact_secrets | `pydantic_ai_harness.guardrails.detectors` | ✅ Verified |

**Module renames in 0.23.0** (deprecated aliases still work):
- `pydantic_ai_harness.context` → `pydantic_ai_harness.repo_context`
- `pydantic_ai_harness.cache_stability` → `pydantic_ai_harness.warn_on_cache_busts`
- `pydantic_ai_harness.overflowing_tool_output` → `pydantic_ai_harness.tool_output_limits`
- `GuardResult` → `GuardrailResult`
- `InputGuard` → `InputGuardrail`
- `OutputGuard` → `OutputGuardrail`

### Verified API Signatures (Smoke-Tested Against 0.23.0)

All configuration examples verified against actual class signatures:

**TieredCompaction** — Required: `tiers: Sequence[CompactionStrategy]`
```python
TieredCompaction(
    tiers=[DeduplicateFileReads(...), ClearToolResults(...), SummarizingCompaction(...)],
    target_tokens=120_000,  # Optional: trigger threshold
)
```

**SystemReminders** — Required: none (all optional)
```python
SystemReminders(
    dynamic_reminders=[GoalReanchor(fallback='Stay on task.')],  # Optional
)
```

**SpendLimits** — Required: none (all optional)
```python
SpendLimits(
    budgets=[
        Budget(usd=Decimal('5'), window='run'),  # Budget is keyword-only
        Budget(usd=Decimal('100'), window='day'),
    ],
)
```

**Planning** — Required: none (all optional)
```python
Planning(
    enable_subtasks=True,  # Optional
)
```

**ConversationSearch** — Required: `source: HistorySource`
```python
ConversationSearch(
    source=SnapshotHistorySource(store),  # Required positional
    max_matches=10,
)
```

**Advisor** — Required: `model: ModelSelection` (positional)
```python
Advisor(model='anthropic:claude-opus-4-7')  # Required
```

**ToolGuardrail** — Required: none (guard or result_guard optional)
```python
ToolGuardrail(
    guard=lambda ctx, args: args.get('path', '').startswith('docs/'),
    tools=['write_file'],
)
```

### Feature Adoption Strategy

Seven capabilities adopted in four batches, ordered by value/effort ratio:

```
┌─────────────────────────────────────────────────────────────┐
│              FEATURE ADOPTION SEQUENCE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BATCH 1: Quick wins (same commit, biggest bang)            │
│  ─────────────────────────────────────────────────────      │
│  Phase 1: Compaction (CRITICAL value, LOW effort)           │
│  ├── TieredCompaction with 3 tiers                          │
│  ├── DeduplicateFileReads → ClearToolResults → Summarizing  │
│  └── Prevents context overflow (most common failure mode)   │
│                                                             │
│  Phase 2: SystemReminders (HIGH value, VERY LOW effort)     │
│  ├── GoalReanchor — zero-cost, one line of code             │
│  └── Prevents instruction fade in long runs                 │
│                                                             │
│  BATCH 2: Security + Cost (independent, can parallel)       │
│  ─────────────────────────────────────────────────────      │
│  Phase 3: Guardrails upgrade (HIGH value, LOW-MEDIUM)       │
│  ├── Migrate GuardResult → GuardrailResult (drop-in)        │
│  ├── Add ToolGuardrail for tool call validation             │
│  ├── Add hidden tools (zero-cost security)                  │
│  └── Add ready-made detectors (redact_secrets, etc.)        │
│                                                             │
│  Phase 4: SpendLimits (HIGH value, LOW-MEDIUM)              │
│  ├── Cross-window USD/token budgets                         │
│  ├── Per-tenant scoped budgets                              │
│  └── Redis store for multi-process                          │
│                                                             │
│  BATCH 3: Build on compaction                               │
│  ─────────────────────────────────────────────────────      │
│  Phase 5: Planning (MEDIUM-HIGH value, LOW-MEDIUM)          │
│  ├── Replaces test-only dynamic_workflow                    │
│  ├── Planner/executor split for cost optimization           │
│  └── Production-ready task tracking                         │
│                                                             │
│  Phase 6: ConversationSearch (MEDIUM-HIGH value, LOW)       │
│  ├── BM25 search over persisted history                     │
│  ├── Recovers compaction-dropped messages                   │
│  └── Requires StepPersistence (already have)                │
│                                                             │
│  BATCH 4: Use-case specific                                 │
│  ─────────────────────────────────────────────────────      │
│  Phase 7: Advisor (MEDIUM value, LOW-MEDIUM)                │
│  ├── Multi-model consultation (cheap executes, expensive    │
│  │   reviews)                                               │
│  └── Best for high-stakes decision agents                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Feature 1: Compaction (CRITICAL)

**What it does:** Automatically trims conversation context when approaching model limits using a tiered strategy that escalates from zero-cost to LLM-based compaction.

**Recommended configuration:**
```python
from pydantic_ai_harness.compaction import (
    TieredCompaction,
    DeduplicateFileReads,
    ClearToolResults,
    SummarizingCompaction,
)

compaction = TieredCompaction(
    tiers=[
        DeduplicateFileReads(file_key=lambda msg: msg.content),  # Zero cost
        ClearToolResults(max_tokens=1, keep_pairs=3),            # Zero cost
        SummarizingCompaction(max_messages=1, keep_messages=20), # 1 LLM call
    ],
    target_tokens=120_000,  # Trigger at 80% of 150K context
)
```

**Available strategies (9 total):**
- `SlidingWindowCompaction` — drops oldest messages (zero cost)
- `SummarizingCompaction` — LLM summarizes older messages (1 call)
- `TieredCompaction` — chains strategies, escalates until fit (recommended)
- `ClearToolResults` — replaces old tool results with placeholder
- `DeduplicateFileReads` — blanks superseded file reads
- `ClampOversizedMessages` — truncates oversized parts
- `WarnNearLimits` — injects URGENT/CRITICAL warnings
- `ReportContextUsage` — reports context usage metrics
- `FallbackCompaction` — tries strategies in order on failure

**Also available:** `pin()` to protect content through compaction, `compact_now()` for manual compaction, receipts, tracing.

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Short conversations (< 10 turns): no compaction triggered
- Long conversations (> 50 turns): compaction preserves key facts
- Compaction receipts visible in traces

### Feature 2: SystemReminders (HIGH)

**What it does:** Re-injects critical instructions mid-run to counter context drift, using cache-safe mechanisms.

**Recommended configuration:**
```python
from pydantic_ai_harness.context import SystemReminders, GoalReanchor

reminders = SystemReminders(
    dynamic_reminders=[GoalReanchor()],  # Zero-cost, one line
)
```

**Available options:**
- `Reminder` — fires on fixed cadence (every N model requests)
- `GoalReanchor` — zero-cost, restates original goal each request (recommended)
- `LLMReminder` — model-generated stay-on-task nudge
- Dynamic reminders — callable evaluated every request

**Configuration:** `max_fires`, `first_after`, `trigger` predicate, `tag`, `on_fire` callback

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Instructions re-injected at specified intervals
- No duplicate reminders in context
- Agent behavior consistent across long conversations

### Feature 3: Guardrails Upgrade (HIGH)

**What it does:** Enhances existing guardrails with ToolGuardrail, ready-made detectors, and new outcomes (replace, retry, approve).

**Migration path:**
```python
# Old (0.11.0)                    # New (0.23.0)
GuardResult                       GuardrailResult
InputGuard                        InputGuardrail
OutputGuard                       OutputGuardrail
```

**New capabilities:**
```python
from pydantic_ai_harness.guardrails import (
    ToolGuardrail,
    redact_secrets,
    redact_personal_data,
    blocked_keywords,
)

# Tool call validation
tool_guard = ToolGuardrail(
    guard=lambda ctx, args: args["path"].startswith("docs/"),
    tools=["write_file"],  # Only apply to specific tools
)

# Hidden tools (zero-cost security — model never sees the tool)
hidden_guard = ToolGuardrail(
    hidden=True,  # Tool completely invisible to model
    tools=["dangerous_tool"],
)

# Ready-made detectors
secret_guard = redact_secrets(only=["api_key", "password"])
pii_guard = redact_personal_data(only=["email", "phone"])
keyword_guard = blocked_keywords(["rm -rf", "sudo"])
```

**Integration point:** `agent-docs-sync/guardrails.py` — migrate existing guards, add ToolGuardrail

**Verification:**
- Existing InputGuard/OutputGuard work after migration
- ToolGuardrail blocks invalid tool args
- Hidden tools invisible to model
- Ready-made detectors redact sensitive content

### Feature 4: SpendLimits (HIGH)

**What it does:** Tracks and enforces USD/token budgets across agent runs, with per-model and per-tenant breakdowns.

**Recommended configuration:**
```python
from pydantic_ai_harness.control import SpendLimits, Budget
from decimal import Decimal

spend_limits = SpendLimits(
    budgets=[
        Budget(usd=Decimal("5"), window="run"),
        Budget(usd=Decimal("100"), window="day"),
        Budget(usd=Decimal("2000"), window="month", warn_at=0.8),
    ],
    per_model_limits={
        "anthropic:claude-sonnet-4-6": Budget(usd=Decimal("2"), window="run"),
        "anthropic:claude-opus-4-7": Budget(usd=Decimal("4"), window="run"),
    },
    scope=lambda ctx: ctx.deps.tenant_id,  # Per-tenant budgets
    expose_tools=True,  # Give agent a get_spend tool
)
```

**Available options:**
- Cross-window budgets: per-run, per-conversation, per-day, per-month, per-total
- Scoped budgets (per-tenant, per-user via `scope` callable)
- Pure counters (no ceiling, just accounting)
- Custom pricing functions
- `on_spend` callback with `SpendSnapshot`
- `warn_at` threshold for advance warning
- Stores: `InMemorySpendStore`, `RedisSpendStore`
- `status()` and `exhausted()` for programmatic checks

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Cost tracked in OTel spans (existing instrumentation)
- Budget exceeded → agent raises `SpendLimitExceeded`
- Per-model breakdown visible in traces

### Feature 5: Planning (MEDIUM-HIGH)

**What it does:** Model-owned task plans with persistence and planner/executor split.

**Recommended configuration:**
```python
from pydantic_ai_harness.reasoning import Planning

planning = Planning(
    max_tasks=10,
    enable_subtasks=True,  # Allow subtask decomposition
    store=SqlitePlanStore(database=":memory:"),  # Persistent plans
)
```

**Available options:**
- Tools: `write_plan`, `read_plan`, `add_task`, `update_task_status`, `remove_task`
- Subtasks and dependencies with `enable_subtasks=True`
- Statuses: pending, in_progress, completed, cancelled, blocked
- Persistence: `InMemoryPlanStore`, `SqlitePlanStore`, `PostgresPlanStore`, `RedisPlanStore`
- Separate planner/executor runs (planner writes plan, executor follows it)
- Plan events for UI integration

**Integration point:** `agent-core/_ai/agent.py` — replace dynamic_workflow with Planning

**Verification:**
- Model creates task plan at start
- Plan updated as tasks complete
- Plan visible in agent context
- Planner/executor split works correctly

### Feature 6: ConversationSearch (MEDIUM-HIGH)

**What it does:** BM25 search over persisted conversation history, including compaction-dropped messages.

**Recommended configuration:**
```python
from pydantic_ai_harness.memory import ConversationSearch, SnapshotHistorySource

search = ConversationSearch(
    history_source=SnapshotHistorySource(store),  # Use existing StepPersistence store
    scope="conversation",  # Search within current conversation
    max_results=10,
    min_score=0.3,
)
```

**Available options:**
- BM25 full-text search over persisted conversation history
- Recovers compaction-dropped messages (reads pre-compaction snapshots)
- Cross-run or run-scoped search
- Tunable BM25 parameters (k1, b)
- Provenance metadata on results

**Integration point:** `agent-core/sdk/memory.py` — add to memory layer

**Verification:**
- Search returns relevant history
- Compacted turns searchable
- BM25 ranking works correctly

### Feature 7: Advisor (MEDIUM)

**What it does:** Executor model consults a separate advisor model before decisions.

**Recommended configuration:**
```python
from pydantic_ai_harness.reasoning import Advisor

advisor = Advisor(
    model="anthropic:claude-opus-4-7",  # Expensive model reviews
    max_uses=3,  # Max consultations per executor request
    max_tokens=4096,  # Max tokens per consultation
    forward_history=True,  # Pass executor context to advisor
)
```

**Available options:**
- Native path (Anthropic/OpenRouter) — zero latency overhead
- Local fallback — runs separate Pydantic AI agent
- `max_uses`, `max_tokens`, `forward_history` configuration
- Streaming: executor pauses during consultation
- Caching for Anthropic native path

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list (if use case fits)

**Verification:**
- Advisor consulted before high-stakes decisions
- Consultation logged in traces
- Graceful fallback on advisor failure

### Risk Assessment

| Feature | Risk | Mitigation |
|---|---|---|
| Compaction | Medium — could drop critical context | TieredCompaction with pin() for critical content; receipts allow verification |
| SystemReminders | Low — re-injection of instructions | GoalReanchor is zero-cost; no behavioral change |
| Guardrails | Low — validation layer | Additive; invalid calls blocked with clear messages |
| SpendLimits | Low — additive cost tracking | Budget limits configurable; default to generous limits |
| Planning | Low — model-owned plans | Cache-safe reminder; auto-update on completion |
| ConversationSearch | Low — search over history | BM25 is well-tested; max results bounded |
| Advisor | Low — consultation only | Graceful fallback; max_uses cap |
