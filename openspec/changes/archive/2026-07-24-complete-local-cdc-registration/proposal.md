## Why

The local platform provisions outbox tables, publications, and replication
slots for several services but only registers the order connector end to end.
Specs and service documentation therefore overstate CDC readiness, while local
acceptance cannot prove that committed outbox records from every owning service
reach Kafka.

## What Changes

- Add canonical Debezium outbox connector configurations for payment,
  inventory, shipping, notification, customer, and catalog.
- Add idempotent connector registration to the Docker Compose and local kind
  startup paths, with bounded retries and fail-closed diagnostics.
- Make service startup/readiness depend on required connector registration
  where the service claims CDC-backed event publication.
- Extend local acceptance and static validation to check connector state,
  source table/publication alignment, target topic routing, and representative
  end-to-end outbox delivery.
- Update service runbooks and status statements only after retained local
  evidence proves each connector path.
- Keep staging/production rollout, cloud secret delivery, and CI/CD promotion
  outside this change.

## Capabilities

### New Capabilities

- `local-cdc-registration`: Defines complete, idempotent, observable local
  Debezium connector registration and outbox-to-Kafka acceptance across all
  CDC-owning services.

### Modified Capabilities

None. Existing service specs already require CDC publication; this capability
adds the missing cross-service local bootstrap and acceptance contract.

## Impact

- Affected services: payment, inventory, shipping, notification, customer, and
  catalog; order remains the reference implementation and regression baseline.
- Affected deployment paths: root Docker Compose overlays, local kind overlays,
  connector configuration, infrastructure-init roles, health/readiness, and
  local acceptance scripts.
- Data ownership and public event contracts remain unchanged. Existing outbox
  rows, Postgres publications/slots, and Kafka topic names are preserved.
- Rollout is service-by-service in local environments with idempotent
  create-or-update registration. Rollback removes the new registration
  workloads/config mounts without deleting outbox rows, replication
  publications, slots, or Kafka topics.
