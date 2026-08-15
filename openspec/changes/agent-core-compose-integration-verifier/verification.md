# Verification evidence

## Source provenance

- Repository: `~/Developer/go-microservices`
- Branch: `main`
- Implementation commit: `8a2dea18315a4e7c1b0105202cf8f7d3098c1099`
- Store: `~/Developer/openspec-store`
- Unrelated preserved paths: `services/order-service/.tool-versions`, `.omp/`

Committed-content verification used `git show HEAD:<path>` and SHA-256 comparison for all owned paths. Every committed hash matched the working-tree hash and the owned diff after commit was zero.

## Deterministic gates

All commands ran against the implementation commit or its exact pre-commit tree:

- `gofmt -w platform/cmd/agent-core/main.go platform/cmd/agent-core/main_test.go` — exit 0
- `go test ./cmd/agent-core/...` from `platform/` — exit 0; package passed
- `go vet ./cmd/agent-core/...` from `platform/` — exit 0
- `go build ./cmd/agent-core` from `platform/` — exit 0
- `make -C platform verify` — exit 0; full platform tests, vet, and build passed
- `bash -n scripts/agent-core-integration-test.sh` — exit 0
- `bash -n scripts/agent-core-integration-regression-test.sh` — exit 0
- `bash scripts/agent-core-integration-regression-test.sh` — exit 0; 18 passed, 0 failed
- `git diff --cached --check` — exit 0 before commit

The regression suite used temporary Git repositories and stubbed `go`/`docker` executables. It covered outside-cwd build, explicit Compose file/env selection, cleanup, caller-owned binary preservation, invalid overrides, empty/malformed Compose status, and health exit-code propagation. No Docker stack, credentials, network, or business data were required by that suite.

## Review findings resolved

- Removed the stale HTTP probe against Temporal gRPC port `7233`.
- Removed unused HTTP imports/helpers/constants.
- Passed the repository Compose file, interpolation env file, and project explicitly.
- Added object/array Compose JSON parsing and fail-closed handling for empty, malformed, missing, stopped, and unhealthy records.
- Made shell health polling bounded and fail closed; fixed health-command exit propagation under `set -e`.
- Replaced grep-only regression checks with executable fixture tests.

## Scope boundary

No canonical existing spec was overwritten. The existing `platform-health` contract remains the runtime health-registry/`healthcheck` contract; this change documents the separate local Compose integration verifier. No active OpenSpec change was found that already owned `platform/cmd/agent-core`.
