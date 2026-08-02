## Why

Phase 3 addresses K8s and ArgoCD configuration gaps identified during the Phase 2 audit. The NetworkPolicy at `deploy/k8s/base/networkpolicy-allow-system.yaml` currently allows DNS, OTel, and intra-namespace traffic but is missing egress rules for PostgreSQL (port 5432) and Kafka (port 9092), which means services cannot reach their databases or message brokers when deployed behind the default-deny policy. The ArgoCD ApplicationSet already has retry/backoff configured, but the `services-verify` Makefile target only covers the original 5 services and excludes the 3 newly extracted domains (payment, inventory, shipping). Additionally, the Kustomize base templates use a `SERVICE_NAME` placeholder that is not resolved via Kustomize `replacements` or `nameSuffix`, requiring per-service overlays to substitute it manually.

## What Changes

- **NetworkPolicy: Add PostgreSQL egress rule** — Allow TCP egress to port 5432 for database access
- **NetworkPolicy: Add Kafka egress rule** — Allow TCP egress to port 9092 for message streaming
- **Makefile: Expand services-verify** — Add payment-service, inventory-service, shipping-service to the verification loop
- **Specs delta: Update k8s-network-policies** — Add ADDED requirements for PostgreSQL and Kafka egress
- **Specs delta: Update k8s-gitops-workflow** — Add requirements for retry, image updater, and notifications

## Capabilities

### Modified Capabilities

- `k8s-network-policies`: Add egress rules for PostgreSQL and Kafka to the system-allow NetworkPolicy
- `k8s-gitops-workflow`: Document retry/backoff configuration (already in applications.yaml), image updater, and notification integration

### New Capabilities

- None — all changes are gap-closure on existing capabilities

## Impact

### Affected Files

- `deploy/k8s/base/networkpolicy-allow-system.yaml` — Add 2 egress rules
- `Makefile` — Add 3 services to services-verify loop
- `openspec/specs/k8s-network-policies/spec.md` — Already has ADDED requirements (specs delta documents alignment)
- `openspec/specs/k8s-gitops-workflow/spec.md` — Already has ADDED requirements (specs delta documents alignment)

### Affected Services

- All 8 microservices benefit from PostgreSQL and Kafka egress rules
- payment-service, inventory-service, shipping-service gain verification coverage

### Dependencies

- No new dependencies introduced
- Changes are backwards-compatible (additive rules only)

### Rollout Approach

1. Add NetworkPolicy egress rules (additive, no existing rules modified)
2. Update Makefile services-verify (additive loop entries)
3. Create specs delta for audit trail

### Rollback Approach

- NetworkPolicy: Remove added egress rules from YAML
- Makefile: Remove added service entries from loop
