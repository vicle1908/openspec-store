# Design: Portable agent-core Compose integration verifier

## Scope boundary

The verifier is a local test utility, not a service runtime. It observes the Compose containers used by the local data-plane stack and does not mutate business data or replace the shared `platform/health` registry.

## Binary

`platform/cmd/agent-core` is built by the platform Go module. It exposes:

- `agent-core version` — prints the binary version and exits zero.
- `agent-core health` — checks `postgres`, `kafka`, `temporal`, and `mailpit` through `docker compose ps --format json`, prints an indented JSON report, and exits zero only when every selected container is running and healthy (or has no health field).

The binary accepts:

- `AGENT_CORE_HEALTH_TIMEOUT` as a Go duration, defaulting to `30s`.
- `AGENT_CORE_COMPOSE_FILE`, `AGENT_CORE_COMPOSE_ENV_FILE`, and `AGENT_CORE_COMPOSE_PROJECT` to select the Compose file, interpolation env file, and project. When unset, it preserves normal Docker Compose discovery.

Compose output is parsed as either one JSON object or a JSON array. Empty output, malformed JSON, missing service records, stopped containers, and non-healthy health states are failures. A malformed record is never silently treated as healthy.

## Shell entry point

`scripts/agent-core-integration-test.sh` derives the repository root from its own location. Defaults are:

- Compose file: `deploy/docker-compose.yaml`
- Compose interpolation env file: `deploy/tools.env`
- Project: `go-microservices`
- Binary output: `bin/agent-core`
- Health timeout: `60s`

The script validates the Docker and Compose prerequisites, builds the binary unless `AGENT_CORE_BIN` points to an executable, starts the four selected services, polls bounded health state, runs `agent-core health`, and removes the Compose stack and only a binary built by that invocation. A caller-owned override binary is never removed.

Health timeout parsing accepts positive `s`, `m`, or `h` durations and fails closed for invalid values. Compose polling treats command failure, invalid JSON, and an empty container list as errors rather than success.

## Verification

The regression script uses temporary directories and stubbed executables; it never starts Docker or mutates the repository. Go unit tests cover Compose JSON object/array parsing, empty output, malformed output, missing records, stopped containers, unhealthy containers, and healthy records. The focused platform gates are `gofmt`, `go test ./cmd/agent-core/...`, `go vet ./cmd/agent-core/...`, and `go build ./cmd/agent-core`.
