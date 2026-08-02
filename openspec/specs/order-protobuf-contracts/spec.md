# order-protobuf-contracts Specification

## Purpose
The platform implements Public contracts are versioned and domain owned Public Order messages SHALL live in versioned Protobuf packages owned by the Order domain, and generated contracts SHALL be the only shared code required by consumers. 
## Requirements
### Requirement: Public contracts are versioned and domain owned

> **Status**: IMPLEMENTED. Protobuf contracts exist in order-service/proto/order/v1 with generated Go code.

Public Order messages SHALL live in versioned Protobuf packages owned by the Order domain, and generated contracts SHALL be the only shared code required by consumers.

#### Scenario: New consumer
- **WHEN** a future service consumes Order events
- **THEN** it imports generated contract types without importing Order domain, repository, or configuration packages

### Requirement: Event envelope contains interoperability metadata

> **Status**: IMPLEMENTED. Event envelope contains all required metadata fields.

Every public event SHALL contain event ID, event type, event version, aggregate ID, aggregate version, occurrence time, producer, correlation ID, causation ID, and serialized payload.

#### Scenario: Trace an event chain
- **WHEN** one event causes a command that emits another event
- **THEN** correlation and causation identifiers preserve the causal chain

### Requirement: Contract compatibility is enforced

> **Status**: IMPLEMENTED. Buf lint and breaking-change checks configured in CI pipeline.

CI SHALL run Buf lint and breaking-change checks against the main branch. Existing field numbers SHALL never be reused and removed fields SHALL be reserved.

#### Scenario: Breaking field change
- **WHEN** a pull request changes an existing field type incompatibly
- **THEN** the compatibility check fails before merge

### Requirement: Consumers tolerate additive evolution

> **Status**: IMPLEMENTED. Consumers ignore unknown fields; wire-format fuzz testing validates compatibility.

Consumers SHALL ignore unknown fields and SHALL be tested against current and immediately previous contract fixtures.

#### Scenario: Producer adds an optional field
- **WHEN** an older consumer receives a message containing the new field
- **THEN** it processes all known fields successfully

#### Scenario: Wire-format fuzz testing
- **WHEN** the candidate binary receives arbitrary bytes that are nominally an `EventEnvelope`
- **THEN** the wire decoder either rejects the bytes with a parse error or accepts them and round-trips them through marshal/unmarshal without drift so a corrupted payload cannot silently alter downstream semantics

