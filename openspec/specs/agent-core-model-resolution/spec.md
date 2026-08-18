# agent-core-model-resolution Specification

## Purpose

Define configuration-driven model and proxy resolution for agent-core, including the active giaoduc Anthropic Messages setup and the OpenAI-compatible alternative.

## Requirements

### Requirement: Thinking Field Migration

**WHEN** `AgentConfig.thinking` is referenced in consumer code
**THEN** the system SHALL NOT have a `thinking` field on `AgentConfig`
**AND** consumers SHALL use the `Thinking` capability or `model_settings` dict instead.

#### Scenario: Dead field removed
- **GIVEN** `AgentConfig` is defined in `_ai/config.py`
- **WHEN** the codebase is searched for `AgentConfig.thinking`
- **THEN** zero references SHALL be found outside of test assertions for removal

### Requirement: Effective model diagnostics match execution

Agent-core diagnostics SHALL report the effective model chain and non-secret provider route that the next construction call will use from the same resolved profile snapshot.

#### Scenario: Diagnostic and constructed chain agree

- **WHEN** the effective-config diagnostic and model construction are run from one profile
- **THEN** their model identifiers and order SHALL match

#### Scenario: Missing provider credential metadata

- **WHEN** a selected provider lacks its required registered environment key
- **THEN** diagnostics and construction SHALL fail with the same provider and environment-key name
- **AND** neither output SHALL reveal credential values

### Requirement: Model Resolution from Caller Context

Public model construction SHALL have exactly two authoritative paths:

1. `create_model(model: Model, *, context: None = None) -> Model`; or
2. `create_model(model: str, *, context: ModelConstructionContext) -> Model`.

An explicit `Model` MUST be returned by object identity without accessing the optional context or any configuration, environment, credential, provider, or fallback source. A string MUST be the exact canonical primary alias selected by `context.primary_route`; it SHALL NOT be a wire model, provider prefix, localized alias, display name, or consumer-local model. The string path SHALL automatically construct the primary and ordered fallback chain from the exact routes in the context. The factory SHALL NOT rediscover or replace any route field from environment variables, YAML, dotenv, raw kwargs, native CLI configuration, model prefixes, provider defaults, or another fallback list.

`create_model` SHALL be the only public model factory. `create_fallback_model`, `create_model_with_fallback`, and the agent-core public `infer_model` re-export MUST be removed. Any protocol/fallback construction helpers SHALL be private and SHALL accept exact route/context types only.

#### Scenario: Explicit Model is returned unchanged

- **GIVEN** a caller passes an already constructed Pydantic-AI `Model`
- **WHEN** `create_model` is called
- **THEN** it SHALL return the same object by identity
- **AND** it SHALL not inspect a context or read configuration, environment, credentials, providers, or fallbacks

#### Scenario: Canonical alias constructs the complete chain

- **GIVEN** a complete context selects canonical primary alias `primary-a` and ordered fallback aliases `fallback-b`, `fallback-c`
- **WHEN** `create_model("primary-a", context=context)` is called
- **THEN** it SHALL construct the primary and fallbacks in exactly that route order
- **AND** each model SHALL use its route's model kind, wire model, provider ID, protocol, endpoint metadata, credential reference, and behavior

#### Scenario: String must match selected canonical alias

- **GIVEN** a complete context whose primary canonical alias is `primary-a`
- **WHEN** a caller supplies a different alias, wire model, provider-prefixed string, localized alias, or display name
- **THEN** construction SHALL fail with a redacted identity-mismatch diagnostic
- **AND** no provider, credential, or fallback model SHALL be constructed

#### Scenario: Missing context fails before discovery

- **GIVEN** a caller supplies a string without a complete `ModelConstructionContext`
- **WHEN** `create_model` is called
- **THEN** construction SHALL fail before configuration, environment, provider, credential, fallback, or native-auth access
- **AND** no model SHALL be instantiated

#### Scenario: Anthropic Messages route is exact

- **GIVEN** a selected route carries model kind `anthropic`, typed protocol `messages`, one wire model, and one canonical provider ID
- **WHEN** its provider model is constructed
- **THEN** the Anthropic Messages implementation SHALL use those exact route values
- **AND** no prefix, `api_mode`, endpoint, or environment inference SHALL replace them

#### Scenario: OpenAI Chat and Responses routes remain distinct

- **GIVEN** selected routes carry `openai_chat` and `openai_responses` model kinds with their matching typed protocols
- **WHEN** the provider models are constructed
- **THEN** each SHALL use its matching protocol-specific implementation
- **AND** canonical alias, wire model, and provider identity SHALL remain distinct values

#### Scenario: Route kind and protocol mismatch fails closed

- **GIVEN** a selected route has an incompatible model/factory kind and typed protocol
- **WHEN** canonical context construction or model construction validates the route
- **THEN** it SHALL fail with a redacted relationship diagnostic
- **AND** no primary or fallback provider model SHALL be created

#### Scenario: Raw constructor authorities are absent

- **WHEN** the public model factory signature and active exports are inspected
- **THEN** raw `base_url`, `api_key`, `providers`, `model_config`, `snapshot`, and `fallback_ids` parameters SHALL be absent
- **AND** `_UNSET`, legacy-kwarg, transition-release, and migration-exception shims SHALL be absent

#### Scenario: Public fallback factories are absent

- **WHEN** agent-core public modules and SDK exports are inspected
- **THEN** `create_fallback_model`, `create_model_with_fallback`, and public `infer_model` SHALL be absent
- **AND** callers SHALL use `create_model` for both single-model and fallback-chain construction

#### Scenario: Native authentication cannot select a route

- **GIVEN** the context explicitly selects a supported native provider route
- **WHEN** final provider construction delegates authentication to the provider library
- **THEN** only that library MAY read its documented authentication environment after route selection
- **AND** project code SHALL perform no environment lookup for model, provider, endpoint, protocol, fallback, or behavior selection
- **AND** canonical resolution failure SHALL never fall through to native authentication

### Requirement: Canonical Model Selection Schema

The canonical LLM schema SHALL contain exactly these model-selection sections:

- `providers.<provider_id>` owns explicit `transport` (`native` or `endpoint`), typed `protocol`, provider-bound `auth_env` reference, optional `cli_provider` identity, and a normalized `base_url` that is required for endpoint transport and forbidden for native transport;
- `models.<canonical_alias>` owns one `provider` reference, one wire-model `model` value, and supported behavior such as reasoning effort or context window; and
- `defaults` owns one primary model alias in `model`, an ordered alias tuple in `fallback`, optional global behavior defaults, and explicit `cli_models` mappings.

Canonical resolution SHALL validate every relationship before returning a profile. It SHALL project each selected alias to an exact immutable `ResolvedModelRoute` with separate fields for `canonical_alias`, closed `model_kind`, `wire_model`, `provider_id`, explicit `transport`, typed `protocol`, normalized non-secret endpoint metadata, provider-bound credential-reference metadata, behavior, and structured provenance. `model_kind` SHALL be produced by a closed validated protocol/factory mapping; it SHALL NOT be inferred from provider names, wire models, endpoints, credentials, or environment. Protected credential values MUST NOT appear in the schema, profile, route, context digest, diagnostics, exceptions, or evidence.

Top-level `model`, `gateway`, `providers.*.api_key_env`, `api_mode`, legacy-only documents, and mixed canonical/unsupported documents MUST fail validation. There is no normalization, projection, alias, or compatibility mode for those inputs.

#### Scenario: Canonical config binds exact routes

- **GIVEN** canonical `defaults` selects aliases defined in `models` and each model references a provider defined in `providers`
- **WHEN** the caller resolves the profile and construction context
- **THEN** the primary and ordered fallback aliases SHALL project to complete exact routes
- **AND** provider endpoint, protocol, credential reference, and CLI identity SHALL remain owned by the referenced canonical provider

#### Scenario: Alias and wire model remain distinct

- **GIVEN** canonical alias `review-default` names wire model `gpt-5.6-sol`
- **WHEN** the profile and route are projected
- **THEN** both identities SHALL be retained in distinct immutable fields
- **AND** neither SHALL be reinterpreted as the provider ID or model kind

#### Scenario: Provider and model kind remain distinct

- **GIVEN** canonical provider `shopapikey` uses typed protocol `messages`
- **WHEN** a route is projected
- **THEN** the route SHALL preserve `shopapikey` as provider ID and the closed Messages factory kind as model kind
- **AND** agent-core SHALL not infer either identity from the other

#### Scenario: Native and endpoint transports are explicit

- **GIVEN** one provider declares `transport: native` and another declares `transport: endpoint`
- **WHEN** canonical schema validation and route projection run
- **THEN** the native provider SHALL forbid `base_url` and the endpoint provider SHALL require one normalized HTTP(S) `base_url`
- **AND** construction SHALL not infer transport from endpoint presence, provider name, protocol, credentials, or environment

#### Scenario: Undefined relationships fail together

- **GIVEN** canonical configuration contains undefined provider references, undefined primary/fallback aliases, or invalid CLI alias relationships
- **WHEN** validation runs
- **THEN** it SHALL report all non-secret relationship errors in one redacted failure
- **AND** it SHALL return no partial profile or route

#### Scenario: Unsupported old schema fails closed

- **GIVEN** configuration contains a top-level `model` or `gateway` section, `providers.*.api_key_env`, `api_mode`, or a mixture with canonical fields
- **WHEN** canonical validation runs
- **THEN** it SHALL reject the document
- **AND** it SHALL NOT normalize, ignore, project, default, or fall back from any unsupported field

#### Scenario: Explicit run override is selection-only

- **GIVEN** an operation supplies an explicit model override
- **WHEN** canonical profile resolution applies it
- **THEN** the override MUST name one existing canonical alias
- **AND** the alias SHALL resolve through its already declared model/provider relationship
- **AND** the override SHALL NOT inject endpoint, credential, provider, protocol, wire-model, or fallback mappings

#### Scenario: Credential values never enter serializable state

- **WHEN** canonical configuration, profile, route, context identity, diagnostic, exception, provenance, or evidence is serialized
- **THEN** it SHALL contain only non-secret credential-reference and provider-binding metadata
- **AND** no protected value or value-derived fingerprint SHALL be present

### Requirement: Clean model and agent construction boundaries

`create_model` and `build_agent` SHALL be the only public string-aware construction boundaries. `build_agent` SHALL accept either an explicit `Model` or one canonical alias plus a complete `ModelConstructionContext`; it SHALL call `create_model` for the string path and SHALL call no configuration or profile resolver. `ConsumerRuntimeProfile` SHALL contain only pure framework/runtime settings and SHALL have no model-selection field, settings projection, profile identity, or I/O-producing default. `CallerSnapshot` and every snapshot-shaped public input MUST be removed.

`BaseAgent` SHALL accept an already constructed `Model` only. It MUST NOT accept a string, profile, context, config mapping, provider mapping, or fallback input and MUST NOT call `create_model`, `load_settings`, `load_agent_config`, `resolve_agent_profile`, or another selection/resolution function. Agent-core CLI composition SHALL resolve one context before `build_agent` and SHALL not maintain an independent `_create_runtime_model` authority.

`ModelConstructionContext` SHALL be a final slotted non-dataclass with a module-private factory-only construction path. Direct public construction MUST fail. It SHALL reject shallow/deep copy, pickle/reduction, `vars`, dataclass `asdict`/`astuple`/`replace`, Pydantic model/type-adapter dumping, and any advertised serialization hook. Its deterministic SHA-256 identity SHALL cover canonical JSON for agent identity, ordered primary/fallback canonical aliases, model kinds, wire models, provider IDs, transport kinds, protocols, normalized endpoint metadata, provider-bound credential-reference metadata, behavior, structured provenance identity, and source fingerprints. The digest MUST NOT include or derive from credential values.

#### Scenario: build_agent explicit Model path is pure

- **GIVEN** `build_agent` receives an explicit `Model` and optional pure runtime profile
- **WHEN** it constructs the agent
- **THEN** it SHALL preserve the model by object identity
- **AND** it SHALL access no context, profile, configuration, environment, credential, provider, or fallback source

#### Scenario: build_agent string path delegates once

- **GIVEN** `build_agent` receives a canonical alias and complete context
- **WHEN** it constructs the agent
- **THEN** it SHALL call the sole public `create_model` boundary using those inputs
- **AND** it SHALL resolve no profile or configuration itself
- **AND** it SHALL pass the resulting `Model` into `BaseAgent`

#### Scenario: Runtime profile has no LLM authority

- **WHEN** `ConsumerRuntimeProfile` is constructed or serialized
- **THEN** it SHALL contain only pure framework/runtime fields
- **AND** it SHALL have no `model`, settings projection, canonical-profile identity, provider identity, fallback list, or I/O-producing default

#### Scenario: BaseAgent rejects string construction

- **GIVEN** a caller attempts to pass a string or configuration authority to `BaseAgent`
- **WHEN** Python validates the public constructor call
- **THEN** the call SHALL fail through the clean `Model`-only signature
- **AND** `BaseAgent` SHALL perform no resolution or compatibility handling

#### Scenario: CLI composition resolves one context

- **WHEN** an agent-core CLI operation needs a canonical model
- **THEN** its composition root SHALL resolve one context and invoke `build_agent` or `create_model`
- **AND** `_create_runtime_model` or another CLI-owned model-selection authority SHALL be absent

#### Scenario: Context direct construction is unavailable

- **WHEN** external code attempts to instantiate `ModelConstructionContext` without the module-private factory capability
- **THEN** construction SHALL fail
- **AND** no incomplete, forged, or empty-digest context SHALL be produced

#### Scenario: Context cannot be copied or serialized

- **WHEN** code applies copy, deepcopy, pickle/reduction, `vars`, dataclass serialization/replacement, Pydantic dumping, or an advertised context serialization hook
- **THEN** the operation SHALL raise `TypeError("ModelConstructionContext is process-local")`
- **AND** no credential resolver, credential value, or usable context clone SHALL be emitted

#### Scenario: Context digest covers complete safe identity

- **GIVEN** two contexts differ in any selected non-secret agent, route, behavior, provenance, credential-reference, endpoint, order, or source-fingerprint field
- **WHEN** their identity digests are computed from canonical JSON
- **THEN** the digests SHALL differ deterministically
- **AND** protected credential values SHALL have no effect on either digest

#### Scenario: Concurrent construction remains isolated

- **GIVEN** two callers supply different valid contexts simultaneously
- **WHEN** both construct agents
- **THEN** each agent SHALL use only its own exact routes and credential binding
- **AND** no mutable cache or global selection state SHALL cross the operations

#### Scenario: Active public examples use only clean boundaries

- **WHEN** active source, tests, templates, examples, and documentation are searched
- **THEN** string construction SHALL occur only through `create_model` or `build_agent` with a complete context
- **AND** direct `BaseAgent` examples SHALL pass an already constructed `Model`
- **AND** removed factories, snapshots, compatibility properties, mapping loaders, raw kwargs, and local fallback examples SHALL be absent

### Requirement: Canonical route behavior and run settings

Canonical `models.<alias>` and `defaults` definitions MAY contain only registered typed behavior fields, including supported reasoning effort, temperature, maximum tokens, service tier, and context window. Canonical resolution SHALL validate their types, ranges, model-kind/protocol capability, and precedence, then copy the effective immutable behavior into each exact `ResolvedModelRoute`. Arbitrary `extra_model_settings`, raw provider request bodies/headers, and unknown behavior keys MUST be rejected.

`create_model` SHALL use route behavior only for construction-time provider/model capabilities. Request-scoped behavior SHALL be applied at the public agent-run boundary from the route's typed defaults plus an optional typed/allowlisted run override. Run overrides SHALL NOT change canonical alias, model kind, wire model, provider, protocol, endpoint, credential reference, or fallback order. CLI and SDK paths MUST apply the same behavior merge and MUST NOT reload configuration.

#### Scenario: Canonical reasoning effort is projected

- **GIVEN** a canonical model or default declares a supported reasoning effort
- **WHEN** its route is resolved and the agent is built
- **THEN** the immutable route SHALL carry the effective effort
- **AND** the matching public capability/request setting SHALL translate it for the selected model kind and protocol

#### Scenario: Canonical numeric behavior is validated

- **GIVEN** canonical behavior declares temperature or maximum tokens
- **WHEN** schema/profile validation runs
- **THEN** temperature SHALL be between 0.0 and 2.0 and maximum tokens between 1 and 1,000,000
- **AND** out-of-range values SHALL fail before route/context construction

#### Scenario: Unsupported behavior field is rejected

- **GIVEN** canonical configuration or a run override includes an unknown field, arbitrary provider settings, raw headers/body, or a secret-shaped key
- **WHEN** behavior validation runs
- **THEN** validation SHALL fail with the logical field identified and value omitted
- **AND** the field SHALL not reach model or request construction

#### Scenario: Model-specific behavior overrides canonical defaults

- **GIVEN** `defaults` defines one typed behavior value and the selected `models.<alias>` defines another supported value for the same field
- **WHEN** the exact route is resolved
- **THEN** the model-specific value SHALL win
- **AND** provenance SHALL retain both selected and shadowed non-secret sources

#### Scenario: Typed run override changes behavior only

- **GIVEN** a route carries canonical typed behavior and a run supplies a supported typed behavior override
- **WHEN** the agent run begins
- **THEN** the run override SHALL win for that request
- **AND** every route identity, transport, credential binding, and fallback position SHALL remain unchanged

#### Scenario: Unsupported capability fails before provider access

- **GIVEN** behavior is valid in general but unsupported by the selected model kind or protocol
- **WHEN** canonical route or run behavior is validated
- **THEN** the operation SHALL fail with model kind, protocol, and logical behavior field identified
- **AND** no credential or provider request SHALL occur

#### Scenario: CLI and SDK apply identical behavior

- **GIVEN** CLI and SDK composition receive the same exact context and typed run override
- **WHEN** they execute an agent run
- **THEN** they SHALL produce the same effective request behavior
- **AND** neither SHALL read YAML, dotenv, process environment, settings projections, or consumer-local configuration

#### Scenario: Absent behavior uses provider-library defaults

- **GIVEN** neither canonical route behavior nor a run override specifies an optional field
- **WHEN** the agent runs
- **THEN** project code SHALL omit that field
- **AND** it SHALL not synthesize an old-schema or environment default

#### Scenario: Fallback routes retain their own behavior

- **GIVEN** primary and fallback canonical aliases define different supported behavior
- **WHEN** `create_model` constructs the chain
- **THEN** each route SHALL retain its own construction-time capability behavior
- **AND** request-scoped settings SHALL be applied through the documented enclosing run boundary without changing fallback order

#### Scenario: Provider verification is evidence-bound

- **WHEN** a provider route is accepted for release
- **THEN** deterministic tests SHALL prove protocol/factory/request construction without network access
- **AND** any live-success claim SHALL identify the current endpoint metadata fingerprint, canonical route, executable/library, repository SHAs, nested outcome, and authorization in retained evidence
- **AND** no mutable endpoint or historical success SHALL be normative proof by itself

### Requirement: Supported typed provider protocols

Agent-core SHALL support Anthropic Messages, OpenAI Chat Completions, and OpenAI Responses only when canonical resolution supplies a matching closed `model_kind` and typed `protocol` pair in an exact route. Provider class, endpoint suffix behavior, request format, and response handling SHALL follow that pair. `api_mode`, model/provider prefixes, endpoint inspection, and environment state SHALL have no protocol-selection authority.

#### Scenario: Anthropic Messages construction

- **GIVEN** an exact route selects model kind `anthropic` and protocol `messages`
- **WHEN** its provider model is constructed
- **THEN** agent-core SHALL use the Anthropic Messages provider/model implementation
- **AND** it SHALL preserve the route's wire model, provider ID, and endpoint metadata

#### Scenario: OpenAI Chat construction

- **GIVEN** an exact route selects model kind `openai_chat` and protocol `openai_chat`
- **WHEN** its provider model is constructed
- **THEN** agent-core SHALL use the OpenAI Chat Completions provider/model implementation
- **AND** it SHALL not route through Responses or Messages

#### Scenario: OpenAI Responses construction

- **GIVEN** an exact route selects model kind `openai_responses` and protocol `responses`
- **WHEN** its provider model is constructed
- **THEN** agent-core SHALL use the OpenAI Responses provider/model implementation
- **AND** it SHALL not route through Chat Completions or Messages

#### Scenario: Unsupported pair is rejected

- **GIVEN** a route contains an unregistered or incompatible model-kind/protocol pair
- **WHEN** canonical context or model construction validates it
- **THEN** construction SHALL fail before credential access or model instantiation
- **AND** no prefix, endpoint, or native-auth fallback SHALL select another protocol

### Requirement: Typed Responses streaming aggregation boundary

Streaming aggregation for OpenAI Responses SHALL activate only for a route whose validated model kind is `openai_responses` and protocol is `responses`. The provider integration SHALL parse SSE events through Pydantic AI's Responses model boundary, combine text deltas deterministically, normalize an empty successful completion to an empty string, and propagate upstream provider/transport exceptions unchanged. It SHALL NOT select aggregation behavior from `api_mode`, endpoint text, provider name, or model prefix.

#### Scenario: SSE stream aggregation

- **GIVEN** an exact Responses route and an SSE stream with multiple output-text delta events
- **WHEN** model execution completes
- **THEN** the returned text SHALL equal the deltas concatenated in event order
- **AND** transport framing SHALL not appear in the result

#### Scenario: Empty completion output normalization

- **GIVEN** an exact Responses route whose successful stream contains no output-text delta
- **WHEN** model execution completes
- **THEN** the returned text SHALL be the empty string
- **AND** the result SHALL not be `None`

#### Scenario: Upstream exception propagated

- **GIVEN** the selected Responses provider raises an authentication, transport, or protocol exception
- **WHEN** streaming execution is awaited
- **THEN** agent-core SHALL propagate the upstream exception
- **AND** it SHALL not convert the error into an empty successful response or try another protocol outside the canonical fallback chain

### Requirement: Provider-specific reasoning effort validation sets

The canonical schema SHALL accept the union effort vocabulary (`minimal`, `low`, `medium`, `high`, `xhigh`, `max`) in `models.<alias>.reasoning_effort` and `defaults.reasoning_effort`. At route construction, agent-core SHALL validate the effort against the closed provider-specific set selected by the route's model kind: Anthropic routes SHALL accept `low`, `medium`, `high`, `max`; OpenAI Chat and OpenAI Responses routes SHALL accept `minimal`, `low`, `medium`, `high`, `xhigh`. An effort value that is schema-valid but unsupported by the selected model kind SHALL fail before credential access or model instantiation, identifying the model kind and the rejected value.

#### Scenario: Anthropic route rejects xhigh

- **GIVEN** a canonical model declares `reasoning_effort: xhigh`
- **AND** its route selects model kind `anthropic`
- **WHEN** the route behavior is validated for construction
- **THEN** construction SHALL fail identifying `xhigh` as unsupported for the Anthropic route
- **AND** no credential access or model instantiation SHALL occur

#### Scenario: OpenAI route rejects max

- **GIVEN** a canonical model declares `reasoning_effort: max`
- **AND** its route selects model kind `openai_chat` or `openai_responses`
- **WHEN** the route behavior is validated for construction
- **THEN** construction SHALL fail identifying `max` as unsupported for the OpenAI route

#### Scenario: Schema accepts the union vocabulary

- **GIVEN** canonical configuration declares any of `minimal`, `low`, `medium`, `high`, `xhigh`, or `max` as a reasoning effort
- **WHEN** canonical schema validation runs
- **THEN** the value SHALL be accepted at the schema layer
- **AND** provider-specific rejection SHALL occur only at route construction

#### Scenario: Effort maps to the provider-native request field

- **GIVEN** a route with a supported effort value
- **WHEN** request settings are built
- **THEN** Anthropic routes SHALL carry the effort as the Anthropic effort setting
- **AND** OpenAI routes SHALL carry the effort as the OpenAI reasoning effort setting
