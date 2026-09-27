# Spec Delta: shb-agent-runtime

## Purpose
Modernizes the `shb-agent-core` runtime from simulated keyword matching to production Pydantic AI v2 (`pydantic-ai>=2.51.0`) with real model gateway connectivity, provider fallback, type-safe tool validation, and hermetic `TestModel` testing.

## MODIFIED Requirements

### Requirement: Autonomous ReAct Execution Engine
The `shb-agent-core` runtime SHALL execute autonomous ReAct cycles using Pydantic AI v2 `Agent` with typed dependencies (`RunContext[ShbAgentDeps]`), dynamic system prompts, schema-validated parameters, and typed structured output (`ShbAgentOutput`).

#### Scenario: Tool call execution within loop
- **WHEN** an agent evaluates a prompt requiring domain data (such as account balance or transaction status)
- **THEN** the execution engine invokes the registered `@agent.tool` function with validated typed arguments, processes the returned result, and produces a structured `ShbAgentOutput` completion

#### Scenario: Model retry on tool validation error
- **WHEN** the model generates arguments that fail Pydantic model validation on a registered tool
- **THEN** Pydantic AI SHALL trigger a model retry with validation feedback to correct the argument shape

### Requirement: Provider-Agnostic Model Resolution
The `shb-agent-core` runtime SHALL resolve model endpoints dynamically via OpenAI-compatible gateways (OmniRoute `http://127.0.0.1:20128/v1` or direct providers) supporting primary and fallback model chains with automated connection failure failover.

#### Scenario: Gateway connection and model invocation
- **WHEN** an agent session is initialized with default settings
- **THEN** the model resolver SHALL construct an `OpenAIModel` configured to query `SHB_MODEL_GATEWAY_URL` using `SHB_DEFAULT_MODEL`

#### Scenario: Fallback model invocation on provider error
- **WHEN** the primary model endpoint returns a connection timeout, rate limit, or 5xx error
- **THEN** the model chain SHALL sequentially fail over to `SHB_FALLBACK_MODEL` without terminating the agent session

## ADDED Requirements

### Requirement: Typed Tool Contracts and Validation
Every registered tool in `shb_agent.tools` SHALL declare typed Pydantic models for inputs and outputs, exposing JSON Schemas for model tool-calling protocols.

#### Scenario: Parameter validation rejection
- **WHEN** an invocation passes invalid data types or malformed account numbers to a tool
- **THEN** the tool validation layer SHALL reject the call before executing the underlying business function

#### Scenario: Dynamic context injection
- **WHEN** a tool requires internal services or configuration
- **THEN** the tool SHALL access `ctx.deps` (`ShbAgentDeps`) directly from the Pydantic AI `RunContext` without relying on global singletons

### Requirement: Hermetic Evaluation with TestModel
The `shb-agent-core` test suite SHALL support deterministic offline testing using `pydantic_ai.models.test.TestModel` without network calls or API costs.

#### Scenario: Zero-cost deterministic testing
- **WHEN** unit tests execute against `ShbAgent` configured with `TestModel`
- **THEN** the test suite executes hermetically without network egress and verifies agent control flow and tool selection

#### Scenario: Mocked tool execution in test harness
- **WHEN** `TestModel` is configured with predefined tool call responses
- **THEN** the agent correctly transitions to the synthesis phase and asserts expected output structures
