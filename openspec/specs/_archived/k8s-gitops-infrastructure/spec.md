# OpenSpec: Kubernetes GitOps Infrastructure

## Metadata

- **id**: k8s-gitops-infrastructure
- **status**: draft
- **created**: 2026-07-16
- **updated**: 2026-07-16
- **authors**: [devops team]
- **reviewers**: [architects, platform team]
- **related**: deployment-platform-strategy, platform-observability

## Purpose

The platform needs a production-grade Kubernetes infrastructure supporting GitOps deployments, multi-environment promotion, secure secrets management, and zero-downtime deployments.

## Goals

1. Define K8s cluster requirements and naming conventions
2. Establish GitOps workflow using ArgoCD
3. Standardize namespace and service account structure
4. Integrate with existing OTel Collector (v0.156.0)
5. Provide secrets management strategy

---

## Cluster Architecture

### Cluster Per Environment

```
┌─────────────────────────────────────────────────────────────┐
│              microservices-platform                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   local/kind    │     staging     │        production       │
│   (development) │   (pre-prod)    │     (production)        │
│  • Local kind   │  • Cloud K8s    │  • Multi-AZ K8s        │
│  • Single node  │  • 3 nodes      │  • 5+ nodes            │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Namespace Structure

```yaml
# namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: microservices
  labels:
    istio-injection: enabled
---
apiVersion: v1
kind: Namespace
metadata:
  name: microservices-staging
  labels:
    istio-injection: enabled
---
apiVersion: v1
kind: Namespace
metadata:
  name: observability
```

---

## GitOps Workflow

### Repository Structure

```
deploy/
├── k8s/
│   ├── base/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── networkpolicy.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       ├── local/
│       ├── staging/
│       └── production/
└── argocd/
    └── applications.yaml
```

### Kustomize Base Configuration

```yaml
# deploy/k8s/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

commonLabels:
  app.kubernetes.io/part-of: microservices-platform
  app.kubernetes.io/managed-by: kustomize

resources:
- deployment.yaml
- service.yaml
- hpa.yaml
- pdb.yaml
- serviceaccount.yaml

namespace: microservices
```

### Production Overlay

```yaml
# deploy/k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: microservices

resources:
- ../../base

patches:
- path: resources.yaml
  target:
    kind: Deployment

replicas:
- name: SERVICE_NAME
  count: 3
```

---

## ArgoCD ApplicationSet

```yaml
# deploy/argocd/applications.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices-services
spec:
  generators:
  - matrix:
      generators:
      - grid:
          values:
            service:
              - order-service
              - notification-service
              - customer-service
              - catalog-service
              - reporting-service
              - payment-service
      - grid:
          values:
            environment:
              - staging
              - production
  template:
    spec:
      project: microservices
      source:
        repoURL: https://github.com/org/microservices
        targetRevision: HEAD
        path: deploy/k8s/overlays/{{environment}}
      destination:
        server: '{{values.cluster}}'
        namespace: microservices
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

---

## Secrets Management

### External Secrets Operator

```yaml
# deploy/k8s/base/externalsecret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: SERVICE_NAME-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: SERVICE_NAME-secrets
    creationPolicy: Owner
  data:
  - secretKey: DATABASE_URL
    remoteRef:
      key: SERVICE_NAME/database
      property: url
```

---

## Observability Integration

### OTel Collector Sidecar

```yaml
# Part of deployment.yaml
- name: otel-agent
  image: otel/opentelemetry-collector-contrib:0.156.0
  args:
  - --config=/etc/otel-agent-config/config.yaml
  env:
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector:4317"
```

---

## CI/CD Pipeline

### Build and Push

```bash
#!/bin/bash
# scripts/ci/build-and-push.sh

SERVICE_NAME="${1:-}"
IMAGE_TAG="${2:-$(git rev-parse --short HEAD)}"
REGISTRY="${REGISTRY:-ghcr.io/org}"

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag "${REGISTRY}/${SERVICE_NAME}:${IMAGE_TAG}" \
  --push \
  -f "services/${SERVICE_NAME}/Dockerfile.${SERVICE_NAME}" \
  .

cosign sign --yes "${REGISTRY}/${SERVICE_NAME}:${IMAGE_TAG}"
```

---

## Requirements

### Requirement: GitOps infrastructure separates environment ownership

Kubernetes GitOps configuration SHALL identify environment-specific
namespaces, service accounts, secrets, observability, and promotion ownership
without embedding production credentials in repository manifests.

#### Scenario: GitOps reconciles an environment

- **WHEN** the environment's reviewed desired state changes
- **THEN** the GitOps controller reconciles only that environment's declared resources
- **AND** secrets remain supplied through the configured external secret boundary

## Migration Checklist

- [ ] K8s clusters provisioned
- [ ] ArgoCD installed
- [ ] Vault/External Secrets configured
- [ ] Container registry accessible
- [ ] Per-service overlay created
- [ ] Rollback tested

---

## References

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kustomize Reference](https://kubectl.docs.kubernetes.io/)
- [External Secrets Operator](https://external-secrets.io/)
