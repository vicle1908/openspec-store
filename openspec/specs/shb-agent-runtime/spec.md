# shb-agent-runtime Specification

## Purpose
Defines the autonomous agent runtime, multi-provider model resolution, tool registries, and execution loops for the Saigon - Hanoi Bank (SHB) agent ecosystem.

## Requirements

### Requirement: Provider-Agnostic Model Resolution
The `shb-agent-core` runtime SHALL resolve model endpoints dynamically via OpenAI-compatible gateways (OmniRoute `http://127.0.0.1:20128/v1` or direct providers) supporting primary and fallback model chains with automated connection failure failover.

#### Scenario: Gateway connection and model invocation
- **WHEN** an agent session is initialized with default settings
- **THEN** the model resolver SHALL construct an `OpenAIModel` configured to query `SHB_MODEL_GATEWAY_URL` using `SHB_DEFAULT_MODEL`

#### Scenario: Fallback model invocation on provider error
- **WHEN** the primary model endpoint returns a connection timeout, rate limit, or 5xx error
- **THEN** the model chain SHALL sequentially fail over to `SHB_FALLBACK_MODEL` without terminating the agent session

### Requirement: Autonomous ReAct Execution Engine
The `shb-agent-core` runtime SHALL execute autonomous ReAct cycles using Pydantic AI v2 `Agent` with typed dependencies (`RunContext[ShbAgentDeps]`), dynamic system prompts, schema-validated parameters, and typed structured output (`ShbAgentOutput`) backed by Pydantic AI `>=2.53.0`.

#### Scenario: Tool call execution within loop
- **WHEN** an agent evaluates a prompt requiring domain data (such as account balance or transaction status)
- **THEN** the execution engine invokes the registered `@agent.tool` function with validated typed arguments, processes the returned result, and produces a structured `ShbAgentOutput` completion

#### Scenario: Model retry on tool validation error
- **WHEN** the model generates arguments that fail Pydantic model validation on a registered tool
- **THEN** Pydantic AI SHALL trigger a model retry with validation feedback to correct the argument shape

#### Scenario: Dynamic context injection with upgraded runtime
- **WHEN** dynamic system prompts or tools evaluate runtime state
- **THEN** Pydantic AI 2.53.0 SHALL refresh dependencies and evaluate system prompt closures without state leakage

### Requirement: Command-Line Interface Entrypoint
The package SHALL provide an executable command-line interface named `shb-agent` allowing operators to run interactive sessions, batch prompt evaluations, and tool inspection workflows.

#### Scenario: Interactive session launch
- **WHEN** an operator executes `shb-agent run --interactive`
- **THEN** the CLI initializes the agent session using `~/.shb/.env` configurations and accepts terminal input

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
