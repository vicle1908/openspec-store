# Proposal: Fix Testcontainers Aggregate Schema Validation and CI Pre-Push Linting

## Why
When PR #40 was pushed to remote, two CI gates failed:
1. `service-integration`: Failed at `testcontainers-validate-evidence` with `unsupported aggregate schema "go-microservices.testcontainers-aggregate/v1"` because `tests/ecosystem-verification/cmd/validate-evidence/main.go` strictly checked for the pre-rename schema `microservices.testcontainers-aggregate/v1`, while `scripts/aggregate-testcontainers-evidence.sh` outputs `go-microservices.testcontainers-aggregate/v1`.
2. `verify-pr`: Failed in `catalog-service` during `govulncheck` because CI was configured with `GO_VERSION: "1.26.5"`. `govulncheck` reported standard library vulnerability `GO-2026-5026` in `net/http@go1.26.5`, which is patched in `net/http@go1.26.6`.
3. Missing pre-push CI lint target: Developers had no unified local command (`make lint-ci`) to run `actionlint`, supply chain action pin checks, retention checks, module root integrity, and evidence schema validation before pushing to remote.

## What Changes
1. **Schema Acceptance in Evidence Validator**:
   Update `tests/ecosystem-verification/cmd/validate-evidence/main.go` to accept `go-microservices.testcontainers-aggregate/v1` as the primary schema and preserve `microservices.testcontainers-aggregate/v1` for backward compatibility. Update unit tests in `main_test.go`.
2. **Go Toolchain Patch in CI Workflows**:
   Update `GO_VERSION: "1.26.6"` in `.github/workflows/verify.yml` (and related workflows where appropriate) to resolve stdlib vulnerability `GO-2026-5026` (`net/http@go1.26.5` -> `1.26.6`).
3. **Local CI Linting Target (`make lint-ci`)**:
   Add a dedicated `lint-ci` Makefile target that runs `actionlint`, `scripts/verify-go-modules.sh`, `actionpin.py`, `verify-retention.py`, and `testcontainers-validate-evidence`.

## Capabilities

### Modified Capabilities
- `testcontainers-ecosystem-verification`: Accept `go-microservices.testcontainers-aggregate/v1` as valid aggregate manifest schema alongside legacy `microservices.testcontainers-aggregate/v1`.
- `platform-verification`: Update CI toolchain patch to Go 1.26.6 to eliminate known Go stdlib vulnerability `GO-2026-5026` in `net/http`.

## Impact
- `tests/ecosystem-verification/cmd/validate-evidence/main.go`: Validator accepts current aggregate schema.
- `.github/workflows/verify.yml`: CI runner uses Go 1.26.6 to pass `govulncheck`.
- `Makefile`: Provides `lint-ci` target for pre-push validation.
