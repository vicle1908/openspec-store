## ADDED Requirements

### Requirement: Collector configuration matches the pinned binary

Every OpenTelemetry Collector configuration used by local, CI, staging, or production deployment SHALL validate with the exact pinned Collector image before the deployment can start or be promoted.

#### Scenario: Supported Collector configuration validates

- **WHEN** CI runs the pinned Collector image's configuration validation command against every tracked Collector configuration
- **THEN** each configuration exits zero and all referenced receivers, processors, exporters, extensions, and internal-telemetry fields are supported by that image

#### Scenario: Removed configuration field blocks promotion

- **WHEN** a Collector configuration contains a field or component rejected by the pinned image
- **THEN** validation exits non-zero, identifies the configuration path, and prevents local acceptance and deployment promotion

### Requirement: Collector readiness reflects pipeline availability

Collector health SHALL be determined through an enabled health endpoint or supported internal-telemetry endpoint and SHALL remain false when configuration loading or required pipeline startup fails.

#### Scenario: Valid pipelines become ready

- **WHEN** the Collector loads all required pipelines and starts its configured health endpoint
- **THEN** the container or Pod readiness check succeeds and OTLP clients can connect to the documented receiver ports

#### Scenario: Collector process exits during startup

- **WHEN** configuration decoding or pipeline initialization causes the Collector process to exit
- **THEN** dependent acceptance tests fail readiness and retain the Collector startup logs

### Requirement: Required telemetry assertions fail closed

Cross-service acceptance and post-deployment verification SHALL require telemetry from every service named by the acceptance profile and MUST NOT convert a missing trace, metric, or log assertion into a passing result.

#### Scenario: Expected service traces are present

- **WHEN** the acceptance workflow completes successfully
- **THEN** the verifier finds correlated traces for every required service and records their trace identifiers in evidence

#### Scenario: Required telemetry is absent

- **WHEN** a required service produces no matching telemetry within the bounded observation window
- **THEN** the verifier exits non-zero and identifies the missing service and signal
