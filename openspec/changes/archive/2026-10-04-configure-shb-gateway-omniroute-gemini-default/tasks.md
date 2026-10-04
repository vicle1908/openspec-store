# Tasks

## 1. OpenSpec Delta Specs & Validation

- [x] 1.1 Author proposal.md, design.md, tasks.md, and delta specs for `shb-core-foundation` and `shb-agent-runtime`
- [x] 1.2 Validate change strictly using `openspec validate configure-shb-gateway-omniroute-gemini-default --strict --store openspec-store`

## 2. Configuration & Environment Updates

- [x] 2.1 Update `~/.shb/.env` setting `SHB_DEFAULT_MODEL=gemini-3.8-flash-high`
- [x] 2.2 Update `~/.shb/.env.example` template with `SHB_DEFAULT_MODEL=gemini-3.8-flash-high`

## 3. Code & Test Updates in shb-core

- [x] 3.1 Update `default_model` field default in `shb_core.config.ShbSettings` to `gemini-3.8-flash-high`
- [x] 3.2 Update `tests/test_config.py` in `shb-core` to assert `gemini-3.8-flash-high`
- [x] 3.3 Execute test suite in `shb-core` with `uv run pytest -p no:cacheprovider`

## 4. Verification & Integration Testing

- [x] 4.1 Execute test suite in `shb-agent-core` with `uv run pytest -p no:cacheprovider`
- [x] 4.2 Verify `shb-agent models-list` and agent execution against OmniRoute with `gemini-3.8-flash-high`
- [x] 4.3 Validate all OpenSpec specs with `openspec validate --all --strict --store openspec-store`
