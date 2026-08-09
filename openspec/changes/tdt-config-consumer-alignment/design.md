# Design: TDT Config Consumer Alignment

## Architecture

```
~/.tdt/config.yaml
  model:
    primary: nhà cung cấp dịch vụ AI:Advance
    fallback: [nhà cung cấp dịch vụ AI-chat:fable-5]
    thinking: high
    temperature: 0.7
    max_tokens: 4096
        │
        ▼
  load_settings() → Settings
        │
        ▼
  _create_runtime_model(settings)
        │
        ▼
  create_fallback_model(primary, fallbacks)
        │
        ▼
  FallbackModel(primary, fallback1, ...)
```

## Gap

`_create_runtime_model()` only passes `primary` and `fallback` to `create_model`/`create_fallback_model`.
The behavior fields (`thinking`, `temperature`, `max_tokens`, `top_p`, `service_tier`, `extra_model_settings`)
are loaded into `settings.model` but never applied to the runtime model.

## Solution

1. `_create_runtime_model()` reads behavior fields from `settings.model`
2. Passes them as `model_settings` kwarg to `create_model()` / `create_fallback_model()`
3. `create_model()` accepts optional `model_settings` dict
4. `create_fallback_model()` accepts optional `model_settings` dict

## File Changes

### `src/agent_core/cli/utils.py`
- Extract behavior settings from `settings.model`
- Pass as `model_settings` to `create_model()`/`create_fallback_model()`

### `src/agent_core/_ai/models.py`
- `create_model()` accepts optional `model_settings: dict[str, Any] = None`
- `create_fallback_model()` accepts optional `model_settings: dict[str, Any] = None`
- Both pass `model_settings` to `infer_model()`

### `tests/ai/test_models.py`
- Add test: behavior settings are passed through to model
- Add test: None/empty settings produce no model_settings
