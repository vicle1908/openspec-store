# shb-agent-runtime Specification

## Purpose
Defines the autonomous agent runtime, multi-provider model resolution, tool registries, and execution loops for the Saigon - Hanoi Bank (SHB) agent ecosystem.

## Requirements

### Requirement: Provider-Agnostic Model Resolution

The `shb-agent-core` runtime SHALL resolve model endpoints dynamically via OpenAI-compatible gateways (OmniRoute `http://127.0.0.1:20128/v1` or direct providers) supporting primary and fallback model chains with automated connection failure failover, defaulting primary model resolution to `gemini-3.8-flash-high`.

#### Scenario: Gateway connection and model invocation
- **WHEN** an agent session is initialized with default settings
- **THEN** the model resolver SHALL construct a model instance configured to query `SHB_MODEL_GATEWAY_URL` using `gemini-3.8-flash-high` as `SHB_DEFAULT_MODEL`

#### Scenario: Fallback model invocation on provider error
- **WHEN** the primary model endpoint returns a connection timeout, rate limit, or 5xx error
- **THEN** the model chain SHALL sequentially fail over to `SHB_FALLBACK_MODEL` without terminating the agent session

### Requirement: Autonomous ReAct Execution Engine
The `shb-agent-core` runtime SHALL execute autonomous ReAct cycles using Pydantic AI v2 `Agent` with typed dependencies (`RunContext[ShbAgentDeps]`), dynamic system prompts, schema-validated parameters, and typed structured output (`ShbAgentOutput`) backed by Pydantic AI `>=2.53.0`, dynamically registering all domain banking tools, supporting `ModelRetry` parameter correction, and providing streaming response generation.

#### Scenario: Tool call execution within loop
- **WHEN** an agent evaluates a prompt requiring domain data (such as account balance or transaction status)
- **THEN** the execution engine invokes the registered `@agent.tool` function with validated typed arguments, processes the returned result, and produces a structured `ShbAgentOutput` completion

#### Scenario: Model retry on tool validation error
- **WHEN** the model generates arguments that fail Pydantic model validation on a registered tool
- **THEN** Pydantic AI SHALL trigger a model retry with validation feedback to correct the argument shape

#### Scenario: Dynamic context injection with upgraded runtime
- **WHEN** dynamic system prompts or tools evaluate runtime state
- **THEN** Pydantic AI 2.53.0 SHALL refresh dependencies and evaluate system prompt closures without state leakage

#### Scenario: Full domain toolset discovery and binding
- **WHEN** an agent instance initializes with dependencies
- **THEN** the execution engine SHALL bind all registered banking, VietQR, and biller tools directly to the agent tool surface

#### Scenario: Model retry on maker-checker authorization error
- **WHEN** a transfer exceeding 50,000,000 VND is initiated without a valid supervisor approval token
- **THEN** the domain tool SHALL raise a `ModelRetry` exception instructing the model to request supervisor authorization rather than aborting

#### Scenario: Streaming structured execution
- **WHEN** a client invokes `run_stream` or `run_stream_sync`
- **THEN** the agent SHALL yield incremental structured execution updates and token chunks

### Requirement: Command-Line Interface Entrypoint
The package SHALL provide an executable command-line interface named `shb-agent` allowing operators to run interactive sessions, batch prompt evaluations, and tool inspection workflows.

#### Scenario: Interactive session launch
- **WHEN** an operator executes `shb-agent run --interactive`
- **THEN** the CLI initializes the agent session using `~/.shb/.env` configurations and accepts terminal input

### Requirement: Typed Tool Contracts and Validation
Every registered tool in `shb_agent.tools` SHALL declare typed Pydantic models for inputs and outputs, exposing JSON Schemas for model tool-calling protocols and integrating with Pydantic AI `RunContext`.

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
