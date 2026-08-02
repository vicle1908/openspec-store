## ADDED Requirements

### Requirement: Commands are idempotent
Every externally initiated mutating command SHALL require an idempotency key and SHALL persist its outcome for replay within the configured retention period.

#### Scenario: Duplicate successful command
- **WHEN** a client repeats a command with the same idempotency key and equivalent request body
- **THEN** the handler returns the original outcome without applying a second state change

#### Scenario: Reused key with different body
- **WHEN** a client reuses an idempotency key with a different normalized request body
- **THEN** the handler rejects the command as a conflict

### Requirement: State and outbox commit atomically
A successful command SHALL persist the aggregate mutation, aggregate version, idempotency outcome, and all resulting outbox records in one PostgreSQL transaction.

#### Scenario: Outbox insert fails
- **WHEN** an outbox record cannot be inserted
- **THEN** the aggregate and idempotency outcome are not committed

### Requirement: Command conflicts are explicit
The command layer SHALL distinguish validation, domain, not-found, idempotency, and optimistic-concurrency errors.

#### Scenario: Stale aggregate version
- **WHEN** a command attempts to save an aggregate whose stored version has advanced
- **THEN** the handler returns a typed concurrency conflict and does not overwrite the newer state
