# Design: make-agent-limits-configurable-unlimited-default

## Context

Hardcoded limits across agent-core and agent-docs-sync prevent operators from tuning agent behavior. The generate step consumed 1M tokens in one run — the hardcoded `total_tokens_limit=150_000` would have blocked this if enforced. The user wants agents to run freely (unlimited iterations, timeout, tokens) with `budget_usd` as the sole cost safety net.

## Architecture Decision: None = Unlimited

`ConsumerRuntimeProfile` currently uses typed defaults (`max_iterations: int = 15`, `timeout_seconds: float = 180.0`). The change shifts to `Optional[int] = None` / `Optional[float] = None` where `None` means unlimited.

**Why Optional[float] and not math.inf?**
- YAML `null` serializes cleanly as `None`
- JSON: `null` not `Infinity`
- pydantic-ai's `UsageLimits(request_limit=None)` means no cap (verified)
- `asyncio.wait_for(..., timeout=None)` means no timeout (Python standard)

## Config Structure

```yaml
# ~/.tdt/config.yaml
agent:
  max_iterations: null    # null = unlimited (default)
  timeout_seconds: null   # null = unlimited (default)
  total_tokens_limit: null  # null = unlimited (default)
  budget_usd: 5.00        # cost safety net (set by operator)
```

The `agent:` section is already in the config.yaml.example. Operators set their own limits; unset = unlimited.

## Enforcement Points

| Limit | Enforcement | Configurable? |
|---|---|---|
| max_iterations | `UsageLimits(request_limit=N)` in `AgentRuntime.run()` | Yes, via ConsumerRuntimeProfile |
| timeout_seconds | `asyncio.wait_for(..., timeout=N)` in `BaseAgent.run()` | Yes, via ConsumerRuntimeProfile |
| total_tokens_limit | `UsageLimits(total_tokens_limit=N)` in `AgentRuntime.run()` | Yes, via ConsumerRuntimeProfile |
| budget_usd | `BUDGET_EXCEEDED` check in `BaseAgent.run()` | Yes, via FlavorDefaults |

When a limit is `None`:
- `UsageLimits(request_limit=None)` → pydantic-ai runs without iteration cap
- `asyncio.wait_for(..., timeout=None)` → no timeout
- `UsageLimits(total_tokens_limit=None)` → no token cap

## Migration

Existing consumers using default limits will see agents run longer. This is intentional — the old defaults (15 iterations, 180s) were too restrictive for real workloads. Operators who need caps should set explicit values in `~/.tdt/config.yaml`.

## Risks

- [Runaway agent] → Mitigated by `budget_usd` cap. Operators MUST set this.
- [LLM API errors without timeout] → Mitigated by pydantic-ai's built-in retry logic and the budget cap.
- [Existing test expectations] → Tests that assert specific iteration counts may need updating.
