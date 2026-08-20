## Design: Harness Feature Integration (Maximized)

### Feature Adoption Strategy

Eight capabilities adopted in two tiers, each with independent verification:

```
┌─────────────────────────────────────────────────────────────┐
│              FEATURE ADOPTION SEQUENCE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TIER 1: Adopt with upgrade (high value, low effort)        │
│  ─────────────────────────────────────────────────────      │
│  Phase 1: Compaction (highest impact)                       │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure anchored incremental strategy                │
│  └── Verify context trimming works                          │
│                                                             │
│  Phase 2: SpendLimits (cost visibility)                     │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure per-model budgets                            │
│  └── Verify cost tracking in OTel traces                    │
│                                                             │
│  Phase 3: SystemReminders (instruction persistence)         │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure reminder schedule                            │
│  └── Verify instructions persist                            │
│                                                             │
│  Phase 4: Tool Output Limits (context overflow prevention)  │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure truncation thresholds                        │
│  └── Verify large tool results truncated                    │
│                                                             │
│  TIER 2: Adopt shortly after (medium value, medium effort)  │
│  ─────────────────────────────────────────────────────      │
│  Phase 5: ToolGuard (guardrail enhancement)                 │
│  ├── Add to agent-docs-sync guardrails                      │
│  ├── Configure tool-specific validation rules               │
│  └── Verify invalid tool args blocked                       │
│                                                             │
│  Phase 6: Warn On Cache Busts (performance)                 │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure cache monitoring                             │
│  └── Verify cache invalidation detected                     │
│                                                             │
│  Phase 7: Planning (task decomposition)                     │
│  ├── Add to agent-core agent construction                   │
│  ├── Configure planning strategy                            │
│  └── Verify model creates task plans                        │
│                                                             │
│  Phase 8: Conversation Search (history retrieval)           │
│  ├── Add to agent-core memory layer                         │
│  ├── Configure BM25 search                                  │
│  └── Verify history search works including compacted turns  │
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

### Feature 4: Tool Output Limits

**What it does:** Truncates, spills to file, or summarizes oversized tool returns at the source.

**Configuration:**
```python
from pydantic_ai_harness.context import ToolOutputLimits

tool_limits = ToolOutputLimits(
    max_chars=10_000,           # Truncate at 10K chars
    spill_to_file=True,         # Save full output to file
    spill_directory="/tmp/tool-outputs",  # Where to save
    summarize=True,             # Summarize truncated content
)
```

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Large tool results truncated at threshold
- Full output saved to spill directory
- Summarized content provided to agent

### Feature 5: ToolGuard

**What it does:** Validates tool arguments and results against schemas, blocking invalid calls.

**Configuration:**
```python
from pydantic_ai_harness.guardrails import ToolGuard

# Guard for write_file tool
write_guard = ToolGuard(
    tool_name="write_file",
    validate_args=lambda args: args["path"].startswith("docs/"),
    block_message="Write path must start with docs/",
)

# Guard for shell commands
shell_guard = ToolGuard(
    tool_name="run_shell",
    validate_args=lambda args: any(
        cmd in args["command"]
        for cmd in ["rm -rf", "sudo", "chmod 777"]
    ),
    block_message="Dangerous command blocked",
)
```

**Integration point:** `agent-docs-sync/guardrails.py` — add to guardrail construction

**Verification:**
- Invalid tool args blocked with clear message
- Valid tool args pass through unchanged
- Audit trail of blocked attempts

### Feature 6: Warn On Cache Busts

**What it does:** Detects prompt-cache prefix collapses between requests, from the provider's own numbers.

**Configuration:**
```python
from pydantic_ai_harness.context import WarnOnCacheBusts

cache_busts = WarnOnCacheBusts(
    enabled=True,
    log_warnings=True,  # Log to structlog
    alert_threshold=0.5,  # Alert if >50% of cache busted
)
```

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Cache invalidation events logged
- Performance degradation detected
- Cost impact visible in traces

### Feature 7: Planning

**What it does:** Model-owned task plans with a cache-safe live reminder.

**Configuration:**
```python
from pydantic_ai_harness.reasoning import Planning

planning = Planning(
    max_tasks=10,           # Maximum tasks in plan
    reminder_interval=3,    # Remind every 3 tool calls
    auto_update=True,       # Update plan as tasks complete
)
```

**Integration point:** `agent-core/_ai/agent.py` — add to capabilities list

**Verification:**
- Model creates task plan at start
- Plan updated as tasks complete
- Plan visible in agent context

### Feature 8: Conversation Search

**What it does:** BM25 search over stored history, including turns compaction dropped.

**Configuration:**
```python
from pydantic_ai_harness.memory import ConversationSearch

search = ConversationSearch(
    store=memory_store,     # Use existing memory store
    max_results=10,         # Return top 10 matches
    min_score=0.3,          # Minimum relevance score
)
```

**Integration point:** `agent-core/sdk/memory.py` — add to memory layer

**Verification:**
- Search returns relevant history
- Compacted turns searchable
- BM25 ranking works correctly

### Risk Assessment

| Feature | Risk | Mitigation |
|---|---|---|
| Compaction | Medium — could drop critical context | Anchored strategy preserves key messages; receipts allow verification |
| SpendLimits | Low — additive cost tracking | Budget limits are configurable; default to generous limits |
| SystemReminders | Low — re-injection of instructions | Every N tool calls; no duplicate injection |
| Tool Output Limits | Low — truncation at source | Spill to file preserves full output; summarize provides summary |
| ToolGuard | Low — validation layer | Additive; invalid calls blocked with clear messages |
| Warn On Cache Busts | Low — monitoring only | Log warnings; no behavioral change |
| Planning | Low — model-owned plans | Cache-safe reminder; auto-update on completion |
| Conversation Search | Low — search over history | BM25 is well-tested; max results bounded |
