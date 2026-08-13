## ADDED Requirements

### Requirement: Provider-bound credential access

Every public boundary that resolves or reveals protected provider credential material MUST require an explicit, non-empty canonical provider identity. Before reading an environment value, resolution SHALL identify exactly one credential metadata entry for the supplied typed or raw reference and SHALL verify that the selected metadata, any provider carried by the reference, and the requested provider all have the same non-empty provider binding. Missing, duplicate, ambiguous, unbound, or mismatched relationships MUST fail closed. A raw key-name reference SHALL NOT bypass provider binding. The credential-binding identity SHALL be the canonical provider ID, not a CLI adapter identity, protocol, model name, endpoint, or another provider's available credential. Protected material SHALL remain process-local and non-serializable and SHALL NOT appear in profiles, diagnostics, provenance, reports, exceptions, or retained evidence.

#### Scenario: Matching provider accesses protected credential

- **GIVEN** exactly one validated credential reference is bound to canonical provider `giaoduc`
- **WHEN** resolution and reveal are requested with canonical provider identity `giaoduc`
- **THEN** the process-local credential SHALL be available to that provider boundary
- **AND** no serializable profile, diagnostic, provenance record, report, exception, or retained evidence SHALL contain the value

#### Scenario: Public credential boundary requires provider identity

- **GIVEN** a protected provider credential reference or protected credential is available
- **WHEN** public resolution or reveal is invoked without a provider argument or with an empty provider identity
- **THEN** access SHALL fail at the public security boundary before environment lookup or value return
- **AND** the error SHALL identify the missing provider context without exposing protected material

#### Scenario: Raw key reference is bound before environment lookup

- **GIVEN** a raw environment-key name identifies exactly one credential metadata entry bound to canonical provider `giaoduc`
- **WHEN** protected resolution is requested with canonical provider identity `giaoduc`
- **THEN** the resolver SHALL validate the unique provider binding before reading the environment value
- **AND** any returned protected credential SHALL remain bound to `giaoduc`
- **AND** later reveal SHALL still require the matching canonical provider identity

#### Scenario: Credential provider binding is missing or ambiguous

- **GIVEN** a typed or raw credential reference identifies no provider-bound metadata entry or more than one candidate metadata entry
- **WHEN** protected access is requested
- **THEN** access SHALL fail before any environment value is read
- **AND** an available environment variable SHALL NOT make an unbound or ambiguous reference acceptable
- **AND** no protected credential SHALL be constructed or returned

#### Scenario: Typed reference and requested provider disagree

- **GIVEN** a typed credential reference carries provider `anthropic`
- **WHEN** its matched metadata or requested canonical provider identity is `openai-chat`
- **THEN** resolution SHALL fail with a redacted provider-mismatch diagnostic before environment lookup
- **AND** no protected credential SHALL be constructed or substituted

#### Scenario: Cross-provider credential access is rejected

- **GIVEN** a protected credential is bound to canonical provider `anthropic`
- **WHEN** reveal is requested for canonical provider `openai-chat`
- **THEN** access SHALL fail with a redacted provider-mismatch diagnostic
- **AND** the `anthropic` credential SHALL NOT be returned, copied, or substituted

#### Scenario: Another provider credential is available

- **GIVEN** the selected provider's credential is unavailable and another provider's credential is available
- **WHEN** the selected provider attempts protected access
- **THEN** access SHALL fail for the selected provider
- **AND** the other provider's credential SHALL NOT be used as a fallback
