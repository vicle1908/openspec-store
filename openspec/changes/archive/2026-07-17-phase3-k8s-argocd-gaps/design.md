# Phase 3: K8s/ArgoCD Gaps - Technical Design

## Context

The Phase 2 audit identified four gaps in the Kubernetes and ArgoCD infrastructure created during Phase 2 (`openspec/changes/archive/2026-07-17-k8s-deployment-support`). This design addresses each gap with minimal, targeted changes. The platform currently has a default-deny NetworkPolicy, an ArgoCD ApplicationSet, and Kustomize base templates with `SERVICE_NAME` placeholders.

## Goals / Non-Goals

**Goals:**
- Close the NetworkPolicy gap so services can reach PostgreSQL and Kafka
- Ensure all 8 services are covered by the `services-verify` Makefile target
- Document the retry/backoff, image updater, and notification configuration in specs

**Non-Goals:**
- Redesign the NetworkPolicy architecture (current approach is sound)
- Replace the `SERVICE_NAME` placeholder pattern (it is intentional for per-service overlay substitution)
- Add new ArgoCD features not already present in `applications.yaml`

---

## Decisions

### Decision 1: Egress rules use podSelector: {} (namespace-wide)

**Selected:** `podSelector: {}` for PostgreSQL and Kafka egress targets.

**Rationale:**
- Matches the existing service-to-service egress rule pattern already in `networkpolicy-allow-system.yaml`
- PostgreSQL and Kafka are shared infrastructure services; all pods in the namespace need access
- Avoids per-service NetworkPolicy overhead

**Alternative Considered:** Select only specific service pods
- **Rejected:** Too granular for shared infrastructure; every service connects to the database and broker

### Decision 2: Add rules to existing allow-system policy (not new file)

**Selected:** Append to `networkpolicy-allow-system.yaml`.

**Rationale:**
- Single policy for all system egress is easier to maintain
- Already contains DNS, OTel, and service-to-service rules
- Adding a separate file would require managing policy ordering and potential conflicts

**Alternative Considered:** Create separate `networkpolicy-allow-datastores.yaml`
- **Rejected:** Fragmentation adds maintenance burden without benefit; all rules are in the same namespace

### Decision 3: Retry configuration already present - document only

**Selected:** No code change to `deploy/argocd/applications.yaml` (retry with 5 attempts and exponential backoff already configured).

**Rationale:**
- The audit flagged this as missing, but inspection shows it is already present at lines 45-50
- The specs delta documents this requirement as satisfied
- Image updater and notification requirements are added to specs as future implementation targets

---

## Architecture

### NetworkPolicy Egress Flow

```
┌─────────────────────────────────────────────────┐
│ microservices namespace                          │
│                                                  │
│  ┌──────────┐    egress     ┌──────────────┐    │
│  │ service  │──────────────>│ PostgreSQL   │    │
│  │  pod     │  TCP/5432     │ (any ns)     │    │
│  │          │               └──────────────┘    │
│  │          │    egress     ┌──────────────┐    │
│  │          │──────────────>│ Kafka        │    │
│  │          │  TCP/9092     │ (any ns)     │    │
│  └──────────┘               └──────────────┘    │
│                                                  │
│  Existing rules: DNS, OTel, service-to-service   │
│  Existing rules: ingress from ingress controller │
└─────────────────────────────────────────────────┘
```

### Makefile services-verify Coverage

```
Before:
  services-verify → order-service, notification-service, customer-service,
                     catalog-service, reporting-service

After:
  services-verify → order-service, notification-service, customer-service,
                     catalog-service, reporting-service, payment-service,
                     inventory-service, shipping-service
```

---

## File Changes

### 1. `deploy/k8s/base/networkpolicy-allow-system.yaml`

Add two egress rules after the existing service-to-service rule:

```yaml
# PostgreSQL egress
- to:
  - podSelector: {}
  ports:
  - protocol: TCP
    port: 5432
# Kafka egress
- to:
  - podSelector: {}
  ports:
  - protocol: TCP
    port: 9092
```

### 2. `Makefile` (services-verify target)

Add three services to the for-loop at line 88:

```
services/payment-service services/inventory-service services/shipping-service
```

### 3. Specs Delta (openspec/changes/phase3-k8s-argocd-gaps/specs/)

Two spec files documenting the ADDED requirements for audit trail.

---

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Overly broad egress (podSelector: {}) | Any pod can reach PostgreSQL/Kafka | Mitigated by default-deny ingress on the PostgreSQL/Kafka namespaces |
| services-verify may fail for new services | CI blocks on unverified services | Services have Makefiles with verify-pr targets; skip logic handles missing services |

---

## Verification

1. Validate NetworkPolicy YAML: `kubectl apply --dry-run=client -f deploy/k8s/base/networkpolicy-allow-system.yaml`
2. Validate Makefile: `make -n services-verify` (dry-run shows all 8 services)
3. Verify specs delta matches implementation
