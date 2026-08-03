## Why

`TestProcessRecord_ConcurrentSameOrderUsesDeterministicID` in the order-service
fails intermittently on CI with "expected exactly one starter call across
concurrent deliveries, got 2". This is a race condition in the receipt store's
`PutPending` implementation.

The race window:
1. Goroutine A: `Get()` → ErrReceiptMissing
2. Goroutine B: `Get()` → ErrReceiptMissing
3. Goroutine A: `PutPending()` → succeeds (writes pending)
4. Goroutine B: `PutPending()` → succeeds (existing is StatePending, so
   `ok && state != StatePending` is false — falls through)
5. Both goroutines proceed to start the workflow

Root cause: `PutPending` only rejects overwrites when the existing receipt is
NOT in `StatePending`. It allows overwriting a pending receipt, which defeats
the deduplication guarantee.

## What Changes

- `PutPending` in the test fake: reject when receipt already exists regardless
  of state (atomic insert-or-fail semantics)
- This matches the real database behavior: `INSERT ... ON CONFLICT DO NOTHING`
  returns 0 affected rows, which maps to `ErrReceiptExists`

## Capabilities

### Modified Capabilities

- `receipt-store`: `PutPending` now provides true insert-or-fail semantics

## Impact

- **Ownership boundary:** Order-service test infrastructure only
- **Repository surfaces:** `services/order-service/internal/application/orchestration/processor_test.go`
- **Contracts and data:** No service, API, or contract changes
- **Compatibility:** Existing crash-recovery test unchanged (it reads pending
  receipts but never writes over them)
- **Rollout:** Commit, push PR, verify CI passes
- **Rollback:** Revert the test fake change
