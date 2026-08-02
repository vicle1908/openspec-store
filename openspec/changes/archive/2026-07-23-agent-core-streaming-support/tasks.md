## 1. Types — Define Missing Streaming Types

- [x] 1.1 Add `StreamChunk` dataclass to `_ai/types.py` with fields: `text: str | None`, `output: Any | None`, `tool_call: dict[str, Any] | None`, `done: bool`
- [x] 1.2 Add `ApprovalRequestChunk` dataclass to `_ai/types.py` with fields: `tool_name: str`, `args: dict[str, Any]`, `risk_level: str`

## 2. AgentRuntime — Implement run_stream()

- [x] 2.1 Add `run_stream(user_content, deps, output_type)` method to `AgentRuntime` in `_ai/agent.py`
- [x] 2.2 Wrap pydantic-ai's `Agent.run_stream()` to yield `StreamChunk` instances
- [x] 2.3 Handle `UsageLimitExceeded` in streaming (yield final `StreamChunk(done=True)`)
- [x] 2.4 Handle approval gate in streaming (yield `StreamChunk` with `tool_call` approval request)

## 3. Stream Approval — Fix Broken Imports

- [x] 3.1 Verify `stream_approval.py` imports work with newly defined types
- [x] 3.2 Remove any dead code or unused imports in `stream_approval.py`

## 4. Tests

- [x] 4.1 Test `StreamChunk` construction with text
- [x] 4.2 Test `StreamChunk` construction with output
- [x] 4.3 Test `StreamChunk` construction with tool_call
- [x] 4.4 Test `StreamChunk` done flag
- [x] 4.5 Test `ApprovalRequestChunk` construction
- [x] 4.6 Test `AgentRuntime.run_stream()` yields `StreamChunk` instances (mock model)
- [x] 4.7 Test `AgentRuntime.run_stream()` handles usage limit exceeded

## 5. Spec & Docs Alignment

- [x] 5.1 Remove DEFERRED status from AR-5 in `openspec/specs/agent-runtime/spec.md`
- [x] 5.2 Update `ai-agents-comparison/agent-core-feature-mapping.md` to reflect streaming implemented

## 6. Validation

- [x] 6.1 Run `ruff check . --fix && ruff format .` from agent-core root
- [x] 6.2 Run `mypy src/agent_core/ --strict` — zero errors
- [x] 6.3 Run `pytest tests/ -x` — all tests pass (1 pre-existing failure in tests/memory/)
