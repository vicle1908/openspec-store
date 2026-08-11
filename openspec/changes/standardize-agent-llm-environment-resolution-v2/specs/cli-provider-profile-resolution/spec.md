## Purpose

Define a provider-neutral configuration contract for agent repositories that invoke LLM provider CLIs while preserving each CLI's isolated authentication and runtime policy. This spec governs how the canonical provider/model/default profile (defined by `provider-model-profile-resolution`) projects into each native CLI's configuration format.

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Each CLI adapter declares its target native format

Each CLI-provider consumer SHALL declare the native configuration format it targets (e.g., Codex `config.toml`, Kimi `config.toml`, Pi `mcp.json`) and SHALL project the canonical provider/model/default profile into that format's schema. The projection SHALL preserve the provider identity, wire model ID, alias, and effort; it SHALL NOT project credential values.

#### Scenario: Codex adapter projects to config.toml format

- **WHEN** a Codex CLI adapter receives the canonical profile
- **THEN** the adapter SHALL project `model_providers.<name>.base_url` and `wire_api` from the provider definition
- **AND** the adapter SHALL project the model alias and effort into the Codex config schema
- **AND** the adapter SHALL NOT project `auth_env` or any credential value

#### Scenario: Kimi adapter projects to config.toml format

- **WHEN** a Kimi CLI adapter receives the canonical profile
- **THEN** the adapter SHALL project `[providers.<name>]` with `type`, `base_url` from the provider definition
- **AND** the adapter SHALL project `[models.<alias>]` with `provider`, `model`, `max_context_size`
- **AND** the adapter SHALL NOT project API key values

#### Scenario: Pi adapter projects to mcp.json format

- **WHEN** a Pi CLI adapter receives the canonical profile
- **THEN** the adapter SHALL project transport configuration through the MCP boundary
- **AND** the adapter SHALL NOT project credential values into the MCP configuration

#### Scenario: Projection preserves alias and wire model distinction

- **GIVEN** the canonical profile contains alias `cockpit-luna` with wire model `gpt-5.6-luna`
- **WHEN** a CLI adapter projects this into its native format
- **THEN** the native format SHALL contain the wire model ID as the model value
- **AND** the alias SHALL be available for diagnostics and provenance
- **AND** the adapter SHALL not confuse the alias with the wire model ID

### Requirement: No consumer appears implemented until it imports the API

A consumer SHALL NOT be described as integrated, wired, or functioning unless it imports `project_cli_profile()` or an equivalent canonical projection API. Documentation SHALL explicitly state when a consumer is proposed but not implemented.

#### Scenario: ai-harness-skills is not implemented

- **WHEN** `ai-harness-skills` source is audited for `project_cli_profile` or `CLIProviderProfile` imports
- **THEN** no such import SHALL be found
- **AND** documentation SHALL describe the consumer as proposed, not implemented

#### Scenario: ai-review is not implemented

- **WHEN** `ai-review` source is audited for `project_cli_profile` or `CLIProviderProfile` imports
- **THEN** no such import SHALL be found
- **AND** documentation SHALL describe the consumer as proposed, not implemented

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
