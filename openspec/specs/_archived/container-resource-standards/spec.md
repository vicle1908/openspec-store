# OpenSpec: Container Resource Standards

## Metadata

- **id**: container-resource-standards
- **status**: draft
- **created**: 2026-07-16
- **updated**: 2026-07-16
- **authors**: [platform team]
- **reviewers**: [devops, architects]
- **related**: deployment-platform-strategy, k8s-gitops-infrastructure

## Purpose

Current docker-compose files lack explicit resource limits. This leads to:
1. Unpredictable resource consumption in production
2. No autoscaling basis for Kubernetes
3. Difficulty in capacity planning
4. Potential resource starvation of other services

## Goals

1. Define memory and CPU limits for all service roles
2. Add limits to Docker Compose for local parity
3. Provide HPA baseline metrics
4. Document burst/limit ratios

---

## Resource Tiers

### Tier 1: Lightweight Services

| Role | Request Memory | Limit Memory | Request CPU | Limit CPU |
|------|---------------|-------------|-------------|-----------|
| **API-only** | 64Mi | 128Mi | 50m | 100m |
| **Consumer** | 64Mi | 128Mi | 50m | 100m |
| **Scheduler** | 64Mi | 128Mi | 50m | 100m |

### Tier 2: Standard Services

| Role | Request Memory | Limit Memory | Request CPU | Limit CPU |
|------|---------------|-------------|-------------|-----------|
| **API + Worker** | 128Mi | 256Mi | 100m | 250m |
| **API + Consumer** | 128Mi | 256Mi | 100m | 250m |

### Tier 3: Medium Services

| Role | Request Memory | Limit Memory | Request CPU | Limit CPU |
|------|---------------|-------------|-------------|-----------|
| **API + Orchestrator** | 256Mi | 512Mi | 200m | 500m |
| **Temporal Worker Heavy** | 256Mi | 512Mi | 200m | 500m |

### Tier 4: Heavy Services

| Role | Request Memory | Limit Memory | Request CPU | Limit CPU |
|------|---------------|-------------|-------------|-----------|
| **Reporting/Analytics** | 512Mi | 1Gi | 500m | 1000m |
| **ML/AI Processing** | 1Gi | 2Gi | 1000m | 2000m |

---

## Service Resource Mapping

| Service | Roles | Tier | Request Memory | Limit Memory | Request CPU | Limit CPU |
|---------|-------|------|---------------|-------------|-------------|-----------|
| notification-service | API + Worker | Tier 2 | 128Mi | 256Mi | 100m | 250m |
| customer-service | API + Worker | Tier 2 | 128Mi | 256Mi | 100m | 250m |
| catalog-service | API + Orchestrator | Tier 3 | 256Mi | 512Mi | 200m | 500m |
| reporting-service | API + Consumer | Tier 4 | 512Mi | 1Gi | 500m | 1000m |
| payment-service | API + Worker | Tier 2 | 128Mi | 256Mi | 100m | 250m |
| inventory-service | API + Worker | Tier 2 | 128Mi | 256Mi | 100m | 250m |
| shipping-service | API + Worker | Tier 2 | 128Mi | 256Mi | 100m | 250m |
| order-service | API + Orchestrator | Tier 3 | 256Mi | 512Mi | 200m | 500m |

---

## Docker Compose Integration

### Add to Base docker-compose.yaml

```yaml
services:
  order-service-api:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.2'
  
  order-service-worker:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.2'
  
  order-service-orchestrator:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.2'
```

---

## Kubernetes HPA Baselines

### CPU-Based HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: SERVICE_NAME-hpa-cpu
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

### Memory-Based HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: SERVICE_NAME-hpa-memory
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
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Combined HPA with Behavior

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
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
```

---

## Requirements

### Requirement: Container workloads use bounded resource profiles

Repository deployment definitions SHALL assign reviewed CPU and memory
requests or limits from the documented resource tiers before a workload is
treated as production-ready.

#### Scenario: Workload resource policy is evaluated

- **WHEN** a service deployment is reviewed for promotion
- **THEN** its API, worker, scheduler, and migration roles identify their resource tier
- **AND** missing or unreviewed resource bounds remain an explicit readiness gap

## Implementation Checklist

- [ ] Add resource limits to docker-compose.yaml (base)
- [ ] Add resource limits to each service overlay
- [ ] Create k8s/base/hpa.yaml templates
- [ ] Update verify-images to check resource annotations
- [ ] Document in deploy/README.md

---

## References

- [K8s Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [HPA Metrics](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Docker Compose Resources](https://docs.docker.com/compose/compose-file/compose-file-v3/#resources)
