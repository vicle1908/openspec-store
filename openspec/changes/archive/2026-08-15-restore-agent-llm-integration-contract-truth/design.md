## Context

The current repositories contain the pieces of a canonical solution but compose them through competing public paths. `tdt-core` has a typed provider/model/default schema, a recursively frozen `ResolvedAgentProfile`, provider-bound `CredentialResolver`, and non-serializable `ProtectedCredential`. It also still classifies legacy schema, returns `None` for legacy-only input, exports `load_agent_config`, builds settings-shaped projections, and exposes `primary`/`fallback` compatibility properties.

`agent-core` currently exposes `create_model`, `create_fallback_model`, `create_model_with_fallback`, and an SDK `infer_model` re-export. `CallerSnapshot`, `ConsumerRuntimeProfile.model/settings`, `BaseAgent` string construction, `build_agent` configuration loading, and `_create_runtime_model` each preserve another place where model/provider/fallback authority can be reconstructed. Agent-harness and docs-sync consume those shapes; ai-harness-skills can use a contained target as a TDT root; ai-review converts canonical-source `OSError` into local mapping absence; native CLI selection can infer a model when `defaults.cli_models` is absent.

The earlier corrective plan retained migration kwargs, normalization, aliases, and a release transition. That is incompatible with the controlling clean-break decision. This design removes every old public LLM authority in one coordinated ecosystem release.

The work spans independently versioned repositories. Primary-checkout dirt, generated Graphify/GitNexus state, retained evidence, stale worktrees, credential stores, and unrelated active changes are external state. Implementation therefore uses one writer and one dedicated worktree per repository, exact immutable bases, and dependency-ordered integration.

## Goals / Non-Goals

**Goals:**

- Make the canonical `providers` / `models` / `defaults` schema the only accepted LLM schema.
- Make one exact immutable route projection represent each selected primary/fallback relationship.
- Make one factory-created process-local context the only non-`Model` input to public agent-core construction.
- Keep exactly one public model factory and one public SDK composition boundary.
- Make `BaseAgent` and all lower layers configuration-free and `Model`-only.
- Remove mapping/snapshot/settings/profile aliases and consumer-local model fallback from active code, tests, docs, templates, and exports.
- Keep protected values provider-bound, process-local, and absent from every identity, diagnostic, exception, and evidence artifact.
- Verify all participating consumers through their true public paths and exact dependency origins.
- Keep corrective evidence valid after OpenSpec archive relocation.

**Non-Goals:**

- Do not add another route registry, secret container, provider precedence chain, or consumer-owned canonical loader.
- Do not change credential values, native credential stores, or provider authentication protocols.
- Do not redesign Pydantic AI, unrelated domain configuration, authorization, path containment, or Graphify behavior.
- Do not rewrite historical archived changes or evidence.
- Do not refresh generated indexes in the implementation transaction.

## Decisions

### 1. One canonical schema; unsupported schemas fail

The only LLM selection schema is:

```yaml
providers:
  <provider-id>:
    transport: native | endpoint
    base_url: <required-for-endpoint-and-forbidden-for-native>
    protocol: messages | openai_chat | responses
    auth_env: <registered-key-name>
    cli_provider: <optional-native-cli-id>
models:
  <canonical-alias>:
    provider: <provider-id>
    model: <wire-model>
    reasoning_effort: <optional-supported-value>
    context_window: <optional-positive-integer>
defaults:
  model: <canonical-alias>
  fallback: [<canonical-alias>, ...]
  reasoning_effort: <optional-supported-value>
  cli_models:
    <enabled-cli-id>: <canonical-alias>
```

`ProviderModelConfig` validates referential integrity before any profile is returned. Top-level `model`, `gateway`, `providers.*.api_key_env`, `api_mode`, legacy-only documents, and mixed documents are invalid input. The parser does not classify them into a supported mode, normalize them, ignore them, return `None`, or hand them to another loader.

`load_agent_config` and `_legacy_load_agent_config` are removed from `tdt-core` and its public exports. `load_config_mapping` and `load_agent_overlay` may remain as secure source primitives for their explicit domain responsibilities, but they do not project an effective LLM configuration. All active LLM callers use `resolve_agent_profile`.

The global canonical file owns the provider/model catalog. An agent overlay may contain canonical `defaults` selections/behavior, runtime, and explicitly registered domain sections; it cannot define providers, models, endpoints, protocols, credential references, wire models, or CLI relationships. Explicit run, registered consumer-environment, registered shared-environment, agent-overlay, and global-default model selectors may select only aliases already defined in the global catalog. Invalid higher-priority selectors fail instead of falling through. CLI-native selection is stricter: enabled CLI identities require `defaults.cli_models`; consumer-specific environment aliases cannot replace that relationship.

An explicit operation override, where a consumer genuinely needs one, may contain only a canonical alias already defined in `models`. Provider, endpoint, protocol, credential, wire-model, fallback, and arbitrary mapping overrides are invalid.

### 2. Profiles carry exact routes, not reconstruction material

`ResolvedAgentProfile` is redesigned around exact selected route projections:

```python
class ResolvedModelRoute(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_alias: str
    model_kind: ModelKind
    wire_model: str
    provider_id: str
    transport: ProviderTransport
    protocol: ProviderProtocol
    endpoint_metadata: FrozenMapping
    credential_reference: CredentialAvailability
    behavior: FrozenMapping
    provenance: FrozenMapping


class ResolvedAgentProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_name: str
    primary_route: ResolvedModelRoute
    fallback_routes: tuple[ResolvedModelRoute, ...]
    runtime: FrozenMapping
    root: str
    environment_profile: str
    source_fingerprints: FrozenMapping
```

The concrete immutable mapping representation is an implementation choice, but nested mutation must be impossible and the serialized safe form must be deterministic. The public profile has no loose `model`, `fallbacks`, provider-map reconstruction data, settings projection, `.primary`, `.fallback`, or equivalent compatibility property.

`model_kind`, `transport`, and `protocol` are separate closed typed fields. Canonical resolution maps each supported protocol to a model factory kind and validates the pair. `transport=native` forbids `base_url` and delegates endpoint/auth behavior to the selected provider library; `transport=endpoint` requires one normalized HTTP(S) `base_url`. It does not derive these fields from provider ID, alias, wire model, endpoint text, executable, credentials, or environment. `canonical_alias`, `wire_model`, and `provider_id` also remain separate; none is parsed from another.

The profile remains safe to serialize because it contains only credential reference metadata. It never contains the protected value or a value-derived digest.

### 3. The construction context is factory-only and process-local

`ModelConstructionContext` is a final slotted non-dataclass. A module-private factory capability is required by its private construction path; public direct construction fails. The public APIs are:

```python
def build_model_construction_context(
    profile: ResolvedAgentProfile,
) -> ModelConstructionContext: ...


def resolve_model_construction_context(
    agent_name: str,
    *,
    root: str | Path | None = None,
    canonical_alias: str | None = None,
) -> ModelConstructionContext: ...
```

`build_model_construction_context` is source-free. It validates the exact ordered routes already present in the profile, binds one `CredentialResolver` to that profile when any route needs protected material, and constructs the context through the private capability. It never reparses provider maps or reselects a route.

`resolve_model_construction_context` is a composition-root convenience: it resolves one typed profile and immediately builds the context. `root`, when supplied, is the consumer-owned canonical TDT root and never an operation target. `canonical_alias`, when supplied, must identify a model already defined by canonical configuration and cannot alter its route.

The context exposes read-only `profile`, `primary_route`, `fallback_routes`, and `identity_digest`. It rejects:

- direct public construction;
- `copy.copy` and `copy.deepcopy`;
- pickle and reduction hooks;
- `vars` and mutable `__dict__` access;
- `dataclasses.asdict`, `astuple`, and `replace` by not being a dataclass;
- Pydantic model/type-adapter dumping; and
- any public `model_dump`, state, clone, or serialization hook.

Every rejected path raises `TypeError("ModelConstructionContext is process-local")`. The class is not a `BaseModel` and does not advertise a serializable schema.

`identity_digest` is SHA-256 over canonical JSON containing the complete non-secret selected identity:

- agent identity;
- ordered primary/fallback position;
- canonical alias;
- model kind;
- wire model;
- canonical provider ID;
- explicit transport kind and typed protocol;
- normalized endpoint metadata;
- provider-bound credential key-name/availability metadata;
- behavior;
- structured provenance identity; and
- sorted source fingerprints.

Credential values are neither read to compute the digest nor represented directly, encoded, or hashed within it.

### 4. `create_model` is the sole public model factory

The exact public overloads are:

```python
@overload
def create_model(model: Model, *, context: None = None) -> Model: ...


@overload
def create_model(
    model: str,
    *,
    context: ModelConstructionContext,
) -> Model: ...
```

The `Model` path returns the object immediately by identity. It does not inspect a supplied context, compare profiles, wrap fallbacks, or read any source.

The string is a canonical alias assertion. It must equal `context.primary_route.canonical_alias`. The factory creates the primary and every fallback in `context.fallback_routes` through private route-only helpers and returns a Pydantic-AI fallback model only when fallback routes are present. There is no caller-supplied fallback list.

Public `create_fallback_model`, `create_model_with_fallback`, and the agent-core `infer_model` export are deleted. Internal use of Pydantic AI's inference machinery may remain behind private route construction, but it is never a public agent-core selection API and receives only values from the exact selected route.

Raw `base_url`, `api_key`, `providers`, `model_config`, `snapshot`, and `fallback_ids` parameters are absent from the signature. Python signature validation and canonical schema validation reject unsupported calls. There is no sentinel, migration exception, wrapper, deprecated alias, or release transition.

Native authentication is permitted only after the context has selected an explicit supported native route. Project code never reads environment variables to select a model, provider, endpoint, protocol, fallback, or behavior. Canonical failure cannot fall through to native construction.

### 5. `build_agent` composes; `BaseAgent` executes

The public SDK boundary is:

```python
@overload
def build_agent(
    *,
    model: Model,
    profile: ConsumerRuntimeProfile | None = None,
    ...,
) -> BaseAgent: ...


@overload
def build_agent(
    *,
    model: str,
    context: ModelConstructionContext,
    profile: ConsumerRuntimeProfile | None = None,
    ...,
) -> BaseAgent: ...
```

`build_agent` handles the explicit `Model` path first and otherwise delegates exactly once to `create_model`. It never calls `load_settings`, `load_agent_config`, `resolve_agent_profile`, or another loader. It has no profile-identity comparison because `ConsumerRuntimeProfile` no longer carries LLM identity.

`ConsumerRuntimeProfile` contains only pure runtime/framework fields. It has no `model`, no profile/settings projection, and no default factory that performs I/O. Default construction is deterministic and source-free.

`BaseAgent` accepts `Model` only. It owns the run loop, tools, hooks, flavors, memory, and other runtime behavior, but no model/config/provider construction. A direct string call fails at the clean public signature; it is not caught and translated.

Agent-core CLI composition resolves a context once and calls `build_agent` or `create_model`. `_create_runtime_model` and any equivalent CLI-owned selection/fallback authority are removed.

### 6. Consumers use one operation context

Agent-harness resolves one canonical construction context at its run composition root. `HarnessServices`, stage services, and `StageCompositionContext` carry the in-process object to the production stage-agent boundary. Checkpoints and evidence contain only safe profile/context digests. An explicit preconstructed `Model` remains the test/injection zero-read path. `HarnessConfig.load` no longer owns LLM selection or creates a runtime profile with model/settings fields.

Docs-sync extends its existing `DocsSyncOperationContext`. The operation boundary resolves one canonical profile/context; discovery, validation, generation, diagnostics, retries, and same-process resume share it. Duplicate `GenerationConfig` aliases and I/O-producing profile defaults are removed. Provider identity comes from `primary_route.provider_id`, never string splitting. Durable state stores only safe route/profile/context identity; a new process resolves a fresh context and requires a full identity match before write-capable generation.

ai-harness-skills resolves canonical CLI selection from the consumer-owned TDT root. `run.project_root` remains solely the contained target. Every enabled CLI provider needs an explicit `defaults.cli_models` relationship; missing mapping fails before adapter construction. There is no consumer-local model fallback.

ai-review applies the same rule. Canonical source `OSError`, schema, relationship, selection, and projection errors propagate as typed redacted failures. No failure or missing enabled mapping becomes `{}`, `None`, retained reviewer defaults, or native CLI model configuration.

### 7. CLI mappings are explicit and fail closed

`defaults.cli_models` is mandatory for each native CLI identity enabled by a participating consumer. The model alias must exist and its provider must declare the same `cli_provider`. A unique candidate does not imply a mapping.

The selector can report no selection only while inspecting an identity that is both undeclared and not enabled. That result does not authorize launch. At an enabled consumer boundary, missing, invalid, ambiguous, unsupported, or unavailable canonical selection always fails before adapter construction.

A run-scoped override may choose another canonical alias belonging to the same CLI provider relationship. It cannot inject a raw route or consumer-local mapping. The projected result retains both the native adapter identity and canonical provider ID, plus canonical alias, wire model, typed protocol, supported behavior, provider-filtered credential-reference metadata, and provenance.

### 8. Verification proves public behavior and exact dependency identity

Each touched Python repository runs its focused tests plus repository-required full pytest, strict mypy, Ruff check, Ruff format check, and `git diff --check` gates with isolated caches and offline/frozen dependency behavior where supported. Accepted evidence records exact commands, exit codes, pass/skip counts, complete dirt, branch, committed SHA, dependency declaration/lock identity, installed import path, and resolved upstream Git SHA.

Focused tests must prove:

- canonical-only schema rejection for every unsupported/mixed input;
- absence of `load_agent_config`, profile aliases, snapshot APIs, extra public factories, raw kwargs, and public infer re-export;
- exact route projection and complete safe context digest;
- direct context construction/copy/serialization rejection, including dataclass and Pydantic paths;
- explicit `Model` identity with zero reads;
- canonical alias/context chain construction and mismatch failure before access;
- runtime-only `ConsumerRuntimeProfile` and `Model`-only `BaseAgent`;
- one context resolution per agent-core CLI, harness run, and docs-sync operation;
- no consumer-local CLI model fallback;
- contained target independence and ai-review fail-closed source handling; and
- concurrency isolation.

Repository-wide active source/test/template/example/docs searches must find no remaining removed symbol or supported old-schema path. Historical archives and frozen RED evidence are excluded from the absence gate but remain immutable.

### 9. Live acceptance uses two true consumer operations

Live acceptance occurs only after deterministic commits and dependencies are frozen and separate authorization exists. One disposable operation invokes installed `agent-harness run`, reaching `_resolve_runner` and `WorkflowRunner.run`. Another invokes installed `ai-review review`, reaching `run_review` and `ReviewOrchestrator.run_sync`.

Each row has its own fixture, mapping/enablement preflight, executable path/version, canonical provider and alias, nonce or generated artifact, process result, nested result, target before/after fingerprint, duration, and final status. Direct adapter calls are reachability probes only. Missing mapping, disabled provider, absent authorization, credential unavailability, or identity drift records `blocked` without launch.

The currently observed absence of Codex/Claude canonical mappings and ai-review's `codescan`-only enablement is a blocker, not permission to alter configuration.

### 10. Evidence survives archive relocation

The store validator and tests share one read-only lifecycle resolver. A retained change identity resolves to exactly one active `openspec/changes/<name>` root or one unique `openspec/changes/archive/<date>-<name>` root. Missing or ambiguous roots fail deterministically.

While active, `artifactPaths.specs.existingOutputPaths` is the authoritative delta inventory. Retained schema/artifact identities are lifecycle-root-relative so the same validator suite runs after archive. The resolver performs no network access, provider launch, product mutation, or credential-value read.

Corrective evidence supersedes but never rewrites the archived completion claim. Frozen RED, intermediate dirty, final deterministic, live, rollback, and lifecycle records remain separate.

### 11. Integration is one breaking ecosystem release

The dependency order is:

1. validate and approve these clean-break artifacts;
2. implement canonical-only profile/routes/context in `tdt-core` and remove old public surfaces;
3. implement the sole factory and clean agent composition in `agent-core`;
4. migrate agent-harness and docs-sync against the immutable upstream commits;
5. migrate ai-harness-skills and ai-review against the immutable `tdt-core` result;
6. update all active tests/templates/examples/docs and run complete deterministic gates;
7. repair the archive-aware validator and recapture immutable evidence;
8. run separately authorized live rows only when all prerequisites exist;
9. sync only authoritative delta paths, validate, archive, commit, and rerun post-archive gates.

There is no mixed-version supported state. Downstream worktrees bind the exact upstream commits before acceptance, and no downstream evidence is current after an upstream commit changes.

## Risks / Trade-offs

- **Breaking imports and signatures:** old callers fail immediately. Mitigation: migrate every active ecosystem caller, test, template, example, and doc in the same release and enforce an absence search.
- **Context factory enforcement is Python-level, not a security boundary:** determined reflection can inspect private module state. Mitigation: make the supported path unambiguous, structurally prevent ordinary construction/copy/serialization, and test every public mechanism; credential access remains independently provider-bound.
- **Schema conversion is mandatory:** existing old configuration cannot run. Mitigation: convert canonical workspace configuration before product acceptance and fail with redacted field-level diagnostics; do not add runtime normalization.
- **Process-local context complicates resume:** it cannot be persisted. Mitigation: persist complete safe identity, reacquire through the same canonical binding, and fail before writes on drift.
- **Cross-repository version skew:** a consumer may import a stale wheel or checkout. Mitigation: bind dependency declarations/locks/import origins/full SHAs and invalidate downstream evidence after any upstream change.
- **Live prerequisites may remain blocked:** mapping or authorization may be absent. Mitigation: report deterministic readiness separately and do not launch or alter provider state without separate authorization.
- **Concurrent dirt can invalidate evidence:** primary checkouts and worktrees can move. Mitigation: one writer per repository, immutable bases, content fingerprints, and drift validation before every handoff/lifecycle transition.

## Rollback

Rollback is repository-local and dependency ordered: revert consumers before `agent-core`, then revert `agent-core` before `tdt-core`. After each reversal, rerun dependency-origin and deterministic checks and mark all dependent evidence stale. A rollback does not restore a valid completion claim; the corrective OpenSpec change remains open or blocked. No rollback step mutates credentials, cleans external worktrees, or rewrites historical archives.
