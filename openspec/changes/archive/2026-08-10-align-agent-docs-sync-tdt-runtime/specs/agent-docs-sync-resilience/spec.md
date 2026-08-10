## MODIFIED Requirements

### Requirement: Fallback model for provider failover

The doc-sync LLM model SHALL support optional fallback models via the configured TDT provider boundary and a supported fallback model abstraction. When a fallback model ID is configured and constructible, a secondary provider SHALL be attempted after a primary failure covered by the fallback policy. If a route cannot be constructed because its credential is absent, docs-sync SHALL fail closed for that route and preserve a truthful diagnostic; it SHALL not misroute the request to another provider.

#### Scenario: Fallback to secondary model

- **WHEN** the primary model is unavailable for a fallback-eligible transient failure
- **AND** the secondary route is constructible from the TDT provider registry and environment
- **THEN** the fallback model SHALL be attempted in the configured order

#### Scenario: All providers exhausted

- **WHEN** all constructible models in the configured chain fail
- **THEN** an error SHALL be raised or returned with redacted details of the attempted routes
- **AND** the workflow SHALL preserve the failure reason and SHALL not report successful generation

#### Scenario: Fallback route is unconfigured

- **WHEN** a configured fallback route lacks its required credential or has incompatible provider configuration
- **THEN** that route SHALL be excluded from active construction or fail closed
- **AND** the primary route SHALL not be silently redirected through the fallback route's endpoint or credentials

#### Scenario: No fallback configured

- **WHEN** only a single model is configured
- **THEN** the error SHALL be raised or returned directly when that model fails

