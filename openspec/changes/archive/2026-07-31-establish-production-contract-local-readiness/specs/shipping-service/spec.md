## MODIFIED Requirements

### Requirement: ShippingProvider port abstracts the carrier integration

The ShippingProvider port SHALL remain the only application-layer boundary for
dispatch, lookup/reconciliation, and cancellation; the application layer MUST
NOT import a carrier SDK. Local-fast MAY select the concurrency-safe
deterministic in-process stub. Production-contract SHALL select a networked
protocol-faithful carrier sandbox through the same external adapter,
authentication, timeout, idempotency, unknown-outcome reconciliation, and
redaction paths intended for a real carrier. Strict mode SHALL require a
non-stub configured provider and complete provider credentials. Missing or
incompatible provider mode SHALL fail before Shipping becomes ready.

#### Scenario: Shipping uses the stub in local-fast
- **WHEN** Shipping starts in local-fast with the deterministic stub selected
- **THEN** the stub returns repeatable tracking outcomes safely under concurrent calls
- **AND** resulting evidence is ineligible for production-contract readiness

#### Scenario: Shipping uses the networked sandbox in production-contract
- **WHEN** Shipping starts in production-contract with valid sandbox endpoint, identity, trust, and credential inputs
- **THEN** dispatch, lookup, and cancellation use the real network adapter
- **AND** the adapter preserves provider idempotency and redacts credentials

#### Scenario: Network outcome is unknown
- **WHEN** the sandbox applies dispatch but the response is lost
- **THEN** Shipping reconciles by stable provider idempotency identity before retrying
- **AND** one logical shipment transition and one outbox fact are retained

#### Scenario: In-process stub is selected in production-contract
- **WHEN** production-contract selects the deterministic in-process stub
- **THEN** Shipping fails before readiness and no dispatch is accepted

#### Scenario: Application layer imports a carrier SDK
- **WHEN** the architecture test scans the Shipping application packages
- **THEN** the test fails if a carrier SDK bypasses the ShippingProvider port

