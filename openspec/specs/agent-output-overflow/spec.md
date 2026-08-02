# agent-output-overflow

## Purpose

Handles oversized tool outputs by applying configurable overflow actions (summarize, truncate, spill) based on token thresholds, with per-tool override support.

## Requirements

### Requirement: OverflowingToolOutput capability

When `AgentConfig.output_overflow` is set, `AgentRuntime` SHALL create an `OverflowingToolOutput` capability.

#### Scenario: Band-based overflow
- **WHEN** `output_overflow={"bands": [{"over": 1000, "action": "summarize"}]}`
- **THEN** `OverflowingToolOutput(bands=[Band(over=1000, action="summarize")])` SHALL be created

#### Scenario: Per-tool overflow config
- **WHEN** `output_overflow={"per_tool": {"shell_execute": [{"over": 500, "action": "truncate"}]}}`
- **THEN** per-tool bands SHALL be applied only to the specified tools

### Requirement: Overflow actions

Overflow SHALL support three actions: `summarize`, `truncate`, `spill`.

#### Scenario: Summarize action
- **WHEN** a tool output exceeds the `over` threshold with `action: "summarize"`
- **THEN** the output SHALL be summarized using the LLM and replaced with the summary

#### Scenario: Truncate action
- **WHEN** a tool output exceeds the `over` threshold with `action: "truncate"`
- **THEN** the output SHALL be truncated to the threshold

#### Scenario: Spill action
- **WHEN** a tool output exceeds the `over` threshold with `action: "spill"`
- **THEN** the output SHALL be written to disk and replaced with a file pointer

### Requirement: Backward compatibility

Agents without `output_overflow` config SHALL work unchanged.

#### Scenario: No overflow config
- **WHEN** `output_overflow` is `None`
- **THEN** no overflow capability SHALL be added
