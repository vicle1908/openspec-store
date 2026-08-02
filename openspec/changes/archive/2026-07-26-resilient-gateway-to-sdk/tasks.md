## 1. Create ResilientGateway in agent-core

- [x] 1.1 Copy `ResilientGateway` class from `agent-docs-sync/llm/resilient.py` to `agent-core/llm_gateway/resilient.py`
- [x] 1.2 Update imports: change `from agent_core.sdk import ...` to `from agent_core.resilience import ...` and `from agent_core.llm_gateway.types import LLMGateway`
- [x] 1.3 Add `ResilientGateway` to `agent-core/llm_gateway/__init__.py` exports
- [x] 1.4 Add `ResilientGateway` to `agent-core/sdk/__init__.py` re-exports

## 2. Update agent-docs-sync

- [x] 2.1 Update `agent-docs-sync/llm/gateway.py` — change `from .resilient import ResilientGateway` to `from agent_core.llm_gateway import ResilientGateway`
- [x] 2.2 Delete `agent-docs-sync/llm/resilient.py`
- [x] 2.3 Run `pytest tests/` in agent-docs-sync — verify zero failures

## 3. Verification

- [x] 3.1 Run `uv run --directory agent-core ruff check src/llm_gateway/` — lint passes
- [x] 3.2 Run `uv run --directory agent-core pytest tests/llm_gateway/ -x` — tests pass
- [x] 3.3 Run `uv run --directory agent-docs-sync pytest tests/ -x` — tests pass
- [x] 3.4 Verify `from agent_core.sdk import ResilientGateway` works
