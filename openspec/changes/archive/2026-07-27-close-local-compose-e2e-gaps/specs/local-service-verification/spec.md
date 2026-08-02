## ADDED Requirements

### Requirement: Live verification covers real lifecycle and integration behavior

Each service’s local integration gate SHALL distinguish process health from
real operations. For Shipping, the gate MUST exercise dispatch, replay,
completion, cancellation, persistence inspection, and outbox/CDC observation.
Temporal/Nexus acceptance MUST record workflow terminal status and operation
identity. A passing health probe alone MUST NOT produce a passing integration
result.

#### Scenario: Real lifecycle passes

- **WHEN** the local gate dispatches a shipment, replays it, and completes or
  cancels it through the public boundary
- **THEN** the expected HTTP responses, persisted state, and exactly-once
  business side-effect count are verified

#### Scenario: Integration dependency is unavailable

- **WHEN** Kafka, Debezium, Postgres, Temporal, or a required service is
  unreachable
- **THEN** the integration gate exits non-zero and retains diagnostics rather
  than reporting health-only success

#### Scenario: Focused and full evidence are distinct

- **WHEN** only the Temporal/Nexus pilot is executed
- **THEN** evidence is labeled focused and cannot satisfy the full eight-service
  Compose readiness gate
