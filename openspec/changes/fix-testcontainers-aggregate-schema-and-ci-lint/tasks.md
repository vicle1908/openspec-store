# Tasks

## 1. OpenSpec Change Specification & Delta Validation

- [ ] 1.1 Author delta spec for `testcontainers-ecosystem-verification` defining dual schema acceptance (`go-microservices.testcontainers-aggregate/v1` and `microservices.testcontainers-aggregate/v1`). Verification: strict OpenSpec validation passes.
- [ ] 1.2 Author delta spec for `platform-verification` documenting Go toolchain patch 1.26.6 in CI workflows to eliminate stdlib CVEs. Verification: strict OpenSpec validation passes.
- [ ] 1.3 Validate change strictly in central store using `openspec validate fix-testcontainers-aggregate-schema-and-ci-lint --strict --store openspec-store`. Verification: exit code 0, 0 errors.

## 2. Evidence Validator Schema Alignment

- [ ] 2.1 Update `tests/ecosystem-verification/cmd/validate-evidence/main.go` to accept `go-microservices.testcontainers-aggregate/v1` as the primary schema and allow `microservices.testcontainers-aggregate/v1` for backward compatibility. Verification: `go test ./tests/ecosystem-verification/...` passes.
- [ ] 2.2 Update unit tests in `tests/ecosystem-verification/cmd/validate-evidence/main_test.go` to assert valid handling of both schema variants and rejection of unapproved schemas. Verification: `go test -v ./tests/ecosystem-verification/cmd/validate-evidence/...` passes.

## 3. CI Workflow Toolchain Patch

- [ ] 3.1 Update `GO_VERSION: "1.26.6"` in `.github/workflows/verify.yml` so that standard library vulnerability `GO-2026-5026` in `net/http@go1.26.5` is cleared in CI. Verification: run `actionlint .github/workflows/verify.yml` and `python3 tools/actionpin/actionpin.py`.
- [ ] 3.2 Update `GO_VERSION: "1.26.6"` in `.github/workflows/release-evidence.yml`, `.github/workflows/lgtm-e2e.yml`, and `.github/workflows/gitops-reconcile.yml` for workflow consistency. Verification: run `actionlint` and `python3 scripts/verify-retention.py`.

## 4. Local Pre-Push CI Lint Target (`make lint-ci`)

- [ ] 4.1 Add `lint-ci` target in root `Makefile` that runs `actionlint`, `scripts/verify-go-modules.sh`, `actionpin.py`, `verify-retention.py`, and `testcontainers-validate-evidence`. Verification: run `make lint-ci` locally and confirm clean pass.

## 5. End-to-End Remote CI Verification & Knowledge Capture

- [ ] 5.1 Commit all changes to `fix/ci-verification-and-coverage` following Conventional Commits, push to remote, and monitor GitHub Actions runs for PR #40. Verification: all CI checks report green.
- [ ] 5.2 Update Notion entity documentation via `ntn` CLI and record lessons learned into `agentmemory`. Verification: `agentmemory` and `ntn` exit 0.
