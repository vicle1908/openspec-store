# Tasks: agent-core-model-resolution-hardening

## P1: Streaming model tests

- [x] [historical] Add test: stream aggregates text output into ModelResponse
- [x] [historical] Add test: stream handles empty/null completion output
- [x] [historical] Add test: stream preserves tool calls
- [x] [historical] Add test: stream propagates usage metadata
- [x] [historical] Add test: stream propagates finish reason
- [x] [historical] Add test: stream handles malformed/non-ResponseCompletedEvent items
- [x] [historical] Add test: stream propagates upstream exception
- [x] [historical] Add test: request() delegates to request_stream() + get()

## P1: Fallback chain tests

- [x] [historical] Add test: no fallback config returns single model
- [x] [historical] Add test: single fallback returns FallbackModel
- [x] [historical] Add test: multiple fallbacks returns FallbackModel
- [x] [historical] Add test: explicit Model instance bypasses fallback construction
- [x] [historical] Add test: empty fallback list returns single model

## P2: Consumer integration tests

- [x] [historical] Add test: build_agent() uses create_model_with_fallback()
- [x] [historical] Add regression test: existing string-model behavior with no fallback

## P2: Documentation

- [x] [historical] Document streaming compatibility boundary in _StreamingResponsesModel docstring
- [x] [historical] Document fallback chain precedence in create_model_with_fallback() docstring

## Verification

- [x] [historical] Run `uv run pytest tests/ -q` — all tests pass
- [x] [historical] Run `uv run ruff check src/ tests/` — clean
- [x] [historical] Run `uv run mypy src/agent_core/ --strict` — clean


---

> **Historical record:** This change was archived with 20 incomplete task(s) (0/20 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
