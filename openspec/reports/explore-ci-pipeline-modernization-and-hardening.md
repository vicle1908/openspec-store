# OpenSpec Exploration Report: CI/CD Pipeline Modernization and Failure Prevention

**Date:** 2026-10-03  
**Target Repository:** `~/Developer/platform/go-microservices`  
**OpenSpec Root:** `~/Developer/platform/openspec-store`  
**Author:** Hermes Agent (Nous Research)

---

## 1. Executive Summary & Objective

In multi-service monorepos like `go-microservices` (8 microservices, shared `platform/` library, Kafka, Temporal, Debezium CDC, PostgreSQL, Redis), CI/CD pipelines represent the primary governance boundary. While the pipeline enforces high standards (aggregate statement coverage $\ge 80.0\%$, strict agent guidance bounds, container manifest verification, zero secret leaks), recent pull requests (PR #41 and PR #42) encountered repeated failures prior to successful merge.

This exploration analyzes the root causes of PR pipeline failures, investigates modern CI/CD best practices, and proposes an architectural roadmap for pipeline resilience, deterministic caching, toolchain synchronization, and automated documentation parity.

---

## 2. Comprehensive Root Cause Audit of Monorepo PR Failures

An audit of pipeline failures in PR #41 and PR #42 reveals eight interacting failure vectors across five architectural layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CI/CD Pipeline Failure Vectors                        │
├──────────────────────────┬────────────────────────────┬─────────────────────┤
│ Toolchain & Linter Layer │ Governance & Quality Layer │ Infrastructure & OS │
├──────────────────────────┼────────────────────────────┼─────────────────────┤
│ 1. Triplicate Go Version │ 3. Statement Coverage Drop │ 6. Actions Cache    │
│    Declaration Drift     │ 4. Doccheck Table Mismatch │    Tar Collision    │
│ 2. Compiler vs Linter    │ 5. AGENTS.md Word Count    │ 7. Docker Hub Rate  │
│    Go 1.27 AST Crash     │    Violation (> 550 words) │    Limit / Timeout  │
│                          │                            │ 8. Distroless CVE   │
└──────────────────────────┴────────────────────────────┴─────────────────────┘
```

### Detailed Breakdown

1. **Toolchain Version Drift (Triplicate Declarations)**:
   - *Problem:* Go compiler versions were declared independently in 18 `go.mod` files, the root `Makefile` (`GO_VERSION := 1.27.1`), and four separate GitHub Actions workflow YAML files (`verify.yml`, `lgtm-e2e.yml`, `gitops-reconcile.yml`, `release-evidence.yml`).
   - *Consequence:* Bumping `go.mod` to Go 1.27 while workflows retained `GO_VERSION: "1.26.6"` caused runners to install older compilers, failing preflight checks immediately.

2. **Linter AST Panic on Go 1.27**:
   - *Problem:* Embedded analyzers (such as `staticcheck` within older `golangci-lint` distributions) crashed when parsing Go 1.27 AST nodes (`*ast.KeyValueExpr`).
   - *Consequence:* `make lint` failed during static checks on valid code until disabled via a local `.golangci.yml`.

3. **Double-Entry Test Coverage & Documentation Drift**:
   - *Problem:* `tools/doccheck` strictly validates that the markdown table in `docs/local-service-verification.md` matches verified statement coverage within $\pm 0.5\%$.
   - *Consequence:* Raising test coverage in one service to clear the $\ge 80.0\%$ threshold automatically broke `make validate-documentation` because the table was not updated simultaneously.

4. **Actions Cache Directory Ordering Collision**:
   - *Problem:* `actions/cache` was placed after tool bootstrap scripts (`scripts/contract-tools.sh bootstrap`).
   - *Consequence:* Bootstrap wrote read-only files (`0555`) into `~/go/pkg/mod`. Subsequent cache restore tar extraction failed with `Cannot open: File exists` (status 2).

5. **Unauthenticated Registry Rate-Limiting & Duplicate Queries**:
   - *Problem:* `scripts/verify-images.sh` made unauthenticated HTTPS calls to Docker Hub and Quay.io without retries or exponential backoff. Additionally, duplicate entries in `deploy/tools.env` (`REDIS_VERSION` and `REDIS_CLI_VERSION`) caused duplicate queries.
   - *Consequence:* A single dropped packet or 429 response on `redis:8.8.1-alpine3.23` failed `lgtm-e2e`.

6. **Agent Guidance Prose Limits**:
   - *Problem:* `tools/agentguide` enforces an upper ceiling of 550 words on `AGENTS.md`.
   - *Consequence:* Expanding technical guidance caused word counts to reach 565 words, blocking CI.

---

## 3. Modern Best Practices for Go Monorepos

### A. Dynamic Toolchain Resolution (`actions/setup-go`)
- **Industry Standard:** Use `actions/setup-go@v5` with `go-version-file: 'go.mod'` rather than hardcoded environment variables.
- **Benefits:** Single source of truth. Bumping the root or platform `go.mod` automatically updates all CI workflows without editing four YAML files.

### B. Resilient HTTP Registry Verification with Exponential Backoff
- **Industry Standard:** External network calls to rate-limited public APIs (Docker Hub, Quay.io) must use bounded retries (e.g., 3 attempts, 2s/4s backoff) and query deduplication.
- **Benefits:** Completely eliminates flaky preflight failures caused by ephemeral registry drops.

### C. Automated Documentation Synchronization (`sync-coverage-docs`)
- **Industry Standard:** Coverage metrics documented in markdown should be generated directly from machine-readable test artifacts (`summary.json`) via an idempotent script, rather than manually edited.
- **Benefits:** Guarantees documentation currency without breaking `tools/doccheck`.

### D. Smart Path Filtering & Concurrency
- **Industry Standard:** Use `dorny/paths-filter` to skip heavyweight E2E or platform smoke tests on changes that only touch documentation or standalone service logic, while keeping the full gate mandatory for cross-service PRs.

---

## 4. Proposed Architectural Changes

### Phase 1: Immediate Hardening (Current Change)
1. **Registry Manifest Check Hardening (`scripts/verify-images.sh`)**:
   - Add a 3-attempt retry loop with 2s exponential backoff in `fetch_manifest_via_http`.
   - Deduplicate `IMAGES` array before inspection.
2. **Automated Documentation Coverage Sync (`scripts/sync-coverage-docs.py`)**:
   - Create a script and Make target `make sync-coverage-docs` that reads `services/*/artifacts/verification/coverage/summary.json` and updates `docs/local-service-verification.md`.
3. **Workflow Version Normalization**:
   - Align workflow setup steps to reference canonical Go versioning.

### Phase 2: Workflow Path Filtering & Concurrency Optimization
- Introduce path-based matrix gating in `verify.yml` so standalone service PRs run focused checks in parallel, converging on a final unified check.

---

## 5. Next Steps

1. Create OpenSpec change `modernize-ci-pipeline-architecture` in `openspec-store`.
2. Apply Phase 1 enhancements in `go-microservices`.
3. Execute full local verification and promote to GitHub via Pull Request.
