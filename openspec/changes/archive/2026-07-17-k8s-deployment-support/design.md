# K8s Deployment Support - Technical Design

## Context

The microservices platform currently uses Docker Compose for local development and testing. Production deployments require Kubernetes orchestration, GitOps workflows, and proper resource management. This design addresses the technical implementation of K8s deployment infrastructure while maintaining compatibility with the existing Docker Compose setup.

The platform follows a hexagonal architecture with Go services using Temporal for workflow orchestration, PostgreSQL for persistence, Kafka for messaging, and OTel for observability. All services use the same binary entrypoint pattern with role-based commands (api, worker, migrate, infrastructure).

## Goals / Non-Goals

**Goals:**
- Add Kubernetes deployment support without breaking Docker Compose workflows
- Enable GitOps-based deployments using ArgoCD
- Standardize resource allocation across local and cloud environments
- Provide autoscaling capabilities for production workloads
- Ensure security compliance with non-root containers and least-privilege access

**Non-Goals:**
- Replace Docker Compose as the local development topology
- Implement multi-cluster federation
- Deploy a specific cloud provider (AWS/EKS, GCP/GKE, Azure/AKS)
- Service mesh implementation (Istio/Linkerd) - deferred to Phase 2
- Database provisioning via K8s operators

---

## Decisions

### Decision 1: Kustomize over Helm

**Selected:** Kustomize

**Rationale:** 
- Native Kubernetes tool with no additional installation required
- Template-free approach leverages the existing layered Compose pattern
- Environment-specific overlays align with the current `docker-compose.*.yaml` overlay structure
- Git-native diffing and merge workflows

**Alternative Considered:** Helm
- Provides templating with `{{ .Values }}` variables
- Larger ecosystem with Chart repositories
- **Rejected:** Adds complexity and a separate tooling dependency; our use case doesn't need Helm's advanced features

### Decision 2: ArgoCD over FluxCD

**Selected:** ArgoCD

**Rationale:**
- GitOps dashboard provides visibility for developers
- ApplicationSet CRD enables declarative multi-service deployments
- Mature RBAC and notification integrations
- Used by the existing platform-observability spec

**Alternative Considered:** FluxCD
- Kubernetes-native, operator-based approach
- **Rejected:** ArgoCD's UI provides better developer experience for this platform's team structure

### Decision 3: External Secrets Operator over direct Vault injection

**Selected:** External Secrets Operator (ESO)

**Rationale:**
- Kubernetes-native secrets management using Custom Resources
- Supports multiple backends (Vault, AWS SM, GCP SM, Azure KV)
- Automatic secret synchronization and rotation
- Aligns with GitOps principles - secrets are defined as code

**Alternative Considered:** Vault Agent Sidecar
- **Rejected:** Requires additional sidecar containers and more complex deployment configuration

### Decision 4: HorizontalPodAutoscaler v2 over v1

**Selected:** autoscaling/v2

**Rationale:**
- Supports multiple metric types (CPU, memory, custom)
- Allows behavior configuration for scale-up/scale-down policies
- Container resource metrics for precise allocation
- Standard in Kubernetes 1.27+

**Alternative Considered:** autoscaling/v2beta2
- **Rejected:** v2 is stable and recommended; v2beta2 is deprecated

### Decision 5: Overlay structure mirrors Compose

**Selected:** `deploy/k8s/overlays/{local,staging,production}`

**Rationale:**
- Developers already understand the Compose overlay pattern
- Maps directly to the existing `deploy/docker-compose.*.yaml` structure
- Easy to correlate local behavior with production behavior

---

## Directory Structure

```
deploy/
├── k8s/
│   ├── base/                              # Shared templates (immutable)
│   │   ├── deployment.yaml                # Base Deployment
│   │   ├── service.yaml                   # ClusterIP/LoadBalancer
│   │   ├── serviceaccount.yaml            # ServiceAccount + Role
│   │   ├── hpa.yaml                      # HorizontalPodAutoscaler
│   │   ├── pdb.yaml                      # PodDisruptionBudget
│   │   ├── networkpolicy.yaml             # NetworkPolicy templates
│   │   ├── externalsecret.yaml            # ExternalSecret reference
│   │   └── kustomization.yaml            # Base Kustomization
│   └── overlays/
│       ├── local/                         # Kind/Minikube
│       │   ├── kustomization.yaml
│       │   ├── resources.yaml            # Local resource limits
│       │   └── static-secrets.yaml      # Local static secrets
│       ├── staging/
│       │   ├── kustomization.yaml
│       │   └── resources.yaml
│       └── production/
│           ├── kustomization.yaml
│           └── resources.yaml
├── argocd/
│   ├── project.yaml                       # AppProject
│   └── applications.yaml                  # ApplicationSet
└── docker-compose.*.yaml                  # Existing Compose files
```

---

## Resource Tiers

| Tier | Memory Request | Memory Limit | CPU Request | CPU Limit | Services |
|------|---------------|--------------|------------|-----------|----------|
| Lightweight | 64Mi | 128Mi | 50m | 100m | migrate, topics-init |
| Standard | 128Mi | 256Mi | 100m | 250m | API-only, worker |
| Medium | 256Mi | 512Mi | 200m | 500m | API+Orchestrator |
| Heavy | 512Mi | 1Gi | 500m | 1000m | reporting |

---

## Service-to-Role Mapping

| Service | Roles | Tier | API Port | Metrics Port |
|---------|-------|------|----------|--------------|
| order-service | api, worker, orchestrator | Medium | 8080 | 9090 |
| notification-service | api, worker | Standard | 8081 | 9091 |
| customer-service | api, worker | Standard | 8082 | 9092 |
| catalog-service | api, worker, orchestrator | Medium | 8083 | 9093 |
| reporting-service | api, consumer | Heavy | 8084 | 9094 |
| payment-service | api, worker | Standard | 8086 | 9096 |
| inventory-service | api, worker | Standard | TBD | TBD |
| shipping-service | api, worker | Standard | TBD | TBD |

---

## CI/CD Pipeline Integration

### Build Stage
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag "${REGISTRY}/${SERVICE}:${SHA}" \
  --push \
  -f "services/${SERVICE}/Dockerfile.${SERVICE}"
```

### ArgoCD Sync
```yaml
# ArgoCD watches the overlays path and syncs on changes
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

### Image Tag Strategy
- CI: Use git SHA (e.g., `sha-abc1234`)
- Releases: Use semver tag (e.g., `v1.2.3`)
- Latest: Track main branch (e.g., `latest`)

---

## Security Considerations

### Container Security
- All images use distroless/static-debian12:nonroot (UID 65532)
- Security context prevents privilege escalation
- seccomp profile uses RuntimeDefault
- Capabilities dropped (ALL)

### Network Security
- Default deny-all NetworkPolicy per namespace
- Explicit allow rules for DNS, OTel, service-to-service
- Ingress via IngressController only

### Secrets Security
- No secrets in Git (only ExternalSecret references)
- Vault backend with Kubernetes auth
- Secrets encrypted at rest by Vault

---

## Migration Plan

### Phase 1: Docker Compose Resource Limits (Day 1)
1. Add `deploy.resources` blocks to existing Compose files
2. Test locally with resource constraints
3. Verify no breaking changes

### Phase 2: K8s Base Templates (Day 2-3)
1. Create `deploy/k8s/base/` directory
2. Generate Deployment, Service, ServiceAccount templates
3. Verify with `kustomize build`
4. Test on kind cluster

### Phase 3: Environment Overlays (Day 4-5)
1. Create staging overlay with reduced resources
2. Create production overlay with full resources
3. Test deployment workflow

### Phase 4: ArgoCD Integration (Day 6-7)
1. Install ArgoCD
2. Create AppProject and ApplicationSet
3. Configure sync policies
4. Test automated deployments

### Rollback
- Docker Compose: Remove `deploy.resources` blocks
- K8s: `kubectl delete -k deploy/k8s/overlays/<env>`
- ArgoCD: Disable auto-sync, manual reconciliation

---

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| K8s knowledge gap | Delay in debugging | Document common issues; pair with experienced team member |
| Resource miscalculation | OOM kills or throttling | Start conservative; adjust based on production metrics |
| Vault dependency | Local dev friction | Provide static secrets for local overlay |
| Multi-arch build time | CI slowdown | Use BuildKit cache; parallelize builds |
| ArgoCD complexity | Team adoption | Start with read-only access; gradual permissions |

---

## Open Questions

1. **Registry choice:** Which container registry for production? (GHCR, ECR, GCR, ACR)
2. **Cluster provisioning:** IaC tool for K8s cluster creation? (Terraform, Pulumi, eksctl)
3. **Service mesh:** Deferred to Phase 2 - Istio or Linkerd when ready?
4. **Canary deployments:** Initial rollout strategy or full replacement?
5. **Image signing:** Adopt Cosign for supply chain security?

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Kubernetes | 1.28+ | Container orchestration |
| Kustomize | 5.x | Template-free configuration |
| ArgoCD | 2.x | GitOps controller |
| External Secrets Operator | 0.9+ | Secrets management |
| Vault | 1.15+ | Secrets backend |
| OTel Collector | 0.156.0 | Observability (existing) |

---

## Testing Strategy

1. **Unit tests:** Validate Kustomize builds produce valid YAML
2. **Integration tests:** Deploy to kind cluster; verify pods start
3. **Smoke tests:** Run existing contract tests against K8s deployment
4. **Load tests:** Verify HPA scales correctly under load
5. **Chaos tests:** Verify PDB maintains availability during disruptions
