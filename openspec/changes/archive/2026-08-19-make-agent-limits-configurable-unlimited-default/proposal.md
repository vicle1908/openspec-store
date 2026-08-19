## Why

The agent ecosystem has hardcoded limits scattered across code that should be configurable via `~/.tdt/config.yaml`:

1. **`total_tokens_limit=150_000`** — hardcoded in `AgentRuntime.run()` with zero config path. The generate step consumed 1M tokens in one run; this cap would have blocked it.

2. **`max_iterations` and `timeout_seconds`** — hardcoded in `ConsumerRuntimeProfile` defaults (15/180s) and overridden by flavor defaults (8-20 / 90-300s). These should be configurable via `~/.tdt/config.yaml`.

3. **`budget_usd=0.50`** — hardcoded in `doc_full_sync` flavor. Operators should be able to set their own budget or leave it unlimited.

**Target philosophy**: Agents run freely (no iteration, timeout, or token caps) as long as the LLM is generating responses. The operator controls limits via `~/.tdt/config.yaml`. Unset = unlimited. `budget_usd` is the cost safety net — operators set it if they want cost protection.

## Review Findings (GitNexus + Agent Team)

**agent-core impact** (GitNexus: 17 files, MEDIUM risk): ConsumerRuntimeProfile has 6 direct consumers. Two files require type annotation updates (`agent_base/agent.py`, `_ai/agent.py`). `FlavorDefaults` already accepts None, so no flavor changes needed. The `AgentRuntime.__init__` default `max_iterations=10` is overridden by profile, so it remains non-None unless explicitly passed None.

**agent-docs-sync impact** (review agent): `EffectiveRuntimeControls` uses non-optional `int`/`float` fields that would break if None flows through. `_apply_environment` cannot parse "None" from env vars — needs a sentinel convention. The spec text hardcodes `max_iterations=20, timeout=300s` and needs updating. Flavor defaults should remain as-is (per-role safety rails). `RuntimeConfigLike` protocol returns concrete `float`, not `float | None`.

**Environment variable parsing**: `DOCS_SYNC_MAX_ITERATIONS=None` would cause `ValueError` since `int("None")` is invalid. Need a sentinel convention (e.g., `"none"` maps to Python `None`).

## What Changes

- **BREAKING**: Default `max_iterations` changes from `15`/`10`/`20` to `None` (unlimited).
- **BREAKING**: Default `timeout_seconds` changes from `180.0`/`120.0`/`300.0` to `None` (unlimited).
- `total_tokens_limit` becomes configurable via `ConsumerRuntimeProfile` (default `None` = unlimited).
- **BREAKING**: Default `budget_usd` changes from `0.50` (doc_full_sync) to `None` (unlimited).
- All four limits configurable via `~/.tdt/config.yaml` under `agent:`, with `null`/unset meaning unlimited.
- `budget_usd` remains available as a cost safety net — operators set it explicitly when they want cost protection.
- Flavor defaults become override hints (only applied if no operator config is present).

## Config Structure

```yaml
# ~/.tdt/config.yaml
agent:
  max_iterations: null    # null = unlimited (default)
  timeout_seconds: null   # null = unlimited (default)
  total_tokens_limit: null  # null = unlimited (default)
  budget_usd: null         # null = unlimited (default); set e.g. 5.00 for cost cap
```

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-core-model-resolution`: Update `ConsumerRuntimeProfile` to accept `None` for `max_iterations`/`timeout_seconds`/`total_tokens_limit`; document unlimited-as-default behavior; document `budget_usd` as the optional cost safety net.

## Impact

- **Code**: `agent_core/sdk/config.py`, `agent_core/_ai/agent.py` (3 sites), `agent_core/agent_base/agent.py`, `agent_core/_ai/agent.py` (enforcement)
- **Specs**: agent-core-model-resolution (limits + budget)
- **Behavior**: All limits become unlimited by default; budget_usd defaults to None
- **Migration**: Consumers relying on default caps will see agents run longer. Set `budget_usd` in config if cost control is needed.
