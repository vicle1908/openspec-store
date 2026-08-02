## ADDED Requirements

### Requirement: DynamicWorkflow dependency compatibility

Every repository enabling DynamicWorkflow SHALL install a Harness/Monty combination satisfying the Harness package metadata and SHALL prove that the capability imports and executes.

#### Scenario: Import preflight

- **WHEN** DynamicWorkflow is enabled
- **THEN** the preflight SHALL import `DynamicWorkflow`
- **AND** it SHALL report the installed Harness and Monty versions

#### Scenario: Incompatible Monty version

- **WHEN** the installed Monty version does not satisfy Harness requirements
- **THEN** startup SHALL fail with an actionable `uv` remediation
- **AND** the workflow SHALL not fall back to an ordinary agent

### Requirement: Functional workflow agents

Each DynamicWorkflow catalog agent SHALL have the instructions, tools, structured output, and dependencies required for its declared operation.

#### Scenario: Scanner agent

- **WHEN** the scanner is advertised as running GitNexus, Graphify, and repository scans
- **THEN** it SHALL receive the corresponding read-only tools
- **AND** an integration test SHALL observe a structured scan result

#### Scenario: Host-controlled persistence

- **WHEN** the model-authored workflow produces discovery results
- **THEN** no DynamicWorkflow catalog agent SHALL receive a state-write tool
- **AND** any subsequent persistence SHALL run through the deterministic host
  path under the consumer containment policy

### Requirement: Bounded DynamicWorkflow execution

DynamicWorkflow SHALL configure finite host-enforced limits for agent calls, retries, subagent usage, and sandbox resources.

#### Scenario: Resource configuration

- **WHEN** the docs-sync adaptive workflow is constructed
- **THEN** `max_agent_calls`, `max_retries`, `sub_agent_usage_limits`, and `WorkflowResourceLimits` SHALL be finite

#### Scenario: Limit reached

- **WHEN** a workflow exceeds a configured call or resource limit
- **THEN** execution SHALL stop with a structured failure
- **AND** no unbounded fallback execution SHALL begin

### Requirement: DynamicWorkflow remains optional

Deterministic discovery, file scanning, state persistence, and reporting SHALL have a non-DynamicWorkflow path.

#### Scenario: Adaptive workflow disabled

- **WHEN** DynamicWorkflow is not configured
- **THEN** the deterministic pipeline SHALL run normally
- **AND** the system SHALL not claim that model-authored orchestration executed
