# Flavor Composition Specification

## Purpose

Define the migration of the custom `Flavor` dataclass composition system to map to pydantic-ai agent configuration.

## ADDED Requirements

### Requirement: FL-1: Flavor to Instructions Mapping

`BaseAgent._apply_flavors()` SHALL map `Flavor` to agent configuration.

`FlavorPrompt.content` strings SHALL be concatenated and appended to the agent's instructions via `AgentRuntime.append_instructions()`.

#### Scenario: Flavor prompts are concatenated

- **GIVEN** `Flavor(prompts=[FlavorPrompt(content="System prompt"), FlavorPrompt(content="Extra context")])`
- **WHEN** `_apply_flavors()` is called
- **THEN** `AgentRuntime.append_instructions()` is called with the concatenated string

### Requirement: FL-2: Flavor Tool Policy Mapping

`FlavorToolPolicy.allow` SHALL call `AgentRuntime.restrict_tools(allow=..., deny=[])`.

`FlavorToolPolicy.deny` SHALL call `AgentRuntime.restrict_tools(allow=[], deny=...)`.

#### Scenario: Flavor allow list restricts tools

- **GIVEN** `FlavorToolPolicy(allow=["read_file", "grep_search"])`
- **WHEN** `_apply_flavors()` is called
- **THEN** `AgentRuntime.restrict_tools(allow=["read_file", "grep_search"], deny=[])` is called

#### Scenario: Flavor deny list excludes tools

- **GIVEN** `FlavorToolPolicy(deny=["shell_execute", "write_file"])`
- **WHEN** `_apply_flavors()` is called
- **THEN** `AgentRuntime.restrict_tools(allow=[], deny=["shell_execute", "write_file"])` is called

### Requirement: FL-3: Flavor Defaults Mapping

`FlavorDefaults.max_iterations` SHALL set the agent's `max_iterations` parameter.

`FlavorDefaults.timeout_seconds` SHALL set the agent's `timeout_seconds` parameter.

#### Scenario: Flavor defaults override agent settings

- **GIVEN** `FlavorDefaults(max_iterations=15, timeout_seconds=180.0)`
- **WHEN** `_apply_flavors()` is called
- **THEN** the agent's effective `max_iterations` is 15
- **AND** the agent's effective `timeout_seconds` is 180.0

### Requirement: FL-4: merge_flavors Unchanged

`merge_flavors()` SHALL be unchanged — it composes `Flavor` objects as before.

The `Flavor`, `FlavorPrompt`, `FlavorToolPolicy`, `FlavorDefaults` dataclasses SHALL be unchanged.

#### Scenario: merge_flavors produces combined Flavor

- **GIVEN** two `Flavor` objects
- **WHEN** `merge_flavors([flavor1, flavor2])` is called
- **THEN** a combined `Flavor` with concatenated prompts and union tool policies is returned
