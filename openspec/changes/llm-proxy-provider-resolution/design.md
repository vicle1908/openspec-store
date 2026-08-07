# Design: LLM Proxy Provider Resolution

## Architecture

### Configuration Flow

```
~/.tdt/config.yaml          os.environ                    agent-core/_ai/models.py
─────────────────────        ──────────────                ─────────────────────────
model:                       HERMES_CUSTOM_GIAODUC_        _resolve_proxy_from_env()
  base_url: https://...        API_KEY=pmv_...             │
  api_key_env: HERMES_...                                   ├─ 1. MODEL_BASE_URL + MODEL_API_KEY
  primary: openai-chat:                                    ├─ 2. config.base_url + env[config.api_key_env]
    Advance                                                └─ 3. OMNIROUTE_URL + OMNIROUTE_API_KEY
```

### Priority Chain

1. **Explicit env vars** (`MODEL_BASE_URL` + `MODEL_API_KEY`): Highest priority
2. **Config.yaml** (`model.base_url` + env var from `model.api_key_env`): Default path
3. **OmniRoute** (`OMNIROUTE_URL` + `OMNIROUTE_API_KEY`): Fallback

### Config Schema

```yaml
model:
  primary: openai-chat:Advance      # Default model (or anthropic:Advance)
  base_url: https://api.giaoduc.online/v1  # Proxy endpoint
  api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY  # Env var name for API key
  fallback:                         # Fallback models
    - openai-chat:fable-5
  timeout_seconds: 120
```

### Supported API Formats

The giaoduc provider supports two API formats via the same endpoint:

#### OpenAI Chat Completions (`openai-chat:Advance`)
- Endpoint: `POST /v1/chat/completions`
- Auth: `Authorization: Bearer <key>`
- Model kind: `openai-chat:Advance`
- Features: Streaming, tool calling, reasoning content

#### Anthropic Messages (`anthropic:Advance`)
- Endpoint: `POST /v1/messages`
- Auth: `x-api-key: <key>` + `anthropic-version: 2023-06-01`
- Model kind: `anthropic:Advance`
- Features: Thinking blocks, tool use, system prompts

### Provider Detection

pydantic-ai automatically routes to the correct endpoint based on model kind:
- `openai-chat:*` → `/v1/chat/completions` (OpenAI format)
- `anthropic:*` → `/v1/messages` (Anthropic format)
- `openai-responses:*` → `/v1/responses` (not supported by giaoduc)

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

The provider factory is created based on the model kind prefix:
- `openai-chat:*` → `OpenAIProvider(base_url, api_key)`
- `anthropic:*` → `AnthropicProvider(base_url, api_key)`

## Testing

Real LLM verification passed:

```
Provider: giaoduc (https://api.giaoduc.online/v1)
Model: openai-chat:Advance (OpenAI) / anthropic:Advance (Anthropic)
Q: What is 2 + 2? Reply with just the number.
A: 4 ✅
```
