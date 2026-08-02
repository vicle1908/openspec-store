# OpenSpec: Deployment Platform Strategy

## Metadata

- **id**: deployment-platform-strategy
- **status**: draft
- **created**: 2026-07-16
- **updated**: 2026-07-16
- **authors**: [platform team]
- **reviewers**: [architects, devops]
- **related**: 
  - k8s-gitops-infrastructure
  - container-resource-standards
  - platform-runtime

## Purpose

The microservices platform supports local development via Docker Compose but lacks Kubernetes deployment capabilities. Production deployments require cloud-native orchestration, GitOps-based pipelines, and consistent deployment semantics.

## Goals

1. **Extend** the existing layered Compose pattern to Kubernetes
2. **Maintain** parity between local development and production deployment
3. **Adopt** GitOps practices for declarative infrastructure
4. **Standardize** resource allocation across all services
5. **Enable** zero-downtime deployments with rolling updates

---

## Current State

| Component | Current | Assessment |
|-----------|---------|------------|
| Multi-stage builds | golang → distroless/nonroot | ✅ Good |
| Health checks | `/health/ready` with timeout | ✅ Good |
| Layer caching | Separate go mod download | ✅ Good |
| Multi-arch | verify-images.sh | ✅ Good |
| Resource limits | None | ❌ Missing |
| K8s manifests | None | ❌ Missing |
| Secrets | env_file + env vars | ⚠️ Needs K8s native |

---

## Proposed Solution

### Target Architecture

```
deploy/
├── k8s/
│   ├── base/                    # Shared templates
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       ├── local/
│       ├── staging/
│       └── production/
└── argocd/
    └── applications.yaml
```

### Deployment Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: SERVICE_NAME
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
  template:
    spec:
      serviceAccountName: SERVICE_NAME
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
      containers:
      - name: SERVICE_NAME
        image: $IMAGE
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
        securityContext:
          allowPrivilegeEscalation: false
          seccompProfile:
            type: RuntimeDefault
          capabilities:
            drop:
            - ALL
```

### HPA Template

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: SERVICE_NAME-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: SERVICE_NAME
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Service Inventory

| Service | API Port | Metrics | Tier |
|---------|----------|---------|------|
| order-service | 8080 | 9090 | API+Orchestrator |
| notification-service | 8081 | 9091 | API+Worker |
| customer-service | 8082 | 9092 | API+Worker |
| catalog-service | 8083 | 9093 | API+Orchestrator |
| reporting-service | 8084 | 9094 | Heavy |
| payment-service | 8086 | 9096 | API+Worker |
| inventory-service | TBD | TBD | API+Worker |
| shipping-service | TBD | TBD | API+Worker |

---

## Requirements

### Requirement: Hosted deployment strategy remains declarative

Hosted deployment configuration SHALL preserve local Compose as the
development topology while using declarative Kubernetes and GitOps promotion
for hosted environments.

#### Scenario: A hosted environment is promoted

- **WHEN** a reviewed application revision is promoted beyond local development
- **THEN** the target environment is reconciled from version-controlled manifests
- **AND** local Compose evidence is not represented as hosted deployment proof

## Implementation Phases

### Phase 1: Foundation
- [ ] Create deploy/k8s/base/ templates
- [ ] Create deploy/k8s/overlays/{local,staging,production}/
- [ ] Add resource limits to Docker Compose

### Phase 2: GitOps
- [ ] Set up ArgoCD ApplicationSet
- [ ] Configure secrets management

### Phase 3: Production
- [ ] Enable HPA for all services
- [ ] Add network policies
- [ ] Implement service mesh

---

## Open Questions

1. Service mesh: Istio or K8s native?
2. Registry: GHCR, ECR, GCR, or ACR?
3. Image signing: Adopt Cosign?
4. Secrets: ExternalSecrets Operator vs. Vault?

---

## References

- [K8s Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [ArgoCD](https://argo-cd.readthedocs.io/)
- [Kustomize](https://kubectl.docs.kubernetes.io/)
