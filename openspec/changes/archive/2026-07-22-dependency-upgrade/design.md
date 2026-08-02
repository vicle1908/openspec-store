# Design: Dependency Upgrade

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPENDENCY UPGRADE ARCHITECTURE               │
└─────────────────────────────────────────────────────────────────┘

  CURRENT STATE:
  ══════════════

  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │ Temporal 1.29.7 │     │ PostgreSQL 17   │     │ Kafka 4.2.1     │
  │ (older version) │     │ (older version) │     │ (older version) │
  └─────────────────┘     └─────────────────┘     └─────────────────┘

  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │ pgx v5.9.2      │     │ pgx v5.10.0     │     │ go-redis v9.21.0│
  │ (catalog only)  │     │ (other services)│     │ (current)       │
  └─────────────────┘     └─────────────────┘     └─────────────────┘

  PROPOSED STATE:
  ═══════════════

  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │ Temporal 1.31.2 │     │ PostgreSQL 18.4 │     │ Kafka 4.3.1     │
  │ (latest + v2 GA)│     │ (latest stable) │     │ (latest stable) │
  └─────────────────┘     └─────────────────┘     └─────────────────┘

  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │ pgx v5.10.0     │     │ pgx v5.10.0     │     │ go-redis v9.21.0│
  │ (aligned)       │     │ (aligned)       │     │ (current)       │
  └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Technical Design

### 1. PostgreSQL Upgrade (17-alpine → 18.4-alpine)

**File:** `deploy/tools.env`

```bash
# Current
POSTGRES_VERSION=17-alpine

# Proposed
POSTGRES_VERSION=18.4-alpine
```

**Benefits:**
- Security fixes (5 CVEs): CVE-2026-6479, CVE-2026-6473, CVE-2026-6476, CVE-2026-6638, CVE-2026-6477
- Planner improvements (nondeterministic collation, partition pruning)
- Generated columns fixes
- Logical replication improvements
- Backup & recovery fixes
- Time zone data updated to 2026b

**Migration Path:**
1. Update `deploy/tools.env`
2. Test locally with `docker compose up -d`
3. Verify database operations
4. Deploy to staging
5. Deploy to production

**Note:** No dump/restore required for upgrades from 18.X. For upgrades from earlier versions, see PostgreSQL 18.2 release notes.

### 2. Kafka Upgrade (4.2.1 → 4.3.1)

**File:** `deploy/tools.env`

```bash
# Current
KAFKA_VERSION=4.2.1

# Proposed
KAFKA_VERSION=4.3.1
```

**Benefits:**
- Critical bugfixes including Kafka Streams RocksDB memory leak fix
- Stability improvements

**Migration Path:**
1. Update `deploy/tools.env`
2. Test locally with `docker compose up -d`
3. Verify Kafka operations
4. Deploy to staging
5. Deploy to production

### 3. Temporal Upgrade (v1.29.7 → v1.31.2)

**File:** `deploy/tools.env`

```bash
# Current
TEMPORAL_SERVER_VERSION=1.29.7

# Proposed
TEMPORAL_SERVER_VERSION=1.31.2
```

**Benefits:**
- Worker Versioning v2 GA (deployment APIs fully available)
- Security fix for CVE-2026-5724
- Serverless workers support (pre-release)
- Principal attribution for audit trails
- Cloud IAM auth for SQL databases
- Nexus overhaul with better error handling

**Migration Path:**
1. Update `deploy/tools.env`
2. Test locally with `docker compose up -d`
3. Verify workflow execution
4. Deploy to staging
5. Deploy to production

### 5. pgx Alignment (v5.9.2 → v5.10.0)

**Files:** `services/catalog-service/go.mod`, `services/*/go.mod`

**Current State:**
- catalog-service: pgx v5.9.2
- order-service: pgx v5.10.0
- notification-service: pgx v5.10.0
- payment-service: pgx v5.10.0
- shipping-service: pgx v5.10.0

**Proposed State:**
- All services: pgx v5.10.0

**Migration Path:**
1. Update `services/catalog-service/go.mod`
2. Run `go mod tidy` in catalog-service
3. Test catalog-service
4. Verify no breaking changes

### 6. Grafana Upgrade (13.1.0 → 13.1.1)

**File:** `deploy/tools.env`

```bash
# Current
GRAFANA_VERSION=13.1.0

# Proposed
GRAFANA_VERSION=13.1.1
```

**Benefits:**
- Go 1.26.5 update
- Provisioning improvements
- Bug fixes

### 7. Temporal SDK Alignment

**Files:** `services/*/go.mod`

**Current State:**
- temporal/sdk v1.46.0 (all services)

**Proposed State:**
- temporal/sdk v1.46.0+ (align with server v1.31.2)

**Note:** The SDK version should be compatible with server v1.31.2. Check temporal.io compatibility matrix.

## Configuration Changes

### Environment Variables

No new environment variables required. Existing configuration remains valid.

### Docker Compose Changes

Update image versions in `deploy/tools.env`:
```bash
TEMPORAL_SERVER_VERSION=1.31.2
GRAFANA_VERSION=13.1.1
```

### Kubernetes Changes

Update image versions in Kubernetes manifests:
- `deploy/k8s/base/redis-statefulset.yaml` — No changes (Redis already latest)
- `deploy/k8s/base/redis-configmap.yaml` — No changes

## Security Considerations

### CVE-2026-5724 (Temporal)
- **Severity:** MEDIUM
- **Impact:** Replication streaming endpoint authorization issue
- **Mitigation:** Set `system.disableStreamingAuthorizer` to `true` if using authorization + replication
- **Fixed in:** v1.31.2

### Dependency Scanning
- Run `govulncheck` after upgrade
- Verify no new vulnerabilities introduced
- Check for known issues in release notes

## Performance Considerations

### Temporal v1.31.2
- Worker Versioning v2 GA may have performance implications
- Test workflow execution latency before and after upgrade
- Monitor memory usage during upgrade

### pgx v5.10.0
- Check for performance improvements in release notes
- Benchmark critical database operations
- Verify connection pooling behavior unchanged

## Testing Strategy

### Unit Tests
- Run all existing unit tests
- Verify no breaking changes in API

### Integration Tests
- Test workflow execution with Temporal v1.31.2
- Test database operations with pgx v5.10.0
- Test Redis operations (unchanged)

### Performance Tests
- Benchmark critical paths
- Compare before/after metrics
- Verify no performance regression

### Security Tests
- Run vulnerability scan
- Verify CVE-2026-5724 mitigation
- Check for new security advisories

## Rollback Strategy

### Temporal Rollback
1. Revert `deploy/tools.env` to `TEMPORAL_SERVER_VERSION=1.29.7`
2. Redeploy Temporal server
3. Verify workflow execution

### pgx Rollback
1. Revert `services/catalog-service/go.mod` to pgx v5.9.2
2. Run `go mod tidy`
3. Redeploy catalog-service

### Grafana Rollback
1. Revert `deploy/tools.env` to `GRAFANA_VERSION=13.1.0`
2. Redeploy Grafana
3. Verify dashboards
