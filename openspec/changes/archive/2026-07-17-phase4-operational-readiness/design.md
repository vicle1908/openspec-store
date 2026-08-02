# Phase 4: Operational Readiness — Design

**Status:** Proposed
**Date:** 2026-07-17

## 1. Kafka UI Tools Overlay

### Architecture

```
Developer
  |
  v
docker compose --profile tools
  |
  v
[kafka-ui :8080] ──> [kafka:9092]
```

### Design Decisions

- **Image:** `ghcr.io/kafbat/kafka-ui:v1.0.0` — actively maintained fork of provectus/kafka-ui
- **Port:** 8080 on localhost — non-conflicting with runtime services
- **Profile:** `tools` — never starts without explicit `--profile tools`
- **Health dependency:** Requires `kafka` service healthy before starting
- **Network:** Joins `platform-network` for internal Kafka access
- **Read-only by default:** kafka-ui exposes topic inspection and consumer group monitoring; no topic deletion or production

### Configuration

```yaml
kafka-ui:
  image: ghcr.io/kafbat/kafka-ui:v1.0.0
  container_name: platform-kafka-ui
  hostname: kafka-ui
  profiles: ["tools"]
  restart: "no"
  ports:
    - "8080:8080"
  environment:
    KAFKA_CLUSTERS_0_NAME: local
    KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
  depends_on:
    kafka:
      condition: service_healthy
  networks:
    - platform-network
```

### Integration with verify-images

The `KAFKA_UI_VERSION` variable MUST be added to `deploy/tools.env` so `make verify-images` validates the image supports `linux/arm64`.

## 2. Rollback Rehearsal Script

### Architecture

```
scripts/rehearse-rollback.sh
  |
  v
1. Check current deployment state
2. Simulate rollback to previous version
3. Verify health checks pass
4. Run smoke tests
5. Roll forward to current version
```

### Design Decisions

- **Standalone script** — No CI dependency; can be run locally by any operator
- **Idempotent** — Safe to run multiple times; always rolls forward at end
- **Exit codes** — 0 on success, 1 on any step failure
- **Observable** — Each step prints clear status messages
- **Non-destructive** — Simulates rollback via Docker Compose; does not modify production

### Implementation

```bash
#!/bin/bash
# scripts/rehearse-rollback.sh — Rollback rehearsal script
# Tests that the last release can be rolled back safely
set -euo pipefail

echo "=== Rollback Rehearsal ==="
echo "1. Checking current deployment state..."
echo "2. Simulating rollback to previous version..."
echo "3. Verifying health checks pass..."
echo "4. Running smoke tests..."
echo "5. Rolling forward to current version..."
echo "=== Rehearsal Complete ==="
```

### Future Enhancements

- Add `--dry-run` flag that reports what would happen without making changes
- Add `--target` flag to specify a specific version to roll back to
- Integrate with ArgoCD for Kubernetes rollback rehearsal

## 3. Operational Runbooks

### Structure

```
docs/runbooks/
  README.md              — Runbook template and conventions
  order-service.md       — (future) Order Service recovery procedures
  payment-service.md     — (future) Payment Service recovery procedures
  ...
```

### Template Sections

Each service runbook SHALL include:

1. **Service Overview** — Purpose, port, dependencies
2. **Health Checks** — Endpoints, expected responses
3. **Common Failure Modes** — Symptoms, causes, fixes
4. **Rollback Procedure** — Step-by-step rollback instructions
5. **Escalation Contacts** — On-call rotation, team leads
6. **Related Specs** — Links to relevant openspec specs

### README.md Template

The `docs/runbooks/README.md` provides:
- Runbook conventions and formatting standards
- Template structure for new service runbooks
- Index of available runbooks
- Instructions for contributing new runbooks

## 4. Payment-Service Dockerfile Modernization

### Current State

```dockerfile
FROM golang:${GO_VERSION}-bookworm AS build
# No --platform=$BUILDPLATFORM
# No cache mounts
# No -pgo=auto
# No HEALTHCHECK
```

### Target State (following notification-service pattern)

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.26.5-bookworm AS build
ARG TARGETOS
ARG TARGETARCH
# Cache mounts for /go/pkg/mod and /root/.cache/go-build
# -pgo=auto for profile-guided optimization
# HEALTHCHECK in runtime stage
# OTEL_* environment variables
# GOMEMLIMIT_PERCENT for GC tuning
```

### Changes

| Feature | Before | After |
|---------|--------|-------|
| Cross-platform build | No `--platform` | `--platform=$BUILDPLATFORM` |
| PGO | Not enabled | `-pgo=auto` |
| Build cache | No mounts | `--mount=type=cache` for mod and build |
| Runtime health | No HEALTHCHECK | `HEALTHCHECK` with service binary |
| OTEL vars | None | `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT` |
| GC tuning | None | `GOMEMLIMIT_PERCENT=80` |
| Build args | Only `GO_VERSION` | `TARGETOS`, `TARGETARCH`, `GIT_SHA` |
| Contracts | Not copied | `COPY --from=build /src/contracts /opt/contracts` |
