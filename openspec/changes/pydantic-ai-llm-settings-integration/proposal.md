# Proposal: pydantic-ai LLM Settings Integration

## Why

agent-core uses pydantic-ai v2 (2.18.0) but only exposes a narrow slice of its model configuration. The `ModelSettings` in `foundation/settings.py` has basic fields (primary, fallback, base_url, api_key), while pydantic-ai's `pydantic_ai.settings.ModelSettings` TypedDict offers rich per-request controls:

- **`thinking`** — unified reasoning effort (low/medium/high/xhigh) across all providers
- **`temperature`**, **`top_p`**, **`top_k`** — sampling controls
- **`max_tokens`** — generation limit
- **`tool_choice`** — function tool control
- **`parallel_tool_calls`** — parallel execution
- **`service_tier`** — cross-provider tier selection (auto/default/flex/priority)
- **`timeout`** — per-request timeout override
- **Provider-specific settings** — `anthropic_thinking`, `openai_reasoning_effort`, etc.

Currently:
1. `AgentConfig.thinking` field exists but is dead code (never consumed).
2. `model_settings: dict[str, Any] | None` on `AgentConfig` flows through to `AgentRuntime.run()` but is opaque — no typed support, no validation, no config-driven defaults.
3. There's no way to set thinking effort, temperature, or other provider settings from `config.yaml` or env vars.

## What Changes

### 1. New `ThinkingSettings` in `foundation/settings.py`
A typed pydantic-settings model for thinking/reasoning config, loadable from `config.yaml` and env vars.

### 2. Extended `ModelSettings` in `foundation/settings.py`
Add optional fields for the most impactful cross-provider settings: `thinking`, `temperature`, `max_tokens`, `service_tier`. These become defaults that can be overridden per-run via `model_settings`.

### 3. New `Thinking` capability integration in `sdk/agents.py`
When thinking is configured, automatically inject `pydantic_ai.capabilities.Thinking` into the capabilities list passed to `AgentRuntime`. This replaces the dead `AgentConfig.thinking` field.

### 4. Config → `model_settings` bridge in `sdk/agents.py`
Build a `model_settings` dict from `ModelSettings` fields and merge with per-call overrides, so consumers get config-driven defaults with runtime flexibility.

### 5. Remove dead `AgentConfig.thinking` field
Clean-break removal of the unused field from `_ai/config.py`.

### 6. Security hardening (from review)
- Blocklist for dangerous `extra_model_settings` keys (`extra_headers`, `extra_body`)
- Sensitive key rejection validator in `extra_model_settings`
- Range validators for `temperature` (0.0-2.0) and `max_tokens` (1-1000000)
- Exclude `extra_model_settings` from `model_dump()` serialization

### Scope

- **agent-core only** — no other repos consume these settings directly.
- `pydantic-ai>=2.18.0` already supports all needed features.
- No new dependencies required.
