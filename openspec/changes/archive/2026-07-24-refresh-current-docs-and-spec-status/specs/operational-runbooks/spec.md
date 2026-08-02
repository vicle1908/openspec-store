## MODIFIED Requirements

### Requirement: Runbooks are discoverable

> **Status**: PARTIAL. The root index and shared local CDC runbook exist; root per-service runbook coverage remains incomplete.

The `docs/runbooks/README.md` SHALL include an index that distinguishes root
per-service runbooks, shared platform procedures, and links to service-local
runbooks where those are the current owner documentation. Each entry SHALL
identify the service or procedure, its canonical path, and whether it is
implemented, shared, service-local, or planned.

#### Scenario: Operator finds available runbooks
- **WHEN** an operator navigates to `docs/runbooks/`
- **THEN** the README lists every available root or shared runbook with a valid link and lists all eight services with an explicit status

#### Scenario: Service-local runbook is not misclassified
- **WHEN** a service has an operational document under `services/<service>/docs/`
- **THEN** the root index links to that path as service-local guidance rather than claiming a root `docs/runbooks/<service>.md` exists

#### Scenario: Missing runbook remains visible
- **WHEN** a service has no complete operational runbook
- **THEN** the index marks it planned or partial and does not represent the platform as having complete runbook coverage
