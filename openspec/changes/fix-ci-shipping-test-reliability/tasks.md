## 1. Add TEMPORAL_NEXUS_PILOT_MAX_FAILURES env var

- [ ] 1.1 Add `TEMPORAL_NEXUS_PILOT_MAX_FAILURES=2` to the environment map in test-shipping main.go
- [ ] 1.2 Verify the env var is passed to the pilot script

## 2. Validate locally

- [ ] 2.1 Verify Go code compiles: `go build ./tests/ecosystem-verification/cmd/test-shipping/...`
- [ ] 2.2 Run OpenSpec validation: `openspec validate fix-ci-shipping-test-reliability --store openspec-store`

## 3. Commit and push

- [ ] 3.1 Commit changes
- [ ] 3.2 Push PR branch
- [ ] 3.3 Verify CI passes on PR
- [ ] 3.4 Merge and verify CI passes on main
