## 1. Type Definition

- [x] 1.1 Define `StreamChunk` dataclass in `agent_core/_ai/types.py` with fields: `text`, `output`, `tool_call`, `usage`, `done`
- [x] 1.2 Define `ApprovalRequestChunk` for streaming approval interrupts

## 2. AgentRuntime Streaming (Pydantic AI)

- [x] 2.1 Implement `run_stream()` method in `AgentRuntime` wrapping `pydantic_ai.Agent.run_stream()`
- [x] 2.2 Handle text chunk streaming: yield `StreamChunk(text=delta)` for each text token
- [x] 2.3 Handle structured output streaming: yield `StreamChunk(output=validated_model)` for validated chunks
- [x] 2.4 Handle tool call streaming: yield `StreamChunk(tool_call=...)` when tools are invoked
- [x] 2.5 Handle usage tracking: yield `StreamChunk(usage=...)` at stream end

## 3. LangGraph Workflow Streaming

- [x] 3.1 Add `stream_mode` parameter to `WorkflowEngine.run()` (default: None for backward compat)
- [x] 3.2 Implement `stream_mode="messages"` for token-by-token LLM streaming
- [x] 3.3 Add `version="v2"` support for unified StreamPart format
- [x] 3.4 Implement `get_stream_writer()` support for custom node emissions
- [x] 3.5 Implement `stream_mode="checkpoints"` for checkpoint events during streaming
- [x] 3.6 Add streaming yield to `WorkflowEngine.run()` async iterator

## 4. MCP Integration

- [x] 4.1 Add `mcp_servers` parameter to `AgentRuntime` constructor
- [x] 4.2 Implement MCPToolset capability integration (wraps FastMCP Client)
- [x] 4.3 Support local (stdio) and remote (Streamable HTTP, SSE) MCP servers
- [x] 4.4 Wire MCP tools through ToolRegistry for governance
- [x] 4.5 Add MCP server configuration to settings
- [x] 4.6 Support provider-native MCP execution when available (nhà cung cấp dịch vụ AI, nhà cung cấp dịch vụ AI)

## 5. Thinking Capability

- [x] 5.1 Add `Thinking` capability import from pydantic_ai.capabilities
- [x] 5.2 Add `thinking` parameter to `AgentRuntime` constructor (default: None)
- [x] 5.3 Wire Thinking capability into agent capabilities list
- [x] 5.4 Support effort levels: "minimal", "low", "medium", "high", "xhigh"
- [x] 5.5 Verify provider-adaptive behavior (nhà cung cấp dịch vụ AI, nhà cung cấp dịch vụ AI, Google)

## 6. ToolSearch Capability

- [x] 6.1 Add `ToolSearch` capability import from pydantic_ai.capabilities
- [x] 6.2 Add `tool_search` parameter to `AgentRuntime` constructor (default: None)
- [x] 6.3 Wire ToolSearch capability into agent capabilities list
- [x] 6.4 Support strategy parameter: 'keywords', 'bm25', 'regex', or custom callable

## 7. ApprovalGate Integration

- [x] 7.1 Detect approval-needed state during streaming via `HandleDeferredToolCalls` capability
- [x] 7.2 Yield `ApprovalRequestChunk` when approval is needed
- [x] 7.3 Implement stream pause/resume mechanism for approval workflow
- [x] 7.4 Verify approval flow works identically to non-streaming path

## 8. BaseAgent Public API

- [x] 8.1 Add `run_stream()` method to `BaseAgent` that delegates to `AgentRuntime.run_stream()`
- [x] 8.2 Add `run_stream_sync()` synchronous wrapper for non-async consumers
- [x] 8.3 Update `BaseAgent` type hints and docstrings

## 9. Tests

- [x] 9.1 Create `tests/agent_base/test_streaming.py`
- [x] 9.2 Test streaming yields text chunks incrementally
- [x] 9.3 Test streaming with structured output yields validated model instances
- [x] 9.4 Test streaming completion yields `done=True` chunk
- [x] 9.5 Test approval gate interrupts stream correctly
- [x] 9.6 Test stream resumes after approval granted
- [x] 9.7 Test LangGraph streaming mode="messages" yields token chunks
- [x] 9.8 Test get_stream_writer() custom emissions
- [x] 9.9 Test backward compatibility: `run()` still works unchanged
- [x] 9.10 Run `pytest tests/agent_base/ -x`

## 10. Validation

- [x] 10.1 Run `mypy agent_core/_ai/ --strict`
- [x] 10.2 Run `ruff check agent_core/_ai/ && ruff format agent_core/_ai/`
- [x] 10.3 Run full test suite `pytest tests/ -x`
