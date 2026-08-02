## Purpose

This specification defines requirements for Dynamic Workflow.

## Requirements

### Requirement: Full official DynamicWorkflow configuration

The public composition API SHALL allow consumers to configure the supported DynamicWorkflow agent catalog, tool name, maximum calls, retries, usage forwarding, model inheritance, subagent usage limits, sandbox resource limits, stable ID, description, and deferred loading without dropping arguments.

#### Scenario: Bounded workflow composition

- **WHEN** a consumer composes DynamicWorkflow
- **THEN** its full supported usage/resource policy SHALL reach the upstream capability unchanged

#### Scenario: Deferred loading

- **WHEN** DynamicWorkflow has a stable ID and `defer_loading=true`
- **THEN** the orchestration tool SHALL remain out of the prompt until loaded through the supported capability mechanism

#### Scenario: Future upstream option

- **WHEN** a future public option is configured on a pre-built capability
- **THEN** `agent-core` SHALL pass it through without a framework code change

### Requirement: Adaptive workflow boundary

DynamicWorkflow SHALL be used only where model-authored orchestration provides material value and SHALL not replace deterministic workflow steps.

#### Scenario: Deterministic operation

- **WHEN** the operation is file discovery, state persistence, link validation, or report formatting
- **THEN** it SHALL execute in deterministic code or a static LangGraph node

#### Scenario: Adaptive operation

- **WHEN** the operation requires bounded model-selected research, classification, comparison, or synthesis
- **THEN** DynamicWorkflow MAY be selected explicitly
- **AND** it SHALL use structured outputs and finite authority
