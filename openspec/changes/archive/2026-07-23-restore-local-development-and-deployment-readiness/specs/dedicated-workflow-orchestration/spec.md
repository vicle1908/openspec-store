## ADDED Requirements

### Requirement: Canonical eight-service Compose topology

The platform SHALL maintain one root Compose file set that includes the base data plane and the order, payment, inventory, shipping, notification, customer, catalog, and reporting service overlays. The same file set SHALL be used by local full-stack startup and cross-service CI.

#### Scenario: Canonical model includes all service boundaries

- **WHEN** CI renders the canonical Compose model and lists its services
- **THEN** every required API, worker, orchestrator, consumer, migration, topic initializer, and infrastructure initializer for all eight services is present

#### Scenario: Undefined cross-service dependency is rejected

- **WHEN** an overlay declares a dependency on a service absent from the canonical model
- **THEN** Compose model validation exits non-zero before images are built or containers are created

### Requirement: Cross-service workflow validates real network boundaries

The full-stack acceptance test SHALL exercise the order workflow through the deployed HTTP, Temporal, PostgreSQL, Kafka, and reporting boundaries and SHALL NOT replace a required peer service with an in-process implementation or test double.

#### Scenario: Order workflow reaches extracted services

- **WHEN** the acceptance test creates an order and drives fulfillment to completion
- **THEN** payment, inventory, and shipping calls cross their deployed HTTP boundaries, Temporal records the workflow, public events traverse Kafka, and reporting observes the outcome

#### Scenario: Acceptance provisions inventory through the owning service

- **WHEN** the acceptance test creates a catalog product whose identifier is used as the inventory SKU
- **THEN** it provisions on-hand stock through the deployed inventory-service API before creating the order
- **AND** it does not write the inventory schema directly or substitute a repository or in-process test double
- **AND** the validation activity uses the read-only inventory availability endpoint while the reservation activity remains the sole stock-holding mutation

#### Scenario: Peer failure produces retry-safe evidence

- **WHEN** a configured peer service fails during the acceptance workflow
- **THEN** the workflow follows its retry or compensation contract without duplicate externally visible effects and the evidence report identifies the failed boundary and final state
