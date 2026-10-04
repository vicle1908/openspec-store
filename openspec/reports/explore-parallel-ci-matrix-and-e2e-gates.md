# Exploration Report: Parallel CI Matrix DAG, Fast-Fail Preflight, and Newman E2E Gates

**Date:** 2026-10-04  
**Workspace:** `~/Developer/platform/go-microservices`  
**OpenSpec Store:** `~/Developer/platform/openspec-store`  
**Current Baseline Commit on `main`:** `016dd80` (PR #48)  

---

## 1. Executive Summary

Over pull requests #43 through #48, the `go-microservices` delivery pipeline achieved critical baseline resilience:
- Root `.go-version` (`1.27.1`) toolchain single source of truth.
- Native `actions/setup-go@v5` module caching eliminating tar permission collisions (`0555` read-only directories).
- Automated coverage documentation synchronization (`make sync-coverage-docs`).
- Container image manifest query deduplication and 3-attempt exponential backoff retries (`scripts/verify-images.sh`).
- PR-scoped workflow concurrency with safe preemption (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`).
- Tracked developer pre-push hook automation (`make install-hooks` / `.githooks/pre-push`).
- Architecture Decision Record 0009 (`docs/adr/0009-go-1.27-toolchain-and-ci-pipeline-architecture.md`) and local Notion mirror (`docs/notion-ci-pipeline-architecture.md`).

However, the primary verification workflow (`.github/workflows/verify.yml`) remains architecturally constrained by a **monolithic sequential loop**:
- The single runner job `PR gate (verify-pr)` executes repository preflight, platform verification, and an 8-service unit test and coverage loop serially.
- Wall-clock PR execution time currently ranges from **7m 30s to 8m 30s**.
- If a late-stage service (e.g. `shipping-service` or `reporting-service`) fails, developers wait ~7 minutes before receiving feedback, and failure diagnostics for subsequent services are completely lost.
- Furthermore, while a comprehensive Postman Collection and Newman test suite was implemented in PR #41 (`tests/postman/`), it runs only ad-hoc during local development and is not yet wired as an automated gate in CI.

This exploration explores decomposing `.github/workflows/verify.yml` into a **4-tier parallel DAG with a status aggregator rollup anchor**, while integrating headless Newman execution directly into `.github/workflows/lgtm-e2e.yml`.

---

## 2. Comparative Architecture: Sequential Loop vs. 4-Tier Matrix DAG

### Current Sequential Architecture (`.github/workflows/verify.yml`)

```
[PR Opened]
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Job: PR gate (verify-pr) [Runs on single ubuntu-latest runner, ~7m 45s]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. Checkout & Setup Go 1.27.1 (SSOT)                                    (~25s)  │
│ 2. Preflight (Module integrity, Actionpin, Retention, Actionlint)       (~35s)  │
│ 3. Guidance, Coverage parity check, Documentation check                 (~30s)  │
│ 4. Platform Verification (`make -C platform verify`)                    (~1m15s)│
│ 5. Sequential Service Loop (for svc in catalog customer ...):           (~5m00s)│
│    ├── catalog-service                                                  │
│    ├── customer-service                                                 │
│    ├── inventory-service                                                │
│    ├── notification-service                                             │
│    ├── order-service                                                    │
│    ├── payment-service                                                  │
│    ├── reporting-service                                                │
│    └── shipping-service                                                 │
│ 6. Generate Step Summary & Upload Artifacts                             (~10s)  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Proposed 4-Tier Matrix DAG Architecture

```
[PR Opened]
    │
    ├─────────────────────────────────────────┐
    ▼                                         ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│ Tier 1: preflight         │   │ Tier 2: platform-verify   │
│ - Module integrity        │   │ - platform build & test   │
│ - Actionpin verification  │   │ - contract validations    │
│ - Agent guidance bounds   │   │ - OTel telemetry checks   │
│ - Coverage table parity   │   │                           │
│ - Inline govulncheck      │   │                           │
│ (~35s - 45s)              │   │ (~1m 15s)                 │
└─────────────┬─────────────┘   └─────────────┬─────────────┘
              │                               │
              └───────────────────────────────┼───────────────────────────────┐
                                              ▼                               │
                        ┌───────────────────────────────────────────┐         │
                        │ Tier 3: service-verify-matrix             │         │
                        │ strategy: matrix (8 services)             │         │
                        │ fail-fast: false                          │         │
                        │ ├── catalog-service                       │         │
                        │ ├── customer-service                      │         │
                        │ ├── inventory-service                     │         │
                        │ ├── notification-service                  │         │
                        │ ├── order-service                         │         │
                        │ ├── payment-service                       │         │
                        │ ├── reporting-service                     │         │
                        │ └── shipping-service                      │         │
                        │ (~1m 45s - 2m 15s concurrent)             │         │
                        └─────────────────────┬─────────────────────┘         │
                                              │                               │
                                              ▼                               │
                        ┌───────────────────────────────────────────┐         │
                        │ Tier 4: PR gate (verify-pr)               │◄────────┘
                        │ needs: [preflight, platform-verify,       │
                        │         service-verify-matrix]            │
                        │ if: always()                              │
                        │ - Aggregates upstream conclusion results  │
                        │ - Fails if any upstream failed/cancelled  │
                        │ - Emits unified $GITHUB_STEP_SUMMARY      │
                        │ - Satisfies Branch Protection Context     │
                        │ (~10s)                                    │
                        └───────────────────────────────────────────┘
```

---

## 3. Detailed Component Analysis

### A. Tier 1: Fast-Fail Preflight (`preflight`)
- **Objective:** Detect syntax, formatting, guidance, actionpinning, and known vulnerability regressions in $< 45$ seconds before spinning up larger matrices.
- **Tasks Executed:**
  - `bash scripts/verify-go-modules.sh`
  - `python3 tools/actionpin/actionpin.py --root . --lock verification/github-actions-lock.json`
  - `make validate-agent-guidance`
  - `python3 scripts/sync-coverage-docs.py --check`
  - `make validate-documentation`
  - `govulncheck ./...` (inline standard library and dependency vulnerability scanning)

### B. Tier 2: Platform Shared Runtime Verification (`platform-verify`)
- **Objective:** Compile and execute tests for the shared base module `platform/` on Go 1.27.1.
- **Tasks Executed:**
  - `make -C platform verify`

### C. Tier 3: 8-Way Service Verification Matrix (`service-verify-matrix`)
- **Objective:** Parallelize execution across all 8 independent services with isolated logs, dedicated runners, and non-blocking failure reporting (`fail-fast: false`).
- **Matrix Configuration:**
  ```yaml
  strategy:
    fail-fast: false
    matrix:
      service:
        - catalog-service
        - customer-service
        - inventory-service
        - notification-service
        - order-service
        - payment-service
        - reporting-service
        - shipping-service
  ```
- **Job Steps:**
  - Checkout & setup Go 1.27.1 via `.go-version` with native caching.
  - Per-service linter validation: `gofmt -l`, `go vet`, `golangci-lint run`.
  - Unit and race testing: `go test -race ./...`.
  - Strict statement coverage enforcement: `./scripts/check-coverage.sh ${{ matrix.service }} 80`.
  - Save coverage and test artifacts under `artifacts/verification/${{ matrix.service }}`.

### D. Tier 4: Aggregator Anchor Job (`PR gate (verify-pr)`)
- **Objective:** Evaluate the outcomes of all upstream jobs and provide a single authoritative status check for GitHub branch protection.
- **Critical Branch Protection Contract:**
  Branch protection on `main` requires exactly:
  ```json
  ["PR gate (verify-pr)", "Deployment validation (report only)", "Gitleaks secret scan"]
  ```
  The aggregator job MUST retain the exact name `PR gate (verify-pr)`.
- **Failure Aggregation Logic:**
  ```yaml
  verify-pr:
    name: PR gate (verify-pr)
    runs-on: ubuntu-latest
    needs: [preflight, platform-verify, service-verify-matrix]
    if: always()
    steps:
      - name: Evaluate upstream gate results
        run: |
          if [ "${{ needs.preflight.result }}" != "success" ] || \
             [ "${{ needs.platform-verify.result }}" != "success" ] || \
             [ "${{ needs.service-verify-matrix.result }}" != "success" ]; then
            echo "ERROR: One or more upstream verification gates failed or were cancelled." >&2
            exit 1
          fi
          echo "SUCCESS: All upstream verification gates completed cleanly."
  ```

### E. Automated Headless Newman CI Quality Gate (`lgtm-e2e.yml`)
- **Objective:** Integrate the automated API integration and E2E saga test suites into `.github/workflows/lgtm-e2e.yml` after the Docker Compose stack converges.
- **Execution Workflow:**
  1. Docker Compose stack is brought up with `--profile smoke`.
  2. Newman runs headless against live ports:
     ```bash
     ./tests/postman/run-newman.sh --env tests/postman/environments/go-microservices.ci.postman_environment.json feature
     ./tests/postman/run-newman.sh --env tests/postman/environments/go-microservices.ci.postman_environment.json e2e
     ```
  3. Emit JUnit XML test summaries to `tests/postman/reports/` and upload via `actions/upload-artifact`.

---

## 4. Performance & Turnaround Comparison

| Metric | Sequential Architecture (Current) | 4-Tier Matrix DAG (Proposed) | Improvement |
| --- | --- | --- | --- |
| **Preflight Feedback Time** | ~7m 30s (runs sequentially with tests) | **~35s** (Tier 1 fast-fail) | **~92% faster** |
| **Total PR Gate Wall-Clock Time** | ~7m 45s – 8m 30s | **~2m 30s – 3m 00s** | **~65% reduction** |
| **Failure Diagnosis Isolation** | Monolithic log (single buffer) | Discrete per-service logs | **100% isolated** |
| **Failure Masking** | Service 7 failure aborts Service 8 | `fail-fast: false` runs all services | **Zero masked failures** |
| **Branch Protection Compatibility** | Context: `PR gate (verify-pr)` | Context: `PR gate (verify-pr)` | **100% compatible** |
| **API Saga Verification in CI** | Ad-hoc / Local only | Automated headless in `lgtm-e2e` | **Automated in CI** |

---

## 5. Implementation Roadmap & Recommendation

We recommend initiating a formal OpenSpec change:
- **Change Name:** `parallel-ci-matrix-and-e2e-pipeline-gates`
- **Scope:**
  1. Refactor `.github/workflows/verify.yml` into the 4-tier DAG (`preflight`, `platform-verify`, `service-verify-matrix`, and rollup anchor `PR gate (verify-pr)`).
  2. Wire `./tests/postman/run-newman.sh` into `.github/workflows/lgtm-e2e.yml`.
  3. Validate all action pins with `tools/actionpin/actionpin.py`.
  4. Perform live verification via a dedicated pull request with auto-merge enabled.
