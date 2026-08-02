# Phase 1: Test Coverage — Implementation Tasks

## 1. Foundation — Shared Test Helpers

### 1.1 payment-service test helpers
- [x] Create `services/payment-service/internal/testutil/db.go` — testcontainers PostgreSQL setup
- [x] Create `services/payment-service/internal/testutil/mocks.go` — mock Repository, UnitOfWork
- [x] Create `services/payment-service/internal/testutil/fixtures.go` — payment factory functions

### 1.2 inventory-service test helpers
- [x] Create `services/inventory-service/internal/testutil/db.go` — testcontainers PostgreSQL setup
- [x] Create `services/inventory-service/internal/testutil/mocks.go` — mock Repository, UnitOfWork
- [x] Create `services/inventory-service/internal/testutil/fixtures.go` — reservation factory functions

### 1.3 shipping-service test helpers
- [x] Create `services/shipping-service/internal/testutil/db.go` — testcontainers PostgreSQL setup
- [x] Create `services/shipping-service/internal/testutil/mocks.go` — mock Repository, UnitOfWork
- [x] Create `services/shipping-service/internal/testutil/fixtures.go` — shipment factory functions

### 1.4 notification-service test helpers
- [x] Create `services/notification-service/internal/testutil/mocks.go` — mock Provider, RateLimiter, Repository
- [x] Create `services/notification-service/internal/testutil/fixtures.go` — notification factory functions

### 1.5 customer-service test helpers
- [x] Create `services/customer-service/internal/testutil/mocks.go` — mock Repository, GDPRStore
- [x] Create `services/customer-service/internal/testutil/fixtures.go` — customer factory functions

## 2. payment-service Unit Tests (1 → 30+)

### 2.1 Domain tests
- [x] Add `services/payment-service/internal/domain/payment/payment_test.go` — payment aggregate lifecycle
- [x] Test: NewPayment creates with pending status
- [x] Test: Capture transitions pending → captured
- [x] Test: Refund transitions captured → refunded
- [x] Test: Void transitions pending → voided
- [x] Test: Invalid transitions rejected
- [x] Test: Idempotent capture (same operation ID)
- [x] Test: Money validation (negative amount rejected)
- [x] Test: Currency validation
- [x] Test: Version increments on state change
- [x] Test: PendingEvents emitted correctly

### 2.2 Application tests
- [x] Add `services/payment-service/internal/application/application_test.go`
- [x] Test: CreatePayment command handler
- [x] Test: CapturePayment command handler
- [x] Test: RefundPayment command handler
- [x] Test: MarkFailed command handler (no VoidPayment handler exists - uses MarkFailed)
- [x] Test: Idempotency key handling
- [x] Test: Error paths (not found, conflict)

## 3. inventory-service Unit Tests (1 → 30+)

### 3.1 Domain tests
- [x] Add `services/inventory-service/internal/domain/reservation/reservation_test.go`
- [x] Test: NewReservation creates with pending status
- [x] Test: Confirm transitions pending → confirmed
- [x] Test: Release transitions pending/confirmed → released
- [x] Test: Invalid transitions rejected
- [x] Test: Quantity validation (positive integers)
- [x] Test: Version increments on state change
- [x] Test: PendingEvents emitted correctly

### 3.2 Application tests
- [x] Add `services/inventory-service/internal/application/orchestration/activities_test.go`
- [x] Test: ReserveInventory activity
- [x] Test: ReleaseInventory activity
- [x] Test: ConfirmInventory activity
- [x] Test: Idempotent operations
- [x] Test: Error paths

## 4. shipping-service Unit Tests (1 → 30+)

### 4.1 Domain tests
- [x] Add `services/shipping-service/internal/domain/shipment/shipment_test.go`
- [x] Test: NewShipment creates with pending status
- [x] Test: Dispatch transitions pending → dispatched
- [x] Test: Complete transitions dispatched → delivered
- [x] Test: Cancel transitions pending → cancelled
- [x] Test: Invalid transitions rejected
- [x] Test: Carrier validation (stub/ups/fedex)
- [x] Test: Version increments on state change
- [x] Test: PendingEvents emitted correctly

### 4.2 Application tests
- [x] Add `services/shipping-service/internal/application/orchestration/activities_test.go`
- [x] Test: DispatchShipment activity
- [x] Test: CompleteShipment activity
- [x] Test: CancelShipment activity
- [x] Test: Idempotent operations
- [x] Test: Error paths

## 5. notification-service Unit Tests (2 → 30+)

### 5.1 Domain tests (expand existing)
- [x] Expand `services/notification-service/domain/notification/notification_test.go`
- [x] Test: New notification creation with all channels
- [x] Test: Template versioning
- [x] Test: All status transitions (pending → dispatching → delivered/failed)
- [x] Test: Retry logic
- [x] Test: Max attempts enforcement
- [x] Test: Rehydrate from snapshot

### 5.2 Dispatcher tests
- [x] Add `services/notification-service/application/orchestration/dispatcher_test.go`
- [x] Test: Provider selection by channel
- [x] Test: Rate limiting integration
- [x] Test: Exponential backoff
- [x] Test: Durable receipt recording

### 5.3 Handler tests
- [x] Add `services/notification-service/adapters/http/server_test.go`
- [x] Test: Create notification endpoint
- [x] Test: Get notification endpoint
- [x] Test: List notifications endpoint
- [x] Test: Error responses

## 6. customer-service Unit Tests (3 → 30+)

### 6.1 Domain tests (expand existing)
- [x] Expand `services/customer-service/domain/customer/customer_test.go`
- [x] Test: Address management (add, update, remove)
- [x] Test: Default shipping/billing flags
- [x] Test: Email verification flow
- [x] Test: Status transitions (active → soft-deleted → purged)

### 6.2 GDPR tests
- [x] Expand `services/customer-service/internal/domain/gdpr/export_test.go`
- [x] Test: Export data format
- [x] Test: Purge workflow
- [x] Test: Retention timer

### 6.3 Handler tests
- [x] Add `services/customer-service/adapters/http/handlers_test.go`
- [x] Test: CRUD endpoints
- [x] Test: GDPR export endpoint
- [x] Test: GDPR delete endpoint
- [x] Test: Error responses

## 7. Architecture Tests (All 6 Services)

### 7.1 payment-service
- [x] Add `services/payment-service/test/architecture/solewriter_test.go`
- [x] Add `services/payment-service/test/architecture/ports_test.go`
- [x] Add `services/payment-service/test/architecture/domain_test.go`

### 7.2 inventory-service
- [x] Add `services/inventory-service/test/architecture/solewriter_test.go`
- [x] Add `services/inventory-service/test/architecture/ports_test.go`
- [x] Add `services/inventory-service/test/architecture/domain_test.go`

### 7.3 shipping-service
- [x] Add `services/shipping-service/test/architecture/solewriter_test.go`
- [x] Add `services/shipping-service/test/architecture/ports_test.go`
- [x] Add `services/shipping-service/test/architecture/domain_test.go`

### 7.4 notification-service
- [x] Add `services/notification-service/test/architecture/solewriter_test.go`
- [x] Add `services/notification-service/test/architecture/ports_test.go`
- [x] Add `services/notification-service/test/architecture/domain_test.go`

### 7.5 customer-service
- [x] Add `services/customer-service/test/architecture/solewriter_test.go`
- [x] Add `services/customer-service/test/architecture/ports_test.go`
- [x] Add `services/customer-service/test/architecture/domain_test.go`

### 7.6 catalog-service
- [x] Add `services/catalog-service/test/architecture/solewriter_test.go`
- [x] Add `services/catalog-service/test/architecture/ports_test.go`
- [x] Add `services/catalog-service/test/architecture/domain_test.go`

## 8. Integration Tests (3 Services)

### 8.1 payment-service
- [x] Add `services/payment-service/test/integration/repository_test.go`
- [x] Test: CRUD operations against real PostgreSQL
- [x] Test: Transaction rollback
- [x] Test: Connection pool resilience

### 8.2 inventory-service
- [x] Add `services/inventory-service/test/integration/repository_test.go`
- [x] Test: CRUD operations against real PostgreSQL
- [x] Test: Transaction rollback
- [x] Test: Connection pool resilience

### 8.3 shipping-service
- [x] Add `services/shipping-service/test/integration/repository_test.go`
- [x] Test: CRUD operations against real PostgreSQL
- [x] Test: Transaction rollback
- [x] Test: Connection pool resilience

## 9. Cross-Service Smoke Tests

- [x] Add `services/order-service/cmd/order-service/smoke_customer_contract_test.go`
- [x] Add `services/order-service/cmd/order-service/smoke_catalog_contract_test.go`
- [x] Add `services/order-service/cmd/order-service/smoke_notification_contract_test.go`
- [x] Add `services/order-service/cmd/order-service/smoke_reporting_contract_test.go`

## 10. CI Integration

- [x] Add coverage threshold check script `scripts/check-coverage.sh`
- [x] Add coverage gate to each service's Makefile verify-pr target
- [x] Verify `make verify-pr` passes for all 8 services

## Verification

- [x] Run `make verify-pr` — all services pass
- [x] Verify test counts: payment ≥30, inventory ≥30, shipping ≥30, notification ≥30, customer ≥30
- [x] Verify architecture tests pass in all 7 non-order services
- [x] Verify integration tests pass with testcontainers
- [x] Verify cross-service smoke tests compile
