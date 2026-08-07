# LLM Proxy Provider Resolution

## Problem
The `create_model()` function in `agent-core/_ai/models.py` needs to resolve LLM provider endpoints and API keys. Previously, this was hardcoded to specific providers (OmniRoute, shopapikey). The new approach reads configuration from `~/.tdt/config.yaml` to support any OpenAI-compatible proxy.

## Solution
Add configuration-driven proxy resolution that reads from `~/.tdt/config.yaml`:

1. **Config format**: `model.base_url` and `model.api_key_env` in config.yaml
2. **Priority chain**: Explicit env vars > config.yaml > OmniRoute fallback
3. **No hardcoded URLs**: All provider URLs come from config

## Benefits
- **Flexibility**: Switch providers by editing config.yaml, not code
- **Security**: API keys referenced by env var name, not stored in config
- **Consistency**: Uses same config pattern as other TDT tools

## Files Changed
- `agent-core/_ai/models.py`: Added `_load_tdt_model_config()`, updated `_resolve_proxy_from_env()`
- `~/.tdt/config.yaml`: Added model section with base_url and api_key_env
