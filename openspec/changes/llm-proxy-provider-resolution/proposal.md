# LLM Proxy Provider Resolution

## Problem
The `create_model()` function in `agent-core/_ai/models.py` needs to resolve LLM provider endpoints and API keys. Previously, this was hardcoded to specific providers (OmniRoute, shopapikey). The new approach reads configuration from `~/.tdt/config.yaml` to support any OpenAI-compatible or Anthropic-compatible proxy.

## Solution
Add configuration-driven proxy resolution that reads from `~/.tdt/config.yaml`:

1. **Config format**: `model.base_url` and `model.api_key_env` in config.yaml
2. **Priority chain**: Explicit env vars > config.yaml > OmniRoute fallback
3. **No hardcoded URLs**: All provider URLs come from config
4. **Dual API support**: Works with both OpenAI Chat Completions and Anthropic Messages APIs

## Verified Provider: giaoduc

The giaoduc provider (`https://api.giaoduc.online/v1`) supports:

| API Format | Endpoint | Model Kind | Status |
|------------|----------|------------|--------|
| OpenAI Chat Completions | `/v1/chat/completions` | `openai-chat:Advance` | ✅ Verified |
| Anthropic Messages | `/v1/messages` | `anthropic:Advance` | ✅ Verified |
| OpenAI Responses | `/v1/responses` | `openai-responses:Advance` | ❌ Not supported |

### Features Supported

**OpenAI Chat Completions** (`openai-chat:Advance`):
- Standard chat completions
- Streaming responses
- Tool/function calling
- Reasoning content (thinking)

**Anthropic Messages** (`anthropic:Advance`):
- Messages API format
- Thinking/reasoning blocks
- Tool use
- System prompts

## Benefits
- **Flexibility**: Switch providers by editing config.yaml, not code
- **Security**: API keys referenced by env var name, not stored in config
- **Consistency**: Uses same config pattern as other TDT tools
- **Dual API**: Can use either OpenAI or Anthropic format with same provider

## Files Changed
- `agent-core/_ai/models.py`: Added `_load_tdt_model_config()`, updated `_resolve_proxy_from_env()`
- `~/.tdt/config.yaml`: Added model section with base_url and api_key_env
- `~/.tdt/.env`: Added `HERMES_CUSTOM_GIAODUC_API_KEY`
