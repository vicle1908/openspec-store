# agent-core-model-resolution-hardening

## Why

The ecosystem review identified that the streaming model boundary and fallback chain have insufficient test coverage. These are the highest-risk changes because they modify the model protocol boundary between agent-core and pydantic-ai.

1. **Streaming model under-tested**: `_StreamingResponsesModel` overrides the SSE aggregation protocol. Only type-check and trivial mock tests exist. No coverage of actual SSE aggregation, text output, tool calls, usage metadata, finish reason, malformed events, or upstream exceptions.

2. **Fallback chain untested**: `create_model_with_fallback()` reads TDT config and constructs `FallbackModel`. Zero test coverage for any scenario.

3. **Consumer integration untested**: `build_agent()` now calls `create_model_with_fallback()` instead of `create_model()`. No regression test for existing string-model behavior.

## What Changes

### Testing
- Add streaming model tests: SSE aggregation, text output, empty completion, tool calls, usage metadata, finish reason, malformed events, upstream exceptions
- Add fallback chain tests: no fallback config, single fallback, multiple fallbacks, explicit Model bypass
- Add consumer integration test: `build_agent()` uses `create_model_with_fallback()`

### Documentation
- Document the streaming compatibility boundary in `_StreamingResponsesModel` docstring
- Document fallback chain precedence in `create_model_with_fallback()` docstring
- Document that fallback construction does NOT eagerly fail for unused fallbacks

### Repos in scope
- `agent-core` (models.py, tests/ai/test_models.py, sdk/agents.py)
