## ADDED Requirements

### Requirement: Liveness, readiness, and startup probes
The platform SHALL expose three HTTP probe endpoints: `/health/live`, `/health/ready`, and `/health/startup`. The liveness probe SHALL always return `200 OK` while the process is responsive, regardless of downstream dependency state. The readiness probe SHALL return `200 OK` only when every registered dependency check reports healthy. The startup probe SHALL return `200 OK` after the service has finished initial setup (database migrations applied, Kafka topics provisioned, Debezium connectors registered, Temporal namespace and worker registration complete) and SHALL return `503 Service Unavailable` until then.

#### Scenario: Liveness probe succeeds while a dependency is down
- **WHEN** the database is unreachable
- **THEN** `/health/live` returns `200 OK` because the process itself is still running

#### Scenario: Readiness probe fails while a dependency is down
- **WHEN** the database is unreachable
- **THEN** `/health/ready` returns `503 Service Unavailable` with the failing dependency in the response body

#### Scenario: Startup probe fails until setup is complete
- **WHEN** the database migrations have not yet been applied
- **THEN** `/health/startup` returns `503 Service Unavailable`
- **AND WHEN** migrations are applied and topics provisioned
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