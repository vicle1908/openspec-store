## Current State

The `fakeReceiptStore.PutPending` method checks:
```go
if existing, ok := s.records[key]; ok && existing.State != StatePending {
    return ErrReceiptExists
}
```

This only rejects overwrites when the existing receipt is NOT in `StatePending`.
When two goroutines race past `Get()` before either writes, both succeed at
`PutPending` because the second one overwrites the first's pending receipt.

## Proposed Change

Change `PutPending` to reject any existing receipt regardless of state:
```go
if _, ok := s.records[key]; ok {
    return ErrReceiptExists
}
```

This provides atomic insert-or-fail semantics matching the real database
`INSERT ... ON CONFLICT DO NOTHING` behavior.

## Files Changed

- `services/order-service/internal/application/orchestration/processor_test.go`:
  One-line change in `PutPending`
