# order-aggregate Specification

## Purpose
The platform implements Order enforces lifecycle invariants The Order aggregate SHALL be the sole authority for Order lifecycle transitions and SHALL reject transitions that violate its state machine or business invariants. 
## Requirements
> **Status**: IMPLEMENTED. Order aggregate exists at services/order-service/internal/domain/order/ with state machine, ULID identifiers, Money value objects, domain events, and error handling.

### Requirement: Order enforces lifecycle invariants
The Order aggregate SHALL be the sole authority for Order lifecycle transitions and SHALL reject transitions that violate its state machine or business invariants.

#### Scenario: Valid transition
- **WHEN** a paid order is moved to processing
- **THEN** the aggregate records the processing state and emits one domain event

#### Scenario: Invalid transition
- **WHEN** a cancelled order is requested to ship
- **THEN** the aggregate returns a typed domain error without changing state or emitting an event

### Requirement: Order uses canonical identifiers and money
The Order aggregate SHALL use canonical ULIDs for public identities and SHALL represent money as an integer minor-unit amount plus an ISO 4217 currency code.

#### Scenario: Order identity round trip
- **WHEN** an Order ULID is persisted and exposed through REST, Protobuf, Kafka, and Temporal
- **THEN** every representation contains the same canonical 26-character identifier

#### Scenario: Invalid money
- **WHEN** a command supplies a negative amount or unsupported currency
- **THEN** aggregate creation fails before persistence

### Requirement: Order emits versioned facts
Each successful state change SHALL increment the aggregate version and record immutable domain facts containing the resulting aggregate version.

#### Scenario: Consecutive changes
- **WHEN** two valid state changes are applied in sequence
- **THEN** their emitted facts contain monotonically increasing aggregate versions

### Requirement: Identifier parsers reject non-canonical encodings
Order identifiers (OrderID, CustomerID, LineItemID, ProductID) SHALL be parsed only from canonical Crockford base32 ULIDs. A non-canonical encoding (lowercase form, mixed case, or any other valid-but-non-canonical ULID spelling) MUST be rejected with the canonical invalid-identifier error so that two strings that decode to the same ULID cannot drift through the system under different identity-bearing fields.

#### Scenario: Non-canonical ULID is rejected
- **WHEN** a client submits an identifier whose characters decode to a valid ULID but whose spelling is not the canonical Crockford base32 encoding
- **THEN** parsing fails with `ErrInvalidID` and the canonical form is the only accepted representation

