# Design: Upgrade pydantic-ai-harness 0.11.0 → 0.23.0

## Architecture Changes

### AgentRuntime Capability Stack

Before (0.11.0):
```
Instrumentation → PrepareTools → supplied_capabilities → SystemReminders
```

After (0.23.0):
```
Instrumentation → PrepareTools → supplied_capabilities → TieredCompaction → SystemReminders
                                                                    ↓
                                                           SpendLimits (optional)
                                                                    ↓
                                                           Planning (optional)
                                                                    ↓
                                                           Advisor (optional)
```

### New Parameters (AgentRuntime.__init__)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_tokens` | `int` | `120_000` | Target token count for TieredCompaction |
| `spend_limit_per_run_usd` | `float \| None` | `5.0` | Per-run USD budget |
| `spend_limit_per_day_usd` | `float \| None` | `100.0` | Per-day USD budget |
| `enable_planning` | `bool` | `False` | Enable task plan tracking |
| `advisor_model` | `Any \| None` | `None` | Cheaper model for decision review |
| `advisor_max_uses` | `int \| None` | `3` | Max advisor consultations per run |

### Type Changes

| Field | Before | After |
|-------|--------|-------|
| `ConsumerRuntimeProfile.max_iterations` | `int` (default 15) | `int \| None` (default None) |
| `ConsumerRuntimeProfile.timeout_seconds` | `float` | `float \| None` (default None) |

## Import Changes

### agent-core (new imports in _ai/agent.py)
```python
from pydantic_ai_harness.compaction import (
    ClearToolResults, DeduplicateFileReads, SummarizingCompaction, TieredCompaction,
)
from pydantic_ai_harness.planning import Planning
from pydantic_ai_harness.spend import Budget, SpendLimits
from pydantic_ai_harness.system_reminders import GoalReanchor
from pydantic_ai_harness import SystemReminders
from pydantic_ai_harness.advisor import Advisor
```

### agent-harness (import boundary fix)
```python
# Before:
from agent_core.lifecycle_identity import AssuranceLevel, ...
# After:
from agent_core.sdk import AssuranceLevel, ...
```

## Spec Changes

### Archived/Historical (7 specs)
- `_standalone/harness-compaction` — describes removed harness_config interface
- `_standalone/harness-runtime-authoring` — describes removed harness_config interface
- `agent-core-compose-integration-verifier` — describes non-existent Go infrastructure
- `public-api` — describes pre-migration API with ~15 removed symbols
- `agent-compaction` — describes removed _build_harness_capabilities()
- `builtin-hooks` — describes removed HookRegistry/register_pack pattern
- (harness-compaction already had staleness notice)

### Updated (5 specs)
- `vendor-isolation` — HookAdapter → create_budget_hooks
- `harness-integration` (standalone) — _build_harness_capabilities → build_agent
- `integration-guide` — version baseline updated
- `agent-docs-harness` — capability list updated
- `public-api` — version references updated

## Dev Tooling Changes

| Tool | Before | After |
|------|--------|-------|
| ruff | >=0.16.1 | >=0.16.3 |
| pre-commit-hooks | agent-core only | all 3 repos |
| Scheduler expected counts | 18 schedules, 4 manifests | 21 schedules, 5 manifests |
