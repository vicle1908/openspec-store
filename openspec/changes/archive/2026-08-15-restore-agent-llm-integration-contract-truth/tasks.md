## 1. Ownership, Baseline, and Stop Conditions

- [x] 1.1 Assign one human-visible writer to each of `openspec-store`, `tdt-core`, `agent-core`, `agent-harness`, `agent-docs-sync`, `ai-harness-skills`, and `ai-review`; record its dedicated worktree, branch, immutable 40-character base SHA, closest `AGENTS.md`, toolchain, and raw pre-edit dirt.
- [x] 1.2 Re-scan registered worktrees, active OpenSpec changes, and current owner messages for overlap; fingerprint every external source/test/evidence/generated/store/worktree change and preserve it without cleaning, pruning, resetting, copying, staging, committing, or using it as a patch source.
- [x] 1.3 Freeze a RED baseline of every current public compatibility surface and contradiction: old schemas, `load_agent_config`, profile aliases/projections, snapshot types, extra model factories, public infer export, config-owning `BaseAgent`, CLI-owned model resolution, and consumer-local CLI fallback.
- [x] 1.4 Record stop conditions: stop on unresolved ownership, overlapping dirt, new normative behavior, changed upstream identity, missing dependency origin, or credential-bearing work without current authorization; never count a skipped or blocked prerequisite as passed.

## 2. Delta Operation and Scenario Treatment

This change has the following operation matrix:

| Spec | REMOVED | ADDED | MODIFIED |
|------|---------|-------|----------|
| agent-config-resolution | 12 | 7 | 0 |
| agent-core-model-resolution | 18 | 6 | 0 |
| cli-provider-profile-resolution | 5 | 5 | 3 |
| **Total** | **35** | **18** | **3** |

- [x] 2.1 Record one replacement/disposition for every scenario beneath all 35 REMOVED requirements; the exact baseline gate is 142/142 old scenarios accounted.
- [x] 2.2 Preserve all 14 baseline scenarios beneath the three MODIFIED CLI/evidence requirements byte-for-byte and prove 14/14 with SHA-256 block comparison.
- [x] 2.3 Re-run current production/test/template/example/docs/worktree searches for every removed symbol, old schema field, mapping/snapshot path, local fallback, route reconstruction, credential boundary, canonical-root call, and native adapter invocation; classify current product code separately from archives, frozen evidence, generated state, fixtures, and stale worktrees.
- [x] 2.4 Run GitNexus context/impact for every public symbol removed or changed and record direct callers, affected flows, risk, and the exact replacement task before editing.
- [x] 2.5 Review the three authoritative delta paths from `artifactPaths.specs.existingOutputPaths`; confirm no unrelated capability is changed and stop if implementation needs another normative behavior.

## 3. tdt-core Canonical-Schema-Only Resolution

- [x] 3.1 Make `ProviderModelConfig` accept only canonical `providers`, `models`, and `defaults`; add explicit `native`/`endpoint` transport with conditional `base_url` validation, validate every provider/model/default/CLI relationship, and aggregate redacted non-secret relationship errors.
- [x] 3.2 Remove schema classification/normalization for old or mixed inputs. Top-level `model`, `gateway`, `providers.*.api_key_env`, `api_mode`, legacy-only documents, and mixed documents must fail validation rather than return `None`, defaults, or a projection.
- [x] 3.3 Make the global canonical catalog own providers/models/defaults; restrict agent overlays to canonical `defaults` selection/behavior, runtime, and explicitly registered domain sections, and forbid catalog/route definitions in overlays.
- [x] 3.4 Require every explicit or registered environment selector to name an existing canonical alias and preserve typed source precedence/provenance; invalid higher-priority selectors fail instead of falling through.
- [x] 3.5 Remove `_legacy_load_agent_config`, public `load_agent_config`, its public exports, its compatibility cache/projection, and old-schema tests. Retain source mapping/overlay primitives only where their non-LLM ownership is explicit.
- [x] 3.6 Migrate every active `tdt-core` internal caller and every participating ecosystem caller to `resolve_agent_profile`; delete phase-compatibility test modules and rewrite retained behavior tests against typed canonical resolution.
- [x] 3.7 Restrict explicit run model overrides to a canonical alias already defined in `models`; reject raw wire-model, provider, endpoint, protocol, credential, executable, fallback, or arbitrary mapping overrides.
- [x] 3.8 Add canonical-only schema, canonical overlay, selector precedence, undefined-relationship aggregation, explicit-alias override, protected-value exclusion, cache identity, and concurrent-resolution tests.

## 4. tdt-core Exact Routes and Process-Local Context

- [x] 4.1 Add an immutable `ResolvedModelRoute` with separate `canonical_alias`, closed `model_kind`, `wire_model`, `provider_id`, explicit transport, typed `protocol`, recursively immutable normalized endpoint metadata, provider-bound credential-reference metadata, behavior, and structured provenance.
- [x] 4.2 Redesign `ResolvedAgentProfile` to expose `primary_route` and ordered `fallback_routes`; remove loose model/fallback/provider reconstruction fields, settings projections, and `primary`/`fallback` compatibility properties.
- [x] 4.3 Implement a closed validated protocol-to-model-kind relationship; reject mismatches before context or credential construction and never infer kind/provider from alias, wire model, endpoint, executable, credentials, or environment.
- [x] 4.4 Implement `ModelConstructionContext` as a final slotted non-dataclass with a module-private factory capability and no public direct construction path.
- [x] 4.5 Make the context reject copy, deepcopy, pickle/reduction, `vars`, dataclass `asdict`/`astuple`/`replace`, Pydantic model/type-adapter dumping, and every advertised state/clone/dump hook with `TypeError("ModelConstructionContext is process-local")`.
- [x] 4.6 Implement source-free `build_model_construction_context(profile)` that consumes exact profile routes, binds the existing provider-bound `CredentialResolver`, and performs no map reconstruction, file read, environment selection, or credential reveal.
- [x] 4.7 Implement composition-root `resolve_model_construction_context(agent_name, *, root=None, canonical_alias=None)` using one typed profile resolution; ensure `root` is consumer-owned and the optional alias is defined canonically.
- [x] 4.8 Compute deterministic SHA-256 over canonical JSON for the complete non-secret agent, ordered route, behavior, provenance, credential-reference, endpoint, and source-fingerprint identity; prove credential values are neither read nor value-derived in the digest.
- [x] 4.9 Add construction-capability, recursive immutability, exact-route, digest sensitivity, copy/serialization, provider-bound reveal, cross-provider rejection, native-route, and concurrency tests.
- [x] 4.10 Run tdt-core focused and full pytest, strict mypy, Ruff check, Ruff format check, and `git diff --check` with isolated caches; record exact commands/exits/counts/dirt and commit the clean result.

## 5. agent-core Sole Model Factory

- [x] 5.1 Make public `create_model` support only `Model` with `context=None` or canonical-alias `str` with complete `ModelConstructionContext`; the `Model` path returns by identity before any context/source access.
- [x] 5.2 Make the string path require an exact match with `context.primary_route.canonical_alias` and build the complete ordered primary/fallback chain from exact routes through private context-only helpers.
- [x] 5.3 Remove public `create_fallback_model`, `create_model_with_fallback`, agent-core's public `infer_model` re-export, and their exports/docs/tests; keep any library inference call private and route-bound.
- [x] 5.4 Remove public `base_url`, `api_key`, `providers`, `model_config`, `snapshot`, and `fallback_ids` kwargs plus `_UNSET`, transition, migration-exception, wrapper, or deprecated-alias handling.
- [x] 5.5 Delete `_resolve_proxy_from_model_id` and every agent-core project-code environment/config/prefix precedence read; native provider authentication may occur only in the selected provider library after exact route selection.
- [x] 5.6 Replace old top-level model behavior, Thinking, provider escape-hatch, and CLI reload paths with typed allowlisted behavior carried on exact routes plus typed run-scoped overrides; reject arbitrary extra settings, raw headers/body, unknown fields, and unsupported capabilities.
- [x] 5.7 Route Messages, Chat Completions, and Responses only from the exact typed model-kind/protocol pair; migrate Responses streaming aggregation off `api_mode` and preserve deterministic delta ordering, empty-string normalization, and upstream exception propagation.
- [x] 5.8 Add exact public-path tests for Model identity/zero reads, canonical alias chain order, alias mismatch, missing context, all typed protocols, Responses streaming, model-kind/protocol mismatch, typed behavior/ranges/capabilities, raw-kwarg signature rejection, removed exports, native-auth boundary, safe diagnostics, and concurrent isolation.

## 6. agent-core Clean Composition Boundaries

- [x] 6.1 Remove `CallerSnapshot` and every snapshot-shaped type/property/test; do not leave an alias or adapter.
- [x] 6.2 Make `ConsumerRuntimeProfile` pure runtime/framework state: remove LLM `model`, settings/profile projections, canonical identity duplication, and I/O-producing default factories.
- [x] 6.3 Make `build_agent` accept only explicit `Model` or canonical alias plus complete context; delegate string construction exactly once to `create_model` and call no configuration/profile resolver.
- [x] 6.4 Make `BaseAgent` accept an already constructed `Model` only; remove string/config/context/provider/fallback parameters, constructor resolution, `load_settings`, and any compatibility error handling.
- [x] 6.5 Remove `_create_runtime_model` and migrate agent-core CLI composition to resolve one canonical context then call public `build_agent`/`create_model`.
- [x] 6.6 Update all active agent-core tests, CLI templates, examples, README/API docs, and annotations to the clean signatures; direct `BaseAgent` examples must construct/pass `Model` first.
- [x] 6.7 Run an active-tree absence gate for every removed symbol/kwarg/profile property/config loader/string-BaseAgent example, excluding frozen historical evidence only.
- [x] 6.8 Run agent-core focused and full pytest, strict mypy, Ruff check, Ruff format check, and `git diff --check`; record exact commands/exits/counts/dirt, bound tdt-core origin/SHA, and commit the clean result.

## 7. agent-harness Run Composition

- [x] 7.1 Remove `load_agent_config` and `ConsumerRuntimeProfile.model/settings` from `HarnessConfig`; keep harness domain configuration separate from LLM selection.
- [x] 7.2 Resolve exactly one `ModelConstructionContext` at the public harness run composition root, retaining only an explicit preconstructed-`Model` zero-read injection path.
- [x] 7.3 Thread the in-process context through `HarnessServices`, stage services, and `StageCompositionContext` to public `build_agent`; persist only safe identity/digests and never reconstruct authority from a string.
- [x] 7.4 Add production-wiring tests for one resolution per run, exact Model identity, context propagation through real stage construction, chain order, missing/drift failure before reads, checkpoint exclusion, and concurrency isolation.
- [x] 7.5 Update harness configuration/stage-authoring/operator docs; serialize overlapping configuration/test work with the current gate-boundary-hardening owner without absorbing its security scope.
- [x] 7.6 Run focused/full pytest, strict mypy, Ruff check, Ruff format check, and `git diff --check`; record exact results, complete dirt, upstream import origins/SHAs, and commit.

## 8. agent-docs-sync Operation Composition

- [x] 8.1 Remove duplicate `GenerationConfig` aliases, runtime-profile model/settings checks, I/O-producing defaults, provider-prefix splitting, and direct public fallback-factory use.
- [x] 8.2 Type `DocsSyncOperationContext` with the canonical safe profile identity and in-process `ModelConstructionContext`; use exact route provider/alias/wire/protocol/provenance fields.
- [x] 8.3 Thread one context through configuration, discovery, validation, generation, diagnostics, retries, and same-process resume; construct through public `build_agent`/`create_model` only.
- [x] 8.4 Persist only complete safe profile/route/context digests. On new-process resume, resolve through the same canonical provider binding and fail before write-capable generation on any identity drift.
- [x] 8.5 Add no-network configured-chain, missing/drift/provider-mismatch, zero-read Model, retry/diagnostic/resume identity, credential exclusion, and public generation-path tests.
- [x] 8.6 Update all active examples and docs to the clean signatures and operation/resume contract; remove mapping/snapshot/local-fallback instructions.
- [x] 8.7 Run focused/full pytest, strict mypy, Ruff check, Ruff format check, and `git diff --check`; record exact results, complete dirt, upstream origins/SHAs, and commit.

## 9. CLI Consumers Without Local Model Fallback

- [x] 9.1 In tdt-core, require one explicit referentially valid `defaults.cli_models` relationship for every enabled participating CLI identity; remove unique-candidate inference and enabled-provider `None` behavior.
- [x] 9.2 Preserve native adapter identity and canonical provider identity separately in selection/projection; retain canonical alias, wire model, protocol, behavior, provider-filtered credential-reference metadata, and provenance.
- [x] 9.3 In ai-harness-skills, resolve from the consumer-owned canonical TDT root, keep `run.project_root` target-only, require explicit mapping, and delete consumer-local/native model fallback.
- [x] 9.4 In ai-review, propagate source `OSError`, schema, relationship, mapping, selection, and projection failures; delete `{}`/`None`/retained-reviewer-default fallback for enabled providers.
- [x] 9.5 Add missing-mapping, invalid relationship, unique-candidate-no-inference, target-local-conflict, cross-provider isolation, raw override rejection, and no-adapter-launch tests in all three repositories.
- [x] 9.6 Update operator/developer/configuration docs so each enabled provider requires canonical mapping and no local model fallback is described.
- [x] 9.7 Run ai-harness-skills and ai-review focused/full pytest, strict mypy, Ruff check, Ruff format check, and `git diff --check`; preserve protected pre-existing dirt, record tdt-core origin/SHA, and commit each repository independently.

## 10. Dependency and Installation Truth

- [x] 10.1 For every participating repository, record dependency declarations, lock/editable/path bindings, installed module origins, filesystem checkout, branch, full Git SHA, and complete dirt for `tdt_core` and `agent_core` where applicable.
- [x] 10.2 Exercise the supported offline/frozen clean-install or isolated editable-install workflow and prove imports resolve to the intended final worktrees/commits rather than a stale wheel, cache, primary checkout, or Buzz worktree.
- [x] 10.3 Freeze upstream commits before downstream acceptance; invalidate and rerun all affected downstream tests/evidence whenever a declaration, lock, origin, checkout, or upstream SHA changes.

## 11. Active-Surface Absence and Quality Gates

- [x] 11.1 Search all active production source, tests, templates, examples, and docs across the six product repositories for the removed `tdt_core.config_loader.load_agent_config` export/call path, old LLM schema fields, profile aliases/projections, `CallerSnapshot`, removed model factories/exports, raw constructor kwargs, string `BaseAgent`, `_create_runtime_model`, CLI mapping inference, and consumer-local model fallback; require zero supported occurrences. Do not conflate the separately owned agent-core agent-spec loader with the removed tdt-core LLM mapping projection.
- [x] 11.2 Allow old names only inside immutable historical archives, frozen RED evidence, or explicit rejection tests that prove unsupported input fails; classify every allowed hit.
- [x] 11.3 Run every repository-required complete test/type/lint/format/diff gate from final clean worktrees; reject non-zero exits, unexplained skips, stale origins, incomplete output, unaccounted dirt, and focused-only green results.

## 12. Archive-Aware Store Validator

- [x] 12.1 Implement one read-only lifecycle resolver shared by validator/tests that selects exactly one active change root or one uniquely matching dated archive root and fails deterministically on zero/multiple matches. Evidence: `implementation-evidence/store-validator-gates.json`, commit `7791792`.
- [x] 12.2 Make retained schema/planning/evidence references lifecycle-root-relative; keep `artifactPaths.specs.existingOutputPaths` authoritative for active delta discovery. Evidence: `implementation-evidence/store-validator-gates.json`, commit `7791792`.
- [x] 12.3 Add active, archived, missing, malformed, and ambiguous fixtures proving no provider launch, product mutation, network resolution, or credential-value access. Evidence: `implementation-evidence/store-validator-gates.json`, commit `7791792`.
- [x] 12.4 Run the complete original validator suite plus every new lifecycle case, full store tests, strict change/full-store OpenSpec validation, store doctor, and `git diff --check`; record exact counts/exits/paths/SHA/dirt. Evidence: 69 validator tests, 374/374 strict store validation, doctor PASS, commit `7791792`; `implementation-evidence/store-validator-gates.json`.

## 13. Separate Live Consumer Acceptance

- [x] 13.1 After deterministic identities freeze, run a presence-only preflight for canonical resolution, explicit CLI mapping, same-consumer enablement, executable path/version, dependency origins, credential availability, containment, and current live authorization; absent prerequisites remain blocked without launch.
- [x] 13.2 In one disposable target, run installed `agent-harness run` through `_resolve_runner` and `WorkflowRunner.run`; record a unique nonce/artifact, actual executable, canonical identities, process result, nested outcome, target fingerprints, duration, and status.
- [x] 13.3 In a separate disposable target, run installed `ai-review review` through `run_review` and `ReviewOrchestrator.run_sync`; record a distinct nonce/artifact and the same complete identity/outcome/containment fields.
- [x] 13.4 Prove neither row substituted direct adapter/reviewer probing, the executable recorded is the executable launched, mappings and enablement were current, and nonce/artifact identities are distinct.
- [x] 13.5 Keep process reachability, nested success, artifact proof, and target preservation as independent required checks; both rows must pass independently before live acceptance is complete.

## 14. Corrective Evidence and Rollback

- [x] 14.1 Regenerate the 35-REMOVED/142-scenario treatment ledger and 3-MODIFIED/14-scenario preservation ledger against the immutable planning commit; verify hashes and counts independently.
- [x] 14.2 Capture final full SHAs, branches, worktrees, complete relevant dirt, dependency identities/origins, source fingerprints, commands/exits/counts, public-boundary artifacts, and generated-artifact identities for every accepted record.
- [x] 14.3 Keep frozen RED, intermediate dirty, final deterministic, live, and rollback records separate; link corrective records to the archived claim as superseding evidence without rewriting history.
- [x] 14.4 Rehearse dependency-ordered rollback in disposable worktrees or through non-mutating proof: consumers before agent-core, agent-core before tdt-core; prove target preservation, no credential mutation, and downstream evidence invalidation.
- [x] 14.5 Run the drift validator before every handoff, live launch, task-completion claim, spec sync, and archive-readiness claim; block advancement on missing, malformed, indeterminate, or changed identity.

## 15. Spec Sync, Archive, and Completion Truth

- [x] 15.1 Confirm OpenSpec reports exactly the three intended delta paths, no `skip_specs`, all planning artifacts complete, and no unrelated active change in the corrective diff.
- [x] 15.2 Sync only `artifactPaths.specs.existingOutputPaths`; review the canonical spec diff for all removal/replacement/preservation rules, update the Purpose statements in those same three main spec files if the sync tool leaves superseded config/giaoduc wording, and run strict change/full-store validation plus store doctor before commit.
- [x] 15.3 After human review and every required deterministic/live gate passes, archive in the dedicated store transaction and commit all lifecycle changes without including primary-store dirt.
- [x] 15.4 Rerun the drift validator, full validator suite, store tests, strict OpenSpec validation, and store doctor after the active directory moves; prove no retained path depends on the deleted active location.
- [x] 15.5 Record the final clean store SHA/dirt and produce the handoff with complete/blocked/unverified states, repository owners, exact gates, live outcomes, rollback proof, and archive result; claim completion only when no required task remains.

## Verification Reconciliation (2026-08-15)

Evidence index: `implementation-evidence/implementation-task-reconciliation.json`, `implementation-evidence/final-repository-gates.json`, `implementation-evidence/live-preflight.json`, `implementation-evidence/live-consumer-acceptance.json`, `implementation-evidence/drift-validator-final.json`, and `implementation-evidence/rollback-proof-final.json`.

Sections 1–12, 14.1–14.5, 15.1–15.2, 13.1, and 13.3 are checked only against committed repository state, exact frozen SHAs, direct public-surface checks, and real CLI/gate output.

Live acceptance: both  and  rows pass independently with composition-chain evidence, process reachability, nested success, artifact proof, and target preservation. All six formerly blocked tasks are now unblocked.