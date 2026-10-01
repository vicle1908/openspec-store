# platform-verification Delta Specification

## ADDED Requirements

### Requirement: Postman and Newman automated API verification

The platform verification suite SHALL provide machine-readable Postman collections and Newman automation runners under `tests/postman/` that validate microservice REST interfaces and distributed saga workflows without requiring compiled Go test binaries.

The test suite SHALL be divided into two distinct tiers:
1. **Feature Integration Tier**: A dedicated collection (`go-microservices.feature-integration.postman_collection.json`) validating isolated endpoints across all 8 microservices (`customer`, `catalog`, `inventory`, `payment`, `shipping`, `notification`, `order`, `reporting`) and supporting infrastructure (Debezium CDC connectors, Mailpit SMTP message inspection, OpenTelemetry Collector health, Prometheus metrics).
2. **End-to-End Saga Tier**: A sequential business transaction collection (`go-microservices.e2e-saga.postman_collection.json`) executing the complete order fulfillment saga across service boundaries, with asynchronous polling assertions confirming saga progression to `shipped` state.

Pre-request scripting SHALL generate non-colliding dynamic identifiers (valid 26-character Crockford Base32 ULIDs, timestamps, idempotency keys, and correlation IDs) to ensure test runs remain hermetic and independent.

#### Scenario: Isolated feature integration test execution
- **WHEN** the feature integration test suite executes via Newman against a healthy local stack
- **THEN** every microservice endpoint responds with expected HTTP status codes, correct contract schemas, and non-empty responses
- **AND** negative boundary tests (invalid bodies, missing required headers) are rejected with corresponding 400 or 422 errors.

#### Scenario: End-to-end saga workflow verification
- **WHEN** the end-to-end saga collection executes against the running local stack
- **THEN** a customer is registered, a catalog product is created and priced, stock is provisioned, and an order is placed
- **AND** the test runner polls the order resource until the underlying Temporal saga advances the order status to `shipped`
- **AND** outbound SMTP delivery in Mailpit and revenue projections in the reporting service are verified with 100% assertion pass rate.

#### Scenario: Headless CLI test execution with Newman
- **WHEN** `make newman-test`, `make newman-e2e`, or `make newman-all` is invoked from the repository root
- **THEN** Newman executes the collections headlessly using the local environment definition
- **AND** emits machine-readable JUnit XML and terminal CLI reports without hanging.
