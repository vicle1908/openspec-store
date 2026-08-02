## Why

A comprehensive audit of all 10 archived openspec changes (69 spec files) against actual code revealed a systematic gap: many specs describe capabilities that are partially implemented, deferred, or not yet wired. The main specs in `openspec/specs/` were synced from delta specs but do not reflect the actual implementation state (IMPLEMENTED/PARTIAL/DEFERRED). This misalignment blocks accurate progress tracking, makes it impossible to distinguish "done" from "planned," and prevents confident archival of remaining work.

The audit identified ~65-70% overall platform completion. The primary gaps are:
- **Test coverage**: Non-order services have 1-15 tests vs the 90/90/80 targets
- **Architecture tests**: Most services only have `layering_test.go` (1 of 12+ required categories)
- **Operational gaps**: Missing broker UI, rollback rehearsal script, runbooks, agent config wiring
- **Platform features**: Worker Versioning v2, Kafka retry-topic chain, circuit breaker not implemented
- **K8s/ArgoCD**: Missing PostgreSQL/Kafka egress network policies, ArgoCD retry/notifications/image updater
- **Spec accuracy**: Many specs don't mark requirements as IMPLEMENTED/PARTIAL/DEFERRED

## What Changes

- Update all 50 main specs in `openspec/specs/` with implementation status annotations (IMPLEMENTED/PARTIAL/DEFERRED) based on audit evidence
- Create delta specs for capabilities that need requirement-level updates
- Create a new change to address the remaining operational and platform gaps
- Generate executable tasks for the highest-priority gaps
- Ensure every SHALL/MUST requirement maps to verifiable implementation evidence

## Capabilities

### Modified Capabilities

- `order-aggregate`: Mark all requirements as IMPLEMENTED (confirmed by audit)
- `order-command-handler`: Mark all requirements as IMPLEMENTED
- `order-outbox-cdc`: Mark all requirements as IMPLEMENTED, note Debezium config drift (database.dbname)
- `order-protobuf-contracts`: Mark all requirements as IMPLEMENTED
- `order-repository-port`: Mark all requirements as IMPLEMENTED
- `order-rest-api`: Mark fuzz testing as DEFERRED, rest as IMPLEMENTED
- `order-temporal-workflow`: Mark circuit breaker as DEFERRED, rest as IMPLEMENTED
- `platform-observability`: Mark all requirements as IMPLEMENTED
- `platform-contracts`: Mark protovalidate annotations as PARTIAL, rest as IMPLEMENTED
- `platform-kafka-harness`: Mark idempotent consumer as PARTIAL, producer idempotence as PARTIAL, retry-topic chain as DEFERRED
- `platform-health`: Mark all requirements as IMPLEMENTED
- `platform-runtime`: Mark all requirements as IMPLEMENTED
- `platform-cache`: Mark all requirements as IMPLEMENTED
- `platform-temporal-versioning`: Mark Worker Versioning v2 as DEFERRED, deterministic workflow as PARTIAL (workflowcheck exists)
- `platform-hexagonal-enforcement`: Mark as PARTIAL (only layering tests in most services)
- `platform-extensibility`: Mark as PARTIAL (cross-service HTTP client exists, agent configs not wired)
- `platform-projection`: Mark all requirements as IMPLEMENTED
- `catalog-product`: Mark as IMPLEMENTED with CANNOT VERIFY for attribute schema enforcement
- `catalog-pricing-snapshot`: Mark as IMPLEMENTED, Redis cache ADR-gated
- `customer-profile`: Mark as IMPLEMENTED, email/address validation CANNOT VERIFY
- `customer-gdpr-export`: Mark as IMPLEMENTED, cryptographic erasure evidence CANNOT VERIFY
- `notification-aggregate`: Mark as IMPLEMENTED, idempotency CANNOT VERIFY
- `notification-dispatcher`: Mark rate limiting as IMPLEMENTED, exponential backoff CANNOT VERIFY
- `reporting-projection`: Mark all requirements as IMPLEMENTED
- `inventory-service`: Mark domain/temporal as IMPLEMENTED, architecture tests as PARTIAL
- `payment-service`: Mark domain/temporal as IMPLEMENTED, architecture tests as PARTIAL
- `shipping-service`: Mark domain/temporal as IMPLEMENTED, architecture tests as PARTIAL
- `k8s-deployment-base`: Mark as IMPLEMENTED
- `k8s-hpa-template`: Mark as IMPLEMENTED
- `k8s-network-policies`: Mark PostgreSQL/Kafka egress as DEFERRED
- `k8s-pdb-template`: Mark as IMPLEMENTED
- `k8s-secrets-integration`: Mark as IMPLEMENTED
- `k8s-gitops-workflow`: Mark CreateNamespace/retry/image-updater as DEFERRED
- `docker-compose-resource-limits`: Mark as IMPLEMENTED
- `compose-tools-profile`: Mark broker UI as DEFERRED
- `developer-memory`: Mark agent config wiring as DEFERRED, scripts as IMPLEMENTED
- `platform-verification`: Mark traceability enforcement as DEFERRED
- `release-cadence-pipeline`: Mark rollback rehearsal as DEFERRED
- `rollback-rehearsal`: Mark as NOT IMPLEMENTED (script doesn't exist)

### New Capabilities

- `test-coverage-gap-closure`: Requirements for increasing test coverage in non-order services to meet 90/90/80 targets
- `architecture-test-expansion`: Requirements for expanding architecture tests from 1 to 12+ categories per service
- `operational-readiness`: Requirements for broker UI, rollback rehearsal, runbooks, agent config wiring

## Impact

- **Specs**: 50 main spec files need status annotations
- **Tasks**: New tasks for test coverage, architecture tests, operational gaps
- **No code changes**: This change is spec-only; implementation comes via separate changes
- **No API changes**: No breaking changes to any service contract
- **No dependency changes**: No new libraries or version bumps
