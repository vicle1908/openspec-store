## Purpose

This specification defines requirements for Orchestration Command Api.

## Requirements

### Requirement: Native LangGraph Command authority

Supported workflow nodes SHALL use native LangGraph `Command` for combined state updates and routing. `agent-core` SHALL not maintain a second command semantic model after the migration window.

#### Scenario: State update and goto

- **WHEN** a node returns `Command(update=..., goto=...)`
- **THEN** LangGraph SHALL apply the update and route to the specified node

#### Scenario: Resume command

- **WHEN** a paused workflow receives an authorized human response
- **THEN** it SHALL resume through the native interrupt/command mechanism
- **AND** the response SHALL be associated with the correct thread and interrupt

#### Scenario: Invalid target

- **WHEN** a command targets an invalid node
- **THEN** graph validation or execution SHALL report the invalid target without wrapper translation

### Requirement: CommandResult compatibility migration

Legacy `CommandResult` handlers SHALL be supported through an isolated adapter for a documented migration window.

#### Scenario: Legacy handler

- **WHEN** a legacy handler returns `CommandResult`
- **THEN** the adapter SHALL produce an equivalent native `Command`
- **AND** it SHALL emit a deprecation warning containing the native replacement

#### Scenario: New workflow

- **WHEN** a new workflow is created
- **THEN** it SHALL use native `Command`
- **AND** it SHALL not depend on the compatibility adapter
