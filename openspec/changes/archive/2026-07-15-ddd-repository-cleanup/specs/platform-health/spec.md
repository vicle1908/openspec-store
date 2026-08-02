# platform-health (Delta Spec)

This delta modifies the `platform-health` specification to document the migration requirements for existing services that use incompatible health implementations.

## MODIFIED Requirements

### Requirement: Liveness, readiness, and startup probes

The platform SHALL expose three HTTP probe endpoints: `/health/live`, `/health/ready`, and `/health/startup`. The liveness probe SHALL always return `200 OK` while the process is responsive, regardless of downstream dependency state. The readiness probe SHALL return `200 OK` only when every registered dependency check reports healthy. The startup probe SHALL return `200 OK` after the service has finished initial setup (database migrations applied, Kafka topics provisioned, Debezium connectors registered, Temporal namespace and worker registration complete) and SHALL return `503 Service Unavailable` until then.

**Migration requirement**: Services currently using `map[string]Check` API (functional style) SHALL migrate to `Registry`-based design with `Check` interface.

#### Scenario: Liveness probe succeeds while a dependency is down
- **WHEN** the database is unreachable
- **THEN** `/health/live` returns `200 OK` because the process itself is still running

#### Scenario: Readiness probe fails while a dependency is down
- **WHEN** the database is unreachable
- **THEN** `/health/ready` returns `503 Service Unavailable` with the failing dependency in the response body

#### Scenario: Service migrates from functional to interface Check type
- **WHEN** a service uses `map[string]func(ctx context.Context) error` for health checks
- **THEN** it SHALL rewrite to use `Registry.Register(ProbeKind, Check)` with `Check` interface
- **AND** it SHALL implement `Name()` and `Run(ctx context.Context) error` methods

### Requirement: Probe response format

The readiness and startup probe responses SHALL be JSON with the schema `{"status": "ok" | "degraded" | "unavailable", "checks": [{"name": "database", "status": "ok" | "fail" | "timeout", "latency_ms": 12, "message": ""}]}`. The probe response SHALL NOT include sensitive information such as connection strings, passwords, or internal hostnames.

#### Scenario: Probe response JSON omits connection strings
- **WHEN** a check reports a failure
- **THEN** the JSON response's `message` field for that check contains the failure reason but no DSN, password, or hostname
