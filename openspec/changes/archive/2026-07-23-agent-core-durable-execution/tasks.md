## 1. Add Durable Execution Config

- [x] 1.1 Add `durable_execution` field to `AgentConfig` in `config.py`
- [x] 1.2 Add `_build_durable_execution_capability()` to `agent.py`

## 2. Wire DBOSDurability

- [x] 2.1 Implement DBOS backend in `_build_durable_execution_capability()`
- [x] 2.2 Wire `DBOSDurability` with default config options

## 3. Wire Optional Temporal/Prefect

- [x] 3.1 Implement Temporal backend with optional import
- [x] 3.2 Implement Prefect backend with optional import
- [x] 3.3 Add ImportError handling for missing dependencies

## 4. Update Documentation

- [x] 4.1 Add durable execution section to `harness-integration.md`
- [x] 4.2 Add durable execution to `configuration.md` summary table

## 5. Tests

- [x] 5.1 Test DBOS durability wiring
- [x] 5.2 Test missing dependency error handling

## 6. Verify

- [x] 6.1 Run `ruff check` and `mypy --strict`
- [x] 6.2 Run `pytest tests/ -x`
