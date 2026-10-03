# shb-agent-runtime Specification Delta

## MODIFIED Requirements

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

### Requirement: Typed Tool Contracts and Validation
Every registered tool in `shb_agent.tools` SHALL declare typed Pydantic models for inputs and outputs, exposing JSON Schemas for model tool-calling protocols and integrating with Pydantic AI `RunContext`.

#### Scenario: Parameter validation rejection
- **WHEN** an invocation passes invalid data types or malformed account numbers to a tool
- **THEN** the tool validation layer SHALL reject the call before executing the underlying business function

#### Scenario: Dynamic context injection
- **WHEN** a tool requires internal services or configuration
- **THEN** the tool SHALL access `ctx.deps` (`ShbAgentDeps`) directly from the Pydantic AI `RunContext` without relying on global singletons
