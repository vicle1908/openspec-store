## ADDED Requirements

### Requirement: Nexus version dimensions evolve independently

The platform SHALL track Protobuf schema version, Nexus Service/Operation
version, handler Workflow implementation version, and Worker
build/deployment version as separate dimensions. Workflow patching or Worker
Versioning SHALL NOT be presented as public contract versioning.

#### Scenario: Compatible field is added

- **WHEN** a producer adds a backward-compatible optional Protobuf field
- **THEN** old callers continue to use the existing Service/Operation version
- **AND** contract compatibility and Event History replay tests pass

#### Scenario: Business contract breaks

- **WHEN** a producer changes Operation semantics or payload incompatibly
- **THEN** it registers a new Service or Operation version and Task Queue
- **AND** the old contract remains routable until callers and in-flight
  operations drain

#### Scenario: Workflow implementation changes compatibly

- **WHEN** handler Workflow code changes without a public contract change
- **THEN** Workflow patching or Worker Versioning preserves replay
- **AND** the public Service/Operation version remains unchanged

### Requirement: Nexus identity participates in durable duplicate protection

Every mutating Nexus request SHALL carry a stable operation identity, business
key, contract version, and deterministic request fingerprint into the handler
Workflow and application command. Database idempotency retention SHALL cover
the business retry window and SHALL NOT rely solely on Temporal Namespace
retention or Workflow ID history.

#### Scenario: Exact duplicate is replayed

- **WHEN** an operation with an already committed identity and matching
  fingerprint is replayed
- **THEN** no second aggregate, provider, or outbox mutation occurs
- **AND** the retained result is returned

#### Scenario: Workflow history has expired

- **WHEN** Temporal retention no longer contains the original Workflow but the
  business idempotency window remains active
- **THEN** the database idempotency record still prevents a duplicate side
  effect

#### Scenario: Identity conflicts with new input

- **WHEN** the same operation identity arrives with a different fingerprint
- **THEN** the handler returns a non-retryable idempotency conflict before any
  side effect

### Requirement: Durable payloads are isolated from domain implementation

Every Nexus and handler Workflow input/output recorded in Event History SHALL
use a versioned durable DTO. Private aggregate structs, domain events,
repository types, adapter types, and generated peer-domain aliases SHALL NOT be
serialized into Event History.

#### Scenario: Domain aggregate evolves

- **WHEN** a private Shipment field or invariant changes
- **THEN** existing Workflow histories continue to replay through the durable
  DTO mapping
- **AND** no public contract change is implied unless integration semantics
  changed

#### Scenario: Unsupported durable version is received

- **WHEN** a handler receives an unsupported DTO or contract version
- **THEN** it returns a non-retryable version error before external I/O
- **AND** migration diagnostics include the version dimensions without payload
  secrets

### Requirement: Namespace strategy remains environment-scoped for the pilot

The Nexus pilot SHALL preserve one Temporal Namespace per environment and
service-owned Task Queues. Endpoint abstraction SHALL hide target details from
callers but SHALL NOT be used to claim security isolation that the shared
Namespace does not provide.

#### Scenario: Pilot endpoint is provisioned

- **WHEN** the Shipping endpoint is created in an environment
- **THEN** it targets the Shipping-owned Task Queue in that environment's
  Namespace
- **AND** callers reference only the endpoint and versioned contract

#### Scenario: Stronger isolation is required

- **WHEN** security or organizational requirements require a separate
  Namespace
- **THEN** a separate migration decision updates the context map,
  authorization, endpoint target, and drain plan
- **AND** the pilot does not silently adopt namespace-per-service
