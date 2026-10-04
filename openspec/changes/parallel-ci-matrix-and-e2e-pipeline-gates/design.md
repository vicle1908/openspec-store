# Design: 4-Tier Parallel CI Matrix DAG and Headless Newman E2E Gates

## Architecture Overview
This change modernizes the primary CI delivery pipeline (`.github/workflows/verify.yml`) and end-to-end integration workflow (`.github/workflows/lgtm-e2e.yml`) across `go-microservices` by:
1. **Decomposing `verify.yml` into a 4-Tier Parallel DAG**:
   - `preflight`: Fast-fail static checks (<45s) validating module integrity, action pinning, agent guidance word counts, coverage documentation parity, and doccheck.
   - `platform-verify`: Dedicated compilation and test execution for the shared `platform/` module (~1m 15s).
   - `service-verify-matrix`: Concurrent 8-way execution matrix across `services/*-service` with `fail-fast: false`, providing isolated per-service logs and statement coverage enforcement (~2m 15s).
   - `verify-pr`: Lightweight fan-in aggregator rollup job (`if: always()`) that evaluates all upstream results, generates a unified `$GITHUB_STEP_SUMMARY`, and satisfies the exact required status check context name `PR gate (verify-pr)`.
2. **Automating Headless Newman Verification in CI (`lgtm-e2e.yml`)**:
   - Adding automated execution of the Postman collections and Newman runner (`tests/postman/run-newman.sh`) after the Docker Compose stack converges and smoke tests pass.
   - Uploading JUnit XML test results via `actions/upload-artifact`.
3. **Preserving 100% Branch Protection Compatibility**:
   - Retaining the exact required check context name `PR gate (verify-pr)` in the fan-in aggregator so GitHub branch protection and auto-merge function without re-configuration.

---

## Detailed Component Design

### 1. 4-Tier Parallel Verification DAG Specification

```yaml
name: verify

on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

permissions:
  contents: read

jobs:
  preflight:
    name: Fast-fail preflight checks
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          submodules: true
          fetch-depth: 0
      - uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
        with:
          go-version-file: '.go-version'
          cache: true
          cache-dependency-path: '**/go.sum'
      - name: Verify Go module integrity
        run: bash scripts/verify-go-modules.sh --root . --manifest verification/go-module-roots.txt
      - name: Validate pinned GitHub Actions
        run: python3 tools/actionpin/actionpin.py --root . --lock verification/github-actions-lock.json
      - name: Validate agent guidance
        run: make validate-agent-guidance
      - name: Verify coverage documentation parity
        run: python3 scripts/sync-coverage-docs.py --check
      - name: Validate documentation
        run: make validate-documentation

  platform-verify:
    name: Platform runtime verification
    runs-on: ubuntu-latest
    needs: [preflight]
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
        with:
          go-version-file: '.go-version'
          cache: true
          cache-dependency-path: '**/go.sum'
      - name: Verify platform module
        run: make -C platform verify

  service-verify-matrix:
    name: ${{ matrix.service }}
    runs-on: ubuntu-latest
    needs: [platform-verify]
    timeout-minutes: 20
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
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-go@b7ad1dad31e06c5925ef5d2fc7ad053ef454303e # v7.0.0
        with:
          go-version-file: '.go-version'
          cache: true
          cache-dependency-path: '**/go.sum'
      - name: Verify service
        run: |
          make -C services/${{ matrix.service }} verify-pr
          ./scripts/check-coverage.sh ${{ matrix.service }} 80

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
            echo "preflight: ${{ needs.preflight.result }}" >&2
            echo "platform-verify: ${{ needs.platform-verify.result }}" >&2
            echo "service-verify-matrix: ${{ needs.service-verify-matrix.result }}" >&2
            exit 1
          fi
          echo "SUCCESS: All verification gates completed successfully."
      - name: Generate PR gate summary
        run: |
          cat << 'EOF' >> "$GITHUB_STEP_SUMMARY"
          ## PR Gate Verification Summary

          | Tier | Component | Status |
          | --- | --- | --- |
          | Tier 1 | Fast-Fail Preflight (Modules, Actions, Guidance, Docs) | ✅ Passed |
          | Tier 2 | Platform Runtime Verification (`platform/`) | ✅ Passed |
          | Tier 3 | 8-Way Service Matrix (Catalog, Customer, Inventory, etc.) | ✅ Passed |
          | Tier 4 | Fan-In Aggregation Anchor | ✅ Passed |
          EOF
```

---

### 2. Automated Newman Integration in `lgtm-e2e.yml`

In `.github/workflows/lgtm-e2e.yml`, immediately following the smoke container exit code verification:
```yaml
      - name: Run Newman integration and E2E saga test suite
        run: |
          set -euo pipefail
          ./tests/postman/run-newman.sh --env tests/postman/environments/go-microservices.ci.postman_environment.json all

      - name: Upload Newman test reports
        if: always()
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: newman-reports-${{ github.sha }}
          path: tests/postman/reports/
          retention-days: 14
```
