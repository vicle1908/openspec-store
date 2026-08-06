# platform-health Specification

## Purpose

Implements liveness, readiness, and startup probes with role-based check registration, per-check timeouts, and a Registry that aggregates multiple checks for the platform's health endpoint.
## Requirements
> **Status**: LOCALLY VERIFIED. Probe primitives and deployment-level
> startup/readiness passed retained local kind acceptance, including Temporal
> namespace initialization and worker convergence. Collector and service
> readiness evidence is local-only; staging and production health remain
> unverified.
>
> **Acceptance evidence:** `make dev-up`, `make dev-smoke`, and `make validate-deployment` must pass for the target commit. Retain the `go-microservices.deployment-validation/v1` manifest at `artifacts/deployment-validation/<run-id>/manifest.json` (or the configured artifact root) with referenced health and smoke results.

### Requirement: Liveness, readiness, and startup probes
The platform SHALL expose `/health/live`, `/health/ready`, and
`/health/startup` for every HTTP service that advertises standard health
probes. Liveness SHALL return `200 OK` while the process is responsive,
regardless of downstream dependency state. Readiness SHALL return `200 OK`
only when registered dependencies are healthy. Startup SHALL return `503
Service Unavailable` until initial setup is complete and `200 OK` only after
the service's migrations, messaging setup, and worker registration
requirements have completed. The endpoint behavior MUST be backed by the same
health registry used by container healthchecks.

#### Scenario: All advertised probes are reachable
- **WHEN** a healthy Shipping API is running
- **THEN** live, ready, and startup probes each return `200 OK`

#### Scenario: Liveness probe succeeds while a dependency is down
- **WHEN** the database is unreachable
- **THEN** `/health/live` returns `200 OK` because the process itself is still running

#### Scenario: Readiness probe fails while a dependency is down
- **WHEN** the database is unreachable
- **THEN** `/health/ready` returns `503 Service Unavailable` with the failing dependency in the response body

#### Scenario: Startup remains fail-closed
- **WHEN** a required migration, topic, connector, or worker registration is incomplete
- **THEN** `/health/startup` returns `503 Service Unavailable` and includes the failing setup category
- **AND WHEN** all required setup has completed
- **THEN** `/health/startup` returns `200 OK`

### Requirement: Dependency checks with timeout
The platform SHALL provide a `Check` interface with a `Run(ctx) error` method. Each registered check SHALL be invoked with a configurable per-check timeout (default 5 seconds) when the readiness probe runs. If a check times out, the probe response SHALL include `check_status=timeout` for that dependency. Checks SHALL run in parallel with a shared 10-second upper bound.

#### Scenario: Dependency check times out within its budget
- **WHEN** a registered check does not return within the per-check timeout
- **THEN** the readiness probe reports the dependency with `status=timeout` and a non-200 response

#### Scenario: Dependency checks run in parallel
- **WHEN** three checks each take 2 seconds
- **THEN** the readiness probe's overall latency is roughly 2 seconds, not 6

### Requirement: Role probe subcommand
The platform SHALL provide a `healthcheck` subcommand that performs the same checks as the readiness probe but exits 0 on success and non-zero on failure. Docker Compose and Kubernetes SHALL invoke this subcommand as the `healthcheck.test` command.

#### Scenario: Healthcheck subcommand exits 0 on healthy dependencies
- **WHEN** every dependency check reports healthy
- **THEN** `healthcheck` exits 0

#### Scenario: Healthcheck subcommand exits non-zero on unhealthy dependencies
- **WHEN** any dependency check fails
- **THEN** `healthcheck` exits non-zero and prints the failing dependencies to stderr

### Requirement: Probe response format
The readiness and startup probe responses SHALL be JSON with the schema `{"status": "ok" | "degraded" | "unavailable", "checks": [{"name": "database", "status": "ok" | "fail" | "timeout", "latency_ms": 12, "message": ""}]}`. The probe response SHALL NOT include sensitive information such as connection strings, passwords, or internal hostnames.

#### Scenario: Probe response JSON omits connection strings
- **WHEN** a check reports a failure
- **THEN** the JSON response's `message` field for that check contains the failure reason but no DSN, password, or hostname

### Requirement: Registry-based health check aggregation

The platform SHALL provide a `*Registry` type that aggregates multiple `*Check` instances and exposes HTTP handlers for liveness, readiness, and startup probes.

#### Scenario: Registry aggregates multiple checks
- **WHEN** multiple checks are registered with a Registry
- **THEN** the readiness handler returns aggregated status
- **AND** individual check results are included in the response

### Requirement: Nexus health separates local readiness from remote dependency state

The platform health registry SHALL classify Nexus checks as local role
readiness, remote dependency health, or deployment convergence. Only a local
condition that prevents the process from serving its advertised role SHALL
make its Kubernetes readiness probe fail.

#### Scenario: Handler is locally ready

- **WHEN** the handler registration, poller, owned Task Queue, and callback
  route are operational
- **THEN** the handler role reports ready
- **AND** evidence identifies its endpoint, Service, Operation, Task Queue, and
  build without secrets

#### Scenario: Handler registration is missing

- **WHEN** a service advertises an Operation but its local handler or poller is
  absent
- **THEN** that handler role returns `503`
- **AND** the response identifies the missing local component

#### Scenario: Caller remote endpoint is unavailable

- **WHEN** an otherwise healthy caller cannot reach a remote Nexus endpoint
- **THEN** its dependency status becomes degraded and circuit/retry state is
  observable
- **AND** its readiness remains healthy when it can still accept work and
  apply its durable retry or configured fallback policy

### Requirement: Nexus deployment convergence is validated separately

Endpoint existence, declared target, authorization policy, registry drift, and
callback routability SHALL be checked by deployment validation and retained as
evidence. A failed convergence check SHALL block rollout but SHALL NOT be
misrepresented as process liveness.

#### Scenario: Endpoint target drifts

- **WHEN** the live endpoint target differs from the declared Namespace or Task
  Queue
- **THEN** deployment convergence fails with the exact drift
- **AND** running service liveness is unchanged

#### Scenario: Non-local authorization is missing

- **WHEN** staging or production lacks the declared Authorizer policy
- **THEN** deployment validation fails before the endpoint is advertised
- **AND** evidence contains no credential or token

### Requirement: Health checks are bounded and non-mutating

Every Nexus health check SHALL use a bounded timeout, redact credentials and
payloads, and SHALL NOT execute a mutating business Operation. End-to-end
non-production validation SHALL use an isolated non-mutating canary or
disposable test Operation.

#### Scenario: Routine readiness runs

- **WHEN** Kubernetes invokes a readiness endpoint
- **THEN** the check inspects local registration and bounded control-plane
  state
- **AND** it creates no Shipment, carrier dispatch, aggregate mutation, or
  outbox fact

#### Scenario: Canary fails

- **WHEN** the non-production canary cannot complete through callback routing
- **THEN** deployment acceptance fails with a redacted diagnostic
- **AND** no production business Operation was invoked

### Requirement: Healthcheck image compatibility is validated

Every Compose healthcheck command SHALL exist in the selected runtime image
for both linux/arm64 and linux/amd64. Overlay files MUST NOT replace a
repository-built image with an upstream image when that replacement removes
the probe executable or health endpoint.

#### Scenario: Arm64 collector healthcheck succeeds

- **WHEN** the arm64 Compose model starts the custom OTel collector
- **THEN** the image contains the configured probe executable and the collector healthcheck reaches `200`

#### Scenario: Probe executable is absent

- **WHEN** Compose resolves an image that lacks its configured healthcheck executable
- **THEN** preflight or Compose validation fails before claiming readiness
