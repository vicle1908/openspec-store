## Purpose

This specification defines requirements for Harness Integration.

## Requirements

### Requirement: AgentConfig harness fields

`AgentConfig` SHALL accept typed `capabilities` and `toolsets` sequences as the primary Harness integration surface. It MAY accept the legacy per-capability dictionary fields only through the documented compatibility adapter during the deprecation window.

#### Scenario: Typed default config

- **WHEN** `AgentConfig(model=...)` is created without capabilities or toolsets
- **THEN** no optional Harness capabilities SHALL be added
- **AND** TDT mandatory policy capabilities SHALL remain explicit

#### Scenario: Typed capabilities populated

- **WHEN** `AgentConfig` receives official Harness capability instances
- **THEN** `AgentRuntime` SHALL pass them to Pydantic AI unchanged

#### Scenario: Typed toolsets populated

- **WHEN** `AgentConfig` receives official toolset instances
- **THEN** `AgentRuntime` SHALL compose them without converting them to individual functions

#### Scenario: Legacy field used

- **WHEN** a supported legacy context-compaction, guardrail, step-persistence, subagent, planning, repo-context, output-overflow, cache-monitoring, limit-warning, docs-access, DynamicWorkflow, filesystem, shell, or durability dictionary is used during the compatibility window
- **THEN** the compatibility adapter SHALL construct the official capability
- **AND** it SHALL emit a migration warning

### Requirement: AgentRuntime harness wiring

`AgentRuntime.__init__()` SHALL compose pre-built official capabilities and toolsets. Generic upstream capability construction SHALL remain in upstream libraries or narrow public TDT policy factories, not in an exhaustive runtime switch over feature keys.

#### Scenario: Capability passthrough

- **WHEN** a pre-built Harness capability is supplied
- **THEN** `AgentRuntime` SHALL preserve its type, identity, ordering, stable ID, description, deferred-loading setting, and constructor policy

#### Scenario: New upstream capability

- **WHEN** a future public Harness capability satisfies the supported capability protocol
- **THEN** a consumer SHALL be able to compose it without modifying `_build_harness_capabilities`

#### Scenario: TDT secure-profile factory

- **WHEN** a TDT factory constructs a commonly used capability profile
- **THEN** that factory SHALL expose every policy decision it owns
- **AND** it SHALL return public upstream capability objects

#### Scenario: No private imports

- **WHEN** capabilities or stores are constructed
- **THEN** only documented public upstream modules SHALL be imported


### Requirement: Capability authority profiles

The system SHALL classify optional capabilities by authority and SHALL require explicit activation for capabilities that can mutate files, execute commands/code, access external networks, or author runtime behavior.

#### Scenario: Read-only capability

- **WHEN** a consumer enables a read-only compaction or instrumentation capability
- **THEN** it SHALL not gain filesystem, shell, code, or network authority

#### Scenario: Mutating capability

- **WHEN** a consumer enables a mutating/high-authority capability
- **THEN** it SHALL provide bounded roots/allowlists, finite limits, and audit configuration
