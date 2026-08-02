## Purpose

This specification defines requirements for Hooks.

## Requirements

### Requirement: Pydantic AI Hooks are lifecycle authority

The agent lifecycle SHALL be represented by one official Pydantic AI `Hooks` capability. TDT hook packs SHALL compose as callbacks on that authority rather than as a parallel lifecycle engine.

#### Scenario: Full lifecycle coverage

- **WHEN** consumers register supported callbacks
- **THEN** they SHALL be able to observe or wrap run, node, model, tool validation, tool execution, output validation, output processing, errors, deferred calls, and event streams according to the public Hooks contract

#### Scenario: Callback return values

- **WHEN** a supported callback modifies request context, validated arguments, output, or error recovery
- **THEN** the modification SHALL propagate according to the upstream protocol
- **AND** an adapter SHALL not discard it

#### Scenario: Exactly-once delivery

- **WHEN** one framework event occurs
- **THEN** one lifecycle authority SHALL deliver it
- **AND** TDT metrics, audit, Langfuse, and MLflow consumers SHALL not double count it

### Requirement: TDT hook pack migration

Existing TDT hook packs SHALL be migrated to official Hooks callbacks or narrowly scoped event consumers with parity tests.

#### Scenario: Budget and audit packs

- **WHEN** budget enforcement or structured audit is registered
- **THEN** it SHALL preserve its current policy behavior on the official lifecycle

#### Scenario: Legacy HookRegistry

- **WHEN** a consumer uses `HookRegistry` during the compatibility window
- **THEN** it SHALL receive a migration warning
- **AND** its supported registrations SHALL be adapted without duplicate dispatch
