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

The harness integration guide SHALL document only capabilities and extras that are available through the public typed composition boundary, including their default/opt-in behavior, canonical module paths, dependency ownership, and failure conditions. Every representative code snippet SHALL import and construct against the frozen `pydantic-ai==2.32.0`, `pydantic-ai-harness==0.23.0`, and resolved dependency tuple without deprecated aliases or unsupported constructor values.

#### Scenario: Capability omitted

- **WHEN** a developer reads the guide for an optional harness capability
- **THEN** the guide SHALL state that omission does not silently enable it
- **AND** the example SHALL use the supported public capability composition path

#### Scenario: Unsupported configuration

- **WHEN** a documented configuration key cannot be materialized by public construction
- **THEN** the key SHALL be removed or documented as rejected
- **AND** the guide SHALL not promise ignored or silently degraded behavior

#### Scenario: Executable canonical example

- **WHEN** the guide shows a capability construction example
- **THEN** an automated documentation gate SHALL import the canonical public symbol and construct the example against the frozen tuple
- **AND** required arguments, enum values, and renamed classes such as `SlidingWindowCompaction` SHALL match the installed public API

### Requirement: Harness documentation covers consumer boundaries

The guide SHALL distinguish agent-core capability ownership, docs-sync approval/containment ownership, agent-harness read-only consumption, and observability ownership.

#### Scenario: Docs-sync write path

- **WHEN** a developer follows the docs-sync guardrail example
- **THEN** it SHALL show bounded ToolGuardrail plus independent containment and approval
- **AND** it SHALL map `write_doc.path` and `sync_spec.main_path` to the canonical write resolver and `shell_execute.command` to the shell guard when that tool is visible
- **AND** it SHALL not imply that a guardrail alone grants write authority

#### Scenario: Shared conversation history

- **WHEN** a developer follows the ConversationSearch example
- **THEN** it SHALL pass the same caller-owned persistence source used by step continuation
- **AND** shared-store examples SHALL use conversation-scoped search with a stable conversation identity and SHALL not expose another conversation's history
- **AND** it SHALL explain process-local versus restart-safe stores

#### Scenario: DynamicWorkflow dependency documentation

- **WHEN** the guide documents DynamicWorkflow support
- **THEN** it SHALL identify agent-core as the optional-extra owner
- **AND** it SHALL show the public `build_agent(..., capabilities=[DynamicWorkflow(...)])` seam and its bounded runtime-authoring authority requirement
- **AND** the documented Monty version SHALL match the frozen harness extra requirement and lockfile
