# Design: agent-core-model-resolution-hardening

## 1. Streaming model test strategy

`_StreamingResponsesModel` overrides two methods:
- `_process_streamed_response()`: Normalizes gateways that omit `response.output` on completion
- `request()`: Aggregates SSE stream via `request_stream()` + `get()`

### Test matrix

| Test | What it covers |
|------|----------------|
| test_stream_aggregates_text_output | Basic SSE to ModelResponse with text |
| test_stream_handles_empty_completion_output | response.output is None normalized to empty list |
| test_stream_preserves_tool_calls | Tool call items in stream |
| test_stream_propagates_usage | Usage metadata from stream |
| test_stream_propagates_finish_reason | Finish reason from completion |
| test_stream_handles_malformed_event | Non-ResponseCompletedEvent items skipped |
| test_stream_propagates_upstream_exception | Exception during iteration |
| test_request_delegates_to_stream | request() calls request_stream() then get() |

### Mock strategy

Use `unittest.mock.AsyncMock` and `unittest.mock.MagicMock` to simulate SSE events. Create realistic event objects from `openai.types.responses`.

## 2. Fallback chain test strategy

`create_model_with_fallback(model)` reads `_load_tdt_model_config()` and checks for `fallback` key.

| Test | Config state | Expected |
|------|-------------|----------|
| test_no_fallback_config | No fallback key | Single model via create_model |
| test_single_fallback | fallback: ["model-b"] | FallbackModel with 2 models |
| test_multiple_fallbacks | fallback: ["b", "c"] | FallbackModel with 3 models |
| test_explicit_model_bypasses | Model instance input | Returns instance as-is |
| test_fallback_uses_create_fallback_model | Has fallback key | Calls create_fallback_model |

### Credential behavior

Fallback models are constructed lazily by FallbackModel. Missing credentials should NOT cause eager failure.

## 3. Consumer integration test

Test that `build_agent()` passes the model string through `create_model_with_fallback()`. Use monkeypatch to verify the correct function is called.

## 4. Fallback chain precedence

1. Explicit `base_url`/`api_key` kwargs
2. Model-specific proxy from TDT config
3. Global TDT config fallback list
4. Native provider env vars
