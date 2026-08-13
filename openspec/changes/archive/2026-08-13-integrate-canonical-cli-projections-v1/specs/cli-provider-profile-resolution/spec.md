## ADDED Requirements

### Requirement: Provider CLI identity mapping

A provider configuration SHALL declare an optional `cli_provider` field that maps
a YAML provider identity (e.g., `tdt-codex`) to a registered CLI identity
(e.g., `codex`). This mapping enables the public `select_canonical_cli_provider()`
API to resolve provider identity correctly without guessing from protocol.

#### Scenario: Provider with cli_provider mapping

- **GIVEN** a YAML provider `tdt-codex` with `cli_provider: codex`
- **WHEN** a consumer calls `select_canonical_cli_provider(profile, cli_provider="codex")`
- **THEN** the selector SHALL resolve to the `tdt-codex` provider definition
- **AND** the credential filtering SHALL use the YAML provider ID `tdt-codex`
- **AND** the protocol SHALL be taken from the provider definition

#### Scenario: Provider without cli_provider mapping

- **GIVEN** a YAML provider `tdt-legacy` without a `cli_provider` field
- **WHEN** a consumer calls `select_canonical_cli_provider(profile, cli_provider="legacy")`
- **THEN** the selector SHALL return `None` for that CLI provider
- **AND** it SHALL NOT guess the mapping from protocol or other heuristics

### Requirement: Default CLI model mapping

A canonical configuration SHALL declare an optional `defaults.cli_models` mapping
that associates each registered CLI provider identity with a specific model alias.
This replaces the current incorrect assumption that `defaults.model` applies to
all enabled providers simultaneously.

#### Scenario: Explicit cli_models mapping

- **GIVEN** `defaults: { model: codex-default, cli_models: { codex: codex-default, claude: claude-review } }`
- **WHEN** the selector resolves for `codex` and `claude`
- **THEN** each SHALL use its own mapped model alias
- **AND** no cross-contamination SHALL occur

#### Scenario: cli_models absent — compatibility fallback

- **GIVEN** `defaults: { model: codex-default }` with no `cli_models`
- **AND** exactly one model belongs to a provider whose `cli_provider` matches
- **WHEN** the selector resolves for that CLI provider
- **THEN** the unique matching alias SHALL be selected as a compatibility fallback

#### Scenario: Ambiguous aliases without cli_models

- **GIVEN** two models both targeting `cli_provider: codex` without explicit `cli_models`
- **WHEN** the selector resolves for `codex`
- **THEN** a `ProfileResolutionError` SHALL be raised identifying the ambiguity

### Requirement: Canonical alias versus wire model

A CLI provider selection SHALL distinguish:

- **canonical_alias**: the key in YAML `models` (e.g., `codex-default`)
- **wire_model**: the model string sent to the endpoint or CLI (e.g., `gpt-5.6-sol`)

The public selection API SHALL expose both fields. Consumers SHALL use
`wire_model` for invocation arguments and `canonical_alias` for diagnostics.

#### Scenario: Codex native invocation uses wire_model

- **GIVEN** a selection with `canonical_alias: codex-default`, `wire_model: gpt-5.6-sol`
- **WHEN** a Codex adapter constructs the CLI command
- **THEN** the `-m` flag SHALL receive `gpt-5.6-sol` (wire_model)
- **AND** the canonical alias SHALL remain available for provenance

#### Scenario: Native alias is provider-owned

- **GIVEN** a selection where the canonical alias differs from the wire model
- **WHEN** the adapter passes arguments to the CLI
- **THEN** the adapter SHALL NOT route the alias through the Pydantic-AI model factory
- **AND** the adapter SHALL use the wire model for provider-specific arguments

### Requirement: Credential filtering by provider ID

The public selection/project API SHALL expose credential key names filtered by the YAML provider ID (e.g., `tdt-codex`), not by the CLI identity. `project_canonical_cli_profile()` passes the selected YAML provider ID to the profile projection so credential ownership remains isolated.

#### Scenario: Credential keys filtered by YAML provider ID

- **GIVEN** a provider `tdt-codex` with `auth_env: OPENAI_API_KEY`
- **WHEN** the selection is resolved for `cli_provider: codex`
- **THEN** `credential_key_names` SHALL contain `OPENAI_API_KEY`
- **AND** no credential value SHALL appear in the selection

#### Scenario: Multi-provider credential isolation

- **GIVEN** providers `tdt-codex` (OPENAI_API_KEY) and `tdt-claude` (ANTHROPIC_API_KEY)
- **WHEN** selections are resolved for both CLI providers
- **THEN** each selection SHALL contain only its own provider's credential key names
- **AND** cross-contamination SHALL be impossible

### Requirement: Selection failure modes

The selector SHALL fail closed for invalid configurations:

#### Scenario: CLI provider absent from valid catalog

- **GIVEN** a valid canonical catalog with `codex` and `claude` but no `kimi`
- **WHEN** `select_canonical_cli_provider(profile, cli_provider="kimi")` is called
- **THEN** the return value SHALL be `None`
- **AND** no error SHALL be raised (graceful degradation)

#### Scenario: Canonical config exists but is invalid

- **GIVEN** a canonical catalog with `cli_models: { codex: nonexistent-model }`
- **WHEN** the selector resolves for `codex`
- **THEN** a `ProfileResolutionError` SHALL be raised before any process launch
- **AND** the error SHALL identify the invalid alias

#### Scenario: Legacy-only profile returns None

- **GIVEN** a legacy-only profile with no `defaults.cli_models` and no new-schema providers
- **WHEN** `select_canonical_cli_provider(profile, cli_provider="codex")` is called
- **THEN** the return value SHALL be `None`
- **AND** the consumer SHALL fall back to its local configuration

### Requirement: Supported fields validation

The selector SHALL validate against the CLI capability registry:

#### Scenario: Unsupported effort rejected

- **GIVEN** a CLI provider with registered efforts `["low", "medium", "high"]`
- **WHEN** `effort="insane"` is passed to the selector
- **THEN** a `ProfileResolutionError` SHALL be raised
- **AND** the error SHALL identify the unsupported effort value

#### Scenario: Limit out of bounds rejected

- **GIVEN** a CLI provider with registered limit `timeout_seconds: [1, 86400]`
- **WHEN** `limits={"timeout_seconds": 999999}` is passed
- **THEN** a `ProfileResolutionError` SHALL be raised before process launch
