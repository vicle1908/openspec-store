## MODIFIED Requirements

### Requirement: Live verification covers real lifecycle and integration behavior

Each service's local integration gate SHALL distinguish process health from
real operations. For Shipping, the gate MUST exercise dispatch, exact replay,
conflicting-fingerprint rejection, concurrent duplicate delivery,
lease-expiry recovery, completion, cancellation, persistence inspection, and
outbox/CDC observation. Temporal/Nexus acceptance MUST record workflow terminal
status, operation identity, canonical fingerprint, carrier call count,
aggregate transition count, outbox count, `run_id`, and `compose_project`. A
passing health probe alone MUST NOT produce a passing integration result.

#### Scenario: Real lifecycle passes

- **WHEN** the local gate dispatches a shipment, replays it, submits a
  conflicting request, completes or cancels it through the public boundary,
  and observes its outbox fact
- **THEN** the expected HTTP responses, persisted state, retained `201` replay,
  typed conflict, and exactly-once business side-effect count are verified

#### Scenario: Concurrent exact duplicate passes safely

- **WHEN** two HTTP requests and two Nexus starts for the same operation and
  fingerprint execute concurrently
- **THEN** one logical carrier effect, one Shipment transition, and one outbox
  fact are observed
- **AND** duplicate callers either attach or receive the documented
  `operation_in_progress` retryable outcome before replaying the retained
  result

#### Scenario: Lease recovery passes safely

- **WHEN** the gate injects a worker crash after the provider request and lets
  the lease expire
- **THEN** the recovering worker performs lookup before execute, uses the same
  provider idempotency key, and does not create a second carrier effect

#### Scenario: Evidence identity is exact

- **WHEN** the integration gate loads a Workflow, smoke, Worker, pilot, or
  acceptance artifact
- **THEN** every artifact matches the invocation's exact `run_id` and
  `compose_project`
- **AND** a missing, stale, or cross-run artifact fails the gate

#### Scenario: Integration dependency is unavailable

- **WHEN** Kafka, Debezium, Postgres, Temporal, or a required service is
  unreachable
- **THEN** the integration gate exits non-zero and retains diagnostics rather
  than reporting health-only success

#### Scenario: Focused and full evidence are distinct

- **WHEN** only the Temporal/Nexus pilot is executed
- **THEN** evidence is labeled focused and cannot satisfy the full eight-service
  Compose readiness gate
