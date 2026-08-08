# Tasks: pydantic-ai LLM Settings Integration

## Slice 1: Settings Model Extension
- [ ] 1.1 Add `thinking`, `temperature`, `max_tokens`, `top_p`, `service_tier`, `extra_model_settings` fields to `ModelSettings` in `foundation/settings.py`
- [ ] 1.2 Add field validators for `thinking` (ThinkingLevel values) and `service_tier` (ServiceTier values)
- [ ] 1.3 Add env var overrides: `MODEL_THINKING`, `MODEL_TEMPERATURE`, `MODEL_TOP_P`, `MODEL_MAX_TOKENS`, `MODEL_SERVICE_TIER`
- [ ] 1.4 Write unit tests for new ModelSettings fields (valid values, env overrides, invalid values)
- [ ] 1.5 Verify config.yaml loading with new fields

## Slice 2: build_agent Integration
- [ ] 2.1 Add `model_settings` and `thinking` params to `build_agent()` in `sdk/agents.py`
- [ ] 2.2 Implement Thinking capability injection from config defaults + overrides
- [ ] 2.3 Implement model_settings dict construction from ModelSettings fields
- [ ] 2.4 Pass model_settings through BaseAgent to AgentRuntime
- [ ] 2.5 Write unit tests for build_agent with thinking/settings

## Slice 3: AgentConfig Cleanup
- [ ] 3.1 Remove dead `thinking: str | bool | None` field from `AgentConfig` in `_ai/config.py`
- [ ] 3.2 Update `AgentConfig` docstring
- [ ] 3.3 Grep all consumers of `AgentConfig.thinking` and fix references
- [ ] 3.4 Update tests referencing `AgentConfig.thinking`

## Slice 4: Security Hardening
- [ ] 4.1 Add `_EXTRA_MODEL_SETTINGS_BLOCKLIST` and `_SENSITIVE_KEYS` to `foundation/settings.py`
- [ ] 4.2 Add `_validate_extra_model_settings` field validator (blocklist + sensitive key rejection)
- [ ] 4.3 Update `ModelSettings.model_dump()` to exclude `extra_model_settings` from serialization
- [ ] 4.4 Add range validators: `temperature` (ge=0.0, le=2.0), `max_tokens` (ge=1, le=1_000_000)
- [ ] 4.5 Add thinking compatibility warning log when thinking configured for non-reasoning model
- [ ] 4.6 Write unit tests: blocklist rejection, sensitive key rejection, range validation, serialization exclusion

## Slice 5: Documentation & Spec Updates
- [ ] 5.1 Update agent-core AGENTS.md with new config fields
- [ ] 5.2 Update existing OpenSpec specs for LLM configuration (agent-core-model-resolution, agent-core-llm-loading)
- [ ] 5.3 Add delta spec for this change

## Verification
- [ ] V.1 All existing tests pass (`uv run pytest tests/`)
- [ ] V.2 `uv run ruff check src/ tests/` clean
- [ ] V.3 `uv run mypy src/agent_core/ --strict` clean
- [ ] V.4 Grep for dead `AgentConfig.thinking` references — zero hits
- [ ] V.5 Grep for blocked `extra_headers`/`extra_body` in extra_model_settings — zero hits in config
- [ ] V.6 Security tests pass (blocklist, sensitive key rejection, range validation)
