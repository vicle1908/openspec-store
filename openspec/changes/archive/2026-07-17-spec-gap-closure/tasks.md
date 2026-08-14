# Spec Gap Closure — Implementation Tasks

## Phase 1: Critical — Test Coverage (Blocks Production Readiness)

### 1.1 customer-service test expansion
- [x] [historical] Add unit tests for domain/customer aggregate (state transitions, invariants)
- [x] [historical] Add unit tests for GDPR export/purge workflows
- [x] [historical] Add unit tests for HTTP handlers (request validation, response formatting)
- [x] [historical] Add unit tests for Postgres repository (CRUD operations, error paths)
- [x] [historical] Add architecture test: sole-writer rule
- [x] [historical] Add architecture test: ports-are-interfaces
- [x] [historical] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.2 notification-service test expansion
- [x] [historical] Add unit tests for domain/notification aggregate (status transitions)
- [x] [historical] Add unit tests for dispatcher (provider selection, retry logic)
- [x] [historical] Add unit tests for rate limiter
- [x] [historical] Add unit tests for HTTP handlers
- [x] [historical] Add unit tests for Postgres repository
- [x] [historical] Add architecture test: sole-writer rule
- [x] [historical] Add architecture test: adapter-implements-one-port
- [x] [historical] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.3 payment-service test expansion
- [x] [historical] Add unit tests for domain/payment aggregate
- [x] [historical] Add unit tests for Temporal activities and workflow
- [x] [historical] Add unit tests for HTTP handlers
- [x] [historical] Add unit tests for Postgres repository
- [x] [historical] Add architecture test: sole-writer rule
- [x] [historical] Add architecture test: ports-are-interfaces
- [x] [historical] Add architecture test: deterministic-workflow
- [x] [historical] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.4 inventory-service test expansion
- [x] [historical] Add unit tests for domain/reservation aggregate
- [x] [historical] Add unit tests for Temporal activities and workflow
- [x] [historical] Add unit tests for HTTP handlers
- [x] [historical] Add unit tests for Postgres repository
- [x] [historical] Add architecture test: sole-writer rule
- [x] [historical] Add architecture test: deterministic-workflow
- [x] [historical] Verify coverage reaches ≥90% unit, ≥80% integration

### 1.5 shipping-service test expansion
- [x] [historical] Add unit tests for domain/shipment aggregate
- [x] [historical] Add unit tests for Temporal activities and workflow
- [x] [historical] Add unit tests for HTTP handlers
- [x] [historical] Add unit tests for Postgres repository
- [x] [historical] Add architecture test: sole-writer rule
- [x] [historical] Add architecture test: deterministic-workflow
- [x] [historical] Verify coverage reaches ≥90% unit, ≥80% integration

## Phase 2: High — Architecture Test Expansion

### 2.1 Expand catalog-service architecture tests
- [x] [historical] Add sole-writer test
- [x] [historical] Add ports-are-interfaces test
- [x] [historical] Add adapter-implements-one-port test
- [x] [historical] Add build-tag-isolation test
- [x] [historical] Add cache-keyspace test (ADR-gated)
- [x] [historical] Verify all 12 categories pass

### 2.2 Expand customer-service architecture tests
- [x] [historical] Add all 12 hexagonal enforcement categories
- [x] [historical] Verify cross-service import test passes

### 2.3 Expand notification-service architecture tests
- [x] [historical] Add all 12 hexagonal enforcement categories
- [x] [historical] Verify cross-service import test passes

### 2.4 Expand payment/inventory/shipping architecture tests
- [x] [historical] Add all applicable hexagonal enforcement categories to each
- [x] [historical] Add deterministic-workflow test to each
- [x] [historical] Add worker-versioning test to each

### 2.5 Cross-service architecture test
- [x] [historical] Implement TestHypotheticalPeerServiceCannotImportOrderInternals
- [x] [historical] Wire into CI pipeline (make verify-pr)

## Phase 3: High — K8s/ArgoCD Gaps

### 3.1 K8s NetworkPolicy egress rules
- [x] [historical] Add PostgreSQL egress rule (port 5432) to networkpolicy-allow-system.yaml
- [x] [historical] Add Kafka egress rule (port 9092) to networkpolicy-allow-system.yaml
- [x] [historical] Verify rules apply to all service pods via label selector

### 3.2 ArgoCD improvements
- [x] [historical] Add CreateNamespace sync option to ApplicationSet
- [x] [historical] Add retry with 5 attempts and exponential backoff
- [x] [historical] Update repoURL from placeholder to actual repository URL
- [x] [historical] Add ArgoCD Image Updater configuration
- [x] [historical] Add ArgoCD notification integration

### 3.3 Kustomize placeholder resolution
- [x] [historical] Resolve SERVICE_NAME placeholder in base/kustomization.yaml replacements block
- [x] [historical] Verify per-service production overlays apply correct nameSuffix

### 3.4 services-verify Makefile update
- [x] [historical] Add payment-service, inventory-service, shipping-service to services-verify loop
- [x] [historical] Verify make services-verify runs all 8 services

## Phase 4: Medium — Operational Readiness

### 4.1 Broker UI
- [x] [historical] Add kafbat/kafka-ui to deploy/docker-compose.tools.yaml
- [x] [historical] Pin KAFKA_UI_VERSION in deploy/tools.env
- [x] [historical] Add to verify-images check

### 4.2 Rollback rehearsal
- [x] [historical] Create scripts/rehearse-rollback.sh
- [x] [historical] Add make test-rollback-rehearsal target
- [x] [historical] Wire into release-evidence.yml

### 4.3 Service runbooks
- [x] [historical] Create docs/runbooks/ directory
- [x] [historical] Create runbook for order-service
- [x] [historical] Create runbook for customer-service
- [x] [historical] Create runbook for catalog-service
- [x] [historical] Create runbook for notification-service
- [x] [historical] Create runbook for reporting-service
- [x] [historical] Create runbook for payment/inventory/shipping services

### 4.4 Agent config wiring
- [x] [historical] Create .claude/settings.json with agentmemory MCP config
- [x] [historical] Create .cursor/mcp.json with agentmemory config
- [x] [historical] Create .codex/config.toml with agentmemory config
- [x] [historical] Add CI sidecar for agentmemory in verify.yml

### 4.5 Payment-service Dockerfile modernization
- [x] [historical] Add --platform=$BUILDPLATFORM build arg
- [x] [historical] Add -pgo=auto build flag
- [x] [historical] Add HEALTHCHECK instruction
- [x] [historical] Verify matches canonical Dockerfile.platform template

## Phase 5: Low — Platform Feature Gaps

### 5.1 Kafka retry-topic chain
- [x] [historical] Implement RetryConsumer in platform/kafka/
- [x] [historical] Add retry topic creation to provision-topics scripts
- [x] [historical] Wire retry consumer into notification-service and reporting-service
- [x] [historical] Add DLQ monitoring

### 5.2 Worker Versioning v2
- [x] [historical] Implement build-ID based worker versioning in platform/temporal/
- [x] [historical] Wire into all services with Temporal workers
- [x] [historical] Add version compatibility tests

### 5.3 Circuit breaker pattern
- [x] [historical] Design circuit breaker interface in platform/
- [x] [historical] Implement for HTTP client calls (order→customer, order→catalog)
- [x] [historical] Add configuration and metrics

### 5.4 Fuzz testing expansion
- [x] [historical] Add fuzz tests for customer-service HTTP handlers
- [x] [historical] Add fuzz tests for notification-service handlers
- [x] [historical] Add fuzz tests for catalog-service handlers
- [x] [historical] Wire fuzz tests into CI pipeline

## Verification

After all tasks complete:
- [x] [historical] Run `make verify-pr` — all services pass
- [x] [historical] Run `make test-e2e` — cross-service smoke passes
- [x] [historical] Run `make verify-images` — all images multi-arch
- [x] [historical] Verify test coverage: order ≥90/90/80, all others ≥90/80/70
- [x] [historical] Verify architecture tests: all services pass 12+ categories
- [x] [historical] Verify K8s manifests: kustomize build succeeds for all overlays
- [x] [historical] Verify ArgoCD: application sync succeeds in staging


---

> **Historical record:** This change was archived with 106 incomplete task(s) (0/106 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
