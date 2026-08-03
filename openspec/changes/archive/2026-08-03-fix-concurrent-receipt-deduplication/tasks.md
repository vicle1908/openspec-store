## 1. Fix receipt store race condition

- [ ] 1.1 Change `PutPending` to reject when receipt already exists (remove `State != StatePending` check)
- [ ] 1.2 Run order-service tests to verify fix: `make -C services/order-service test-race`

## 2. Validate

- [ ] 2.1 Run concurrent test 10 times to confirm no flakiness
- [ ] 2.2 Run crash-recovery test to confirm no regression
- [ ] 2.3 Run full order-service verify-pr

## 3. Commit and push

- [ ] 3.1 Commit changes
- [ ] 3.2 Push PR branch
- [ ] 3.3 Verify CI passes on PR and main
