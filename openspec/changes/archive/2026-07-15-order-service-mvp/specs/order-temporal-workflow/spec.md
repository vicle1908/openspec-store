## ADDED Requirements

### Requirement: Workflow initiation is durable and idempotent
An Order-owned Kafka consumer SHALL start fulfillment from the committed `OrderCreated` integration event, SHALL persist a stateful event receipt before committing its Kafka offset, and SHALL use deterministic workflow ID `order/<order-id>` with workflow-ID reuse rejected. A `pending` receipt MUST remain retryable until workflow initiation is durably confirmed as `started`.

#### Scenario: API process crashes after order commit
- **WHEN** Order creation commits and the API process stops before any Temporal call
- **THEN** Debezium publishes the outbox event and the orchestration consumer starts fulfillment after recovery

#### Scenario: OrderCreated is delivered twice
- **WHEN** the orchestration consumer receives the same event ID more than once
- **THEN** it records or finds one receipt and converges on one workflow execution without duplicate fulfillment effects

#### Scenario: Consumer stops after pending receipt
- **WHEN** the consumer persists a pending receipt and stops before workflow initiation
- **THEN** redelivery retries workflow initiation rather than treating the event as complete

#### Scenario: Consumer stops before offset commit
- **WHEN** workflow initiation succeeds but the consumer stops before marking the receipt started or committing the Kafka offset
- **THEN** redelivery observes the existing workflow through its deterministic ID, marks the receipt started, and commits without creating another execution

### Requirement: Workflow code is deterministic
Order workflow implementations SHALL use deterministic Temporal SDK APIs and SHALL perform I/O, wall-clock access, randomness, and service calls only through recorded workflow APIs or activities.

#### Scenario: Workflow replay
- **WHEN** a completed workflow history is replayed against its compatible worker build
- **THEN** replay completes without a nondeterminism error

### Requirement: Activities and compensations are idempotent
Every activity and compensation SHALL accept a stable operation ID and tolerate retries without duplicating an external effect.

#### Scenario: Payment activity retries after timeout
- **WHEN** payment capture succeeded remotely but its activity response was lost
- **THEN** the retry returns the existing capture result rather than charging again

### Requirement: Fulfillment activities cover the full saga
The Order fulfillment workflow SHALL expose a versioned activity surface that, at MVP, comprises `ValidateInventory`, `ReserveInventory`, `ProcessPayment`, `MarkOrderShipped`, and their compensations `ReleaseInventory` and `RefundPayment`. Each activity SHALL validate its versioned input contract (`Version`, `OrderID`, `OperationID`) and SHALL return a `NonRetryableApplicationError` with a stable `error_type` for invalid inputs and missing dependency wiring so the workflow can fail fast without burning retry budget. Forwarding activities to a not-yet-deployed downstream capability SHALL be implemented by injecting typed activity interfaces (e.g. `InventoryActivities`, `PaymentActivities`, `ShippingActivities`) through the worker composition root rather than calling them directly inside the workflow code.

#### Scenario: Activity receives an unknown contract version
- **WHEN** a caller submits a `Version` value other than the supported contract version
- **THEN** the activity returns a non-retryable validation error and the workflow records a terminal compensation failure rather than invoking a downstream capability

### Requirement: Workflow evolution protects in-flight executions
Worker deployments SHALL use stable task queues and Temporal worker deployment versioning; incompatible logic changes SHALL use SDK versioning or a new workflow type.

#### Scenario: New worker deployment
- **WHEN** a new worker build is promoted while workflows are in flight
- **THEN** existing executions remain routed to a compatible build until migration is explicitly completed

### Requirement: Service boundaries are contract based
The Order workflow SHALL invoke future Payment, Inventory, and Shipping capabilities through versioned activity inputs/results, service-owned task queues, child workflows, or Nexus operations without importing their domain packages.

#### Scenario: Inventory service extraction
- **WHEN** inventory logic moves to an independently deployed service
- **THEN** the Order workflow keeps its orchestration contract while the Inventory service owns execution and data

### Requirement: Workflow state does not replace domain state
Temporal SHALL own orchestration history while PostgreSQL remains authoritative for current Order business state.

#### Scenario: Query current order
- **WHEN** an API client requests current Order state
- **THEN** the service reads the Order model rather than treating workflow history as its query database
