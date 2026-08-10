# Tasks: agent-core-model-resolution-hardening

## P1: Streaming model tests

- [ ] Add test: stream aggregates text output into ModelResponse
- [ ] Add test: stream handles empty/null completion output
- [ ] Add test: stream preserves tool calls
- [ ] Add test: stream propagates usage metadata
- [ ] Add test: stream propagates finish reason
- [ ] Add test: stream handles malformed/non-ResponseCompletedEvent items
- [ ] Add test: stream propagates upstream exception
- [ ] Add test: request() delegates to request_stream() + get()

## P1: Fallback chain tests

- [ ] Add test: no fallback config returns single model
- [ ] Add test: single fallback returns FallbackModel
- [ ] Add test: multiple fallbacks returns FallbackModel
- [ ] Add test: explicit Model instance bypasses fallback construction
- [ ] Add test: empty fallback list returns single model

## P2: Consumer integration tests

- [ ] Add test: build_agent() uses create_model_with_fallback()
- [ ] Add regression test: existing string-model behavior with no fallback

## P2: Documentation

- [ ] Document streaming compatibility boundary in _StreamingResponsesModel docstring
- [ ] Document fallback chain precedence in create_model_with_fallback() docstring

## Verification

- [ ] Run `uv run pytest tests/ -q` — all tests pass
- [ ] Run `uv run ruff check src/ tests/` — clean
- [ ] Run `uv run mypy src/agent_core/ --strict` — clean
