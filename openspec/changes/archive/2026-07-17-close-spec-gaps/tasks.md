# Implementation Tasks

## Aggregate Version Tracking

- [x] 1.1 Add `AggregateVersionStore` interface to `platform/kafka/receipt.go`
- [x] 1.2 Implement `PostgresAggregateVersionStore` with atomic compare-and-swap
- [x] 1.3 Implement `MemoryAggregateVersionStore` for tests
- [x] 1.4 Add migration SQL for `kafka_aggregate_versions` table
- [x] 1.5 Extract `aggregate_id` and `aggregate_version` from event envelope headers
- [x] 1.6 Modify `Consumer.handleRecord()` to check version before processing
- [x] 1.7 Update quarantine to include gap diagnostic message
- [x] 1.8 Add unit tests for aggregate version store
- [x] 1.9 Update `platform-kafka-harness` spec status to IMPLEMENTED

## workflowcheck Static Analysis

- [x] 2.1 Create `platform/workflows/workflowcheck/` package
- [x] 2.2 Implement `go/analysis` compatible checker
- [x] 2.3 Define `Issue` struct with file, line, col, pattern, severity
- [x] 2.4 Implement pattern detection for time.Now, time.Sleep, math/rand
- [x] 2.5 Implement pattern detection for goroutines and channel operations
- [x] 2.6 Load allowlist from `.workflowcheck.yaml`
- [x] 2.7 Add JSON and text output formatters
- [x] 2.8 Create CLI wrapper in `cmd/workflowcheck`
- [x] 2.9 Add unit tests with fixture workflow files
- [x] 2.10 Update `platform-temporal-versioning` spec status to IMPLEMENTED
