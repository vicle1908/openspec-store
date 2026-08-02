# Component Interaction

## Purpose

Define the interaction patterns between harness sub-components including stage interfaces, event/message passing, configuration and state flow, error propagation, observability, and testing boundaries.

## Requirements

### Requirement: Stage interface contract

Every stage SHALL define a typed interface describing its inputs, outputs, and possible failures. The runtime SHALL dispatch to stages exclusively through this interface. Stages SHALL not call each other directly.

#### Scenario: Stage implements interface

- **WHEN** a stage is registered
- **THEN** it SHALL expose an interface declaring expected inputs, produced outputs, and failure modes
- **AND** the runtime SHALL validate registration against the interface

#### Scenario: Direct stage call

- **WHEN** stage A attempts to call stage B directly
- **THEN** the system SHALL block the call and require dispatch through the runtime

### Requirement: Event and message passing

Stages SHALL communicate through a typed event or message bus. Events SHALL be immutable once published. Subscriptions SHALL be typed to prevent schema drift.

#### Scenario: Event publication

- **WHEN** a stage emits an event
- **THEN** the event SHALL be immutable, typed, and delivered to all current subscribers

#### Scenario: Subscription type safety

- **WHEN** a subscriber registers for an event type
- **THEN** the system SHALL validate the subscription matches the event schema

### Requirement: Configuration and state flow

Shared configuration SHALL be injected at workflow initialization and remain immutable during a run. State mutations SHALL occur only through explicit state transition messages.

#### Scenario: Immutable configuration

- **WHEN** a workflow run starts
- **THEN** configuration SHALL be frozen and shared across all stages
- **AND** no stage SHALL mutate configuration during the run

#### Scenario: State transition

- **WHEN** a stage needs to update shared state
- **THEN** it SHALL emit a state transition message
- **AND** the runtime SHALL apply the transition atomically

### Requirement: Error propagation

Component errors SHALL propagate through a typed error channel. Errors SHALL include component identity, error kind, and context. Retries SHALL be bounded and configurable.

#### Scenario: Error propagation

- **WHEN** a component encounters an error
- **THEN** it SHALL emit a typed error with component identity, kind, and context
- **AND** the runtime SHALL route it to the error handler

#### Scenario: Retry exhaustion

- **WHEN** retries are exhausted
- **THEN** the system SHALL surface a terminal error with full context

### Requirement: Observability across components

Cross-component traces SHALL carry correlation identifiers. Metrics SHALL be namespaced per component. Logs SHALL include component identity.

#### Scenario: Correlated trace

- **WHEN** a request crosses component boundaries
- **THEN** the correlation ID SHALL be preserved across all components

### Requirement: Testing boundaries

Components SHALL be testable in isolation through dependency injection or interface stubs. Integration tests SHALL verify component contracts.

#### Scenario: Unit test isolation

- **WHEN** a component is unit tested
- **THEN** all dependencies SHALL be stubbed through interfaces
