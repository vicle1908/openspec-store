# Protocol-Aware Model Resolution

## Why

The current model resolution relies on pydantic-ai's model kind prefix (`anthropic:`, `openai-chat:`, `openai-responses:`, `google:`, etc.) to determine the protocol. This works for giaoduc (which exposes everything via OpenAI-compatible API), but has gaps:

1. **Proxy factory only handles 2 protocols**: `anthropic` → AnthropicProvider, everything else → OpenAIProvider. A Google-native proxy or OpenAI Responses API proxy would be routed incorrectly.
2. **No way to override protocol per-provider**: If giaoduc adds fable-5 support via a non-OpenAI endpoint, there's no config way to specify the protocol.
3. **Ambiguity for multi-protocol proxies**: A single proxy might support both OpenAI Chat and Anthropic Messages — the model kind prefix determines which, but this isn't visible in config.

The question: should `~/.tdt/config.yaml` include an explicit `protocol` field?

## What Changes

### Analysis: Current State

| Config Field | Current | Purpose |
|---|---|---|
| `model.primary` | `anthropic:Advance` | Model kind prefix determines protocol |
| `model.base_url` | `https://api.giaoduc.online/v1` | Proxy endpoint |
| `model.api_key_env` | `HERMES_CUSTOM_GIAODUC_API_KEY` | API key location |

The model kind prefix already encodes the protocol:
- `anthropic:*` → Anthropic Messages API (`/v1/messages`)
- `openai-chat:*` → OpenAI Chat Completions (`/v1/chat/completions`)
- `openai-responses:*` → OpenAI Responses API (`/v1/responses`)
- `google:*` → Google AI API
- `mistral:*` → fable-5 API

### Analysis: Gap

The `_make_proxy_factory()` currently only handles:
- `anthropic` → AnthropicProvider (strips `/v1` from URL)
- Everything else → OpenAIProvider

This means:
- `openai-chat:Advance` → OpenAIProvider → `/v1/chat/completions` ✅
- `anthropic:Advance` → AnthropicProvider → `/v1/messages` ✅
- `google:Advance` → OpenAIProvider → `/v1/chat/completions` (giaoduc exposes via OpenAI-compatible, so this works)
- `openai-responses:Advance` → OpenAIProvider → `/v1/chat/completions` ❌ (should be `/v1/responses`)

### Recommendation: No explicit protocol field needed

The model kind prefix is the protocol. The proxy factory should route based on the prefix:

| Prefix | Provider | Endpoint |
|---|---|---|
| `anthropic:` | AnthropicProvider | `/v1/messages` (strip `/v1` from base) |
| `openai-chat:` | OpenAIProvider | `/v1/chat/completions` (use base as-is) |
| `openai-responses:` | OpenAIProvider | `/v1/responses` (use base as-is) |
| `google:` | OpenAIProvider | `/v1/chat/completions` (giaoduc proxy) |
| `fable-5:` | OpenAIProvider | `/v1/chat/completions` (giaoduc proxy) |

The proxy factory already handles the Anthropic URL difference. The only gap is `openai-responses:*` which should use the OpenAI Responses endpoint — but giaoduc doesn't support it anyway.

### If explicit protocol IS needed in the future

Add to `~/.tdt/config.yaml`:

```yaml
model:
  primary: anthropic:Advance
  base_url: https://api.giaoduc.online/v1
  api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY
  protocol: anthropic  # optional override: anthropic, openai-chat, openai-responses, google
  fallback:
    - openai-chat:fable-5
  timeout_seconds: 120
```

The `protocol` field would override the model kind prefix for proxy routing. This is only needed if a single proxy supports multiple protocols and the model kind prefix alone is ambiguous.

## Files Changed
- `agent-core/_ai/models.py`: Enhanced `_make_proxy_factory()` to route based on model kind prefix
- `~/.tdt/config.yaml`: No change needed for current giaoduc setup
