# agent-core-components Specification

## Purpose
Defines the core components of agent-core: scheduler, tool registry, authority policy, identity resolution, and SDK composition.
## Requirements
### Requirement: Scheduler engine

The scheduler SHALL orchestrate workflow execution with durable execution via DBOS.

#### Scenario: Cron-based scheduling

- **WHEN** the scheduler is configured with a cron expression
- **THEN** it SHALL trigger workflows at the specified intervals
- **AND** execution SHALL be durable (survive restarts)

#### Scenario: Ticket filtering

- **WHEN** new tickets are available
- **THEN** the scheduler SHALL filter by eligibility rules
- **AND** sort by priority before creating workflow runs

### Requirement: Tool registry

The tool registry SHALL manage all available tools and their authorization policies.

#### Scenario: Tool registration

- **WHEN** a tool is registered
- **THEN** it SHALL be classified by authority class (read-only, shell, filesystem-write, network, code-execution)
- **AND** visibility SHALL be controlled by policy

#### Scenario: Tool authorization

- **WHEN** a tool call is made
- **THEN** the registry SHALL check if the tool is registered
- **AND** check if it is visible in the current policy
- **AND** check authority class requirements

### Requirement: Authority policy

The authority policy SHALL enforce least-privilege access across all tool operations.

#### Scenario: Policy intersection

- **WHEN** multiple policies apply (compatibility, consumer, stage)
- **THEN** the effective policy SHALL be the intersection (narrowest grant)
- **AND** no escalation via aliases or duplicates

#### Scenario: Separation of duties

- **WHEN** a high-risk operation is requested (shell, filesystem-write, network, code-execution)
- **THEN** it SHALL require a distinct approver
- **AND** self-approval SHALL be denied

### Requirement: ConfigFileResolver

The ConfigFileResolver SHALL resolve identity via TDT_ACTOR_ID environment variable.

#### Scenario: Identity resolution

- **WHEN** TDT_ACTOR_ID is set
- **THEN** the resolver SHALL return a valid AuthenticatedSubject with HIGH assurance
- **AND** the subject SHALL be normalized as `tdt.subject.v1:config-file:<actor_id>`

#### Scenario: Identity unavailable

- **WHEN** TDT_ACTOR_ID is not set
- **THEN** the resolver SHALL return UNAVAILABLE_PROVIDER
- **AND** the workflow SHALL fail closed

### Requirement: SDK composition

The SDK SHALL provide declarative workflow definition.

#### Scenario: Workflow definition

- **WHEN** a workflow is defined using the SDK
- **THEN** it SHALL specify stages, gates, and toolsets
- **AND** the definition SHALL be validated before execution

