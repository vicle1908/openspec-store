# Design: fable-5 Build CLI Integration

## Architecture

fable-5 Build CLI remains an optional developer CLI process consuming existing provider gateways through `~/.fable-5`. No application request path, agent-core provider factory, or TDT provider contract changes.

## Provider Configuration

```toml
[model_providers.shopapikey]
base_url = "https://api.phanmemvip.shop/v1"
env_key = "HERMES_CUSTOM_SHOPAPIKEY_API_KEY"
api_backend = "responses"
context_window = 1000000

[model.shopapikey-fable-5]
model = "fable-5"
name = "fable-5 (shopapikey)"
model_provider = "shopapikey"

[model_providers.giaoduc]
base_url = "https://api.giaoduc.online"
env_key = "HERMES_CUSTOM_GIAODUC_API_KEY"
api_backend = "messages"
context_window = 1000000

[model.giaoduc-advance]
model = "Advance"
name = "Advance (giaoduc)"
model_provider = "giaoduc"

[model_providers.cockpit]
base_url = "http://localhost:51006/v1"
env_key = "HERMES_CUSTOM_COCKPIT_API_KEY"
api_backend = "responses"
context_window = 1000000

[model.cockpit-sol]
model = "fable-5"
name = "fable-5 (cockpit)"
model_provider = "cockpit"

[model.cockpit-luna]
model = "fable-5"
name = "fable-5 (cockpit)"
model_provider = "cockpit"
```

## Verified Evidence

- Official docs: fable-5, fable-5 -p, XAI_API_KEY, ~/.fable-5, custom models confirmed
- Official source: chat_completions, responses, messages backends confirmed
- Official stable channel: 1.0.0
- shopapikey: HTTP 200 on /v1/models, /v1/responses
- giaoduc: HTTP 200 on /v1/models, /v1/messages (both Bearer and x-api-key)
- cockpit: HTTP 200 on /v1/models, /v1/responses

## Risk

- giaoduc auth form under fable-5 messages backend is not yet proven
- fable-5 binary not installed yet
- config parsing warnings unknown until fable-5 inspect runs

## Acceptance

- fable-5 inspect zero warnings
- all four provider probes return sentinels
- workspace discovery confirmed
- mcp-router routing documented
- rollback path real
- unrelated files untouched