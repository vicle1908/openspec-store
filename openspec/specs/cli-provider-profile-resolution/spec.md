# cli-provider-profile-resolution Specification

## Purpose

Define the provider-neutral contract for resolving canonical TDT provider/model/default profiles into isolated native CLI invocation settings. The contract preserves per-CLI identity, wire model, supported effort, credential-key metadata, provenance, and native authentication boundaries without exposing credential values.

## Requirements

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

Every installed CLI consumer that claims canonical provider integration MUST provide verifiable evidence that its implementation matches the canonical API contract. Claims without evidence SHALL be treated as unverified.

#### Scenario: Consumer claims require evidence

- **WHEN** a consumer claims canonical API integration
- **THEN** the claim MUST include verifiable evidence (test results, API response captures, or schema validation proofs)
- **AND** claims without evidence SHALL be rejected

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

### Requirement: Identity-bound live CLI acceptance evidence

Live CLI acceptance evidence MUST be bound to the exact CLI identity (version, configuration, runtime environment) at the time of execution. Evidence from a different identity SHALL NOT be used to validate the current identity.

#### Scenario: Evidence is identity-bound

- **WHEN** live CLI acceptance evidence is captured
- **THEN** the evidence MUST include the exact CLI identity (version, config hash, runtime env)
- **AND** evidence from a different identity SHALL be rejected

### Requirement: Automated artifact and dependency drift validation

Artifact and dependency drift MUST be automatically validated before each release. Drift detection MUST cover source files, dependencies, configurations, and generated artifacts.

#### Scenario: Drift detection runs automatically

- **WHEN** a release is prepared
- **THEN** automated drift detection MUST run against all tracked artifacts
- **AND** drift findings MUST be classified and resolved before release

### Requirement: Explicit provider CLI identity mapping

A canonical provider MAY declare one registered `cli_provider` identity. Selection SHALL match that explicit relationship only and SHALL preserve the canonical provider ID separately from the native adapter identity. A provider without `cli_provider` has no native CLI relationship. That absence MUST NOT be guessed from protocol, alias, wire model, endpoint, executable, or credentials and MUST NOT authorize launch when a consumer enables the adapter.

#### Scenario: Provider declares a CLI identity

- **GIVEN** canonical provider `tdt-codex` declares `cli_provider: codex`
- **WHEN** selection is requested for native adapter identity `codex`
- **THEN** the selector SHALL resolve `tdt-codex` as the canonical provider
- **AND** credential-reference filtering SHALL use `tdt-codex`
- **AND** adapter capability/executable validation SHALL use `codex`

#### Scenario: Provider has no CLI identity

- **GIVEN** canonical provider `batch-provider` has no `cli_provider`
- **WHEN** catalog inspection requests a native relationship for it
- **THEN** no native CLI relationship SHALL be returned
- **AND** no identity SHALL be inferred from any other provider field

#### Scenario: Enabled adapter cannot use unmapped provider

- **GIVEN** a consumer enables one native adapter identity
- **AND** no canonical provider explicitly declares that identity
- **WHEN** consumer composition begins
- **THEN** it SHALL fail before model selection or process launch
- **AND** no unmapped provider or local configuration SHALL be substituted

### Requirement: Required explicit CLI model mapping

Canonical `defaults.cli_models` SHALL contain exactly one explicit model-alias relationship for every native CLI identity enabled by a participating consumer. Each mapped alias MUST exist in canonical `models`, and that model's provider MUST declare the same `cli_provider` identity. Selection SHALL NOT infer a model from `defaults.model`, a unique candidate, provider name, protocol, wire model, executable, endpoint, credential availability, consumer-local configuration, or native CLI configuration.

#### Scenario: Explicit mappings select independently

- **GIVEN** `defaults.cli_models` maps `codex` to `codex-default` and `claude` to `claude-review`
- **WHEN** canonical selections are resolved
- **THEN** each CLI identity SHALL receive exactly its mapped canonical alias
- **AND** no alias, wire model, provider, or credential metadata SHALL cross between them

#### Scenario: Enabled provider has no mapping

- **GIVEN** a consumer enables `codex` but canonical `defaults.cli_models` has no `codex` entry
- **WHEN** the consumer resolves its invocation profile
- **THEN** resolution SHALL fail before adapter construction or process launch
- **AND** it SHALL NOT infer a candidate or use consumer-local/native CLI model configuration

#### Scenario: Mapping alias is undefined

- **GIVEN** `defaults.cli_models.codex` references an alias absent from canonical `models`
- **WHEN** canonical schema validation runs
- **THEN** validation SHALL fail with the logical mapping and alias identified
- **AND** no partial CLI selection SHALL be returned

#### Scenario: Mapping targets the wrong provider identity

- **GIVEN** `defaults.cli_models.codex` references a model whose provider declares `cli_provider: claude`
- **WHEN** canonical schema validation runs
- **THEN** validation SHALL fail with both non-secret identities
- **AND** no model or credential-reference metadata SHALL be projected to either adapter

#### Scenario: Unique candidate does not imply selection

- **GIVEN** exactly one canonical model belongs to a provider declaring `cli_provider: codex`
- **AND** `defaults.cli_models` does not map `codex`
- **WHEN** selection is requested for an enabled Codex consumer
- **THEN** selection SHALL fail as missing explicit mapping
- **AND** uniqueness SHALL NOT create an implicit default

### Requirement: Fail-closed canonical CLI selection

The selector SHALL preserve the requested native CLI adapter identity and the selected canonical provider ID as distinct typed identities. Candidate discovery SHALL use only explicit `providers.<id>.cli_provider` and `defaults.cli_models` relationships in a valid canonical profile. A successful selection SHALL preserve canonical alias, wire model, provider ID, typed protocol, supported behavior, provider-filtered credential-reference metadata, and redacted provenance.

If an enabled consumer's canonical source is absent, unreadable, malformed, incomplete, ambiguous, or inconsistent, or its explicit CLI mapping cannot produce exactly one supported selection, the operation MUST fail before local configuration, adapter construction, credential access, or process launch. Neither the selector nor a consumer bridge may convert failure into `None`, an empty override, defaults, native CLI configuration, or consumer-local model selection. The selector MAY return no selection only for a CLI identity that the caller is not enabling and that has no provider or mapping relationship in the valid canonical catalog; that result confers no permission to launch it.

#### Scenario: Unconfigured and disabled identity has no selection

- **GIVEN** a valid catalog and an identity that no provider or default mapping declares
- **AND** the consumer is not enabling that identity
- **WHEN** catalog inspection requests its selection
- **THEN** the selector MAY report no selection
- **AND** the result SHALL NOT authorize local configuration or process launch

#### Scenario: Enabled identity without relationship fails

- **GIVEN** a public consumer enables one CLI identity
- **AND** the valid canonical catalog declares no complete provider/model/default relationship for it
- **WHEN** consumer composition begins
- **THEN** the operation SHALL fail with a redacted missing-mapping diagnostic
- **AND** no local or native model configuration SHALL be activated

#### Scenario: Invalid canonical source fails

- **GIVEN** an enabled consumer selects an unavailable, unreadable, malformed, or relationship-invalid canonical source
- **WHEN** resolution is attempted
- **THEN** the original typed failure SHALL propagate in redacted form
- **AND** no adapter, credential access, or process launch SHALL occur

#### Scenario: Ambiguous relationship fails

- **GIVEN** canonical relationships produce zero or multiple eligible selections for an explicit CLI mapping
- **WHEN** selection is requested
- **THEN** selection SHALL fail with the conflicting non-secret identities
- **AND** no candidate SHALL be chosen by order, uniqueness heuristic, or consumer preference

#### Scenario: Provider and adapter identities remain distinct

- **GIVEN** canonical provider `tdt-codex` declares `cli_provider: codex`
- **WHEN** selection and provider-neutral projection are requested for adapter identity `codex`
- **THEN** the result SHALL retain `codex` for adapter capability/executable validation and `tdt-codex` for provider-owned route and credential-reference metadata
- **AND** neither identity SHALL be inferred from protocol, endpoint, alias, wire model, executable, or credential availability

#### Scenario: Consumer bridge cannot restore local selection

- **GIVEN** canonical selection returns or raises any missing, invalid, ambiguous, unsupported, or indeterminate result for an enabled provider
- **WHEN** ai-harness-skills or ai-review handles that result
- **THEN** the bridge SHALL fail before adapter construction
- **AND** it SHALL NOT preserve, merge, or activate a consumer-local model, effort, provider, endpoint, or executable mapping as a fallback

### Requirement: Canonical CLI override and provenance

Canonical provider definitions, model definitions, and provider relationships SHALL come only from the validated canonical profile. A supported run-scoped override MAY select one canonical alias already defined in `models`; it MUST pass the same provider/CLI relationship and capability validation as `defaults.cli_models`. An override SHALL NOT supply a raw wire model, provider, endpoint, protocol, credential reference/value, executable, fallback list, or arbitrary mapping. Every effective selection SHALL retain redacted canonical source and override provenance.

#### Scenario: Run override selects a defined canonical alias

- **GIVEN** canonical model alias `codex-review` belongs to the provider mapped to CLI identity `codex`
- **WHEN** an explicit run-scoped override selects `codex-review`
- **THEN** that alias SHALL become the selection for the operation
- **AND** provider, wire model, protocol, supported behavior, and credential-reference metadata SHALL still come from its canonical definitions
- **AND** provenance SHALL identify the override without exposing values

#### Scenario: Undefined or cross-provider override fails

- **GIVEN** a run-scoped override names an undefined alias or an alias belonging to a different CLI provider relationship
- **WHEN** selection is resolved
- **THEN** resolution SHALL fail before adapter construction
- **AND** no local alias or closest candidate SHALL be substituted

#### Scenario: Raw route override is rejected

- **GIVEN** an override attempts to provide a wire model, provider, endpoint, protocol, credential, executable, fallback list, or mapping
- **WHEN** canonical input validation runs
- **THEN** the unsupported fields SHALL be rejected
- **AND** canonical provider/model definitions SHALL remain unchanged

#### Scenario: Undeclared environment alias has no authority

- **WHEN** an undeclared process-environment key resembles a CLI model or provider selector
- **THEN** it SHALL have no effect on canonical selection, provenance, identity, or cache eligibility
- **AND** strict unknown-input diagnostics MAY report only the key name without reading it as model authority

### Requirement: Canonical alias boundary for CLI and Pydantic models

The provider-neutral CLI projection SHALL expose `canonical_alias` and `wire_model` as distinct values bound to the selected canonical provider and native adapter identity. Native adapters SHALL receive `wire_model` only through their typed projection. Direct Pydantic-AI construction SHALL receive the same `canonical_alias` plus the complete exact construction context. No path SHALL convert a native alias or wire model into a provider-prefixed public model string, and no native CLI argument SHALL be routed through the Pydantic-AI model factory.

#### Scenario: Native adapter receives wire model

- **GIVEN** a canonical selection has alias `codex-default` and wire model `gpt-5.6-sol`
- **WHEN** the Codex adapter constructs its command
- **THEN** its model argument SHALL be `gpt-5.6-sol`
- **AND** `codex-default` SHALL remain the canonical diagnostic/provenance identity

#### Scenario: Pydantic factory receives canonical alias and context

- **GIVEN** the same canonical catalog selects one direct Pydantic-AI route
- **WHEN** agent-core construction begins
- **THEN** `create_model` SHALL receive the selected canonical alias and exact context
- **AND** it SHALL not receive the CLI wire model, native alias, or provider-prefixed reconstruction

#### Scenario: Localized or native alias is rejected at direct boundary

- **GIVEN** a caller supplies a display-only, localized, native CLI, wire-model, or provider-prefixed string to the direct Pydantic-AI boundary
- **WHEN** construction validates it against the context primary route
- **THEN** construction SHALL fail before provider or credential access
- **AND** no string translation or nearest canonical alias SHALL be attempted

#### Scenario: Native authentication remains adapter-local

- **WHEN** a native CLI operation launches from a canonical projection
- **THEN** authentication SHALL remain within that adapter's approved native boundary
- **AND** no credential value SHALL enter the canonical profile, projection, Pydantic model factory, or consumer evidence
