## REMOVED Requirements

### Requirement: Context compaction documentation

**Reason**: The requirement documents removed dictionary fields and strategies rather than the current typed public composition.

**Migration**: Document the typed capability path, explicit defaults, and public behavioral examples.

### Requirement: Guardrails documentation

**Reason**: The requirement documents an obsolete `guardrails` dictionary contract and does not describe production ToolGuardrail composition.

**Migration**: Document Input/OutputGuardrail and ToolGuardrail construction, mode boundaries, containment, approval, and redaction.

### Requirement: Step persistence documentation

**Reason**: The requirement documents obsolete dictionary stores and does not describe caller-owned shared history.

**Migration**: Document typed StepPersistence and ConversationSearch composition using one explicit snapshot source.

## ADDED Requirements

### Requirement: Harness documentation reflects the public typed contract

The harness integration guide SHALL document only capabilities and extras that are available through the public typed composition boundary, including their default/opt-in behavior, module paths, dependency ownership, and failure conditions.

#### Scenario: Capability omitted

- **WHEN** a developer reads the guide for an optional harness capability
- **THEN** the guide SHALL state that omission does not silently enable it
- **AND** the example SHALL use the supported public capability composition path

#### Scenario: Unsupported configuration

- **WHEN** a documented configuration key cannot be materialized by public construction
- **THEN** the key SHALL be removed or documented as rejected
- **AND** the guide SHALL not promise ignored or silently degraded behavior

### Requirement: Harness documentation covers consumer boundaries

The guide SHALL distinguish agent-core capability ownership, docs-sync approval/containment ownership, agent-harness read-only consumption, and observability ownership.

#### Scenario: Docs-sync write path

- **WHEN** a developer follows the docs-sync guardrail example
- **THEN** it SHALL show bounded ToolGuardrail plus independent containment and approval
- **AND** it SHALL not imply that a guardrail alone grants write authority

#### Scenario: Shared conversation history

- **WHEN** a developer follows the ConversationSearch example
- **THEN** it SHALL pass the same caller-owned persistence source used by step continuation
- **AND** it SHALL explain process-local versus restart-safe stores

#### Scenario: DynamicWorkflow dependency documentation

- **WHEN** the guide documents DynamicWorkflow support
- **THEN** it SHALL identify agent-core as the optional-extra owner
- **AND** the documented Monty version SHALL match the frozen harness extra requirement and lockfile
