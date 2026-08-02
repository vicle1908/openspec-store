# Hook System Specification

## Purpose

Define the re-implementation of the `HookRegistry` facade and four built-in hook packs using pydantic-ai v2 hooks.

## ADDED Requirements

### Requirement: HK-1: HookAdapter

`HookAdapter` SHALL be implemented in `_ai/hooks.py`.

`HookAdapter` SHALL wire the existing `HookRegistry` facade to pydantic-ai v2 hooks.

`HookAdapter` SHALL map `HookPoint` values to pydantic-ai lifecycle events:

- `HookPoint.RUN` → agent start/end events
- `HookPoint.MODEL_REQUEST` → model request/response events
- `HookPoint.TOOL_EXECUTE` → tool call events

#### Scenario: HookAdapter fires before_run hook

- **GIVEN** `HookRegistry` has a `before_run` callback registered
- **AND** `HookAdapter` is wired to the pydantic-ai agent
- **WHEN** `agent.run()` is called
- **THEN** the `before_run` callback fires before the agent starts

### Requirement: HK-2: otel_metrics Pack

`otel_metrics` SHALL record via pydantic-ai hooks:

- Histogram: `agent_core.agent.run.duration` (wall-clock ms)
- Histogram: `agent_core.agent.run.iterations` (ReAct loop iterations)
- Counter: `agent_core.agent.tool.calls` (tool execution count)

`OTelMetricsState` SHALL be unchanged.

#### Scenario: otel_metrics records run duration

- **GIVEN** `otel_metrics` pack is registered
- **WHEN** an agent run completes
- **THEN** `OTelMetricsState.run_durations_ms` contains the wall-clock duration

### Requirement: HK-3: structured_audit Pack

`structured_audit` SHALL record an `AuditRecord` for each tool execution with:

- `agent_name`, `tool_name`, `args` (redacted), `success`, `duration_ms`
- Argument redaction for keys containing: secret, token, password, authorization, key

`AuditRecord` and `StructuredAuditState` SHALL be unchanged.

#### Scenario: structured_audit redacts sensitive args

- **GIVEN** `structured_audit` pack is registered
- **WHEN** `shell_execute(command="curl -H 'Authorization: Bearer secret' http://api")` is called
- **THEN** `AuditRecord.args` contains `'Authorization': '[REDACTED]'`

### Requirement: HK-4: approval_gate Pack

`approval_gate` SHALL block execution of tools flagged `requires_approval` until approved via the configured callback.

`ApprovalGateState` SHALL be unchanged.

#### Scenario: approval_gate blocks dangerous tool

- **GIVEN** `approval_gate(dangerous_tools=["shell_execute"])` is registered
- **AND** the approval callback returns `False`
- **WHEN** the model calls `shell_execute(command="rm -rf /")`
- **THEN** the tool is not executed
- **AND** `ApprovalGateState.rejections` is incremented

### Requirement: HK-5: cost_tracker Pack

`cost_tracker` SHALL accumulate:

- `input_tokens`, `output_tokens`, `total_tokens`, `total_cost_usd`

`cost_tracker` SHALL read usage from `pydantic_ai.usage.RunUsage` returned by the agent.

`CostTrackerState` SHALL be unchanged.

#### Scenario: cost_tracker accumulates usage

- **GIVEN** `cost_tracker` pack is registered
- **WHEN** an agent run completes with `RunUsage(prompt_tokens=100, completion_tokens=50)`
- **THEN** `CostTrackerState.input_tokens == 100`
- **AND** `CostTrackerState.output_tokens == 50`

## ADDED Requirements

### Requirement: HK-6: Public Hook API Unchanged

`HookRegistry`, `HookPoint`, `HookPhase`, and the four pack factory functions SHALL have their public signatures unchanged.

Consumer code using these APIs SHALL require no modifications.

#### Scenario: HookRegistry.register signature unchanged

- **GIVEN** existing consumer code calls `registry.register(HookPoint.RUN, HookPhase.BEFORE, callback)`
- **WHEN** the code is run against the migrated `agent-core`
- **THEN** the call succeeds without modification
