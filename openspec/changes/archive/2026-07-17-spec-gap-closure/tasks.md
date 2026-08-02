# Spec Gap Closure — Implementation Tasks

## Phase 1: Critical — Test Coverage (Blocks Production Readiness)

### 1.1 customer-service test expansion
- [ ] Add unit tests for domain/customer aggregate (state transitions, invariants)
- [ ] Add unit tests for GDPR export/purge workflows
- [ ] Add unit tests for HTTP handlers (request validation, response formatting)
- [ ] Add unit tests for Postgres repository (CRUD operations, error paths)
- [ ] Add architecture test: sole-writer rule
- [ ] Add architecture test: ports-are-interfaces
- [ ] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.2 notification-service test expansion
- [ ] Add unit tests for domain/notification aggregate (status transitions)
- [ ] Add unit tests for dispatcher (provider selection, retry logic)
- [ ] Add unit tests for rate limiter
- [ ] Add unit tests for HTTP handlers
- [ ] Add unit tests for Postgres repository
- [ ] Add architecture test: sole-writer rule
- [ ] Add architecture test: adapter-implements-one-port
- [ ] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.3 payment-service test expansion
- [ ] Add unit tests for domain/payment aggregate
- [ ] Add unit tests for Temporal activities and workflow
- [ ] Add unit tests for HTTP handlers
- [ ] Add unit tests for Postgres repository
- [ ] Add architecture test: sole-writer rule
- [ ] Add architecture test: ports-are-interfaces
- [ ] Add architecture test: deterministic-workflow
- [ ] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.4 inventory-service test expansion
- [ ] Add unit tests for domain/reservation aggregate
- [ ] Add unit tests for Temporal activities and workflow
- [ ] Add unit tests for HTTP handlers
- [ ] Add unit tests for Postgres repository
- [ ] Add architecture test: sole-writer rule
- [ ] Add architecture test: deterministic-workflow
- [ ] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.5 shipping-service test expansion
- [ ] Add unit tests for domain/shipment aggregate
- [ ] Add unit tests for Temporal activities and workflow
- [ ] Add unit tests for HTTP handlers
- [ ] Add unit tests for Postgres repository
- [ ] Add architecture test: sole-writer rule
- [ ] Add architecture test: deterministic-workflow
- [ ] Verify coverage reaches ≥90% unit, ≥80% integration

## Phase 2: High — Architecture Test Expansion

### 2.1 Expand catalog-service architecture tests
- [ ] Add sole-writer test
- [ ] Add ports-are-interfaces test
- [ ] Add adapter-implements-one-port test
- [ ] Add build-tag-isolation test
- [ ] Add cache-keyspace test (ADR-gated)
- [ ] Verify all 12 categories pass

### 2.2 Expand customer-service architecture tests
- [ ] Add all 12 hexagonal enforcement categories
- [ ] Verify cross-service import test passes

### 2.3 Expand notification-service architecture tests
- [ ] Add all 12 hexagonal enforcement categories
- [ ] Verify cross-service import test passes

### 2.4 Expand payment/inventory/shipping architecture tests
- [ ] Add all applicable hexagonal enforcement categories to each
- [ ] Add deterministic-workflow test to each
- [ ] Add worker-versioning test to each

### 2.5 Cross-service architecture test
- [ ] Implement TestHypotheticalPeerServiceCannotImportOrderInternals
- [ ] Wire into CI pipeline (make verify-pr)

## Phase 3: High — K8s/ArgoCD Gaps

### 3.1 K8s NetworkPolicy egress rules
- [ ] Add PostgreSQL egress rule (port 5432) to networkpolicy-allow-system.yaml
- [ ] Add Kafka egress rule (port 9092) to networkpolicy-allow-system.yaml
- [ ] Verify rules apply to all service pods via label selector

### 3.2 ArgoCD improvements
- [ ] Add CreateNamespace sync option to ApplicationSet
- [ ] Add retry with 5 attempts and exponential backoff
- [ ] Update repoURL from placeholder to actual repository URL
- [ ] Add ArgoCD Image Updater configuration
- [ ] Add ArgoCD notification integration

### 3.3 Kustomize placeholder resolution
- [ ] Resolve SERVICE_NAME placeholder in base/kustomization.yaml replacements block
- [ ] Verify per-service production overlays apply correct nameSuffix

### 3.4 services-verify Makefile update
- [ ] Add payment-service, inventory-service, shipping-service to services-verify loop
- [ ] Verify make services-verify runs all 8 services

## Phase 4: Medium — Operational Readiness

### 4.1 Broker UI
- [ ] Add kafbat/kafka-ui to deploy/docker-compose.tools.yaml
- [ ] Pin KAFKA_UI_VERSION in deploy/tools.env
- [ ] Add to verify-images check

### 4.2 Rollback rehearsal
- [ ] Create scripts/rehearse-rollback.sh
- [ ] Add make test-rollback-rehearsal target
- [ ] Wire into release-evidence.yml

### 4.3 Service runbooks
- [ ] Create docs/runbooks/ directory
- [ ] Create runbook for order-service
- [ ] Create runbook for customer-service
- [ ] Create runbook for catalog-service
- [ ] Create runbook for notification-service
- [ ] Create runbook for reporting-service
- [ ] Create runbook for payment/inventory/shipping services

### 4.4 Agent config wiring
- [ ] Create .claude/settings.json with agentmemory MCP config
- [ ] Create .cursor/mcp.json with agentmemory config
- [ ] Create .codex/config.toml with agentmemory config
- [ ] Add CI sidecar for agentmemory in verify.yml

### 4.5 Payment-service Dockerfile modernization
- [ ] Add --platform=$BUILDPLATFORM build arg
- [ ] Add -pgo=auto build flag
- [ ] Add HEALTHCHECK instruction
- [ ] Verify matches canonical Dockerfile.platform template

## Phase 5: Low — Platform Feature Gaps

### 5.1 Kafka retry-topic chain
- [ ] Implement RetryConsumer in platform/kafka/
- [ ] Add retry topic creation to provision-topics scripts
- [ ] Wire retry consumer into notification-service and reporting-service
- [ ] Add DLQ monitoring

### 5.2 Worker Versioning v2
- [ ] Implement build-ID based worker versioning in platform/temporal/
- [ ] Wire into all services with Temporal workers
- [ ] Add version compatibility tests

### 5.3 Circuit breaker pattern
- [ ] Design circuit breaker interface in platform/
- [ ] Implement for HTTP client calls (order→customer, order→catalog)
- [ ] Add configuration and metrics

### 5.4 Fuzz testing expansion
- [ ] Add fuzz tests for customer-service HTTP handlers
- [ ] Add fuzz tests for notification-service handlers
- [ ] Add fuzz tests for catalog-service handlers
- [ ] Wire fuzz tests into CI pipeline

## Verification

After all tasks complete:
- [ ] Run `make verify-pr` — all services pass
- [ ] Run `make test-e2e` — cross-service smoke passes
- [ ] Run `make verify-images` — all images multi-arch
- [ ] Verify test coverage: order ≥90/90/80, all others ≥90/80/70
- [ ] Verify architecture tests: all services pass 12+ categories
- [ ] Verify K8s manifests: kustomize build succeeds for all overlays
- [ ] Verify ArgoCD: application sync succeeds in staging
