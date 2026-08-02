## MODIFIED Requirements

### Requirement: Service runbooks SHALL exist for each service

> **Status**: PARTIAL. Root per-service runbooks remain incomplete; shared and service-local procedures are documented separately.

The platform SHALL maintain a discoverable operational runbook in the
repository's documented runbook locations for every deployable service:
order-service, payment-service, inventory-service, customer-service,
notification-service, shipping-service, catalog-service, and
reporting-service. Each service's operational documentation SHALL identify
service purpose and ownership, key dependencies, common failure modes and
remediation steps, escalation contacts, rollback procedure, scaling guidance,
and diagnostic commands. Runbooks MUST be reviewed and updated whenever the
service's deployment or dependency topology changes. Shared procedures such as
local CDC MAY be referenced rather than duplicated.

#### Scenario: Runbook exists for order-service

- **WHEN** an operator reads the canonical order-service operational runbook
- **THEN** the referenced file exists and contains sections for Dependencies, Failure Modes, Remediation, Rollback, Scaling, and Escalation

#### Scenario: Reporting service is included in the runbook inventory

- **WHEN** the runbook index is validated against the eight-service platform inventory
- **THEN** `reporting-service` appears with an explicit runbook status and ownership reference

#### Scenario: Shared local CDC procedure is referenced

- **WHEN** a service relies on the common local Debezium registration and recovery behavior
- **THEN** its documentation links to `docs/runbooks/local-cdc.md` without claiming that shared guidance is a service-specific runbook
