# TDT Config Consumer Alignment

## Problem

CLI agents load model settings via `_create_runtime_model()` in `cli/utils.py`,
which only uses `settings.model.primary` and `settings.model.fallback` to construct
the model chain. It does NOT wire through `thinking`, `temperature`, `max_tokens`,
`top_p`, `service_tier`, or `extra_model_settings` from `ModelSettings`.

This means LLM behavior settings configured in `~/.tdt/config.yaml` are loaded
into `Settings` but ignored by the CLI runtime path.

## Solution

Update `_create_runtime_model()` to apply `ModelSettings` behavior fields to the
model configuration via pydantic-ai's model settings API.

## Scope

- `src/agent_core/cli/utils.py` — wire through behavior settings
- `src/agent_core/foundation/settings.py` — no changes needed (fields already exist)
- `src/agent_core/_ai/models.py` — may need to accept settings kwargs
- `tests/` — add RED tests for behavior settings propagation

## Not in Scope

- CLI templates intentionally have no `model:` section (model is global)
- OpenSpec specs already align with implementation
- Config loading precedence is correct and verified
