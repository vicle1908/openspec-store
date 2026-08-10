## ADDED Requirements

### Requirement: Streaming Responses model aggregation boundary

When a configured provider returns SSE streams for non-stream requests, the system SHALL aggregate the stream into a standard ModelResponse. The aggregation SHALL preserve text output, tool calls, usage metadata, and finish reason from the completion event.

#### Scenario: SSE stream aggregation

- **GIVEN** a provider configured with `api_mode: codex_responses`
- **AND** the provider returns SSE streams for non-stream requests
- **WHEN** a model request is made
- **THEN** the system SHALL aggregate the stream into a single ModelResponse
- **AND** text output, tool calls, usage, and finish reason SHALL be preserved

#### Scenario: Empty completion output normalization

- **GIVEN** a provider that returns `response.output: null` on completion
- **WHEN** the stream is aggregated
- **THEN** the null output SHALL be normalized to an empty list
- **AND** the ModelResponse SHALL be returned without error

#### Scenario: Upstream exception propagated

- **GIVEN** an SSE stream that raises an exception during iteration
- **WHEN** the streaming model processes the event
- **THEN** the exception SHALL be propagated to the caller without masking

### Requirement: Config-driven fallback chain construction

The `create_model_with_fallback()` function SHALL read the TDT config for fallback model identifiers. When fallbacks are configured, it SHALL construct a FallbackModel. The function SHALL resolve model names at construction time but SHALL NOT make network calls or validate API credentials until request time.

#### Scenario: Config-driven fallback

- **GIVEN** `~/.tdt/config.yaml` has `model.fallback: ["provider:model-b"]`
- **WHEN** `create_model_with_fallback("provider:model-a")` is called
- **THEN** a FallbackModel SHALL be returned with primary and fallback

#### Scenario: No fallback configured

- **GIVEN** `~/.tdt/config.yaml` has no `model.fallback` key
- **WHEN** `create_model_with_fallback("provider:model-a")` is called
- **THEN** a single model SHALL be returned via `create_model()`

#### Scenario: Explicit Model instance bypasses fallback

- **GIVEN** a `Model` instance is passed to `create_model_with_fallback()`
- **WHEN** the function is called
- **THEN** the instance SHALL be returned as-is without config lookup
