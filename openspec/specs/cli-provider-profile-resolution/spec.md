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

The selector SHALL treat a requested CLI adapter identity and a selected canonical provider identity as distinct typed identities. Candidate discovery SHALL use only explicit `cli_provider` declarations and `defaults.cli_models` relationships in a valid canonical catalog; it SHALL NOT infer a canonical provider identity from a CLI name, protocol, model, endpoint, executable, or credential availability. A successful selection and its provider-neutral projection SHALL preserve both the requested CLI adapter identity and selected canonical provider ID, use the CLI identity for adapter capability and executable validation, and use the canonical provider ID for provider-owned credential metadata. The selector SHALL distinguish absence of an applicable canonical CLI mapping from a canonical configuration that declares a relationship for the requested CLI but cannot produce one valid selection. It SHALL return no selection only when the requested CLI provider is genuinely absent from a valid canonical catalog—meaning that no provider declaration or default mapping targets that CLI identity—or when the profile is valid and legacy-only. Once any canonical provider or default mapping declares a relationship for the requested CLI identity, a missing, undefined, ambiguous, mismatched, unsupported, or otherwise invalid provider/model relationship MUST fail closed before local fallback or process launch.

#### Scenario: CLI provider absent from valid catalog

- **GIVEN** a valid canonical catalog with `codex` and `claude` but no declaration for `kimi`
- **WHEN** selection is requested for `kimi`
- **THEN** the return value SHALL indicate no canonical selection
- **AND** the consumer MAY use its permitted local configuration

#### Scenario: Canonical config exists but is invalid

- **GIVEN** a canonical catalog maps `codex` to a nonexistent model
- **WHEN** the selector resolves for `codex`
- **THEN** selection SHALL fail before any process launch
- **AND** the error SHALL identify the invalid alias without exposing protected values
- **AND** the consumer SHALL NOT use local fallback

#### Scenario: Legacy-only profile returns None

- **GIVEN** a legacy-only profile with no per-CLI model mapping and no new-schema providers
- **WHEN** selection is requested for `codex`
- **THEN** the return value SHALL indicate no canonical selection
- **AND** the consumer MAY fall back to its local configuration

#### Scenario: Declared provider has no valid model selection

- **GIVEN** the canonical catalog declares a provider for `codex` but no model can be selected for it
- **WHEN** selection is requested for `codex`
- **THEN** selection SHALL fail before local fallback or process launch
- **AND** the error SHALL identify the provider and missing selection relationship

#### Scenario: Declared provider selection is ambiguous

- **GIVEN** the canonical catalog declares multiple eligible models for one CLI provider without an explicit disambiguating selection
- **WHEN** selection is requested for that provider
- **THEN** selection SHALL fail with the conflicting canonical aliases
- **AND** no model or credential from either candidate SHALL be passed to a process

#### Scenario: Canonical provider and CLI adapter identities remain distinct

- **GIVEN** canonical provider `tdt-codex` declares `cli_provider: codex`
- **WHEN** selection and provider-neutral projection are requested for CLI adapter identity `codex`
- **THEN** the result SHALL preserve `codex` as the CLI adapter identity and `tdt-codex` as the canonical provider ID
- **AND** adapter capability and executable validation SHALL use `codex`
- **AND** provider-owned credential metadata SHALL be filtered using `tdt-codex`
- **AND** neither identity SHALL be inferred from or replaced by the protocol, endpoint, model, executable, or credential availability

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

An enabled consumer SHALL NOT be described as integrated, wired, or functioning unless its invocation boundary resolves one canonical profile, consumes the resulting provider-neutral projection while preserving its CLI adapter and canonical provider identities, and constructs provider-specific arguments from that projection. An enabled consumer MAY use local configuration only after canonical profile resolution succeeds and the typed selector explicitly reports genuine mapping absence for that CLI identity. An unavailable or unreadable selected canonical source, canonical schema or relationship error, ambiguous selection, unsupported projection field, or other resolution/projection failure MUST fail before local fallback or process launch. A consumer bridge SHALL NOT convert such a failure into an empty override mapping, `None`, ordinary absence, or local configuration.

#### Scenario: ai-harness-skills canonical runtime wiring

- **WHEN** the harness runtime enables a supported native CLI provider with a canonical selection
- **THEN** the adapter invocation SHALL use the canonical wire model and supported behavior fields
- **AND** diagnostics SHALL preserve the canonical alias and redacted provenance
- **AND** native authentication SHALL remain within the adapter's approved boundary

#### Scenario: ai-review canonical reviewer wiring

- **WHEN** review orchestration enables supported native CLI reviewers with canonical selections
- **THEN** each reviewer SHALL receive only its own projected model and supported behavior fields
- **AND** a provider SHALL NOT receive another provider's model or credential-key metadata
- **AND** native authentication SHALL remain within each reviewer's approved boundary

#### Scenario: Consumer bridge preserves both provider identities

- **GIVEN** a canonical projection selects CLI adapter identity `codex` through canonical provider `tdt-codex`
- **WHEN** `ai-harness-skills` or `ai-review` constructs the native adapter invocation
- **THEN** adapter selection and executable validation SHALL use `codex`
- **AND** diagnostics and retained evidence SHALL preserve `tdt-codex` as the canonical provider ID
- **AND** any credential-key metadata SHALL already be filtered for `tdt-codex`
- **AND** no credential value or another provider's key metadata SHALL be passed to the adapter

#### Scenario: Canonical resolution failure is not mapping absence

- **GIVEN** an enabled consumer selected a canonical source or catalog for its operation
- **WHEN** that source is unavailable or unreadable, or profile resolution, selection, or projection fails
- **THEN** the consumer bridge SHALL propagate a redacted failure before adapter construction or process launch
- **AND** it SHALL NOT return an empty override mapping or `None`
- **AND** it SHALL NOT preserve or activate local model configuration as though the CLI mapping were genuinely absent

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

Live CLI acceptance SHALL be recorded in a durable, credential-safe ledger bound to the exact integrated planning, consumer, and resolved dependency identities that produced the result. The required acceptance matrix SHALL contain exactly two required rows: one `ai-harness-skills` row through its true contained generation boundary and one `ai-review` row through its true reviewer boundary. Each required row SHALL be executed, evaluated, and retained independently, even when one reusable mechanism invokes both boundaries. Every row SHALL bind the exact consumer Git SHA, resolved canonical-library Git SHA, dependency source and lock identity, complete product/test/acceptance-script dirty-state disposition, CLI adapter identity, canonical provider ID, canonical alias, wire model, supported behavior fields, non-secret canonical source fingerprints, redacted command shape, monotonic duration, process result, nested result or report outcome, nonce or generated artifact, target-preservation result, and non-secret shell/provider prerequisite identity and outcome. The ledger MUST distinguish process reachability from successful nested consumer behavior and MUST contain no credential value. A required row MUST be invalidated when its planning identity, participating source identity, resolved dependency identity, unaccounted product/test/acceptance-script diff, canonical source fingerprint, or selected shell/provider prerequisite state changes.

#### Scenario: Successful consumer-boundary acceptance is recorded

- **WHEN** a live native-CLI call succeeds through a participating consumer boundary
- **THEN** the durable record SHALL identify the consumer, exact consumer and canonical-library Git SHAs, dirty-state disposition, CLI provider, canonical alias, wire model, supported behavior fields, redacted command shape, monotonic duration, process exit, nested result or report outcome, and nonce or generated artifact
- **AND** the record SHALL contain no credential value

#### Scenario: Reachable process has an unsuccessful nested result

- **WHEN** the native CLI process starts or exits successfully but the consumer's nested result reports a provider error, incomplete generation, missing nonce, or missing artifact
- **THEN** acceptance SHALL fail
- **AND** the ledger SHALL preserve the process result and nested failure as distinct fields

#### Scenario: Untracked script is not durable acceptance evidence

- **GIVEN** an acceptance script exists without a retained result bound to exact integrated SHAs and dirty-state disposition
- **WHEN** implementation readiness is evaluated
- **THEN** the script SHALL be treated as a test mechanism rather than proof of a successful run
- **AND** the consumer SHALL remain unaccepted until a current durable result is captured

#### Scenario: Source identity changes after acceptance

- **GIVEN** a live result was accepted for exact source identities
- **WHEN** a participating repository advances or gains an unaccounted product diff
- **THEN** the prior live result SHALL be marked stale for release acceptance
- **AND** the affected deterministic and live gates SHALL be rerun

#### Scenario: Two required consumer rows are retained independently

- **WHEN** the minimum live-acceptance matrix is materialized
- **THEN** it SHALL contain exactly one required `ai-harness-skills` row and exactly one required `ai-review` row
- **AND** each row SHALL name one currently supported and enabled provider and one true contained consumer boundary
- **AND** each row SHALL have its own prerequisite status, process result, nested outcome, nonce or generated artifact, target-preservation result, and final row status
- **AND** a shared script MAY execute both rows but SHALL NOT collapse them into one result
- **AND** an optional additional row SHALL NOT replace either required row
- **AND** both required rows MUST pass independently before live acceptance is complete

#### Scenario: Resolved dependency identity changes after acceptance

- **GIVEN** a live row was accepted for exact consumer and canonical-library identities
- **WHEN** the consumer's dependency path, editable-source binding, lock identity, installed module origin, or resolved canonical-library Git SHA changes
- **THEN** the prior row SHALL be marked stale even when the consumer Git SHA is unchanged
- **AND** affected deterministic projection checks and the live consumer row SHALL be rerun against the new resolved dependency
- **AND** a stale candidate, wheel, cache, or editable checkout SHALL NOT satisfy exact-dependency acceptance

#### Scenario: Shell or provider prerequisite changes after acceptance

- **GIVEN** a live row was accepted with one non-secret shell and provider prerequisite identity
- **WHEN** the selected launcher or executable identity, executable version, canonical source fingerprint, provider availability, credential-availability status, environment-loading prerequisite, or owned shell/provider configuration changes
- **THEN** the prior live row SHALL be marked stale
- **AND** presence-only prerequisite checks and the affected live row SHALL be rerun
- **AND** no credential value SHALL be printed, compared, copied, rotated, or retained while recapturing the row

### Requirement: Automated artifact and dependency drift validation

Before a retained deterministic handoff or live row is reused to complete an evidence-backed task, unblock a downstream repository packet, authorize or launch either required live row, synchronize canonical specs, or declare archive readiness, a store-owned non-interactive validator MUST recapture and compare the current credential-safe acceptance identity with the identity retained by that evidence. The validator SHALL resolve the current planning store SHA and corrective-change tree; the concrete proposal, delta-spec, design, task, and evidence-schema paths and non-secret identities, including the current `artifactPaths.specs.existingOutputPaths`; participating repository and worktree SHAs plus complete relevant product, test, acceptance-script, and generated dirty-state disposition; each applicable dependency declaration, lock or editable source, filesystem checkout, installed import origin, and full Git SHA; canonical non-secret source fingerprints and loader identity; and presence-only shell, executable, provider, containment, authorization, credential-availability, and canonical-provider-binding prerequisites. It SHALL emit deterministic machine-readable per-field comparisons, affected-record and downstream-invalidation decisions, and an overall status without treating a missing, malformed, unresolved, indeterminate, or drifted field as current. Any such condition MUST produce a non-zero exit, classify affected evidence as `stale`, `blocked`, or `invalid`, and prevent reuse or lifecycle advancement until dependency-ordered recapture succeeds. The validator SHALL be read-only except for an explicitly selected result output, SHALL NOT launch a provider or consumer operation, mutate a repository or worktree, resolve dependencies from the network, or read, print, compare, serialize, or retain a credential value.

#### Scenario: Current retained evidence passes automated preflight

- **GIVEN** retained deterministic or live evidence contains every required planning, repository, dependency, source, dirt, mechanism, and prerequisite identity
- **WHEN** the validator recaptures the same current identities from their authoritative local sources
- **THEN** it SHALL emit a machine-readable `current` decision with a zero exit
- **AND** the result SHALL identify the exact evidence record and every compared field without containing a credential value
- **AND** only that validated record MAY be considered for the next separately authorized acceptance or lifecycle gate

#### Scenario: Artifact or dependency drift fails closed

- **GIVEN** retained evidence was accepted for one exact planning and dependency topology
- **WHEN** a planning artifact, repository SHA, relevant dirty path, product/test/acceptance mechanism, dependency declaration, lock or editable source, filesystem checkout, import origin, or upstream Git SHA differs from the retained identity
- **THEN** the validator SHALL exit non-zero and identify the changed non-secret fields
- **AND** it SHALL classify the affected record as `stale`, propagate invalidation to dependency-ordered downstream evidence, and block reuse, live launch, task completion, synchronization, and archive readiness
- **AND** a matching consumer SHA alone SHALL NOT override dependency or artifact drift

#### Scenario: Missing or indeterminate identity remains blocked

- **GIVEN** a required evidence field, repository, dependency checkout, import origin, source identity, prerequisite, or retained schema is missing, malformed, inaccessible, or cannot be resolved locally
- **WHEN** automated preflight evaluates the record
- **THEN** the validator SHALL exit non-zero and classify the result as `blocked` or `invalid`, never `current`
- **AND** it SHALL perform no provider call, consumer launch, network dependency resolution, repository or worktree mutation, or credential-value access
- **AND** the affected gate SHALL remain closed until the identity can be recaptured and validation is rerun successfully
