# API Mode Provider Routing

## Why

The current agent-core model resolution relies on pydantic-ai's model kind prefix (`anthropic:`, `openai-chat:`, etc.) to determine the API protocol. This works for simple proxies but doesn't match how Hermes configures providers.

Hermes uses an `api_mode` field to explicitly declare the protocol:
- `anthropic_messages` → AnthropicProvider, base_url WITHOUT `/v1`
- `codex_responses` → OpenAIProvider, base_url WITH `/v1`
- (default) → OpenAIProvider, base_url WITH `/v1` (Chat Completions)

Adding `api_mode` to agent-core's provider config aligns with Hermes and makes the routing explicit rather than inferred.

## What Changes

### Config (`.tdt/config.yaml`)

```yaml
model:
  primary: anthropic:Advance
  base_url: https://api.giaoduc.online
  api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY
  fallback:
    - openai-chat:fable-5
  timeout_seconds: 120

providers:
  giaoduc:
    base_url: https://api.giaoduc.online
    api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY
    api_mode: anthropic_messages
  shopapikey:
    base_url: https://api.phanmemvip.shop/v1
    api_key_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY
    api_mode: codex_responses
```

### Code (`agent-core/_ai/models.py`)

- `_make_proxy_factory()` now accepts `api_mode` parameter
- `_resolve_proxy_from_model_id()` returns `(base_url, api_key, api_mode)` tuple
- `api_mode: anthropic_messages` → AnthropicProvider (strips `/v1` from base_url)
- `api_mode: codex_responses` → OpenAIProvider (uses base_url as-is)
- Default (empty) → OpenAIProvider (Chat Completions)

### Files Changed
- `agent-core/_ai/models.py`: Added api_mode to proxy factory and resolution
- `agent-core/tests/ai/test_models.py`: Added api_mode tests
- `~/.tdt/config.yaml`: Added api_mode to providers
