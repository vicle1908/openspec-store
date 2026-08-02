## Purpose

This specification defines requirements for Agent Yaml Config.

## Requirements

### Requirement: Full AgentSpec fidelity

Agent files SHALL be parsed through the official `AgentSpec`/`Agent.from_file` or `Agent.from_spec` contract, and all supported fields SHALL be preserved unless an explicit TDT policy rejects them.

#### Scenario: Complete spec load

- **WHEN** an agent file declares name, description, instructions, model settings, retries, end strategy, tool timeout, metadata, dependency schema, output schema, and capabilities
- **THEN** the loaded agent SHALL preserve those values

#### Scenario: Tools and toolsets

- **WHEN** a consumer needs tools not represented as an `AgentSpec` field
- **THEN** they SHALL be supplied through the documented registry/toolset composition input
- **AND** the loader SHALL not invent or probe a nonexistent `AgentSpec.tools` field

#### Scenario: Custom capability type

- **WHEN** an agent file contains a registered TDT or Harness custom capability
- **THEN** the loader SHALL use the official custom-capability registration mechanism

#### Scenario: Non-serializable live capability

- **WHEN** a capability reports no serialization name, including Harness `DynamicWorkflow` with live agent objects
- **THEN** it SHALL be supplied through the typed code-composition input
- **AND** the loader SHALL not invent a YAML representation for it

#### Scenario: Unknown capability

- **WHEN** an agent file requests an unregistered capability
- **THEN** loading SHALL fail with its serialization name
- **AND** the capability SHALL not be silently skipped

### Requirement: Configuration security policy

File-based agent configuration SHALL not bypass TDT authority policy.

#### Scenario: High-authority capability in file

- **WHEN** an agent file requests filesystem, shell, code execution, runtime authoring, or network authority
- **THEN** an explicit consumer policy SHALL authorize and bound it before construction

#### Scenario: Secret values

- **WHEN** an agent file is loaded
- **THEN** credentials SHALL continue to resolve from `TDT_HOME`
- **AND** secrets SHALL not be embedded in the agent file or diagnostic output
