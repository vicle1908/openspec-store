# shb-agent-runtime Specification Delta

## MODIFIED Requirements

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
