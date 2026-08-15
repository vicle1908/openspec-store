## Why

The archived `complete-agent-llm-config-integration` change declares completion while the current canonical requirements and implementation still expose multiple competing LLM authorities. `tdt-core` accepts both its canonical `providers`/`models`/`defaults` schema and legacy mapping projections; `agent-core` exposes several model factories, accepts mapping-shaped snapshots and raw routing inputs, and lets `BaseAgent` reopen configuration; CLI consumers may infer a model when `defaults.cli_models` is absent or fall back to consumer-local model configuration.

Those paths make it impossible to prove that model selection, provider routing, fallback order, credential access, diagnostics, and live execution derive from one caller decision. The correction is an immediate breaking clean break: one canonical schema, one typed profile, one process-local construction context, one public model factory, and no legacy, compatibility, alias, shim, or local-fallback authority.

## What Changes

**Operation model:** this change removes 35 superseded requirements, adds 18 clean replacements, and strengthens 3 CLI/evidence requirements. The 142 scenarios beneath removed requirements receive explicit dispositions; all 14 baseline scenarios beneath the three MODIFIED requirements remain verbatim.

### Canonical configuration and profile resolution

- **BREAKING** Accept only the canonical `providers` / `models` / `defaults` LLM schema. Legacy-only and mixed schemas, including top-level `model`, `gateway`, `providers.*.api_key_env`, and `api_mode`, fail closed during canonical validation.
- **BREAKING** Remove the public mapping compatibility projection `load_agent_config` and its legacy loader. Retain secure mapping/overlay primitives only for their explicitly owned non-LLM source-reading responsibilities; they are not model-selection APIs.
- Make `ResolvedAgentProfile` the only public resolved LLM profile. Remove settings-shaped projections and the `primary`, `fallback`, or other compatibility aliases.
- Project each selected primary and fallback into an exact immutable route containing canonical alias, model/factory kind, wire model, canonical provider ID, explicit native/endpoint transport kind, typed protocol, normalized non-secret endpoint metadata, provider-bound credential-reference metadata, behavior, and provenance.
- Permit an explicit run override only when it names an already defined canonical model alias. It cannot inject provider, endpoint, protocol, credential, raw model, or fallback mappings.

### Process-local construction boundary

- Add a source-free `build_model_construction_context(profile)` and a composition-root `resolve_model_construction_context(agent_name)` in `tdt-core`.
- Make `ModelConstructionContext` a final slotted non-dataclass with a factory-only construction path. It rejects direct public construction, `copy`, `deepcopy`, pickle/reduction, `vars`, dataclass helpers, and Pydantic dumping.
- Bind the context to the exact primary/fallback route projections and provider-bound `CredentialResolver`. Its deterministic SHA-256 identity covers the complete canonical non-secret selection and source fingerprints; it never includes or derives from credential values.

### One public agent-core construction model

- **BREAKING** Keep `create_model` as the only public model factory. An explicit Pydantic-AI `Model` is returned by object identity with zero context/config/environment/credential/fallback reads. A canonical alias string requires a complete `ModelConstructionContext` and constructs the ordered primary/fallback chain from that context.
- **BREAKING** Remove public `create_fallback_model`, `create_model_with_fallback`, and the agent-core `infer_model` re-export. Any route/fallback helpers are private and context-only.
- **BREAKING** Remove raw endpoint, secret, provider mapping, model mapping, snapshot, and fallback kwargs from public signatures. Unsupported calls fail through the actual clean signature; there is no `_UNSET` sentinel, transition release, or `MigrationError` shim.
- Keep `build_agent` as the public composition boundary above `create_model`. It accepts either an explicit `Model` or a canonical alias plus complete context.
- Make `ConsumerRuntimeProfile` runtime/framework-only: no LLM `model`, no I/O-producing `settings` default, and no duplicated profile identity.
- Make `BaseAgent` accept an already constructed `Model` only. It does not accept strings or resolve configuration, providers, credentials, or fallbacks.
- Make agent-core CLI composition resolve the canonical context once and call the public `build_agent`/`create_model` boundary.

### Whole-ecosystem consumer convergence

- Make agent-harness resolve one canonical context per run and thread it through production stage composition without persisting it or reconstructing selection from a string.
- Make docs-sync carry one canonical profile/context through configuration, generation, diagnostics, retries, and resume; persist only safe identity and reacquire process-local access through the same provider binding after resume.
- Require every enabled ai-harness-skills and ai-review CLI provider to have an explicit canonical `defaults.cli_models` relationship. Missing or invalid mapping fails before adapter construction; consumer-local model fallback is removed.
- Make ai-harness-skills use the consumer-owned canonical TDT root, never its contained target, and make ai-review propagate canonical source and projection failures instead of converting them to absence.
- Remove or rewrite compatibility tests, fixtures, templates, examples, docs, and exports throughout the active product repositories. Historical archives remain immutable evidence.

### Evidence and lifecycle truth

- Replace the direct-adapter live claim with two separately authorized public consumer operations: installed `agent-harness run`, and installed `ai-review review`. Each requires its own current mapping, enablement, executable identity, nonce or artifact, nested result, and target-preservation proof.
- Keep the store validator executable before and after archive by resolving one unique active or archived lifecycle root and using `artifactPaths.specs.existingOutputPaths` as the authoritative active delta inventory.
- Recapture identities, dependency origins, tests, quality gates, scenario treatment, drift checks, and rollback evidence only after final commits are frozen.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-config-resolution`: replace mapping compatibility resolution with one canonical typed profile and exact process-local construction context.
- `agent-core-model-resolution`: replace old schema, snapshot, multi-factory, config-owning base-agent, and raw-constructor behavior with one clean public factory and composition boundary.
- `cli-provider-profile-resolution`: require explicit canonical CLI mappings, remove consumer-local fallback, and retain identity-bound live/evidence verification across archive relocation.

## Impact

### Ownership boundaries

- `openspec-store`: corrective deltas, archive-aware validator/tests, scenario treatment, evidence, sync, and archive verification.
- `tdt-core`: canonical-schema-only validation, typed route projection, typed profile, process-local context, credential binding, and removal of compatibility exports.
- `agent-core`: one public model factory, clean SDK/base-agent/CLI composition, runtime-only profiles, export cleanup, tests, templates, examples, and docs.
- `agent-harness`: canonical context resolution and production stage propagation.
- `agent-docs-sync`: operation-context propagation, resume identity, generation construction, tests, and docs.
- `ai-harness-skills`: canonical-root selection, explicit CLI mapping, contained public generation boundary, tests, and docs.
- `ai-review`: explicit CLI mapping, fail-closed projection, true reviewer boundary, tests, and docs.

Execution uses one writer and one dedicated worktree per repository. Every repository packet must recapture its branch, immutable base SHA, complete dirt, active ownership, dependency bindings, and runtime import origins before editing. Primary-checkout dirt, stale worktrees, generated state, unrelated active changes, and credential stores remain external and must not be cleaned, reset, copied, staged, committed, or used as patch sources.

The current presence-only preflight finds no canonical Codex or Claude CLI mapping for `ai-harness-skills` or `ai-review`, while ai-review enables only `codescan`. Both live rows therefore remain blocked unless separately authorized non-secret mapping/enablement state and live authorization are present at launch time. This change never reads, prints, copies, rotates, or rewrites credential values.

### Breaking change policy

This is one immediate breaking release. All participating repositories and active examples move to the new signatures and canonical schema together. There is no compatibility phase, deprecated alias, dual schema, mapping adapter, migration exception shim, consumer-local fallback, or release-N/release-N+1 transition.

### Non-goals

- Do not add another precedence chain, credential registry, serialized secret field, or consumer-local TDT loader.
- Do not change credential values or native provider credential stores.
- Do not redesign Pydantic AI, native CLI protocols, or unrelated authorization/path-security/Graphify behavior.
- Do not rewrite historical archived changes or their retained evidence; add corrective supersession evidence instead.
- Do not refresh Graphify or GitNexus indexes as part of implementation; index maintenance remains separately owned.
