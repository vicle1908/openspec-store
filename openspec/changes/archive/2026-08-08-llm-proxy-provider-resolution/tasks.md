# Tasks: LLM Proxy Provider Resolution

## Task 1: Update _ai/models.py
- [x] Add `_load_tdt_model_config()` function
- [x] Update `_resolve_proxy_from_env()` to read from config
- [x] Add `base_url` and `api_key` kwargs to `create_model()`
- [x] Add `base_url` and `api_key` kwargs to `create_fallback_model()`
- [x] Select `AnthropicProvider` for `anthropic:*` and normalize the `/v1` URL
- [x] Remove inactive OmniRoute fallback from the active resolver

## Task 2: Update config.yaml
- [x] Add model section with base_url and api_key_env
- [x] Add HERMES_CUSTOM_GIAODUC_API_KEY to ~/.tdt/.env

## Task 3: Update tests
- [x] Fix test_base_agent_requires_model → test_base_agent_has_default_model

## Task 4: Verify dual API support
- [x] Test OpenAI Chat Completions (`openai-chat:Advance`)
- [x] Test Anthropic Messages (`anthropic:Advance`)
- [x] Confirm OpenAI Responses not supported (404)

## Task 5: Real LLM verification
- [x] Config loading from ~/.tdt/config.yaml
- [x] Proxy resolution (giaoduc endpoint)
- [x] Model creation (OpenAIChatModel / AnthropicModel)
- [x] Real agent run via OpenAI Chat Completions → "4" ✅
- [x] Real agent run via Anthropic Messages → "4" ✅
- [x] Real agent run loads `~/.tdt/config.yaml` and `.env` without manual env loading → "4" ✅

## Task 6: Update openspec
- [x] Proposal updated with dual API support
- [x] Design updated with Anthropic Messages API
- [x] Delta spec updated with dual API scenarios
- [x] Tasks updated with verification results
