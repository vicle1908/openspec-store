# Design: Testcontainers Aggregate Schema Alignment and Pre-Push CI Linting

## Context
Following the workspace repository rename to `go-microservices`, the aggregate Testcontainers script `scripts/aggregate-testcontainers-evidence.sh` was updated to produce evidence with schema:
`go-microservices.testcontainers-aggregate/v1`.
However, `tests/ecosystem-verification/cmd/validate-evidence/main.go` only checked against the legacy schema `microservices.testcontainers-aggregate/v1`, causing CI step `make testcontainers-validate-evidence` in `service-integration` to abort.

Additionally, `catalog-service` includes `vuln` (`$(GO) tool govulncheck ./...`) in its `verify-static` target. When executed in GitHub Actions with Go toolchain `1.26.5`, `govulncheck` identified standard library vulnerability `GO-2026-5026` in `net/http@go1.26.5`. This vulnerability is fixed in `net/http@go1.26.6`.

Finally, contributors lacked a single unified `make lint-ci` target to run GitHub Actions workflow linting (`actionlint`), action pin verification (`actionpin.py`), retention checks (`verify-retention.py`), and evidence validation locally before invoking `git push`.

## Goals / Non-Goals

**Goals:**
- Update `tests/ecosystem-verification/cmd/validate-evidence/main.go` to accept `go-microservices.testcontainers-aggregate/v1` while remaining backward-compatible with `microservices.testcontainers-aggregate/v1`.
- Update unit tests in `tests/ecosystem-verification/cmd/validate-evidence/main_test.go` to cover both schema variants.
- Update `GO_VERSION: "1.26.6"` in `.github/workflows/verify.yml` to ensure `govulncheck` in `catalog-service` passes cleanly without flagging unpatched standard library vulnerabilities.
- Add `lint-ci` target in root `Makefile` coordinating:
  1. `actionlint` across workflow files.
  2. `python3 tools/actionpin/actionpin.py --root . --lock verification/github-actions-lock.json`
  3. `python3 scripts/verify-retention.py --root . --baseline-ref origin/main`
  4. `bash scripts/verify-go-modules.sh --root . --manifest verification/go-module-roots.txt`
  5. `go -C tests/ecosystem-verification run ./cmd/validate-evidence --root "$(CURDIR)"` (if aggregate evidence is present).
- Verify all CI jobs report green on GitHub Actions for PR #40.

**Non-Goals:**
- Mutating other service makefile targets or introducing breaking changes to Go module layouts.
- Bypassing vulnerability scanners or loosening security gates.

## Architecture & Data Flow

```
                      Local Pre-Push Loop: `make lint-ci`
                                       |
          +----------------------------+----------------------------+
          |                            |                            |
          v                            v                            v
   [actionlint]             [Supply Chain Verification]    [Evidence Validation]
   .github/workflows/*.yml   - actionpin.py                validate-evidence
                             - verify-retention.py         (accepts v1 & go-v1)
                             - verify-go-modules.sh
                                       |
                                git push origin
                                       |
                        +--------------v--------------+
                        |  GitHub Actions PR Workflows |
                        +-----------------------------+
                               /              \
                              v                v
                     [verify-pr]       [service-integration]
                     Go 1.26.6         validates aggregate
                     (govulncheck      evidence schema:
                      passes stdlib)   PASS
```

## Decisions

1. **Dual Schema Acceptance in Validator**:
   Instead of abruptly dropping the old schema `microservices.testcontainers-aggregate/v1`, the validator will accept either `go-microservices.testcontainers-aggregate/v1` or `microservices.testcontainers-aggregate/v1`. This guarantees existing historical evidence and new aggregate files both validate.
2. **Go Toolchain Patch to 1.26.6**:
   Updating the CI patch level from 1.26.5 to 1.26.6 adheres strictly to the Go 1.26 release stream and resolves known vulnerability `GO-2026-5026` in `net/http` without requiring vulnerability exceptions.
3. **Idempotent CI Lint Target**:
   `make lint-ci` integrates seamlessly into the repository developer workflow and pre-push hooks.
