# Dependency Upgrade Proposal

## Why

The platform's dependencies are mostly current, but several key libraries have newer versions available with important features and security fixes. This upgrade proposal covers:

1. **PostgreSQL 17-alpine → 18.4-alpine**: Latest stable with security fixes (CVE-2026-6479, CVE-2026-6473, CVE-2026-6476, CVE-2026-6638, CVE-2026-6477)
2. **Kafka 4.2.1 → 4.3.1**: Bugfix release with critical fixes including Kafka Streams RocksDB memory leak fix
3. **Temporal v1.29.7 → v1.31.2**: Worker Versioning v2 GA, security fixes (CVE-2026-5724)
4. **pgx v5.9.2 → v5.10.0**: Align versions across services (catalog uses v5.9.2, others use v5.10.0)
5. **Grafana 13.1.0 → 13.1.1**: Go update, provisioning improvements, bug fixes
6. **Redis 8.8-alpine**: Already latest Redis Open Source version (Redis Software 8.2.0-25 is Enterprise, not applicable)

## What Changes

### Docker Images

| Image | Current | Target | Changes |
|-------|---------|--------|---------|
| PostgreSQL | 17-alpine | 18.4-alpine | Security fixes (5 CVEs), bug fixes |
| Kafka | 4.2.1 | 4.3.1 | Critical bugfixes including RocksDB memory leak |
| Temporal | 1.29.7 | 1.31.2 | Worker Versioning v2 GA, security fixes |
| Grafana | 13.1.0 | 13.1.1 | Go update, bug fixes |
| Redis | 8.8-alpine | 8.8-alpine | Already latest (Redis Open Source) |

### Go Dependencies

| Package | Current | Target | Changes |
|---------|---------|--------|---------|
| temporal/sdk | v1.46.0 | v1.46.0+ | Align with server v1.31.2 |
| pgx/v5 | v5.9.2 (catalog) | v5.10.0 | Align across all services |
| go-redis/v9 | v9.21.0 | v9.21.0 | Already latest |
| franz-go | v1.21.5 | v1.21.5 | Already latest |

## Capabilities

### New Capabilities

- `temporal-upgrade`: Upgrade Temporal to v1.31.2 with Worker Versioning v2 GA, security fixes, and new features
- `dependency-alignment`: Align pgx versions across all services to v5.10.0

### Modified Capabilities

- `platform-infrastructure`: Update Docker image versions in tools.env

## Impact

### Affected Code
- `deploy/tools.env` — Update image versions
- `services/*/go.mod` — Update Go dependencies
- `services/*/go.sum` — Update dependency checksums

### Affected Infrastructure
- Docker Compose files — Use updated image versions
- Kubernetes manifests — Use updated image versions

### Dependencies
- Temporal v1.31.2 (security fix for CVE-2026-5724)
- pgx v5.10.0 (align versions)

### Compatibility
- **Non-breaking** — All updates are backward compatible
- Worker Versioning v2 GA is fully compatible with existing workflows
- pgx v5.10.0 is backward compatible with v5.9.2

### Rollout
1. Update `deploy/tools.env` with new versions
2. Update `go.mod` files with new dependencies
3. Run `go mod tidy` to update checksums
4. Test locally with Docker Compose
5. Deploy to staging
6. Deploy to production

### Rollback
- Revert `deploy/tools.env` to previous versions
- Revert `go.mod` files to previous versions
- Run `go mod tidy`
- Redeploy

## Temporal v1.31.2 Features

### Worker Versioning v2 GA
- Deployment APIs are now fully general availability
- Better deployment versioning for workflow and activity workers
- Improved compatibility across versions

### Serverless Workers (Pre-release)
- Workers can run on serverless platforms (AWS Lambda, etc.)
- Automatic invocation and scale-to-zero support
- Reduced infrastructure costs for intermittent workloads

### Principal Attribution
- Server-computed, immutable field in workflow history events
- Provides trustworthy "who did this?" attribution
- Useful for audit trails and compliance

### Cloud IAM Auth for SQL
- New `passwordCommand` config for IAM-based authentication
- Supports AWS RDS, GCP Cloud SQL, and other cloud-managed databases
- Improves security for cloud deployments

### Nexus Overhaul
- Complete rework of error handling
- Nexus now always enabled by default
- Caller timeout support added

### CHASM Framework
- Enabled by default with separate `businessID` spaces
- Supports different archetypes for workflow isolation

### Standalone Activities
- Activities can run independently of workflows
- Gated behind a dynamic config flag
- Useful for fire-and-forget operations

## Security Fixes

### CVE-2026-5724 (MEDIUM)
- Replication streaming endpoint authorization issue
- Users with authorization + replication setups should set `system.disableStreamingAuthorizer` to `true`
- Fixed in v1.31.2

## Validation Plan

1. **Unit Tests**: Run all existing unit tests
2. **Integration Tests**: Run integration tests with updated dependencies
3. **Temporal Tests**: Test workflow execution with v1.31.2
4. **Performance Tests**: Benchmark critical paths
5. **Security Scan**: Run vulnerability scan on updated dependencies

## Timeline

- **Week 1**: Update tools.env and go.mod files
- **Week 2**: Test locally with Docker Compose
- **Week 3**: Deploy to staging and run integration tests
- **Week 4**: Deploy to production
