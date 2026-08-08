# Tasks: API Mode Provider Routing

## Task 1: Add api_mode to provider config
- [x] Add `api_mode` field to `~/.tdt/config.yaml` providers section
- [x] Set giaoduc: `api_mode: anthropic_messages`
- [x] Set shopapikey: `api_mode: codex_responses`

## Task 2: Update models.py
- [x] Add `api_mode` parameter to `_make_proxy_factory()`
- [x] Update `_resolve_proxy_from_model_id()` to return `(base_url, api_key, api_mode)` tuple
- [x] Update `create_model()` to pass api_mode through
- [x] Update `create_fallback_model()` to pass api_mode through

## Task 3: Add tests
- [x] Test api_mode: anthropic_messages routes to AnthropicProvider
- [x] Test api_mode: codex_responses routes to OpenAIProvider
- [x] Test proxy resolution returns api_mode from config

## Task 4: Verify
- [x] All unit tests pass
- [x] Real LLM call: anthropic:Advance → AnthropicMessages → 4 ✅
