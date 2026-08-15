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

An enabled consumer SHALL NOT be described as integrated, wired, or functioning unless its invocation boundary resolves one canonical profile from the consumer-owned canonical TDT root, consumes one explicit `defaults.cli_models` selection while preserving its CLI adapter and canonical provider identities, and constructs provider-specific arguments only from that projection. A contained project, generated artifact, repository under review, or other operation target MUST NOT select or replace the canonical TDT root. Missing mapping, unavailable or unreadable source, schema or relationship error, ambiguous selection, unsupported projection field, or other resolution/projection failure MUST fail before adapter construction, credential access, or process launch. An enabled consumer MUST NOT use consumer-local or native CLI model configuration for missing or failed canonical selection, and a bridge SHALL NOT convert any such state into an empty override, `None`, ordinary absence, or fallback configuration.

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

#### Scenario: Missing mapping for enabled provider fails closed

- **GIVEN** canonical profile resolution succeeds but no explicit CLI model relationship exists for a provider enabled by the consumer
- **WHEN** the consumer builds its invocation
- **THEN** it SHALL fail before adapter construction or process launch
- **AND** it SHALL NOT use a unique candidate, global default, consumer-local setting, or native CLI configuration

#### Scenario: Contained target cannot select canonical sources

- **GIVEN** ai-harness-skills operates on a contained project or ai-review operates on a repository under review
- **WHEN** the consumer resolves its canonical profile
- **THEN** resolution SHALL use the consumer-owned canonical TDT root
- **AND** no configuration file beneath the target root SHALL influence canonical provider, alias, wire-model, behavior, or source selection merely because it is the target

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

#### Scenario: Direct adapter invocation is not consumer acceptance

- **GIVEN** an acceptance mechanism constructs or invokes a provider adapter directly
- **WHEN** implementation readiness is evaluated
- **THEN** that result SHALL be treated as adapter reachability evidence only
- **AND** it SHALL NOT satisfy the required ai-harness-skills generation row or ai-review reviewer row
- **AND** each required row SHALL remain incomplete until its true public consumer operation succeeds

#### Scenario: Duplicate nonce or artifact invalidates independence

- **GIVEN** the two required rows reuse the same nonce or claim the same generated artifact
- **WHEN** live acceptance is evaluated
- **THEN** the rows SHALL NOT be considered independently proven
- **AND** both affected rows SHALL remain incomplete until distinct consumer-owned results are captured

#### Scenario: Resolved executable must match the launched process

- **GIVEN** a required row records one executable path or version
- **WHEN** the consumer operation launches the provider CLI
- **THEN** the retained executable identity SHALL match the actual resolved and launched executable
- **AND** a different shim, candidate path, or reported version SHALL invalidate the row

#### Scenario: Provider is not currently enabled

- **GIVEN** a provider is catalogued but not currently supported and enabled by the selected public consumer operation
- **WHEN** live acceptance is attempted
- **THEN** the prerequisite SHALL be blocked and no process SHALL launch
- **AND** historical availability or disposable configuration SHALL NOT satisfy current enablement

#### Scenario: Current live authorization is absent

- **GIVEN** deterministic verification is complete but current authorization for credential-bearing live operations is absent
- **WHEN** live acceptance is considered
- **THEN** both required live rows SHALL remain blocked without process launch or credential access
- **AND** deterministic readiness SHALL remain separately reportable

### Requirement: Automated artifact and dependency drift validation

Before a retained deterministic handoff or live row is reused to complete an evidence-backed task, unblock a downstream repository packet, authorize or launch either required live row, synchronize canonical specs, or declare archive readiness, a store-owned non-interactive validator MUST recapture and compare the current credential-safe acceptance identity with the identity retained by that evidence. The validator SHALL resolve the current planning store SHA and corrective-change tree; the concrete proposal, delta-spec, design, task, retained schema, and evidence paths and non-secret identities through the change's current active or archived lifecycle location, including the current `artifactPaths.specs.existingOutputPaths`; participating repository and worktree SHAs plus complete relevant product, test, acceptance-script, and generated dirty-state disposition; each applicable dependency declaration, lock or editable source, filesystem checkout, installed import origin, and full Git SHA; canonical non-secret source fingerprints and loader identity; and presence-only shell, executable, provider, containment, authorization, credential-availability, and canonical-provider-binding prerequisites. It SHALL emit deterministic machine-readable per-field comparisons, affected-record and downstream-invalidation decisions, and an overall status without treating a missing, malformed, unresolved, indeterminate, or drifted field as current. Any such condition MUST produce a non-zero exit, classify affected evidence as `stale`, `blocked`, or `invalid`, and prevent reuse or lifecycle advancement until dependency-ordered recapture succeeds. The validator SHALL be read-only except for an explicitly selected result output, SHALL NOT launch a provider or consumer operation, mutate a repository or worktree, resolve dependencies from the network, or read, print, compare, serialize, or retain a credential value.

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

#### Scenario: Active change archives without breaking retained validation

- **GIVEN** the evidence validator and its tests refer to schemas or artifacts owned by an active change
- **WHEN** that change is archived and its lifecycle root moves from `changes/<name>` to `changes/archive/<dated-name>`
- **THEN** the validator SHALL resolve the retained schema and artifacts through the current lifecycle location or a stable store-owned reference
- **AND** the validator's complete retained test suite SHALL remain executable after the active path is removed
- **AND** a deleted active-change path SHALL NOT remain the only hardcoded schema or artifact source

#### Scenario: Archive-aware lookup fails safely

- **GIVEN** neither an active nor archived lifecycle location can be resolved uniquely for retained evidence
- **WHEN** the validator or its tests resolve a required schema or artifact
- **THEN** validation SHALL fail with a deterministic non-secret blocked or invalid result
- **AND** it SHALL not launch product code, access a credential value, search the network, or mutate the store

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
