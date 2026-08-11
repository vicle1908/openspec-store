## MODIFIED Requirements

### Requirement: Standardized resolution precedence

The system SHALL resolve every effective agent LLM value in this priority order from highest to lowest:

1. Explicit run-scoped override supplied by the caller.
2. Consumer-specific process environment declared in the environment-key registry.
3. Shared model process environment declared in the environment-key registry.
4. Agent-specific TDT configuration under `$TDT_HOME/agents/{agent-name}.yaml`.
5. Global TDT configuration under `$TDT_HOME/config.yaml`.
6. Typed code defaults.

An empty value SHALL NOT silently suppress a lower non-empty value unless the registered field explicitly supports clearing. Every resolved field SHALL retain redacted provenance identifying its source class and logical key without retaining a secret value.

#### Scenario: Explicit run override wins

- **GIVEN** a run supplies model `openai-responses:gpt-5.6-luna`
- **AND** consumer environment, agent YAML, and global YAML specify other models
- **WHEN** the agent profile is resolved
- **THEN** the effective model SHALL be `openai-responses:gpt-5.6-luna`
- **AND** its provenance SHALL identify an explicit run override

#### Scenario: Env var overrides agent-specific YAML

- **GIVEN** `DOCS_SYNC_MODEL=openai-chat:fable-5` and `MODEL_PRIMARY=anthropic:Advance`
- **AND** the agent and global YAML files specify other models
- **WHEN** the `agent-docs-sync` profile is resolved
- **THEN** the effective model SHALL be `openai-chat:fable-5`
- **AND** no lower-priority source SHALL replace it later in model construction

#### Scenario: Agent-specific env var overrides agent-specific YAML

- **GIVEN** a registered consumer-specific model key and the shared model key are both set
- **AND** agent YAML specifies another model
- **WHEN** that consumer's profile is resolved
- **THEN** the consumer-specific environment value SHALL win

#### Scenario: Agent-specific YAML overrides global

- **GIVEN** no registered model environment variable is set
- **AND** agent YAML specifies `openai-chat:fable-5`
- **AND** global YAML specifies `anthropic:Advance`
- **WHEN** the profile is resolved
- **THEN** the effective model SHALL be `openai-chat:fable-5`

#### Scenario: Invalid high-priority value fails closed

- **GIVEN** a registered environment key contains an invalid model identifier or invalid typed value
- **WHEN** the profile is resolved
- **THEN** resolution SHALL fail with the logical field and source class
- **AND** it SHALL NOT silently fall back to a lower-priority value

### Requirement: Single config loading function

The system SHALL expose one canonical agent-profile resolution boundary that returns an immutable effective profile containing model, fallbacks, model behavior, provider metadata, runtime values, environment-key metadata, and redacted source provenance. Existing mapping-based loading SHALL remain only as a compatibility projection of the same resolution primitives and SHALL NOT implement a second precedence chain.

#### Scenario: Resolved profile is internally consistent

- **WHEN** a consumer resolves its agent profile
- **THEN** the profile's effective model, fallbacks, behavior settings, providers, runtime values, and provenance SHALL describe the same resolution snapshot
- **AND** downstream consumers SHALL NOT need to reload YAML or dotenv files

#### Scenario: Compatibility mapping uses the same sources

- **WHEN** a legacy caller requests the mapping projection for an agent
- **THEN** the projection SHALL be derived from the canonical loading primitives
- **AND** equivalent fields SHALL match the typed resolved profile

#### Scenario: Function returns merged config

- **WHEN** the compatibility mapping is requested for an agent
- **THEN** it SHALL contain the merged model and runtime projection from the same secure source snapshot

#### Scenario: Explicit agent config path overrides the standard overlay

- **GIVEN** a caller supplies an explicit agent-overlay path
- **WHEN** the profile and source-preserving overlay are loaded
- **THEN** both SHALL use that path instead of the standard agent YAML path
- **AND** diagnostics SHALL identify the explicit source path without exposing values

#### Scenario: Function is idempotent within a process

- **WHEN** the compatibility mapping is requested twice with unchanged effective inputs
- **THEN** both returned mappings SHALL be value-equivalent

#### Scenario: Unknown agent name returns global config only

- **GIVEN** no overlay exists for a valid unknown agent name
- **WHEN** its compatibility mapping is requested
- **THEN** global configuration and defaults SHALL remain available without error

#### Scenario: Default strict key policy

- **WHEN** `load_agent_config("agent-core")` is called without `allowed_overlay_keys`
- **AND** the agent YAML contains a top-level key `gate: {approvers: ["x"]}`
- **THEN** a `ConfigError` SHALL be raised (the default `{"model", "runtime"}` policy applies)

#### Scenario: Harness-expanded key policy accepts domain keys without error

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate", "persistence", "authority"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}` and `persistence: {durable: true}`
- **THEN** the call SHALL succeed without `ConfigError`
- **AND** the returned dict SHALL retain unrelated global sections unchanged; only `model` and `runtime` are affected by the overlay merge; domain keys validated by the allowed set SHALL not cause `ConfigError` but SHALL not be merged

#### Scenario: Cache isolation by allowed-key set

- **GIVEN** `load_agent_config("agent", allowed_overlay_keys={"model", "runtime"})` is called
- **WHEN** `load_agent_config("agent", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **THEN** both calls SHALL resolve independently with no cache collision

#### Scenario: Domain keys excluded from merged result

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}`
- **THEN** the returned dict SHALL retain unrelated global sections unchanged
- **AND** the agent overlay's `gate` section SHALL NOT be merged into or override any global section
- **AND** agent-harness SHALL obtain `gate` from `load_agent_overlay()`

### Requirement: Secure mapping and source-preserving overlay APIs

The resolver SHALL expose `load_config_mapping()` as the secure, non-merging reader
for one selected YAML mapping and `load_agent_overlay()` as the source-preserving
agent-overlay reader. Both APIs SHALL use the canonical root, explicit-file, secret,
and path-containment policy. `allowed_overlay_keys` SHALL be an explicit cacheable
policy input: the default policy permits only `model` and `runtime`, while a registered
consumer policy MAY admit domain sections that remain outside the effective LLM merge.

#### Scenario: Mapping reader does not merge sources

- **WHEN** `load_config_mapping()` reads a selected global or agent YAML file
- **THEN** it SHALL return only that file's validated mapping and source identity
- **AND** it SHALL not apply another file, environment value, or consumer overlay

#### Scenario: Overlay reader preserves domain provenance

- **GIVEN** a registered consumer policy allows a domain section in an agent overlay
- **WHEN** `load_agent_overlay()` reads the overlay
- **THEN** it SHALL retain the domain section with its source provenance
- **AND** `load_agent_config()` SHALL exclude that domain section from the global LLM merge

#### Scenario: Strict policy rejects unregistered domain data

- **GIVEN** the default policy is used for an overlay containing a `gate` or `persistence` section
- **WHEN** the overlay is resolved
- **THEN** validation SHALL fail with the unsupported top-level key
- **AND** a permissive consumer result SHALL not make a later strict request succeed from cache

#### Scenario: Explicit path uses canonical schema

- **GIVEN** a caller selects an explicit agent-overlay path
- **WHEN** the mapping and overlay APIs read that path
- **THEN** they SHALL apply the same mapping, secret, key-policy, and provenance rules as the standard path
- **AND** a legacy wrapped schema SHALL fail with migration guidance

### Requirement: Config caching with test isolation

The system MAY cache parsed configuration inputs, but it MUST NOT return a stale effective profile after the selected `TDT_HOME`, environment profile, explicit paths, overlay-key policy, relevant process environment, or source-file fingerprint changes. Reset behavior SHALL clear all configuration and environment state owned by the resolver without mutating unrelated process environment.

#### Scenario: Relevant environment changes between resolutions

- **GIVEN** a profile was resolved with one registered model environment value
- **WHEN** that process environment value changes and the profile is resolved again
- **THEN** the second effective profile SHALL reflect the new value rather than a cached value

#### Scenario: Cache is populated on first access

- **WHEN** a cacheable configuration source is read for the first time
- **THEN** any stored entry SHALL include the effective root, path, policy, and source fingerprint

#### Scenario: Cache is cleared by reset function

- **WHEN** the public resolver reset is invoked
- **THEN** all agent-config source-cache entries SHALL be cleared

#### Scenario: TDT_HOME changes between resolutions

- **GIVEN** a profile was resolved under one `TDT_HOME`
- **WHEN** `TDT_HOME` changes to another absolute root
- **THEN** subsequent resolution SHALL use only the new root's configuration inputs

#### Scenario: Reset preserves unrelated environment

- **GIVEN** test isolation has loaded configuration and environment state
- **WHEN** the resolver reset is invoked
- **THEN** all resolver-owned caches and loader state SHALL be cleared
- **AND** unrelated process environment values SHALL remain unchanged

#### Scenario: Returned state cannot poison another consumer

- **GIVEN** a consumer receives a resolved mapping or profile
- **WHEN** it attempts to mutate the returned object
- **THEN** subsequent resolutions SHALL retain the original effective values and provenance
- **AND** strict and permissive overlay calls SHALL remain isolated

### Requirement: Secrets remain in .env only

Agent and global YAML MUST NOT contain literal credential values. A provider entry MAY contain an environment-key reference only when the reference is a full valid environment name in the registered provider metadata position. Resolved profiles, caches, diagnostics, and provenance MUST NOT retain or render the resolved credential value.

#### Scenario: Secret in agent YAML is rejected

- **WHEN** YAML contains a literal API key, token, credential, password, DSN, or database URL in a secret-shaped field
- **THEN** resolution SHALL fail with the logical key and source path
- **AND** the diagnostic SHALL omit the value

#### Scenario: Provider environment-key metadata is accepted

- **WHEN** a provider entry contains an environment-key name matching the supported uppercase environment-name grammar
- **THEN** the metadata SHALL be accepted
- **AND** credential resolution SHALL remain at the canonical environment boundary

#### Scenario: Secret reference in a domain field is rejected

- **WHEN** a harness domain section contains provider credential metadata outside the registered provider schema
- **THEN** resolution SHALL fail closed

### Requirement: Unknown top-level keys rejected

Each agent overlay SHALL be validated against an explicit owner-specific top-level key policy. The default policy SHALL permit only model and runtime sections. A consumer MAY register additional domain keys, but those keys SHALL remain source-preserved consumer data and SHALL NOT enter the global LLM merge.

#### Scenario: Unknown top-level key in agent YAML is rejected

- **WHEN** an ordinary agent overlay contains an unregistered `gate` section
- **THEN** resolution SHALL fail with all unsupported top-level keys listed

#### Scenario: Multiple unknown keys reported

- **WHEN** an agent overlay contains multiple unsupported top-level keys
- **THEN** one redacted validation error SHALL list every offending key in deterministic order

#### Scenario: Harness policy accepts owned domain keys

- **WHEN** the harness overlay contains registered gate, persistence, authority, validation, budget, or retention sections
- **THEN** the source-preserving overlay SHALL accept them
- **AND** those sections SHALL NOT override same-named global sections

#### Scenario: Allowed-key policy cannot poison strict cache

- **WHEN** the same file is loaded once with the harness policy and once with the default policy
- **THEN** the two validations SHALL execute independently
- **AND** the permissive result SHALL NOT cause the strict request to succeed

#### Scenario: Allowed keys accepted without error

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}`
- **THEN** the call SHALL succeed without `ConfigError` for the `gate` key

### Requirement: Model factory receives config dict

The model-construction layer MUST receive an already resolved model profile from its caller. It MUST NOT read YAML, dotenv files, or process environment while selecting the primary model, fallbacks, provider route, or behavior settings. Credential material SHALL be supplied through the canonical environment boundary without being added to serializable configuration.

#### Scenario: Model factory uses passed config

- **WHEN** model construction receives a resolved primary, fallbacks, provider metadata, and behavior settings
- **THEN** it SHALL construct the requested model chain from those inputs
- **AND** it SHALL perform no configuration-file read

#### Scenario: Model factory without config falls through to native provider

- **WHEN** an explicit native provider:model identifier is constructed without proxy-provider metadata
- **THEN** the supported native provider resolver SHALL construct it
- **AND** no TDT configuration source SHALL be read

#### Scenario: Removed functions no longer exist

- **WHEN** model-layer source is inspected
- **THEN** removed direct TDT YAML loader functions SHALL not exist

#### Scenario: Model factory cannot change precedence

- **GIVEN** the resolved profile selected an environment-provided model over agent YAML
- **WHEN** the model is constructed
- **THEN** the factory SHALL use that selected model
- **AND** it SHALL NOT reselect the YAML value

### Requirement: Canonical direct-model identifiers

Every direct Pydantic-AI primary and fallback identifier in the resolved profile SHALL
match a registered canonical `provider:model` grammar and provider registry entry.
Localized, unregistered, or display-only aliases SHALL be rejected during resolution;
they SHALL never be treated as a live provider acceptance result.

#### Scenario: Registered canonical identifier is accepted

- **GIVEN** a registered provider accepts a canonical identifier such as `anthropic:Advance`
- **WHEN** the profile resolves the primary or a fallback
- **THEN** the identifier SHALL remain unchanged in the effective profile and provenance

#### Scenario: Localized alias is rejected

- **GIVEN** a source provides a localized or unregistered model alias
- **WHEN** a direct-model profile is resolved or a live gate is prepared
- **THEN** resolution SHALL fail closed with the provider/model field identified
- **AND** it SHALL not fall through to a lower-priority model or invoke a provider

### Requirement: Consumers use load_agent_config for model resolution

Direct Pydantic-AI consumers SHALL obtain LLM inputs from the canonical resolved-agent-profile boundary. CLI-provider consumers SHALL obtain the provider-neutral projection defined by `cli-provider-profile-resolution`. No consumer SHALL independently read global YAML, agent YAML, or dotenv files for LLM fields.

#### Scenario: Direct consumer uses one profile

- **WHEN** agent-core, agent-docs-sync, or agent-harness constructs an agent
- **THEN** model construction and public configuration diagnostics SHALL consume the same resolved profile snapshot

#### Scenario: Agent-core build_agent uses load_agent_config

- **WHEN** agent-core builds an SDK agent without an explicit Model instance
- **THEN** it SHALL consume the canonical resolved profile compatibility boundary
- **AND** it SHALL pass the resolved model/provider inputs to construction

#### Scenario: Agent-docs-sync uses load_agent_config for model

- **WHEN** docs-sync constructs configuration or a generation agent
- **THEN** it SHALL consume the canonical resolved agent profile
- **AND** it SHALL not read global TDT YAML directly for model configuration

#### Scenario: CLI-provider consumer preserves its execution boundary

- **WHEN** ai-harness-skills or ai-review invokes a provider CLI
- **THEN** it SHALL use the provider-neutral profile for alias and effort selection
- **AND** it SHALL leave CLI authentication to the provider's approved credential boundary

## ADDED Requirements

### Requirement: Source-preserving secure configuration input

The configuration provider SHALL be able to load one YAML mapping without merging it, validate its shape and secret policy, and preserve which source supplied every accepted key. Standard agent files SHALL be read through contained, no-follow semantics; unsafe components, symlinks, substituted descendants, and paths escaping the selected root SHALL fail closed.

#### Scenario: Empty or missing optional mapping

- **WHEN** an optional agent overlay is absent or empty
- **THEN** the source-preserving result SHALL be an empty mapping
- **AND** global configuration and defaults MAY still resolve the effective profile

#### Scenario: Malformed or non-mapping YAML

- **WHEN** a selected configuration file is malformed or has a non-mapping root
- **THEN** resolution SHALL fail with the redacted source path
- **AND** it SHALL NOT silently substitute defaults

#### Scenario: Agent overlay symlink escapes TDT_HOME

- **WHEN** a standard agent-overlay path or one of its descendants resolves through a link outside `TDT_HOME`
- **THEN** the read SHALL fail before any external file content is trusted

### Requirement: Redacted effective-config diagnostics

The system SHALL expose a machine-readable effective-profile diagnostic containing the selected model identifier, fallback identifiers, non-secret provider metadata, runtime values, registered environment-key names, and source provenance. It MUST NOT include credential values.

#### Scenario: Diagnostic explains precedence

- **WHEN** multiple sources define the same model field
- **THEN** the diagnostic SHALL identify the winning and shadowed source classes
- **AND** it SHALL not render any protected value

#### Scenario: Provider key is missing

- **WHEN** a selected provider references an unavailable environment key
- **THEN** the diagnostic SHALL identify the provider and missing environment-key name
- **AND** it SHALL fail before a live request without revealing other environment values
