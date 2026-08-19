## MODIFIED Requirements

### Requirement: Clean model and agent construction boundaries

`create_model` and `build_agent` SHALL be the only public string-aware construction boundaries. `build_agent` SHALL accept either an explicit `Model` or one canonical alias plus a complete `ModelConstructionContext`; it SHALL call `create_model` for the string path and SHALL call no configuration or profile resolver. `ConsumerRuntimeProfile` SHALL contain only pure framework/runtime settings and SHALL have no model-selection field, settings projection, profile identity, or I/O-producing default. `CallerSnapshot` and every snapshot-shaped public input MUST be removed.

`BaseAgent` SHALL accept an already constructed `Model` only. It MUST NOT accept a string, profile, context, config mapping, provider mapping, or fallback input and MUST NOT call `create_model`, `load_settings`, `load_agent_config`, `resolve_agent_profile`, or another selection/resolution function. Agent-core CLI composition SHALL resolve one context before `build_agent` and SHALL not maintain an independent `_create_runtime_model` authority.

`AgentRuntime` SHALL pass `deps_type=AgentRuntimeDeps` to pydantic-ai's `Agent` constructor, enabling pydantic-ai to properly type-check the `RunContext[AgentRuntimeDeps]` parameter in tool functions. Tool functions receiving an unexpected context type SHALL be handled gracefully via defensive `hasattr(ctx, "deps")` checks.

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

#### Scenario: AgentRuntime passes deps_type to pydantic-ai Agent

- **WHEN** `AgentRuntime.__init__` constructs the pydantic-ai `Agent`
- **THEN** it SHALL pass `deps_type=AgentRuntimeDeps` as a constructor argument
- **AND** pydantic-ai SHALL be able to type-check `ctx: RunContext[AgentRuntimeDeps]` in tool functions

#### Scenario: Type guard prevents AttributeError on ctx

- **WHEN** `_prepare_tools` or `_run_via_registry` receives a `ctx` that lacks a `deps` attribute
- **THEN** the function SHALL log a warning with the actual `ctx` type and return a safe fallback
- **AND** the agent SHALL continue running without crashing
