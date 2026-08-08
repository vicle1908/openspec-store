# Design: Protocol-Aware Model Resolution

## Architecture

### Current Flow

```
config.yaml model.primary → parse provider prefix → infer_model() → provider_factory()
                                                              ↓
                                                    _make_proxy_factory()
                                                              ↓
                                              anthropic → AnthropicProvider
                                              everything else → OpenAIProvider
```

### Proposed Flow (minimal change)

```
config.yaml model.primary → parse provider prefix → infer_model() → provider_factory()
                                                              ↓
                                                    _make_proxy_factory()
                                                              ↓
                                              anthropic → AnthropicProvider (strips /v1)
                                              openai-chat → OpenAIProvider (uses base as-is)
                                              openai-responses → OpenAIProvider (uses base as-is)
                                              everything else → OpenAIProvider (uses base as-is)
```

### Provider Routing Table

| Model Kind Prefix | Provider Class | Endpoint Path | URL Handling |
|---|---|---|---|
| `anthropic:` | AnthropicProvider | `/v1/messages` | Strip one `/v1` from base URL |
| `openai-chat:` | OpenAIProvider | `/v1/chat/completions` | Use base URL as-is |
| `openai-responses:` | OpenAIProvider | `/v1/responses` | Use base URL as-is |
| `google:` | OpenAIProvider | `/v1/chat/completions` | Use base URL as-is (proxy) |
| `fable-5:` | OpenAIProvider | `/v1/chat/completions` | Use base URL as-is (proxy) |
| `fable-5:` | OpenAIProvider | `/v1/chat/completions` | Use base URL as-is (proxy) |
| `groq:` | OpenAIProvider | `/v1/chat/completions` | Use base URL as-is (proxy) |

### Why not add `protocol` field

The model kind prefix already IS the protocol. Adding a `protocol` field would be:
1. Redundant — the prefix already tells pydantic-ai which model class to use
2. Confusing — two sources of truth (prefix + protocol field) that could conflict
3. Unnecessary — giaoduc exposes everything via OpenAI-compatible API, so all non-anthropic prefixes route through OpenAIProvider

The only case where `protocol` would help is if a proxy supports multiple protocols and you want to override the prefix. But this is an edge case that can be handled by changing the model kind prefix instead.

## Implementation

### _make_proxy_factory() enhancement

```python
def _make_proxy_factory(base_url: str, api_key: str) -> Callable[[str], Any]:
    def _factory(provider_name: str) -> Any:
        if provider_name == "anthropic":
            from pydantic_ai.providers.anthropic import AnthropicProvider
            anthropic_base_url = base_url.rstrip("/").removesuffix("/v1")
            return AnthropicProvider(base_url=anthropic_base_url, api_key=api_key)

        # All other providers (openai-chat, openai-responses, google, fable-5, etc.)
        # use OpenAI-compatible API via proxy
        from pydantic_ai.providers.openai import OpenAIProvider
        return OpenAIProvider(base_url=base_url, api_key=api_key)

    return _factory
```

This is already the current implementation. The only change needed is documentation — clarifying that the model kind prefix determines the protocol.

## Testing

Verified through real LLM calls:
- `anthropic:Advance` → AnthropicProvider → `/v1/messages` → 4 ✅
- `openai-chat:Advance` → OpenAIProvider → `/v1/chat/completions` → 4 ✅
- `openai-chat:fable-5` → OpenAIProvider → `/v1/chat/completions` → 4 ✅ (fallback)
