## MODIFIED Requirements

### Requirement: Liveness, readiness, and startup probes

The platform SHALL expose `/health/live`, `/health/ready`, and
`/health/startup` for every HTTP service that advertises standard health
probes. Liveness SHALL return `200 OK` while the process is responsive.
Readiness SHALL return `200 OK` only when registered dependencies are healthy.
Startup SHALL return `503 Service Unavailable` until initial setup is
complete and `200 OK` only after the service’s migrations, messaging setup,
and worker registration requirements have completed. The endpoint behavior
MUST be backed by the same health registry used by container healthchecks.

#### Scenario: All advertised probes are reachable

- **WHEN** a healthy Shipping API is running
- **THEN** live, ready, and startup probes each return `200 OK`

#### Scenario: Startup remains fail-closed

- **WHEN** a required migration, topic, connector, or worker registration is
  incomplete
- **THEN** startup returns `503` and includes the failing setup category

#### Scenario: Dependency outage affects readiness only

- **WHEN** a downstream dependency becomes unavailable while the process is
  responsive
- **THEN** liveness remains `200` and readiness returns `503`

## ADDED Requirements

### Requirement: Healthcheck image compatibility is validated

Every Compose healthcheck command SHALL exist in the selected runtime image
for both linux/arm64 and linux/amd64. Overlay files MUST NOT replace a
repository-built image with an upstream image when that replacement removes
the probe executable or health endpoint.

#### Scenario: Arm64 collector healthcheck succeeds

- **WHEN** the arm64 Compose model starts the custom OTel collector
- **THEN** the image contains the configured probe executable and the
  collector healthcheck reaches `200`

#### Scenario: Probe executable is absent

- **WHEN** Compose resolves an image that lacks its configured healthcheck
  executable
- **THEN** preflight or Compose validation fails before claiming readiness
