# ADR 001: Docker Compose over Kubernetes for Single-Host Deployment

## Status

Accepted

## Context

Our team needs to deploy an artifact repository for Android (Maven2/AAR) and iOS (Swift SPM) artifact management. The infrastructure will run on a single server initially, serving a small mobile development team (normal scale per user's requirements).

Key constraints:
- Single host (no cluster available)
- Small team (no need for horizontal scaling)
- Limited DevOps expertise
- Need rapid deployment and easy maintenance

## Decision

We will use **Docker Compose** as the deployment orchestration instead of Kubernetes.

## Consequences

### Positive

- **Simpler operations**: No cluster management, no node pools, no scheduling
- **Faster deployment**: `docker compose up` vs cluster provisioning
- **Easier backup**: Single named volume `nexus-data` to archive
- **Lower resource overhead**: No kubelet, no control plane overhead
- **Straightforward networking**: Docker bridge network, simple service names
- **Good migration path**: Compose files can be migrated to Kubernetes later with kompose or manual conversion

### Negative

- **No horizontal scaling**: Cannot run multiple Nexus replicas
- **No auto-healing**: No pod rescheduling on node failure
- **No rolling updates**: Full restart required for updates
- **Future migration cost**: Moving to Kubernetes later requires effort

## Alternatives Considered

| Alternative | Rejected Because |
|------------|-----------------|
| Kubernetes (single node) | Massive complexity for one container; needs cluster setup |
| Kubernetes (managed EKS/GKE) | Cost overhead; unnecessary for single container |
| Docker Swarm | Effectively deprecated; no future |
| Podman + systemd | More complex than Compose for small team |
| Raw Docker (no Compose) | No dependency management, no declarative config |

## Validation

- ✅ `docker compose up` starts both nexus and nginx services
- ✅ `docker compose down` gracefully shuts down with 120s timeout
- ✅ Single volume backup tested: `docker run --rm -v nexus-data:/data alpine tar czf ...`
