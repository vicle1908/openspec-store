## Design: Aggregate-Version Gap Detection

### Problem

The Kafka consumer currently tracks processed events by `(consumer_group, event_id)`. This doesn't detect out-of-order events where the same aggregate emits multiple versions and they arrive out of sequence.

### Solution

Extend the receipt store to track `last_aggregate_version` per `(consumer_group, aggregate_id)`. When a new record arrives:

1. Look up `last_aggregate_version` for this `(consumer_group, aggregate_id)`
2. If record's `aggregate_version <= last_aggregate_version`, quarantine with reason `aggregate_version_gap`
3. Otherwise, process normally and update `last_aggregate_version`

### Schema Change

```sql
-- New table or columns added to existing receipt store
CREATE TABLE kafka_aggregate_versions (
    consumer_group TEXT NOT NULL,
    aggregate_id   TEXT NOT NULL,
    last_version   BIGINT NOT NULL,
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (consumer_group, aggregate_id)
);
```

### Implementation

1. Add `AggregateVersionStore` interface to `platform/kafka/receipt.go`
2. Implement `PostgresAggregateVersionStore`
3. Modify `Consumer.handleRecord()` to check aggregate version before processing
4. Add `aggregate_version` extraction from event envelope headers

---

## Design: workflowcheck Static Analysis

### Problem

Temporal workflows must be deterministic. The platform has a config file but no actual analyzer to detect non-deterministic code patterns.

### Solution

Create a static analysis tool using Go's `go/analysis` package that scans workflow files for non-deterministic patterns.

### Patterns to Detect

| Pattern | Description | Severity |
|---------|-------------|----------|
| `time.Now()` | Wall-clock access | Error |
| `time.Sleep()` | Non-deterministic delay | Error |
| `math/rand` | Non-random randomness | Error |
| `go func()` | Unauthorized goroutines | Error |
| `sync.Mutex` | Non-serializable state | Warning |
| `chan<-` | Channel operations | Warning |

### Implementation

1. Create `platform/workflows/workflowcheck/` package
2. Implement `go/analysis` compatible checker
3. Add `CheckWorkflow(path string) (issues []Issue, err error)` function
4. Create CLI wrapper `cmd/workflowcheck`
5. Integrate into CI pipeline

### Output Format

```json
{
  "file": "services/order-service/internal/adapters/temporal/workflow.go",
  "line": 42,
  "col": 5,
  "pattern": "time.Now()",
  "severity": "error",
  "message": "workflow code must not call time.Now()"
}
```
