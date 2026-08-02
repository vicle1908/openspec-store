# Phase 5: Platform Features — Tasks

## Overview

| Task | Status | Priority |
|------|--------|----------|
| Fuzz tests for customer-service | Complete | P1 |
| Fuzz tests for notification-service | Complete | P1 |
| Fuzz tests for catalog-service | Complete | P1 |
| Kafka retry-topic chain | Not Started | P2 |
| Circuit breaker middleware | Not Started | P2 |
| Worker Versioning v2 design | Not Started | P3 |

---

## Task 1: Fuzz tests for customer-service

- [x] Create `services/customer-service/test/fuzz/http_test.go`
- [x] Add seed corpus (valid JSON, empty object, invalid input)
- [x] Verify handler does not panic on arbitrary input
- [x] Verify handler returns proper error codes for invalid input

## Task 2: Fuzz tests for notification-service

- [x] Create `services/notification-service/test/fuzz/http_test.go`
- [x] Add seed corpus (valid JSON, empty object, invalid input)
- [x] Verify handler does not panic on arbitrary input
- [x] Verify handler returns proper error codes for invalid input

## Task 3: Fuzz tests for catalog-service

- [x] Create `services/catalog-service/test/fuzz/http_test.go`
- [x] Add seed corpus (valid JSON, empty object, invalid input)
- [x] Verify handler does not panic on arbitrary input
- [x] Verify handler returns proper error codes for invalid input

## Task 4: Kafka retry-topic chain

- [ ] Create `pkg/kafkax/retry.go`
- [ ] Create `pkg/kafkax/dead_letter.go`
- [ ] Create `pkg/kafkax/consumer.go` with retry routing
- [ ] Add unit tests
- [ ] Integrate with order-service consumer
- [ ] Add configuration schema

## Task 5: Circuit breaker middleware

- [ ] Create `pkg/resilience/circuit_breaker.go`
- [ ] Create `pkg/resilience/middleware.go`
- [ ] Add unit tests
- [ ] Integrate with service-to-service HTTP calls
- [ ] Add configuration schema
- [ ] Add metrics endpoint

## Task 6: Worker Versioning v2 design

- [ ] Document current workflow versioning approach
- [ ] Design version migration strategy
- [ ] Define deprecation policy
- [ ] Create example implementation
- [ ] Review with team
