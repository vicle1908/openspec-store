## 1. Add TEMPORAL_NEXUS_PILOT_MAX_FAILURES env var

- [x] 1.1 Add `TEMPORAL_NEXUS_PILOT_MAX_FAILURES=2` to the environment map in test-shipping main.go — commit `71b4f2b2bf77fafe1cfcbf2233fa693528e76a3e`
- [x] 1.2 Verify the env var is passed to the pilot script — `runCommand` copies the supplied key/value pair into the child environment; the PR shipping workflow passed

## 2. Validate locally

- [x] 2.1 Verify Go code compiles from the nested module root: `(cd tests/ecosystem-verification && go build ./cmd/test-shipping/...)` — passed 2026-08-03
- [x] 2.2 Run OpenSpec validation after archival: `openspec validate --strict --all --store openspec-store` — 349 passed, 0 failed on 2026-08-03

## 3. Commit and push

- [x] 3.1 Commit changes — implementation commits `71b4f2b2bf77fafe1cfcbf2233fa693528e76a3e` and `a7114713c7a3453ac33d381b538e21d5e1a855da`
- [x] 3.2 Push PR branch — `fix/ci-shipping-reliability-v3`, pull request [#12](https://github.com/vicle1908/go-microservices/pull/12)
- [x] 3.3 Verify CI passes on PR — `service-integration` and `shipping-focused` succeeded in run [30741051002](https://github.com/vicle1908/go-microservices/actions/runs/30741051002)
- [x] 3.4 Merge and verify CI passes on main — merged as `383e67269073493479533f84b52ad758b8b5bff5`; main verify, deployment-validation, and image-build checks succeeded (container integration is PR/manual-dispatch only)

## Completion Summary

- Tasks: 8/8 complete
- Delta specs: none (`skip_specs: true`)
- Local verification: build and focused tests passed from the owning Go module
- Remote verification: PR shipping CI passed; main-branch checks passed
- Archive correction reviewed and validated on 2026-08-03
