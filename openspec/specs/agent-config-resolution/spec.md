# agent-config-resolution Specification

## Purpose
Provides a standardized mechanism for TDT agent repos to load LLM configuration with per-agent overrides from `~/.tdt/agents/{name}.yaml`, using a single resolution chain that all agents share.

## Requirements

### Requirement: Agents directory path resolution

The system SHALL provide a `tdt_agents_dir()` function in `tdt_core.paths` that returns the canonical `~/.tdt/agents/` directory path. The function SHALL validate the agent name component using existing `_validate_component()` rules.

#### Scenario: Agents directory resolves correctly
- **WHEN** `tdt_agents_dir()` is called
- **THEN** it SHALL return `tdt_root() / "agents"`

#### Scenario: Agent config path combines directory and name
- **WHEN** `tdt_config_path_for_agent("agent-docs-sync")` is called
- **THEN** it SHALL return `tdt_agents_dir() / "agent-docs-sync.yaml"`

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

### Requirement: Canonical agent selection precedence and overlay schema

The global canonical configuration SHALL own the complete `providers`, `models`, and `defaults` catalog. An agent overlay MAY contain `defaults` selection/behavior fields, `runtime`, and explicitly registered consumer domain sections. It MUST NOT define or replace `providers`, `models`, endpoint metadata, protocols, credential references, wire models, or CLI relationships. Every model selector from an explicit run override, registered consumer environment input, registered shared environment input, agent overlay, or global default MUST name an alias already defined in the same canonical global `models` catalog.

Effective selection SHALL use this priority order: explicit run-scoped canonical alias, registered consumer alias selector, registered shared alias selector, agent-overlay canonical alias, then global canonical default. Typed behavior inputs SHALL follow their registered precedence independently. Invalid higher-priority aliases or behavior MUST fail closed rather than fall through. Each selected value SHALL retain redacted source provenance.

#### Scenario: Agent overlay selects a canonical alias

- **GIVEN** the global catalog defines aliases `primary-a` and `primary-b`
- **AND** an agent overlay contains `defaults: {model: primary-b}`
- **WHEN** the agent profile is resolved
- **THEN** `primary-b` SHALL project through its global model/provider definition
- **AND** the overlay SHALL not replace route metadata

#### Scenario: Agent overlay cannot define routes

- **GIVEN** an agent overlay contains `providers`, `models`, a raw endpoint, protocol, credential reference, or wire model
- **WHEN** overlay validation runs
- **THEN** it SHALL fail with every unsupported logical key
- **AND** no global route relationship SHALL be shadowed or merged

#### Scenario: Missing overlay uses canonical global defaults

- **GIVEN** no agent overlay exists
- **WHEN** the profile is resolved
- **THEN** the global canonical `defaults.model` and ordered `defaults.fallback` aliases SHALL be selected
- **AND** no old-schema or consumer-local default SHALL be consulted

#### Scenario: Partial overlay changes selection only

- **GIVEN** an agent overlay changes one permitted canonical alias or typed behavior field
- **WHEN** the profile is resolved
- **THEN** unspecified selections and behavior SHALL remain canonical global values
- **AND** provider/model catalog definitions SHALL remain byte-for-byte global inputs

#### Scenario: Explicit alias override wins

- **GIVEN** an explicit run override names a defined canonical alias
- **AND** registered environment, agent overlay, and global defaults select other aliases
- **WHEN** the profile is resolved
- **THEN** the explicit alias SHALL be selected with explicit-override provenance
- **AND** its route SHALL still come entirely from the canonical catalog

#### Scenario: Registered selector must name a canonical alias

- **GIVEN** a registered consumer or shared environment selector contains an undefined, provider-prefixed, localized, or wire-model value
- **WHEN** the profile is resolved
- **THEN** resolution SHALL fail with the logical selector and source class
- **AND** no lower selection SHALL replace it

#### Scenario: Consumer-specific alias selector wins over shared selector

- **GIVEN** registered consumer and shared selectors name different defined canonical aliases
- **WHEN** that consumer's profile is resolved
- **THEN** the consumer-specific alias SHALL be selected
- **AND** the exact route projection SHALL match the canonical definition for that alias

#### Scenario: Agent overlay key policy preserves domain ownership

- **GIVEN** an agent overlay contains `defaults`, `runtime`, and a registered consumer domain section
- **WHEN** the overlay is loaded
- **THEN** selection/runtime fields SHALL be validated by canonical profile resolution
- **AND** the domain section SHALL remain source-preserved consumer data outside LLM selection

#### Scenario: Unregistered overlay key fails

- **GIVEN** an agent overlay contains one or more unregistered top-level keys
- **WHEN** overlay validation runs
- **THEN** one redacted failure SHALL list every unsupported key deterministically
- **AND** a permissive consumer cache entry SHALL not make a strict request succeed

### Requirement: Canonical source mapping and overlay primitives

`load_config_mapping(path)` SHALL remain a secure non-merging, non-caching reader for one YAML mapping, and `load_agent_overlay` SHALL remain a source-preserving reader for one agent overlay. Those primitives SHALL enforce path containment, YAML mapping shape, literal-secret rejection, detached results, and source identity, but SHALL NOT declare an LLM schema valid or merge an effective LLM profile. Only `resolve_agent_profile` SHALL apply canonical provider/model/default validation and selection.

#### Scenario: Mapping reader is source-local

- **WHEN** `load_config_mapping` reads one selected file
- **THEN** it SHALL return only that detached mapping and source identity
- **AND** it SHALL not merge another file, environment selector, agent overlay, or default

#### Scenario: Missing optional overlay is empty source input

- **GIVEN** no agent overlay exists for a valid agent name
- **WHEN** `load_agent_overlay` reads it
- **THEN** it SHALL return an empty detached overlay input
- **AND** canonical profile resolution SHALL continue from the global canonical catalog

#### Scenario: Malformed or non-mapping YAML fails

- **GIVEN** a selected source contains malformed YAML or a non-mapping document
- **WHEN** a source primitive reads it
- **THEN** it SHALL raise a redacted `ConfigError` naming the source path
- **AND** canonical resolution SHALL not treat it as absence

#### Scenario: Literal secret-shaped value fails

- **GIVEN** a selected source contains literal API key, token, password, authorization, DSN, or credential material
- **WHEN** a source primitive validates the mapping
- **THEN** it SHALL fail with the logical key and path
- **AND** the diagnostic SHALL omit the value

#### Scenario: Canonical auth_env metadata is validated later

- **GIVEN** a global mapping contains `providers.<id>.auth_env`
- **WHEN** it is used for LLM resolution
- **THEN** canonical schema validation SHALL require the supported uppercase environment-name grammar and provider binding
- **AND** the source reader SHALL not resolve the credential value

#### Scenario: Unsupported api_key_env is rejected for LLM configuration

- **GIVEN** a selected LLM mapping contains `providers.<id>.api_key_env`
- **WHEN** canonical profile resolution validates it
- **THEN** validation SHALL fail as unsupported schema
- **AND** the key SHALL not be renamed, normalized, or ignored

#### Scenario: Explicit overlay path uses the same clean schema

- **GIVEN** a composition root selects an explicit contained agent-overlay path
- **WHEN** the overlay and profile are resolved
- **THEN** the same canonical key, secret, provenance, and relationship rules SHALL apply
- **AND** no wrapped or mapping compatibility schema SHALL be accepted

#### Scenario: Removed effective mapping function is not called

- **WHEN** active source and tests inspect the source primitives
- **THEN** neither primitive SHALL call or expose `load_agent_config`
- **AND** no effective LLM mapping projection SHALL be returned

### Requirement: Canonical profile caching with test isolation

The resolver MAY cache secure source inputs and fully validated `ResolvedAgentProfile` values. Cache identity MUST include agent identity, canonical root, environment profile, selected source paths, non-secret source fingerprints, overlay key policy, detached explicit inputs, every registered non-secret selector/behavior input, and only credential key-name/availability/provider-binding metadata. Cache reuse SHALL NOT cross any difference in that complete safe identity. Reset SHALL clear resolver-owned caches without mutating unrelated process environment.

#### Scenario: Relevant selector changes between resolutions

- **GIVEN** a profile was resolved with one registered canonical alias selector
- **WHEN** that selector changes to another defined alias and the profile is resolved again
- **THEN** the second profile SHALL contain the newly selected exact route
- **AND** the first cached result SHALL not be reused

#### Scenario: Source fingerprint participates in cache identity

- **GIVEN** one selected canonical source changes without changing its path
- **WHEN** a later resolution begins
- **THEN** its changed non-secret content fingerprint SHALL force revalidation
- **AND** path equality alone SHALL not authorize reuse

#### Scenario: TDT root changes between resolutions

- **GIVEN** a profile was resolved under one canonical TDT root
- **WHEN** a later request selects another absolute canonical root
- **THEN** only the later root's sources and catalog SHALL participate
- **AND** no profile/source cache entry SHALL cross roots

#### Scenario: Reset preserves unrelated environment

- **GIVEN** resolver-owned caches and registered input state exist
- **WHEN** the public resolver reset is invoked
- **THEN** all resolver-owned state SHALL be cleared
- **AND** unrelated process-environment values SHALL remain unchanged

#### Scenario: Returned profile cannot poison cache

- **GIVEN** a consumer receives a recursively immutable resolved profile
- **WHEN** it attempts to mutate route, behavior, runtime, provenance, or fingerprint state
- **THEN** mutation SHALL fail
- **AND** later resolutions SHALL retain validated canonical values

#### Scenario: Cache keys exclude credential values

- **GIVEN** credential availability or binding participates in request identity
- **WHEN** a cache key or diagnostic is produced
- **THEN** it MAY include key name, availability, and provider binding
- **AND** it MUST NOT contain a raw, encoded, hashed, or otherwise value-derived credential representation

### Requirement: Exact route diagnostics match canonical resolution

The system SHALL expose a machine-readable safe diagnostic for the effective typed profile. For each selected route it SHALL report ordered position, canonical alias, model kind, wire model, canonical provider ID, explicit transport, typed protocol, normalized non-secret endpoint metadata, credential key-name/availability/provider-binding metadata, typed behavior, structured provenance, root identity, and non-secret source fingerprints. It MUST NOT contain credential values, arbitrary provider mappings, or compatibility projections.

#### Scenario: Diagnostic explains exact selection and precedence

- **WHEN** multiple permitted sources select the same logical alias or behavior field
- **THEN** the diagnostic SHALL identify the winning and shadowed source classes and the exact resulting route
- **AND** execution SHALL consume that same route/context identity
- **AND** no protected value SHALL be rendered

#### Scenario: Provider credential reference is unavailable

- **WHEN** a selected route's canonical provider references an unavailable credential key
- **THEN** the diagnostic SHALL identify the route provider and missing key name
- **AND** resolution/construction SHALL fail before a live request
- **AND** no other environment value SHALL be read or revealed

### Requirement: Canonical typed agent profile resolution

The system SHALL expose `resolve_agent_profile` as the only public LLM configuration-resolution boundary. It SHALL accept only the canonical `providers`, `models`, and `defaults` schema and SHALL return one recursively immutable `ResolvedAgentProfile`. The profile SHALL contain one exact selected primary route, an ordered tuple of exact fallback routes, exact native CLI selections, runtime values, redacted provenance, root identity, and non-secret source fingerprints. Each route SHALL distinguish canonical model alias, model/factory kind, wire model, canonical provider ID, explicit native/endpoint transport kind, typed protocol, normalized non-secret endpoint metadata, provider-bound credential-reference metadata, behavior, and provenance.

The system MUST remove the public LLM mapping projection `load_agent_config`, its legacy loader, settings-shaped profile projection, and `primary`, `fallback`, or equivalent compatibility aliases. Secure mapping and agent-overlay readers MAY remain only for their explicitly owned source-reading and domain-overlay responsibilities; they SHALL NOT return or select an effective LLM profile. Unsupported legacy-only or mixed LLM schemas MUST fail canonical validation and MUST NOT return `None`, defaults, or a partial mapping.

#### Scenario: Canonical profile is internally exact

- **WHEN** a consumer resolves an agent profile
- **THEN** the primary and fallback route projections SHALL describe the exact canonical aliases, model kinds, wire models, providers, transport kinds, protocols, endpoints, credential references, behavior, provenance, and source fingerprints selected in that request
- **AND** downstream consumers SHALL NOT need a YAML, dotenv, environment, prefix, or mapping reconstruction step

#### Scenario: Canonical schema is required

- **GIVEN** an LLM configuration uses top-level `model`, `gateway`, `providers.*.api_key_env`, `api_mode`, or a mixture of those fields with canonical fields
- **WHEN** canonical profile resolution begins
- **THEN** validation SHALL fail with a redacted logical-field diagnostic
- **AND** no typed profile, compatibility mapping, provider model, or fallback chain SHALL be returned

#### Scenario: Canonical relationships are complete

- **GIVEN** `defaults.model`, a `defaults.fallback` entry, or `defaults.cli_models` references an undefined model alias
- **OR** a model references an undefined provider
- **WHEN** canonical profile resolution begins
- **THEN** validation SHALL report every invalid non-secret relationship
- **AND** resolution SHALL fail before credential access or consumer construction

#### Scenario: Explicit run override names a defined alias

- **GIVEN** a caller supplies an explicit run-scoped model override
- **WHEN** the resolver validates that override
- **THEN** the override MUST name a model alias already defined in canonical `models`
- **AND** it SHALL NOT inject or replace provider, endpoint, protocol, credential-reference, wire-model, or fallback mappings

#### Scenario: Mapping compatibility API is absent

- **WHEN** the supported `tdt_core` public exports and active product call sites are inspected
- **THEN** `load_agent_config`, the legacy LLM loader, and settings-shaped compatibility projections SHALL be absent
- **AND** all participating LLM consumers SHALL use typed profile resolution

#### Scenario: Explicit source path remains one canonical source

- **GIVEN** a composition root supplies an explicitly owned canonical configuration path
- **WHEN** the profile is resolved
- **THEN** that path SHALL participate in the same canonical validation, provenance, and fingerprint rules
- **AND** no mapping compatibility projection or second precedence chain SHALL be activated

#### Scenario: Registered inputs are captured once

- **GIVEN** one resolution request has selected its root, source identities, explicit overrides, and registered environment inputs
- **WHEN** a source or registered input changes during the request
- **THEN** the returned profile SHALL remain coherent with the state captured for that request
- **AND** a later request SHALL observe the change as a different source identity

#### Scenario: Protected values are excluded from identity

- **GIVEN** a selected provider requires protected credential material
- **WHEN** the resolver produces routes, profile identity, provenance, fingerprints, diagnostics, exceptions, cache metadata, or evidence
- **THEN** those surfaces SHALL retain only credential key-name, availability, and canonical provider-binding metadata
- **AND** no raw, encoded, hashed, or otherwise value-derived credential material SHALL appear

#### Scenario: Cache reuse requires complete identity

- **WHEN** a later request differs in agent identity, canonical root, environment profile, selected paths, source fingerprint, explicit canonical alias override, registered non-secret environment state, or credential availability/provider binding
- **THEN** an earlier resolved profile SHALL NOT be reused
- **AND** the later request SHALL resolve its own coherent profile

#### Scenario: Concurrent resolutions remain isolated

- **GIVEN** simultaneous requests resolve different roots, agents, source states, canonical aliases, or provider relationships
- **WHEN** both requests complete
- **THEN** each profile SHALL contain only its own immutable route and source state
- **AND** neither request SHALL mutate, cache-substitute, or expose state from the other

### Requirement: Model factory receives caller-resolved construction context

The model-construction layer MUST receive one complete caller-resolved `ModelConstructionContext` rather than an arbitrary profile, settings object, or mapping. The context SHALL carry the exact immutable primary and fallback route projections selected by the canonical profile and, when protected material is needed, a separate process-local `CredentialResolver` bound to those provider identities. Model construction MUST NOT read YAML, dotenv, TDT configuration, process environment, or consumer configuration while selecting a canonical alias, model kind, wire model, primary, fallback order, provider, endpoint, protocol, credential reference, or behavior.

#### Scenario: Model factory uses exact passed routes

- **WHEN** model construction receives a complete caller-resolved context
- **THEN** it SHALL construct the ordered primary/fallback chain from the exact routes in that context
- **AND** it SHALL perform no independent configuration read, relationship reconstruction, or selection

#### Scenario: Native provider route is explicit

- **GIVEN** the context selects a supported native route without proxy endpoint metadata
- **WHEN** the model is constructed
- **THEN** the selected model kind, wire model, provider ID, and protocol SHALL determine the provider-library boundary
- **AND** native authentication MAY occur only inside that approved provider library after selection
- **AND** project code SHALL perform no environment-owned routing or fallback

#### Scenario: Missing or incomplete context fails before access

- **GIVEN** a string model input has no complete construction context or lacks an exact selected route
- **WHEN** public model construction is invoked
- **THEN** it SHALL fail with an actionable redacted diagnostic
- **AND** it SHALL read no configuration, environment, provider credential, or fallback source
- **AND** it SHALL construct no provider model

#### Scenario: Factory preserves canonical selection

- **GIVEN** the canonical resolver selected one model/provider relationship over another candidate
- **WHEN** the factory constructs the model chain
- **THEN** it SHALL preserve that canonical alias, wire model, provider, protocol, endpoint, and fallback order
- **AND** it SHALL NOT reselect values from prefixes, environment, local configuration, or provider defaults

#### Scenario: Protected access is provider-bound

- **GIVEN** one selected route requires protected provider material
- **WHEN** final provider construction requests it
- **THEN** the process-local resolver SHALL require the same non-empty canonical provider ID as the route
- **AND** cross-provider access SHALL fail before the value is revealed

#### Scenario: Explicit Model bypasses all resolution

- **GIVEN** a caller supplies an already constructed `Model`
- **WHEN** public model or agent construction begins
- **THEN** the same object SHALL be used by identity
- **AND** no context, profile, configuration, environment, credential, provider, or fallback source SHALL be accessed

### Requirement: Composition roots resolve canonical model context

Every participating direct Pydantic-AI composition root SHALL resolve one canonical profile and build one process-local construction context before invoking string-based `create_model` or `build_agent`. Nested factories, SDK builders, base-agent constructors, stage constructors, generation helpers, adapters, and retry paths SHALL NOT call a profile/configuration loader or reconstruct selection. A contained target or repository under review MUST NOT become the canonical TDT root. An enabled native CLI consumer MUST have an explicit canonical CLI model relationship and MUST NOT fall back to consumer-local model configuration.

#### Scenario: Direct consumer resolves once

- **WHEN** agent-core, agent-harness, or agent-docs-sync begins one LLM operation from a canonical alias
- **THEN** its composition root SHALL resolve exactly one canonical profile and construction context before model construction
- **AND** diagnostics and execution SHALL preserve the same safe identity
- **AND** nested construction SHALL resolve no second profile

#### Scenario: build_agent receives context from caller

- **WHEN** an SDK caller builds an agent from a canonical alias
- **THEN** it SHALL supply the complete construction context to `build_agent`
- **AND** `build_agent` SHALL call no configuration or profile loader

#### Scenario: BaseAgent receives only a Model

- **WHEN** `BaseAgent` is constructed
- **THEN** its model argument SHALL already be a Pydantic-AI `Model`
- **AND** `BaseAgent` SHALL own no string, profile, context, configuration, credential, provider, or fallback resolution path

#### Scenario: docs-sync preserves one operation identity

- **WHEN** docs-sync begins generation or synchronization
- **THEN** configuration, generation, diagnostics, retries, and same-process resume checks SHALL use the same safe canonical profile/context identity
- **AND** no nested path SHALL infer provider identity from a model string

#### Scenario: docs-sync resume reacquires process-local access

- **GIVEN** docs-sync resumes retained safe identity in a new process
- **WHEN** a provider model must be reconstructed
- **THEN** the composition root SHALL resolve a fresh context through the same canonical provider binding and compare the complete safe identity
- **AND** identity drift SHALL fail before write-capable generation
- **AND** no credential value SHALL have been serialized

#### Scenario: Enabled CLI consumer requires canonical mapping

- **WHEN** ai-harness-skills or ai-review enables a native CLI provider
- **THEN** its composition root SHALL resolve an explicit canonical CLI mapping from the consumer-owned canonical TDT root
- **AND** missing, invalid, or ambiguous mapping SHALL fail before adapter construction
- **AND** consumer-local model selection SHALL NOT be used

#### Scenario: Contained target cannot select sources

- **GIVEN** a consumer operates on a contained project, generated artifact, or repository under review
- **WHEN** it resolves its canonical LLM or CLI profile
- **THEN** it SHALL use the consumer-owned canonical TDT root
- **AND** target-local files SHALL NOT influence model, provider, protocol, endpoint, credential reference, behavior, or source selection

#### Scenario: Canonical resolution failure stops construction

- **GIVEN** a selected canonical source is unreadable, unavailable, malformed, incomplete, ambiguous, or inconsistent
- **WHEN** a composition root resolves the profile or context
- **THEN** the operation SHALL fail with a redacted diagnostic before model, adapter, process, or write-capable construction
- **AND** no local mapping, default, old schema, or native-auth route SHALL be activated
