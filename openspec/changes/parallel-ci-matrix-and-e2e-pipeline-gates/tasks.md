# Tasks: 4-Tier Parallel CI Matrix DAG and Headless Newman E2E Gates

## 1. 4-Tier Matrix DAG Refactoring in `verify.yml`

- [ ] 1.1 Decompose `.github/workflows/verify.yml` into 4 tiers:
  - `preflight`: Module integrity, Action pinning, Actionlint, Agent guidance, Coverage documentation parity, and Documentation check (~45s)
  - `platform-verify`: Dedicated compilation and test execution for `platform/` module (~1m 15s)
  - `service-verify-matrix`: 8-way concurrent matrix (`fail-fast: false`) testing and enforcing coverage for each service (~2m 15s)
  - `verify-pr`: Lightweight fan-in rollup aggregator (`needs: [preflight, platform-verify, service-verify-matrix]`, `if: always()`)
- [ ] 1.2 Retain exact required status check context name `PR gate (verify-pr)` in the fan-in aggregator job
- [ ] 1.3 Add unified `$GITHUB_STEP_SUMMARY` markdown reporting in the aggregator job

## 2. Headless Newman Integration in `lgtm-e2e.yml`

- [ ] 2.1 Add automated Newman execution step in `.github/workflows/lgtm-e2e.yml` running `./tests/postman/run-newman.sh all` after Compose stack convergence
- [ ] 2.2 Add step uploading JUnit XML test reports from `tests/postman/reports/` via `actions/upload-artifact`

## 3. Local Verification & Supply Chain Pinning

- [ ] 3.1 Verify action pinning across workflows with `tools/actionpin/actionpin.py --root . --lock verification/github-actions-lock.json`
- [ ] 3.2 Verify local pre-push validation passes with 0 errors via `make pre-push`
- [ ] 3.3 Validate workflow syntax using `actionlint`

## 4. Live PR Lifecycle & Verification

- [ ] 4.1 Validate OpenSpec change strictly: `openspec validate parallel-ci-matrix-and-e2e-pipeline-gates --strict --store openspec-store`
- [ ] 4.2 Create feature branch `feat/parallel-ci-matrix-and-e2e-gates` in `go-microservices` and commit pipeline changes
- [ ] 4.3 Open PR #49, arm auto-merge, and monitor 8-way matrix fan-out and aggregator completion live
- [ ] 4.4 Verify all checks pass green and PR auto-merges cleanly into `main`
- [ ] 4.5 Sync local `main` in `go-microservices`, archive OpenSpec change in `openspec-store`, and push to remote `main`
