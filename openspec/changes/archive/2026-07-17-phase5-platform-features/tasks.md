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

- [x] [historical] Create `pkg/kafkax/retry.go`
- [x] [historical] Create `pkg/kafkax/dead_letter.go`
- [x] [historical] Create `pkg/kafkax/consumer.go` with retry routing
- [x] [historical] Add unit tests
- [x] [historical] Integrate with order-service consumer
- [x] [historical] Add configuration schema

## Task 5: Circuit breaker middleware

- [x] [historical] Create `pkg/resilience/circuit_breaker.go`
- [x] [historical] Create `pkg/resilience/middleware.go`
- [x] [historical] Add unit tests
- [x] [historical] Integrate with service-to-service HTTP calls
- [x] [historical] Add configuration schema
- [x] [historical] Add metrics endpoint

## Task 6: Worker Versioning v2 design

- [x] [historical] Document current workflow versioning approach
- [x] [historical] Design version migration strategy
- [x] [historical] Define deprecation policy
- [x] [historical] Create example implementation
- [x] [historical] Review with team


---

> **Historical record:** This change was archived with 17 incomplete task(s) (12/29 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
