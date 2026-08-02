## ADDED Requirements

### Requirement: Nexus contracts follow an explicit bounded-context map

The platform SHALL maintain a canonical context map for every Nexus
relationship. Each entry SHALL identify the provider and caller contexts,
owners, aggregates, ubiquitous-language terms, commands, published facts,
upstream/downstream relationship, and anti-corruption mapping. A deployable
service boundary alone SHALL NOT establish a bounded context.

#### Scenario: Shipping operation is admitted

- **WHEN** `shipping.commands.v1.DispatchShipment` is proposed
- **THEN** the context map identifies Shipping as the command and aggregate
  owner and Order as a caller
- **AND** the Operation uses Shipping vocabulary and documents the Order-to-
  Shipping translation

#### Scenario: Ownership is ambiguous

- **WHEN** two contexts claim authority over the same mutation or aggregate
- **THEN** contract validation fails before an endpoint is provisioned
- **AND** the context map must resolve ownership without a shared table or
  shared domain type

### Requirement: Nexus contracts are versioned and producer-owned

Every advertised Nexus Service and Operation SHALL have a producer-owned,
Buf-managed Protobuf request and response contract with an explicit version.
The contract SHALL describe stable business input and outcome without exposing
a target Namespace, Task Queue, Go Workflow type, private domain type, or
credential.

#### Scenario: Caller invokes a stable contract

- **WHEN** an Order Workflow invokes a Shipping operation
- **THEN** it supplies the endpoint, Service, Operation, version, and contract
  payload
- **AND** it does not select a Shipping Namespace, Task Queue, or Go function

#### Scenario: Durable payload is recorded

- **WHEN** Temporal persists Nexus or handler Workflow input in Event History
- **THEN** the payload uses the versioned integration DTO
- **AND** it contains no private aggregate, domain-event, or adapter type

#### Scenario: Breaking contract change is introduced

- **WHEN** a producer changes business semantics or a field incompatibly
- **THEN** it publishes a new versioned Service or Operation and Task Queue
- **AND** existing callers continue to resolve the previous contract

### Requirement: Integration adapters form anti-corruption boundaries

The caller adapter SHALL map local application/domain values to the
producer-owned contract. The handler adapter SHALL validate and map the
contract to a provider-owned application command before invoking domain
behavior. Application and domain packages SHALL NOT import peer-generated
contracts, Nexus SDK types, or endpoint constants.

#### Scenario: Handler accepts a valid request

- **WHEN** a Shipping Nexus handler receives a valid versioned dispatch request
- **THEN** it maps the request to a Shipping application command
- **AND** the aggregate receives provider-owned value objects rather than the
  generated request type

#### Scenario: Caller attempts to share a domain type

- **WHEN** a Nexus contract or caller imports a peer context's private domain
  type
- **THEN** architecture validation fails with both context names and the
  offending import

### Requirement: Nexus is limited to durable commands

The platform SHALL use Nexus for durable command invocation between Temporal
contexts. Kafka outbox events SHALL remain immutable facts, and HTTP/gRPC or
owned projections SHALL serve ordinary request/response calls and queries.
A Kafka consumer or public HTTP handler SHALL NOT invoke Nexus directly as a
substitute for its existing command/Workflow starter.

#### Scenario: Durable cross-context command uses Nexus

- **WHEN** a running Temporal Workflow needs a long-running command owned by
  another context
- **THEN** it invokes the provider's versioned Nexus operation
- **AND** the provider owns the resulting aggregate transaction and outcome

#### Scenario: State fact is published

- **WHEN** a command changes externally observable aggregate state
- **THEN** the owning context commits a versioned outbox fact atomically with
  the aggregate mutation
- **AND** Debezium publishes that fact to Kafka independently of the Nexus
  response

#### Scenario: Caller needs a query

- **WHEN** a caller needs current read data without a durable mutation
- **THEN** it uses the provider's read API, projection, or an explicitly
  bounded Workflow Query/Update operation
- **AND** it does not introduce a long-running Nexus command as a query bus

### Requirement: Nexus handlers are at-least-once and idempotent

Every mutating handler SHALL tolerate duplicate delivery. The caller SHALL
provide a stable operation identity and business key, and the producer SHALL
persist a request fingerprint, state, and retained result in its own database.
Long-running handlers SHALL use a business-meaningful Workflow ID with
duplicate rejection. The platform SHALL NOT claim exactly-once execution.

#### Scenario: Exact duplicate returns the original outcome

- **WHEN** the same operation identity and request fingerprint are delivered
  more than once
- **THEN** the handler does not repeat the external side effect or aggregate
  mutation
- **AND** it returns the retained outcome

#### Scenario: Identity is reused with different input

- **WHEN** an operation identity is reused with a different request fingerprint
- **THEN** the handler returns a typed non-retryable idempotency conflict
- **AND** it performs no provider call or database mutation

#### Scenario: Retry follows worker failure

- **WHEN** a handler Worker fails after the operation is accepted
- **THEN** a retry resumes from the persisted operation state
- **AND** final aggregate and outbox state contain one committed mutation

### Requirement: External effects use a recoverable transaction protocol

A mutating Nexus handler SHALL NOT hold a PostgreSQL transaction open across
an external network side effect. It SHALL first persist a pending operation
intent, call the external provider with a stable provider idempotency key, and
then atomically commit the aggregate transition, retained result, and outbox
fact through repositories bound to one transaction.

#### Scenario: Provider succeeds and finalization commits

- **WHEN** the provider returns a successful dispatch result
- **THEN** the handler applies the result to the aggregate and commits the
  aggregate, operation result, and outbox fact in one transaction
- **AND** the Nexus operation completes only after that transaction commits

#### Scenario: Finalization fails after provider success

- **WHEN** the provider succeeds but the final database transaction fails
- **THEN** retry uses the same provider idempotency key or result lookup
- **AND** no second carrier dispatch is created

#### Scenario: Provider outcome is unknown

- **WHEN** the provider request times out without a definitive outcome
- **THEN** the operation enters a reconciling state
- **AND** the handler does not claim failure, issue a new provider key, or
  publish a success fact until reconciliation completes

### Requirement: Domain invariants and events remain provider-owned

The provider aggregate SHALL enforce creation and lifecycle invariants and
SHALL decide which domain events occur. Application code SHALL supply time and
external results explicitly. An outbound adapter SHALL map committed domain
events to versioned integration facts; a logging-only Activity SHALL NOT count
as outbox persistence.

#### Scenario: Invalid Shipping transition is requested

- **WHEN** a command attempts to cancel a delivered Shipment or dispatch with
  an invalid address or carrier
- **THEN** the Shipment aggregate returns a typed domain rejection without
  state change, provider call, or event

#### Scenario: Valid Shipping transition commits

- **WHEN** a pending Shipment is finalized with a confirmed carrier result
- **THEN** the aggregate records the transition and domain event using the
  supplied timestamp
- **AND** the same transaction persists the mapped integration fact

### Requirement: Nexus failures use a stable error taxonomy

The handler SHALL map contract/input rejection and domain invariant rejection
to typed non-retryable failures, transient infrastructure failures to
retryable failures, unknown provider outcomes to reconciliation, and
compensation failures to a distinct operator-visible outcome. Public failures
SHALL NOT expose internal error strings, SQL details, or provider payloads.

#### Scenario: Domain rejects a command

- **WHEN** the application command violates a provider-owned invariant
- **THEN** the caller receives the documented non-retryable business error
- **AND** retry policy does not repeat the command

#### Scenario: Temporary infrastructure failure occurs

- **WHEN** the handler cannot reach a required local infrastructure dependency
- **THEN** it returns a typed retryable failure
- **AND** retry/circuit metrics identify the endpoint and Operation without
  sensitive details

### Requirement: Nexus duration and cancellation are explicit

Each operation SHALL declare whether it is synchronous or asynchronous.
Synchronous handlers SHALL finish within the documented 10-second deadline;
longer work SHALL use a Workflow-backed asynchronous operation. Handlers SHALL
honor cancellation where possible, and runbooks SHALL state that termination
can orphan handler work and bypass compensation.

#### Scenario: Long-running operation is asynchronous

- **WHEN** a command can exceed the synchronous deadline
- **THEN** it is implemented as a Workflow-backed asynchronous operation
- **AND** completion is observed through the Nexus operation state

#### Scenario: Caller cancels an operation

- **WHEN** the caller requests cancellation before completion
- **THEN** cancellation propagates to the handler Workflow
- **AND** resulting state is observable without claiming external effects were
  rolled back

### Requirement: Mutating rollout uses one active route

For each operation identity, routing SHALL select either Nexus or the fallback
HTTP/Activity path before the first side effect. A rollout, comparison, or
shadow mode SHALL NOT execute both mutating paths. Rollback SHALL prevent new
Nexus starts before enabling fallback for new identities.

#### Scenario: Pilot request is routed

- **WHEN** the Shipping pilot receives a dispatch operation identity
- **THEN** durable routing records exactly one selected path
- **AND** retries reuse that path

#### Scenario: Rollback begins

- **WHEN** operators disable the Nexus pilot
- **THEN** no new operation identity starts through Nexus
- **AND** in-flight Nexus operations drain or cancel before their identities
  become eligible for any fallback handling

### Requirement: Nexus execution is correlated and observable

The platform SHALL expose operation latency, schedule-to-start latency,
execution failures, retries, duplicate detections, reconciliation state, and
end-to-end outcomes. Logs, traces, metrics, Workflow memo/search attributes,
outbox envelopes, and retained results SHALL propagate operation,
correlation, and causation identities without payload secrets.

#### Scenario: Operation completes

- **WHEN** a Nexus command commits successfully
- **THEN** the caller Workflow, handler Workflow, aggregate transaction, and
  Kafka fact are traceable through correlation and causation identities

#### Scenario: Circuit opens

- **WHEN** repeated retryable failures open the destination-pair circuit
- **THEN** pending Operations expose the blocked state
- **AND** metrics identify the caller Namespace and endpoint without cardinality
  from business payload fields
