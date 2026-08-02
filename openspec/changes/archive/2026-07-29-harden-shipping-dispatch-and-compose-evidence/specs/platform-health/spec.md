## MODIFIED Requirements

### Requirement: Liveness, readiness, and startup probes

The platform SHALL expose `/health/live`, `/health/ready`, and
`/health/startup` for every HTTP service that advertises standard health
probes. Liveness SHALL return `200 OK` while the process is responsive,
regardless of downstream dependency state. Readiness SHALL return `200 OK`
only when registered local dependencies are healthy. For Shipping, the
database SHALL be registered as a readiness and startup dependency and SHALL
be checked with a bounded `pgxpool.Pool.Ping`; Kafka, Debezium, remote Temporal,
and remote Nexus state SHALL remain separate operational or convergence
evidence. Startup SHALL return `503 Service Unavailable` until initial setup
and its registered local checks are complete and `200 OK` only after they pass.

#### Scenario: All advertised probes are reachable

- **WHEN** a healthy Shipping API is running with a reachable database
- **THEN** live, ready, and startup probes each return `200 OK`

#### Scenario: Liveness probe succeeds while a dependency is down

- **WHEN** the Shipping database is unavailable but the HTTP process remains
  responsive
- **THEN** `/health/live` returns `200 OK` because the process itself is still
  running

#### Scenario: Readiness probe fails while the database is down

- **WHEN** the Shipping database ping fails or times out
- **THEN** `/health/ready` and `/health/startup` return `503 Service Unavailable`
- **AND** the response identifies the redacted `database` check

#### Scenario: Remote Nexus state does not break local readiness

- **WHEN** Shipping has a healthy local database and registered worker role but
  a remote Nexus endpoint is unavailable
- **THEN** process liveness and local API readiness remain healthy
- **AND** the remote condition is recorded as separate degraded operational
  evidence

#### Scenario: Startup remains fail-closed

- **WHEN** migrations, local setup, or the database check is incomplete
- **THEN** `/health/startup` returns `503`
- **AND WHEN** setup and all registered local checks complete
- **THEN** `/health/startup` returns `200`

### Requirement: Probe response format

The readiness and startup probe responses SHALL be JSON with the schema
`{"status": "ok" | "degraded" | "unavailable", "checks": [{"name": "database", "status": "ok" | "fail" | "timeout", "latency_ms": 12, "message": ""}]}`.
The probe response SHALL NOT include sensitive information such as connection
strings, passwords, DSNs, internal hostnames, or provider payloads. Database
check failures SHALL use a stable generic message and SHALL preserve the
check name and timeout/failure status.

#### Scenario: Probe response JSON omits connection strings

- **WHEN** a database check reports a failure
- **THEN** the JSON response's `message` field contains a generic database
  failure reason but no DSN, password, hostname, or SQL detail

#### Scenario: Probe response identifies a timeout

- **WHEN** the bounded database ping exceeds its per-check timeout
- **THEN** the response includes `name=database` and `status=timeout`
- **AND** the response remains safe to expose to a probe caller
