## 1. Fix receipt store race condition

- [x] [historical] 1.1 Change `PutPending` to reject when receipt already exists (remove `State != StatePending` check)
- [x] [historical] 1.2 Run order-service tests to verify fix: `make -C services/order-service test-race`

## 2. Validate

- [x] [historical] 2.1 Run concurrent test 10 times to confirm no flakiness
- [x] [historical] 2.2 Run crash-recovery test to confirm no regression
- [x] [historical] 2.3 Run full order-service verify-pr

## 3. Commit and push

- [x] [historical] 3.1 Commit changes
- [x] [historical] 3.2 Push PR branch
- [x] [historical] 3.3 Verify CI passes on PR and main


---

> **Historical record:** This change was archived with 8 incomplete task(s) (0/8 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
