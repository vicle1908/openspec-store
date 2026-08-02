## Why

The spec audit revealed two genuine gaps between documented requirements and implementation:

1. **Aggregate-version gap detection** is specified in `platform-kafka-harness` but not implemented - the receipt store uses `event_id` as primary key instead of tracking `aggregate_version` per consumer group
2. **workflowcheck static analysis** is referenced in `platform-temporal-versioning` with a config file but no analyzer implementation

## What Changes

1. Implement aggregate-version gap detection in the Kafka consumer harness
2. Implement workflowcheck static analysis tool for Temporal workflow code
3. Update specs to reflect implementation status (remove DEFERRED markers once complete)

## Capabilities

### New Capabilities

- `kafka-aggregate-version-tracking`: Track last processed aggregate version per consumer group to detect and quarantine out-of-order events
- `workflowcheck-static-analysis`: Static analyzer to detect non-deterministic patterns in Temporal workflow code

### Modified Capabilities

- `platform-kafka-harness`: Add aggregate-version gap detection requirement (update status from DEFERRED to IMPLEMENTED)
- `platform-temporal-versioning`: Complete workflowcheck implementation (update status from PARTIAL to IMPLEMENTED)

## Impact

- **Code affected**: `platform/kafka/receipt.go`, `platform/kafka/consumer.go`, new `platform/workflows/workflowcheck/`
- **Specs updated**: `platform-kafka-harness`, `platform-temporal-versioning`
- **Dependencies**: None (uses existing franz-go and Temporal SDK patterns)
