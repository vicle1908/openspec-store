# Tasks: LLM Proxy Provider Resolution

## Task 1: Update _ai/models.py
- [x] Add `_load_tdt_model_config()` function
- [x] Update `_resolve_proxy_from_env()` to read from config
- [x] Add `base_url` and `api_key` kwargs to `create_model()`
- [x] Add `base_url` and `api_key` kwargs to `create_fallback_model()`

## Task 2: Update config.yaml
- [x] Add model section with base_url and api_key_env
- [x] Add HERMES_CUSTOM_SHOPAPIKEY_API_KEY to ~/.tdt/.env

## Task 3: Update tests
- [x] Fix test_base_agent_requires_model → test_base_agent_has_default_model

## Task 4: Verification
- [ ] Run real LLM call via shopapikey
- [ ] Verify config loading
- [ ] Verify proxy resolution
