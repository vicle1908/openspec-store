# Phase 3: K8s/ArgoCD Gaps - Implementation Tasks

## 1. NetworkPolicy: PostgreSQL Egress

- [x] 1.1 Add PostgreSQL egress rule (TCP/5432) to `deploy/k8s/base/networkpolicy-allow-system.yaml`

## 2. NetworkPolicy: Kafka Egress

- [x] 2.1 Add Kafka egress rule (TCP/9092) to `deploy/k8s/base/networkpolicy-allow-system.yaml`

## 3. ArgoCD Retry Configuration

- [x] 3.1 Verify retry configuration exists in `deploy/argocd/applications.yaml` (already present: 5 attempts, exponential backoff)
- [x] 3.2 Document retry requirement in specs delta

## 4. Makefile services-verify Expansion

- [x] 4.1 Add payment-service to services-verify loop in root Makefile
- [x] 4.2 Add inventory-service to services-verify loop in root Makefile
- [x] 4.3 Add shipping-service to services-verify loop in root Makefile

## 5. Specs Delta

- [x] 5.1 Create specs delta for k8s-network-policies (PostgreSQL and Kafka egress)
- [x] 5.2 Create specs delta for k8s-gitops-workflow (retry, image updater, notifications)

## 6. Documentation

- [x] 6.1 Create proposal.md for Phase 3 change
- [x] 6.2 Create design.md for Phase 3 change
- [x] 6.3 Create tasks.md for Phase 3 change

---

## Verification Summary

### Implementation Changes
- [x] NetworkPolicy: 2 egress rules added (PostgreSQL TCP/5432, Kafka TCP/9092)
- [x] Makefile: 3 services added to services-verify loop (payment, inventory, shipping)
- [x] ArgoCD: retry configuration verified as already present

### Specs Delta
- [x] k8s-network-policies: 2 ADDED requirements (PostgreSQL egress, Kafka egress)
- [x] k8s-gitops-workflow: 3 ADDED requirements (retry, image updater, notifications)

### Documentation
- [x] proposal.md created
- [x] design.md created
- [x] tasks.md created

---

## Summary

**Total Tasks:** 12
**Completed:** 12 (100%)

### Files Modified
- `deploy/k8s/base/networkpolicy-allow-system.yaml` — 2 egress rules added
- `Makefile` — 3 services added to services-verify loop

### Files Created
- `openspec/changes/phase3-k8s-argocd-gaps/proposal.md`
- `openspec/changes/phase3-k8s-argocd-gaps/design.md`
- `openspec/changes/phase3-k8s-argocd-gaps/tasks.md`
- `openspec/changes/phase3-k8s-argocd-gaps/specs/k8s-network-policies/spec.md`
- `openspec/changes/phase3-k8s-argocd-gaps/specs/k8s-gitops-workflow/spec.md`
