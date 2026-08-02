## 1. Configuration Dataclasses

- [x] 1.1 Create `agent_core/_ai/config.py` with `AgentConfig` dataclass (model required, 9 optional fields with defaults)
- [x] 1.2 Create `agent_core/memory/config.py` with `MemoryConfig` dataclass (context/scratch required, 3 optional fields)
- [x] 1.3 Add `__init__.py` exports for new config modules

## 2. AgentRuntime Integration

- [x] 2.1 Add `config: AgentConfig | None = None` parameter to `AgentRuntime.__init__()`
- [x] 2.2 Update `AgentRuntime.__init__()` to use config when provided (map config fields to internal attributes)
- [x] 2.3 Add deprecation warning when old constructor signature is used
- [x] 2.4 Update `BaseAgent` to accept `AgentConfig` parameter

## 3. Memory Facade Integration

- [x] 3.1 Add `config: MemoryConfig | None = None` parameter to `Memory.__init__()`
- [x] 3.2 Update `Memory.__init__()` to use config when provided
- [x] 3.3 Add deprecation warning when old constructor signature is used

## 4. GatewayFactory

- [x] 4.1 Create `agent_core/llm_gateway/factory.py` with `GatewayFactory` class
- [x] 4.2 Implement `register(name, provider)` with duplicate check
- [x] 4.3 Implement `create(name, **kwargs)` with provider lookup
- [x] 4.4 Implement `list_providers()` returning registered names
- [x] 4.5 Add `__init__.py` exports for factory module
- [x] 4.6 Update `create_gateway()` to use `GatewayFactory` internally

## 5. Protocol Documentation

- [x] 5.1 Document when to use Protocol vs ABC in `docs/architecture.md`
- [x] 5.2 Add Protocol-based example in `docs/extending.md`

## 6. Tests

- [x] 6.1 Create `tests/_ai/test_config.py` for AgentConfig (construction, defaults, serialization)
- [x] 6.2 Create `tests/memory/test_config.py` for MemoryConfig (construction, defaults)
- [x] 6.3 Create `tests/llm_gateway/test_factory.py` for GatewayFactory (register, create, errors)
- [x] 6.4 Update `tests/agent_base/test_agent.py` to test AgentConfig integration
- [x] 6.5 Update `tests/memory/test_memory.py` to test MemoryConfig integration
- [x] 6.6 Add backward compatibility tests for old constructor signatures

## 7. Validation

- [x] 7.1 Run `mypy src/agent_core/ --strict` — verify zero errors
- [x] 7.2 Run `ruff check src/agent_core/` — verify all checks pass
- [x] 7.3 Run full test suite `pytest tests/ -x` — verify all tests pass
