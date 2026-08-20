## Design: Harness Feature Integration

### Feature Adoption Strategy

Each feature is adopted incrementally with its own verification cycle. Features are independent and can be adopted in any order.

```
┌─────────────────────────────────────────────────────────────┐
│              FEATURE ADOPTION SEQUENCE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: Compaction (highest impact)                       │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure anchored incremental strategy                │
│  ├── Verify no context loss on short conversations          │
│  └── Verify context trimming on long conversations          │
│                                                             │
│  Phase 2: SpendLimits (cost visibility)                     │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure per-model budgets                            │
│  ├── Verify cost tracking in OTel traces                    │
│  └── Verify budget enforcement                              │
│                                                             │
│  Phase 3: SystemReminders (instruction persistence)         │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure reminder schedule                            │
│  ├── Verify instructions persist across 10+ tool calls      │
│  └── Verify no duplicate reminders                          │
│                                                             │
│  Phase 4: ToolGuard (guardrail enhancement)                 │
│  ├── Add to agent-docs-sync guardrails                      │
│  ├── Configure tool-specific validation rules               │
│  ├── Verify invalid tool args are blocked                   │
│  └── Verify valid tool args pass through                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Feature 1: Compaction

**What it does:** Automatically trims conversation context when approaching model limits, preserving critical information through anchored incremental strategy.

**Configuration:**
```python
from pydantic_ai_harness.compaction import Compaction, AnchoredCompaction

compaction = Compaction(
    strategy=AnchoredCompaction(
        keep_user_messages=True,      # Never drop user messages
        pin_last_n=5,                 # Keep last 5 exchanges intact
        receipt_prefix="[compacted]", # Mark compacted sections
    ),
    threshold=0.8,  # Trigger at 80% of context window
)
```

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Short conversations (< 10 turns): no compaction triggered
- Long conversations (> 50 turns): compaction preserves key facts
- Compacted sections marked with receipt prefix

### Feature 2: SpendLimits

**What it does:** Tracks and enforces USD/token budgets across agent runs, with per-model and per-tenant breakdowns.

**Configuration:**
```python
from pydantic_ai_harness.control import SpendLimits

spend_limits = SpendLimits(
    max_usd_per_run=1.00,           # $1 per run
    max_tokens_per_run=100_000,     # 100K tokens per run
    max_usd_per_day=10.00,          # $10 per day (cross-run)
    per_model_limits={
        "anthropic:claude-sonnet-4-6": {"max_usd": 0.50},
        "anthropic:claude-opus-4-7": {"max_usd": 0.80},
    },
)
```

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Cost tracked in OTel spans (existing instrumentation)
- Budget exceeded → agent raises `SpendLimitExceeded`
- Per-model breakdown visible in traces

### Feature 3: SystemReminders

**What it does:** Re-injects critical instructions mid-run to counter context drift, using cache-safe mechanisms.

**Configuration:**
```python
from pydantic_ai_harness.context import SystemReminders

reminders = SystemReminders(
    reminders=[
        "You are a documentation agent. Only write to docs/ paths.",
        "Use Diátaxis framework: tutorials, how-to, reference, explanation.",
        "Never modify source code.",
    ],
    every_n_tool_calls=5,  # Re-inject every 5 tool calls
)
```

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Instructions re-injected at specified intervals
- No duplicate reminders in context
- Agent behavior consistent across long conversations

### Feature 4: ToolGuard

**What it does:** Validates tool arguments and results against schemas, blocking invalid calls.

**Configuration:**
```python
from pydantic_ai_harness.guardrails import ToolGuard

tool_guard = ToolGuard(
    tool_name="write_file",
    validate_args=lambda args: args["path"].startswith("docs/"),
    block_message="Write path must start with docs/",
)
```

**Integration point:** `agent-docs-sync/guardrails.py` — add to guardrail construction

**Verification:**
- Invalid tool args blocked with clear message
- Valid tool args pass through unchanged
- Audit trail of blocked attempts

### Risk Assessment

| Feature | Risk | Mitigation |
|---|---|---|
| Compaction | Medium — could drop critical context | Anchored strategy preserves key messages; receipts allow verification |
| SpendLimits | Low — additive cost tracking | Budget limits are configurable; default to generous limits |
| SystemReminders | Low — re-injection of instructions | Every N tool calls; no duplicate injection |
| ToolGuard | Low — validation layer | Additive; invalid calls blocked with clear messages |
