# Design: API Mode Provider Routing

## Architecture

### Configuration Flow

```
~/.tdt/config.yaml          agent-core/_ai/models.py
─────────────────────        ─────────────────────────
model:                       _resolve_proxy_from_model_id()
  primary: anthropic:Advance     ├─ 1. MODEL_BASE_URL + MODEL_API_KEY
  base_url: https://...          ├─ 2. providers map → api_mode
  api_key_env: HERMES_...        └─ 3. model section (legacy)
providers:                           ↓
  giaoduc:                       _make_proxy_factory(api_mode=...)
    base_url: https://...           ├─ anthropic_messages → AnthropicProvider
    api_mode: anthropic_messages    └─ codex_responses/default → OpenAIProvider
  shopapikey:
    base_url: https://.../v1
    api_mode: codex_responses
```

### API Mode Mapping

| api_mode | Provider Class | Endpoint | URL Handling |
|----------|---------------|----------|--------------|
| `anthropic_messages` | AnthropicProvider | `/v1/messages` | Strip `/v1` from base_url |
| `codex_responses` | OpenAIProvider | `/v1/responses` | Use base_url as-is |
| (empty/default) | OpenAIProvider | `/v1/chat/completions` | Use base_url as-is |

### Provider Routing Table

| Provider | api_mode | base_url | Protocol |
|----------|----------|----------|----------|
| giaoduc | `anthropic_messages` | `https://api.giaoduc.online` | Anthropic Messages |
| shopapikey | `codex_responses` | `https://api.phanmemvip.shop/v1` | OpenAI Responses |
| omniroute | (default) | `http://localhost:20128/v1` | OpenAI Chat Completions |

## Implementation

### _make_proxy_factory()

```python
def _make_proxy_factory(
    base_url: str, api_key: str, *, api_mode: str = ""
) -> Callable[[str], Any]:
    def _factory(provider_name: str) -> Any:
        if api_mode == "anthropic_messages" or (
            not api_mode and provider_name == "anthropic"
        ):
            from pydantic_ai.providers.anthropic import AnthropicProvider
            anthropic_base_url = base_url.rstrip("/").removesuffix("/v1")
            return AnthropicProvider(base_url=anthropic_base_url, api_key=api_key)
        from pydantic_ai.providers.openai import OpenAIProvider
        return OpenAIProvider(base_url=base_url, api_key=api_key)
    return _factory
```

### _resolve_proxy_from_model_id()

Returns `(base_url, api_key, api_mode)` tuple instead of just `(base_url, api_key)`.

## Testing

- Unit tests verify api_mode routing (anthropic_messages → AnthropicProvider, codex_responses → OpenAIProvider)
- Real LLM calls verified: `anthropic:Advance` → AnthropicMessages → 4 ✅
