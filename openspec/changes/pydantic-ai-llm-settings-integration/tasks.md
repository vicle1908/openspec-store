# Tasks: pydantic-ai LLM Settings Integration

## Slice 1: Settings Model Extension
- [x] 1.1 Add `thinking`, `temperature`, `max_tokens`, `top_p`, `service_tier`, `extra_model_settings` fields to `ModelSettings` in `foundation/settings.py`
- [x] 1.2 Add field validators for `thinking` (ThinkingLevel values) and `service_tier` (Literal type)
- [x] 1.3 Add env var overrides: `MODEL_THINKING`, `MODEL_TEMPERATURE`, `MODEL_TOP_P`, `MODEL_MAX_TOKENS`, `MODEL_SERVICE_TIER`
- [x] 1.4 Write unit tests for new ModelSettings fields (valid values, env overrides, invalid values)
- [x] 1.5 Verify config.yaml loading with new fields

## Slice 2: build_agent Integration
- [x] 2.1 Add `model_settings` and `thinking` params to `build_agent()` in `sdk/agents.py`
- [x] 2.2 Implement Thinking capability injection from config defaults + overrides
- [x] 2.3 Implement model_settings dict construction from ModelSettings fields
- [x] 2.4 Pass model_settings through BaseAgent to AgentRuntime (shallow merge)
- [x] 2.5 Write unit tests for build_agent with thinking/settings

## Slice 3: AgentConfig Cleanup
- [x] 3.1 Remove dead `thinking: str | bool | None` field from `AgentConfig` in `_ai/config.py`
- [x] 3.2 Update `AgentConfig` docstring
- [x] 3.3 Grep all consumers of `AgentConfig.thinking` and fix references
- [x] 3.4 Update tests referencing `AgentConfig.thinking`

## Slice 4: Security Hardening
- [x] 4.1 Add `_EXTRA_MODEL_SETTINGS_BLOCKLIST` and `_SENSITIVE_KEY_PATTERNS` to `foundation/settings.py`
- [x] 4.2 Add `_validate_extra_model_settings` field validator (blocklist + sensitive key rejection)
- [x] 4.3 Update `ModelSettings.model_dump()` to exclude `extra_model_settings` from serialization
- [x] 4.4 Add range validators: `temperature` (ge=0.0, le=2.0), `max_tokens` (ge=1, le=1_000_000)
- [x] 4.5 Add thinking compatibility warning log when thinking configured for non-reasoning model
- [x] 4.6 Write unit tests: blocklist rejection, sensitive key rejection, range validation, serialization exclusion

## Slice 5: Documentation & Spec Updates
- [x] 5.1 Update agent-core AGENTS.md with new config fields
- [x] 5.2 Update existing OpenSpec specs for LLM configuration (agent-core-model-resolution, agent-core-llm-loading)
- [x] 5.3 Add delta spec for this change

## Verification
- [x] V.1 All existing tests pass (`uv run pytest tests/`) — 667 passes
- [x] V.2 `uv run ruff check src/ tests/` clean
- [x] V.3 `uv run mypy src/agent_core/ --strict` clean
- [x] V.4 Grep for dead `AgentConfig.thinking` references — zero hits
- [x] V.5 Grep for blocked `extra_headers`/`extra_body` in extra_model_settings — zero hits in config
- [x] V.6 Security tests pass (blocklist, sensitive key rejection, range validation)
