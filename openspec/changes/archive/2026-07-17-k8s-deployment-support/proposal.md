## Why

The microservices platform currently supports local development via Docker Compose but lacks Kubernetes deployment capabilities required for production. Without K8s support, the platform cannot leverage GitOps workflows, horizontal autoscaling, proper resource management, or production-grade deployment patterns. This gap blocks the path to production readiness.

## What Changes

- **Add Kubernetes manifests**: Create `deploy/k8s/` directory with Kustomize base templates and environment overlays (local/staging/production)
- **Add GitOps infrastructure**: Create ArgoCD ApplicationSet for declarative deployments
- **Add resource limits**: Add memory/CPU limits to Docker Compose for local parity with K8s
- **Add autoscaling templates**: Create HorizontalPodAutoscaler (HPA) templates for each service role
- **Add PodDisruptionBudget**: Ensure high availability during node operations
- **Add secrets management**: Configure External Secrets Operator integration with Vault backend
- **Add network policies**: Namespace isolation and service communication rules

## Capabilities

### New Capabilities

- `k8s-deployment-base`: Base Kubernetes Deployment, Service, and ConfigMap templates using Kustomize. Includes security context, liveness/readiness probes, and resource requests/limits following container-resource-standards.
- `k8s-gitops-workflow`: ArgoCD ApplicationSet configuration enabling GitOps-based deployments from the monorepo. Supports automated sync, pruning, and health checking.
- `docker-compose-resource-limits`: Add `deploy.resources` blocks to all Docker Compose service definitions matching the resource tiers defined in container-resource-standards.
- `k8s-hpa-template`: HorizontalPodAutoscaler template targeting 70% CPU and 80% memory utilization with scale-up/scale-down policies.
- `k8s-pdb-template`: PodDisruptionBudget ensuring minimum available pods during cluster operations.
- `k8s-secrets-integration`: External Secrets Operator configuration for Vault-backed secret management.
- `k8s-network-policies`: NetworkPolicy templates for namespace isolation and service-to-service communication.

### Modified Capabilities

- `deployment-platform-strategy`: Add K8s architecture section and implementation phases (status: draft → active)
- `container-resource-standards`: Add Docker Compose integration section with concrete resource values per service

## Impact

### Affected Directories

- `deploy/` — New `deploy/k8s/` directory structure
- `deploy/docker-compose.*.yaml` — Resource limits added
- `deploy/argocd/` — New ArgoCD configuration

### Affected Services

All 8 microservices require K8s manifests:
- order-service (API + Orchestrator)
- notification-service (API + Worker)
- customer-service (API + Worker)
- catalog-service (API + Orchestrator)
- reporting-service (API + Consumer)
- payment-service (API + Worker)
- inventory-service (API + Worker)
- shipping-service (API + Worker)

### Dependencies

- Kubernetes cluster (1.28+)
- ArgoCD or FluxCD for GitOps
- Vault for secrets (or External Secrets Operator with cloud provider secrets manager)
- OTel Collector v0.156.0 (already in stack)

### Rollout Approach

Phase 1: Add resource limits to Docker Compose (backwards compatible, low risk)
Phase 2: Create K8s base templates (new directory, no existing code modified)
Phase 3: Add staging environment overlay and verify
Phase 4: Add production environment overlay
Phase 5: Enable ArgoCD sync for staging
Phase 6: Enable ArgoCD sync for production

### Rollback Approach

- Docker Compose resource limits: Remove `deploy.resources` blocks (instant)
- K8s manifests: `kubectl delete -f deploy/k8s/overlays/<env>` (instant)
- ArgoCD: Disable auto-sync, manually manage (gradual)
