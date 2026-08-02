# Tasks: Dependency Upgrade

## Phase 1: PostgreSQL Upgrade

### 1.1 Update tools.env
- [x] Update `POSTGRES_VERSION` from 17-alpine to 18.4-alpine
- [x] Verify image availability

### 1.2 Test PostgreSQL Upgrade
- [x] Test database operations with PostgreSQL 18.4
- [x] Verify all services connect correctly
- [x] Run unit tests
- [x] Run integration tests

## Phase 2: Kafka Upgrade

### 2.1 Update tools.env
- [x] Update `KAFKA_VERSION` from 4.2.1 to 4.3.1
- [x] Verify image availability

### 2.2 Test Kafka Upgrade
- [x] Test Kafka operations with 4.3.1
- [x] Verify producer/consumer functionality
- [x] Run integration tests

## Phase 3: Temporal Upgrade

### 3.1 Update tools.env
- [x] Update `TEMPORAL_SERVER_VERSION` from 1.29.7 to 1.31.2
- [x] Verify image availability

### 3.2 Update Temporal SDK
- [x] Update `go.temporal.io/sdk` in all service go.mod files
- [x] Run `go mod tidy` in each service
- [x] Verify no breaking changes

### 3.3 Test Temporal Upgrade
- [x] Test workflow execution with v1.31.2
- [x] Verify Worker Versioning v2 works
- [x] Test security fix (CVE-2026-5724)
- [x] Run integration tests

## Phase 4: pgx Alignment

### 4.1 Update catalog-service pgx
- [x] Update `github.com/jackc/pgx/v5` in catalog-service/go.mod from v5.9.2 to v5.10.0
- [x] Run `go mod tidy` in catalog-service
- [x] Verify no breaking changes

### 4.2 Validate Alignment
- [x] Verify all services use pgx v5.10.0
- [x] Run unit tests in catalog-service
- [x] Run integration tests

## Phase 5: Grafana Upgrade

### 5.1 Update tools.env
- [x] Update `GRAFANA_VERSION` from 13.1.0 to 13.1.1
- [x] Verify image availability

### 5.2 Test Grafana Upgrade
- [x] Verify dashboards load correctly
- [x] Test provisioning improvements
- [x] Verify bug fixes

## Phase 6: Validation

### 6.1 Unit Tests
- [x] Run all unit tests across services
- [x] Verify no breaking changes

### 6.2 Integration Tests
- [x] Run integration tests with updated dependencies
- [x] Test workflow execution
- [x] Test database operations

### 6.3 Security Scan
- [x] Run `govulncheck` on all services
- [x] Verify CVE-2026-5724 mitigation (Temporal)
- [x] Verify CVE-2026-6479, CVE-2026-6473, CVE-2026-6476, CVE-2026-6638, CVE-2026-6477 mitigation (PostgreSQL)
- [x] Check for new security advisories

### 6.4 Performance Tests
- [x] Benchmark critical paths
- [x] Compare before/after metrics
- [x] Verify no performance regression

## Phase 7: Deployment

### 7.1 Local Testing
- [x] Deploy locally with Docker Compose
- [x] Verify all services start correctly
- [x] Test end-to-end workflows

### 7.2 Staging Deployment
- [x] Deploy to staging environment
- [x] Run full integration test suite
- [x] Verify monitoring and alerting

### 7.3 Production Deployment
- [x] Deploy to production
- [x] Monitor for issues
- [x] Verify all services healthy

## Phase 8: Documentation

### 8.1 Update Documentation
- [x] Update architecture docs with new versions
- [x] Update runbooks with new procedures
- [x] Update dependency matrix

### 8.2 Create Upgrade Runbook
- [x] Document upgrade steps
- [x] Document rollback procedures
- [x] Document validation steps
