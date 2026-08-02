## 1. Gate correctness baseline

- [x] 1.1 Make all service coverage targets parse one numeric result and propagate test or threshold failures
- [x] 1.2 Remove references to nonexistent local validators, Compose files, and generation commands from service static gates
- [x] 1.3 Make reporting traceability fail closed and map every architecture test to retained evidence
- [x] 1.4 Isolate live-stack order and catalog tests behind explicit build tags
- [x] 1.5 Make catalog architecture root discovery terminate under `-trimpath` and remove obsolete helpers
- [x] 1.6 Remove shuffled-test ordering assumptions from inventory activity assertions

## 2. Coverage closure

- [x] 2.1 Raise payment-service aggregate coverage from 18.3% to at least 80% with domain, application, adapter, and runtime behavior tests
- [x] 2.2 Raise catalog-service aggregate coverage from 21.3% to at least 80%
- [x] 2.3 Raise reporting-service aggregate coverage from 21.6% to at least 80%
- [x] 2.4 Raise notification-service aggregate coverage from 25.9% to at least 80%
- [x] 2.5 Raise customer-service aggregate coverage from 27.9% to at least 80%
- [x] 2.6 Raise shipping-service aggregate coverage from 37.7% to at least 80%
- [x] 2.7 Raise inventory-service aggregate coverage from 40.2% to at least 80%
- [x] 2.8 Raise order-service aggregate coverage from 57.2% to at least 80%
- [x] 2.9 Add retained package/layer coverage summaries and exclusions policy, then verify every default threshold without overrides

## 3. Missing fuzz suites

- [x] 3.1 Add inventory HTTP/event parser fuzz targets, committed seeds, regression runner, and bounded short-fuzz runner
- [x] 3.2 Add shipping HTTP/event parser fuzz targets, committed seeds, regression runner, and bounded short-fuzz runner
- [x] 3.3 Run both fuzz regression suites under `verify-pr` and prove missing runners fail closed

## 4. Reproducible contract generation

- [x] 4.1 Verify the pinned Buf and protoc Go plugin workflow against current official Buf documentation and select an authenticated or officially supported cached/local path
- [x] 4.2 Standardize contract lint, build, generation, and generated-diff checks across generated-binding services
- [x] 4.3 Add external-failure classification for registry quota/authentication/network errors without weakening the gate
- [x] 4.4 Prove clean deterministic generation for order, customer, and reporting and retain version/evidence metadata

## 5. Final verification and documentation

- [x] 5.1 Run every service `verify-pr` with its real default threshold, then run root `make verify-pr`
- [x] 5.2 Run strict OpenSpec validation, preflight, and full deployment validation for the exact final source snapshot
- [x] 5.3 Update coverage/fuzz/tooling specs and developer docs with final measured evidence, rollback, and troubleshooting guidance
