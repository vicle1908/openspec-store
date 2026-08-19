# agent-docs-sync-tdt-runtime Specification

## Purpose
Define the shared TDT runtime boundary that lets agent-docs-sync resolve models, provider credentials, and generation limits consistently without copying or exposing secrets.
## Requirements
### Requirement: Shared TDT runtime precedence

The docs-sync runtime SHALL resolve model selection and consumer runtime limits using this precedence: explicit `DOCS_SYNC_*` environment overrides, explicit fields in the target repository's `config.yaml`, the active `$TDT_HOME/config.yaml` and `$TDT_HOME/.env` boundary, then safe code defaults. Provider endpoint and credential selection SHALL remain owned by the active TDT provider registry and secret file.

#### Scenario: Repository omits a primary model

- **WHEN** the target repository configuration does not set `runtime.model`
- **THEN** docs-sync SHALL use the active TDT model primary
- **AND** it SHALL retain the TDT fallback order and provider mapping

#### Scenario: Repository explicitly overrides the primary

- **WHEN** the target repository sets `runtime.model` to a valid provider/model identifier
- **THEN** docs-sync SHALL use that identifier as the primary
- **AND** it SHALL continue to obtain fallback identifiers, provider endpoints, and credentials from TDT

#### Scenario: Environment overrides the consumer primary

- **WHEN** `DOCS_SYNC_MODEL` is set to a valid provider/model identifier
- **THEN** that value SHALL override the repository and TDT primary for the current process
- **AND** the configured TDT fallback list SHALL remain available

#### Scenario: Runtime limits are configured

- **WHEN** `runtime.max_iterations` or `runtime.timeout_seconds` is set in repository configuration or the corresponding `DOCS_SYNC_*` environment variable is set (use `"none"` or `"unlimited"` in env vars to disable the limit)
- **THEN** generation SHALL use the effective resolved values, where the base `ConsumerRuntimeProfile` defaults are `None` (unlimited) and flavor defaults override when no explicit profile is provided
- **AND** hard-coded generation limits SHALL not replace them
- **AND** `None`/unset SHALL mean unlimited (no iteration or timeout cap)

#### Scenario: Secret boundary is preserved

- **WHEN** docs-sync resolves a provider model
- **THEN** credential values SHALL be read only through the active TDT environment/agent-core provider boundary
- **AND** configuration errors, reports, logs, and CLI output SHALL contain at most provider names, model identifiers, environment-variable names, and redacted error summaries

### Requirement: Provider-aware fail-closed resolution

Docs-sync SHALL construct the configured primary and fallback models in their declared order through the supported agent-core model boundary. A provider whose credential or protocol configuration is unavailable SHALL not be silently replaced by a different provider or endpoint.

#### Scenario: All configured routes are constructible

- **WHEN** the primary and every configured fallback route has valid non-secret configuration and an available credential
- **THEN** docs-sync SHALL construct a fallback chain in the declared order
- **AND** a primary request failure covered by the fallback policy SHALL be eligible for the next route

#### Scenario: A fallback route lacks credentials

- **WHEN** a configured fallback route cannot be constructed because its credential is unavailable
- **THEN** docs-sync SHALL fail closed for that route
- **AND** it MAY continue with a constructible primary route
- **AND** it SHALL emit a redacted diagnostic that identifies the unavailable route without exposing a secret

#### Scenario: No route is constructible

- **WHEN** neither the primary nor any configured fallback can be constructed
- **THEN** generation SHALL return an explicit provider/configuration failure
- **AND** the workflow SHALL not report generated documentation

