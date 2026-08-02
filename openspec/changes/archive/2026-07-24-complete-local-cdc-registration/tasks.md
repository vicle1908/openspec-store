## 1. Canonical connector contracts

- [x] 1.1 Inventory every CDC-owning service's outbox table, publication, slot, database role, and Kafka topic against migrations and runtime configuration
- [x] 1.2 Add canonical connector JSON for payment, inventory, and shipping with exact ownership, safe producer, heartbeat, conversion, and routing settings
- [x] 1.3 Validate and complete canonical connector JSON for notification, customer, and catalog
- [x] 1.4 Add secret-safe static connector validation covering required settings, migration alignment, peer-schema exclusion, and unique connector/slot ownership

## 2. Idempotent local registration

- [x] 2.1 Extract or generalize the order connector registration behavior into a bounded, idempotent, diagnostic helper with focused tests
- [x] 2.2 Wire payment, inventory, and shipping Compose infrastructure-init roles to migrations, topics, Debezium readiness, and connector convergence
- [x] 2.3 Wire notification, customer, and catalog Compose infrastructure-init roles to migrations, topics, Debezium readiness, and connector convergence
- [x] 2.4 Make required local service readiness fail closed when connector registration or task convergence fails

## 3. Local kind deployment

- [x] 3.1 Add connector ConfigMaps and registration workloads for all missing local kind service overlays
- [x] 3.2 Add apply-stage ordering and readiness dependencies so migrations, topics, and Debezium precede connector registration and service readiness
- [x] 3.3 Extend deployment validation to reject missing, unsafe, or unreferenced local connector artifacts

## 4. Delivery acceptance and evidence

- [x] 4.1 Add connector and task convergence checks for every CDC-owning service to local Compose/kind acceptance
- [x] 4.2 Add uniquely identified representative outbox-to-Kafka delivery checks with bounded timeouts and duplicate-tolerant identity matching
- [x] 4.3 Retain secret-redacted connector status, task traces, outbox/publication/slot diagnostics, topic observations, and a machine-readable CDC summary

## 5. Documentation and completion

- [x] 5.1 Update affected service READMEs, CDC runbooks, and rollback guidance to match the implemented registration and recovery behavior
- [x] 5.2 Run service-focused tests, strict OpenSpec validation, `make preflight`, `make validate-deployment`, and clean local acceptance for the exact source snapshot
- [x] 5.3 Update main-spec implementation statuses from partial to local-verified only where retained evidence passes, then verify the change against code and deployment
