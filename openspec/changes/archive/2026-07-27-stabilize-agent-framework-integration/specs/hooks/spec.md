## ADDED Requirements

### Requirement: Hook tool filters are enforced

`HookRegistry` SHALL evaluate a registration's `tool_filter` for tool lifecycle points before invoking that hook.

#### Scenario: Matching tool

- **WHEN** a hook is registered with `tool_filter=["write_doc"]`
- **AND** the active tool is `write_doc`
- **THEN** the hook SHALL execute

#### Scenario: Non-matching tool

- **WHEN** a hook is registered with `tool_filter=["write_doc"]`
- **AND** the active tool is `read_doc`
- **THEN** the hook SHALL not execute

#### Scenario: Unfiltered hook

- **WHEN** a tool hook has no `tool_filter`
- **THEN** it SHALL execute for every tool at that hook point

### Requirement: Logical lifecycle events are delivered once

For one agent run, model request, or tool execution, each registered logical lifecycle hook SHALL be delivered once per applicable phase unless the hook is explicitly registered more than once.

#### Scenario: Run completion

- **WHEN** one `BaseAgent.run` completes
- **THEN** each registered RUN after-hook SHALL be called exactly once
- **AND** metric and cost counters SHALL increment once

#### Scenario: Model and tool lifecycle

- **WHEN** a run performs one model request and one tool execution
- **THEN** before/after hooks for each event SHALL be delivered exactly once

#### Scenario: Hook error

- **WHEN** a hook raises an error
- **THEN** the configured error-handling policy SHALL run once
- **AND** duplicate outer dispatch SHALL not retry the hook implicitly
