# Design: LLM Proxy Provider Resolution

## Architecture

### Configuration Flow

```
~/.tdt/config.yaml          os.environ                    agent-core/_ai/models.py
─────────────────────        ──────────────                ─────────────────────────
model:                       HERMES_CUSTOM_SHOPAPIKEY_     _resolve_proxy_from_env()
  base_url: https://...        API_KEY=pmv_...             │
  api_key_env: HERMES_...                                   ├─ 1. MODEL_BASE_URL + MODEL_API_KEY
  primary: openai-chat:                                    ├─ 2. config.base_url + env[config.api_key_env]
    fable-5                                                └─ 3. OMNIROUTE_URL + OMNIROUTE_API_KEY
```

### Priority Chain

1. **Explicit env vars** (`MODEL_BASE_URL` + `MODEL_API_KEY`): Highest priority
2. **Config.yaml** (`model.base_url` + env var from `model.api_key_env`): Default path
3. **OmniRoute** (`OMNIROUTE_URL` + `OMNIROUTE_API_KEY`): Fallback

### Config Schema

```yaml
model:
  primary: openai-chat:fable-5      # Default model
  base_url: https://api.phanmemvip.shop/v1  # Proxy endpoint
  api_key_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY  # Env var name for API key
  fallback:                         # Fallback models
    - openai-chat:claude-sonnet-4.6
  timeout_seconds: 120
```

## Implementation

### _load_tdt_model_config()

Reads `~/.tdt/config.yaml` and returns the `model` section dict. Uses `yaml.safe_load()` with error handling.

### _resolve_proxy_from_env()

Resolves proxy endpoint using the priority chain:
1. Check `MODEL_BASE_URL` + `MODEL_API_KEY` env vars
2. Load config.yaml, get `base_url` and `api_key_env`, resolve API key from env
3. Fall back to `OMNIROUTE_URL` + `OMNIROUTE_API_KEY`

### create_model() / create_fallback_model()

Accept optional `base_url` and `api_key` kwargs. If not provided, auto-detect via `_resolve_proxy_from_env()`.
