# cli-provider-profile-resolution Specification

## Purpose

Define the provider-neutral contract for resolving canonical TDT provider/model/default profiles into isolated native CLI invocation settings. The contract preserves per-CLI identity, wire model, supported effort, credential-key metadata, provenance, and native authentication boundaries without exposing credential values.
## Requirements
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

### Requirement: Provider-neutral CLI profile

A CLI-provider consumer SHALL resolve an immutable profile per provider containing the executable identity, optional model alias, optional effort, bounded invocation limits, registered environment-key names, and redacted source provenance. The profile SHALL NOT contain credential values.

#### Scenario: ai-harness provider alias and effort

- **WHEN** ai-harness resolves its Claude or Codex provider profile
- **THEN** the selected model alias and effort SHALL follow the canonical precedence contract
- **AND** the adapter SHALL pass only supported values to that provider CLI

#### Scenario: ai-review provider profile

- **WHEN** ai-review enables a Claude, Codex, Kimi, or Pi reviewer
- **THEN** the reviewer SHALL receive its provider-neutral executable, alias, effort, and limits
- **AND** disabled reviewers SHALL not require model configuration

#### Scenario: Unsupported field for a provider

- **WHEN** a profile supplies an alias, effort, or limit that the selected CLI does not support
- **THEN** configuration validation SHALL fail before process launch with the provider and logical field identified

### Requirement: Canonical precedence and provenance

CLI-provider profile fields SHALL follow the canonical agent precedence contract and SHALL retain redacted provenance. Consumer-specific aliases MAY be supported only when declared in the environment-key registry with an explicit compatibility status.

#### Scenario: Environment alias overrides YAML alias

- **GIVEN** a registered consumer environment key specifies a model alias
- **AND** agent YAML specifies a different alias
- **WHEN** the CLI-provider profile is resolved
- **THEN** the environment alias SHALL win
- **AND** provenance SHALL identify the registered environment key name

#### Scenario: Undeclared legacy key is ignored or rejected explicitly

- **WHEN** an undeclared environment key resembles a model alias setting
- **THEN** it SHALL NOT silently affect the resolved profile
- **AND** strict diagnostics SHALL report it only if it is part of the configured unknown-key audit

### Requirement: Provider authentication remains isolated

The canonical profile SHALL standardize credential environment-key metadata but MUST NOT read, copy, translate, or inject credential values into another provider CLI's credential store. Each provider CLI SHALL continue to authenticate through its approved native boundary and allowlisted process environment.

#### Scenario: Codex invocation

- **WHEN** a Codex CLI adapter launches
- **THEN** it SHALL use the resolved non-secret model and effort arguments
- **AND** it SHALL retain the adapter's approved environment allowlist and native Codex authentication

#### Scenario: Claude invocation

- **WHEN** a Claude CLI adapter launches
- **THEN** it SHALL use the resolved non-secret model and effort arguments
- **AND** it SHALL retain the adapter's approved environment allowlist and native Claude authentication

#### Scenario: Credential absent

- **WHEN** a CLI's approved native credential boundary is unavailable
- **THEN** the adapter SHALL report the provider as unavailable or fail closed according to its invocation contract
- **AND** it SHALL NOT fall back to another provider's credential

### Requirement: CLI-provider effective-config diagnostics

Each CLI-provider consumer SHALL expose a redacted diagnostic that identifies enabled providers, executable names, effective model aliases, effort, limits, registered credential-key names, and source provenance.

#### Scenario: Healthy provider diagnostic

- **WHEN** provider configuration is valid
- **THEN** diagnostics SHALL report the effective non-secret invocation profile

#### Scenario: Conflicting aliases

- **WHEN** two supported sources define different model aliases
- **THEN** diagnostics SHALL identify the winning and shadowed source classes
- **AND** execution SHALL use the reported winner

### Requirement: Separate runtime boundaries remain explicit

Runtimes with their own model registry or provider-infrastructure role SHALL not be forced through this profile unless a later change defines a versioned bridge. The standard SHALL document the exclusion reason and owner.

#### Scenario: prime-agent boundary

- **WHEN** prime-agent resolves models from its TypeScript model registry and its own credential directory
- **THEN** this change SHALL treat it as a separate runtime boundary
- **AND** it SHALL not redirect its credentials into TDT configuration

#### Scenario: Provider adapter boundary

- **WHEN** claude-code-provider-adapter translates provider protocols
- **THEN** it SHALL remain provider infrastructure rather than a per-agent CLI-profile consumer

### Requirement: Canonical direct-model boundary for CLI projections

The provider-neutral projection SHALL distinguish a native CLI `model_alias` from a direct Pydantic-AI model identifier. If a CLI consumer receives a direct model ID from the canonical resolver, it SHALL be a registered `provider:model` value. Native aliases remain provider-owned invocation arguments and SHALL not be presented as proof of a canonical direct-model route.

#### Scenario: Native alias remains adapter-local

- **GIVEN** an enabled Claude, Codex, Kimi, or Pi adapter supports a provider-specific model alias
- **WHEN** the provider-neutral profile is projected
- **THEN** the alias SHALL remain a non-secret adapter field with its provider identity and provenance
- **AND** the adapter SHALL not route it through the Pydantic-AI model factory

#### Scenario: Localized alias is rejected for direct live use

- **GIVEN** a profile supplies a localized, display-only, or unregistered value where a direct `provider:model` ID is required
- **WHEN** live-provider acceptance is prepared
- **THEN** validation SHALL fail before process launch or provider invocation
- **AND** model construction or a zero-exit CLI wrapper SHALL not count as live success

#### Scenario: Native authentication remains isolated

- **GIVEN** a provider-neutral profile is valid but the provider CLI's native credential boundary is unavailable
- **WHEN** an adapter smoke gate runs
- **THEN** the result SHALL be reported as prerequisite-aware N/A or provider-unavailable
- **AND** it SHALL not use another provider's credential or silently pass

### Requirement: Each CLI consumer declares its native invocation boundary

Each CLI-provider consumer SHALL declare the native invocation format it targets and SHALL project only fields supported by that CLI. The projection SHALL preserve provider identity and canonical wire-model provenance, SHALL pass supported model/effort arguments for Claude/Codex, SHALL retain capability-safe defaults for Kimi/Pi when aliases/effort are unsupported, and SHALL NOT project credential values.

#### Scenario: Codex adapter receives canonical wire model and effort

- **WHEN** an ai-harness or ai-review Codex boundary receives the canonical profile
- **THEN** it SHALL pass `gpt-5.6-sol` (the wire model) to the native Codex command
- **AND** it SHALL pass the supported reasoning effort through the native Codex configuration argument
- **AND** it SHALL retain native authentication and the adapter environment allowlist

#### Scenario: Claude reviewer receives supported model and effort

- **WHEN** the ai-review Claude reviewer receives a canonical projection
- **THEN** it SHALL pass the wire model through `--model`
- **AND** it SHALL pass supported effort through `--effort`
- **AND** it SHALL not project credential values

#### Scenario: Kimi and Pi capability-safe fallback

- **WHEN** the canonical profile has no registered alias/effort capability for Kimi or Pi
- **THEN** the consumer SHALL retain the native executable and local safe defaults
- **AND** it SHALL not invent unsupported model or effort flags
- **AND** it SHALL not project credential values

#### Scenario: Projection preserves alias and wire model distinction

- **GIVEN** the canonical profile contains alias `codex-default` with wire model `gpt-5.6-sol`
- **WHEN** a CLI consumer projects the profile
- **THEN** the native command SHALL receive the wire model ID
- **AND** the canonical alias SHALL remain available for diagnostics/provenance
- **AND** the consumer SHALL not confuse the alias with the wire model ID

### Requirement: Consumer implementation claims require canonical API evidence

A consumer SHALL NOT be described as integrated, wired, or functioning unless its source imports or calls an equivalent canonical projection API. Documentation SHALL name the exact consumer boundary and evidence.

#### Scenario: ai-harness-skills canonical runtime wiring

- **WHEN** `ai-harness-skills` source is audited
- **THEN** `build_runtime()` SHALL resolve a canonical profile and call `get_canonical_overrides()` for enabled Claude/Codex adapters
- **AND** adapter settings SHALL receive canonical model/effort values
- **AND** the full suite and live acceptance evidence SHALL be recorded

#### Scenario: ai-review canonical reviewer wiring

- **WHEN** `ai-review` source is audited
- **THEN** `_build_reviewers()` SHALL call `resolve_canonical_overrides()` at the reviewer construction boundary
- **AND** Claude/Codex SHALL receive supported model/effort arguments while Kimi/Pi retain capability-safe defaults
- **AND** the full suite and live acceptance evidence SHALL be recorded

### Requirement: Native CLI format is advisory, not canonical

The canonical provider/model/default profile is the source of truth. Each native CLI format projection is a lossy translation; the canonical profile SHALL contain strictly more information than any single CLI format. Conflicts between the canonical profile and a projected CLI format SHALL be resolved in favor of the canonical profile.

#### Scenario: Canonical profile has more information than Codex config

- **GIVEN** the canonical profile contains provider definition, model alias, wire model, effort, context limit, and provenance
- **WHEN** this is projected into Codex `config.toml` format
- **THEN** the Codex config SHALL contain base_url, wire_api, model, and effort
- **AND** the Codex config SHALL NOT contain provenance, source fingerprints, or environment-key metadata
- **AND** the canonical profile SHALL be the authoritative source if Codex config is stale

#### Scenario: Conflicting alias between canonical and native

- **GIVEN** the canonical profile specifies alias `shopapikey-fable-5` with wire model `fable-5`
- **AND** a native CLI config contains a different model for the same provider
- **WHEN** the adapter projects the canonical profile
- **THEN** the canonical profile's model SHALL take precedence
- **AND** the adapter SHALL not silently adopt the native CLI's stale value
