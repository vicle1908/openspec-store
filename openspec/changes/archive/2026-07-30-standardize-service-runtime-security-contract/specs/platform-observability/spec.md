## ADDED Requirements

### Requirement: OTLP export uses verified authenticated transport outside local-fast

Every service and Collector hop SHALL use verified TLS for OTLP export in
`production-contract` and `strict`. Exporters SHALL validate the configured
collector identity and SHALL present workload authentication when required by
the receiver policy. A plaintext endpoint or insecure verification flag MUST
fail configuration validation outside `local-fast`; telemetry failure SHALL
not expose application secrets or weaken request processing authorization.

#### Scenario: Service exports through secure OTLP
- **WHEN** a service has a valid trust root, expected Collector identity, and required client authentication
- **THEN** traces and metrics for the selected purposeful operation reach the Collector with their existing resource and correlation attributes

#### Scenario: Operation telemetry is causally correlated
- **WHEN** an authorized or denied purposeful operation crosses multiple service and dependency boundaries
- **THEN** evidence starts from that operation's trace or correlation identity and proves the expected participating services, authenticated identities, and security outcome
- **AND** unrelated recent traces, metrics, or logs do not satisfy the assertion

#### Scenario: Insecure OTLP is selected in production-contract
- **WHEN** a service enables insecure OTLP or configures a plaintext endpoint in production-contract mode
- **THEN** startup fails before readiness

#### Scenario: Collector identity is invalid
- **WHEN** the Collector certificate does not match the configured identity or trust chain
- **THEN** export fails with a redacted trust error and service readiness reflects the required telemetry policy
