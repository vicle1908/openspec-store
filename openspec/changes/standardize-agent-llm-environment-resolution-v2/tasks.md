## 1. Ownership and Reproducible Baseline

- [x] 1.1 Record full 40-character HEADs, branches, worktree paths, repo-local Git identity, dirty-path inventories and SHA-256 fingerprints, Graphify/GitNexus freshness, and the imported module path for all six implementation repositories and the OpenSpec store. Evidence: `EVIDENCE_MANIFEST.md`
- [x] 1.2 Assign one writer per repository and create dedicated worktrees without modifying existing generated, untracked, credential, or concurrent OpenSpec state. Evidence: `EVIDENCE_MANIFEST.md` §5
- [x] 1.3 Reproduce and retain isolated failing probes for agent-core environment precedence, docs-sync projection disagreement, harness production model propagation, harness explicit-config error masking, ignored agent-core `env_file`, and literal default artifact-root expansion. Evidence: `EVIDENCE_MANIFEST.md` §3
- [x] 1.4 Capture a redacted inventory of current model/environment keys and compatibility aliases across the six participating repositories; record `prime-agent`, `claude-code-provider-adapter`, and `code-daily-scan` as explicit boundary cases. Evidence: `EVIDENCE_MANIFEST.md` §4

## 2. tdt-core Canonical Resolution Boundary

- [ ] 2.1 Add frozen resolved-profile, provider-route, environment-key metadata, credential-availability, and per-field provenance models with secret-safe serialization tests.
- [ ] 2.2 Add the packaged environment-key registry with owner, type, precedence, secret classification, consumer, canonical key, and alias status; reject duplicate ownership and incompatible aliases.
- [ ] 2.3 Export the documented environment loader from the public package API and make typed settings/profile resolution initialize the same root/profile/environment-file identity.
- [ ] 2.4 Implement supported explicit environment-file selection and tests proving the selected file is honored rather than replaced by `$TDT_HOME/.env`.
- [ ] 2.5 Extract one secure single-YAML-mapping reader with empty/missing behavior, malformed/non-mapping errors, redacted secret checks, and fresh-dict semantics.
- [ ] 2.6 Apply contained no-follow reads to standard global and agent configuration paths; reject `.`/`..`, unsafe hidden components, symlink escapes, object substitution, and unresolved path variables.
- [ ] 2.7 Add the source-preserving agent-overlay reader with default strict keys and an explicit owner policy for harness domain keys.
- [ ] 2.8 Implement canonical resolved-profile precedence: explicit override, consumer environment, shared model environment, agent YAML, global YAML, then defaults; invalid high-priority values fail closed.
- [ ] 2.9 Keep `load_agent_config()` as a compatibility projection over the same secure primitives and prove equivalent values agree with the typed profile.
- [ ] 2.10 Remove effective-profile caching; key any source cache by root, profile, explicit paths, key policy, and file fingerprints, and unify resolver/environment reset behavior.
- [ ] 2.11 Add machine-readable redacted diagnostics showing winners, shadowed source classes, provider metadata, environment-key names, and missing-key status without values.
- [ ] 2.12 Add full tdt-core unit, concurrency, root-change, file-change, environment-change, cache-policy-isolation, path-race, registry, and redaction test coverage.
- [ ] 2.13 Add a process-local, non-serializable credential-resolver capability that resolves validated credential references to protected values at the provider-construction boundary and cannot enter profiles, checkpoints, caches, or diagnostics.

## 3. agent-core Model Construction

- [ ] 3.1 Change public model constructors and internal helpers to consume an explicit resolved model/provider profile plus the tdt-core credential-resolver capability; keep explicit Model instances as no-resolution run overrides.
- [ ] 3.2 Update CLI runtime creation so an environment-selected primary and fallbacks cannot be replaced by agent-YAML values.
- [ ] 3.3 Update SDK `build_agent()` and every BaseAgent/model-string path to use the same resolved snapshot and fallback order as the CLI.
- [ ] 3.4 Remove YAML, dotenv, TDT config-path, and independent process-environment reads from the model layer, including the model-level credential fallback reader.
- [ ] 3.5 Honor the documented `load_settings(env_file=...)` behavior or remove the unsupported parameter with migration guidance; do not silently ignore it.
- [ ] 3.6 Derive model settings, thinking, provider routing, and fallback behavior once from the resolved profile and pass them at the supported agent-run boundary.
- [ ] 3.7 Update config and health diagnostics to show the actual provider-map route and effective model chain rather than legacy base-url fields.
- [ ] 3.8 Add CLI/SDK/BaseAgent parity tests for all precedence layers, explicit overrides, fallback ordering, invalid model identifiers, missing registered keys, and redacted errors.
- [ ] 3.9 Add a static source-conformance test proving agent-core model construction contains no configuration-file or dotenv read.

## 4. agent-docs-sync Consumer Composition

- [ ] 4.1 Store one immutable resolved agent profile in `DocsSyncConfig` and derive `model`, `settings`, provider, and behavior compatibility projections from it.
- [ ] 4.2 Restrict repository YAML to docs-sync domain fields and reject model, fallback, provider, behavior, legacy wrapper, and unknown sections with migration guidance.
- [ ] 4.3 Apply docs-sync environment keys through the canonical registry and remove consumer-local LLM precedence or dotenv logic.
- [ ] 4.4 Pass the same resolved profile through discovery, validation, generation, subagent, and SDK builder paths without resolving under a different consumer name.
- [ ] 4.5 Make malformed configuration and model/provider construction failures fail closed; do not downgrade them to an unconfigured single-model fallback.
- [ ] 4.6 Add contract tests proving the config shortcut, settings projection, generation profile, constructed chain, and diagnostic all agree for every precedence layer.
- [ ] 4.7 Preserve nested report, provider-error, exit-code, approval, and artifact truthfulness tests while replacing their configuration fixtures.

## 5. agent-harness Source-Preserved Composition

- [ ] 5.1 Replace the silent wrapped-file loader with the tdt-core secure mapping and overlay APIs; malformed, unreadable, non-mapping, and legacy-wrapped explicit files fail with actionable errors.
- [ ] 5.2 Compose canonical LLM/runtime fields with overlay-only gate, persistence, authority, validation, budget, and retention sections; prove global domain sections do not contribute.
- [ ] 5.3 Use one resolved profile for `runtime.model`, compatibility settings, model behavior, and diagnostics; reject invalid localized or malformed provider:model identifiers.
- [ ] 5.4 Propagate the effective model and model behavior through `HarnessServices.production_services()` and `for_stage()` to every agent-backed stage.
- [ ] 5.5 Resolve the default artifact root from the canonical root object instead of a literal environment placeholder and validate containment before constructing `ArtifactStore`.
- [ ] 5.6 Preserve explicit config-path behavior through both LLM and domain inputs while ensuring the standard agent path is not also read.
- [ ] 5.7 Add isolated-root tests for environment precedence, overlay policy, cache isolation, model propagation, explicit-path errors, default-root fallback, symlink escape, and no-write failure behavior.
- [ ] 5.8 Add a production graph test that constructs and executes at least one agent-backed stage with the resolved model instead of a manually injected test-only string.

## 6. CLI-Provider Consumers

- [ ] 6.1 Add the provider-neutral CLI profile projection and validation adapter in tdt-core without importing any consumer's domain types.
- [ ] 6.2 Convert `ai-harness-skills` executable, model-alias, effort, and invocation-limit selection to the provider-neutral profile while preserving its safe process runner and environment allowlists.
- [ ] 6.3 Add ai-harness diagnostics and tests for canonical precedence, unsupported provider fields, alias conflicts, missing native authentication, and absence of credential values.
- [ ] 6.4 Convert `ai-review` from direct `$TDT_HOME/.env` loading to the canonical environment authority and registry for participating fields.
- [ ] 6.5 Add per-reviewer provider-neutral executable, optional model alias, optional effort, and bounded limits for enabled Kimi, Claude, Codex, and Pi reviewers.
- [ ] 6.6 Preserve each ai-review CLI's native authentication and process boundary; add tests proving no credential is copied or substituted between reviewers.
- [ ] 6.7 Add ai-review effective-profile diagnostics, alias/precedence tests, invalid-field failures, and backwards-compatible enable/timeout alias migration tests.
- [ ] 6.8 Add inventory tests documenting why prime-agent, claude-code-provider-adapter, and deterministic code-daily-scan remain outside this migration and fail the inventory gate if they later gain an unregistered direct LLM path.

## 7. Migration, Documentation, and Main-Spec Coherence

- [ ] 7.1 Add a non-secret migration command or dry-run tool that reports repo-local LLM fields, legacy harness wrappers, unsupported keys, and target agent-overlay paths without modifying live files.
- [ ] 7.2 Update configuration and environment-key documentation in all six participating repositories from the generated registry and include redacted effective-config examples.
- [ ] 7.3 Update the OpenSpec main requirements through this change so fallback ownership, consumer composition, repo-local model rejection, harness overlay sourcing, explicit config paths, environment authority, and cache behavior are non-contradictory.
- [ ] 7.4 Record exact supersession mapping from both untracked drafts into this v2 change; preserve their dirty trees until the owner authorizes cleanup and do not sync/archive duplicated deltas twice.
- [ ] 7.5 Update repository spec indexes and cross-repo compatibility documentation with direct-consumer, CLI-provider, infrastructure, and excluded-runtime classifications.

## 8. Deterministic Hard Gates

- [ ] 8.1 Run the complete tdt-core package test suite at its exact committed SHA with isolated writable caches; record pass/skip/fail counts and imported module path.
- [ ] 8.2 Run the complete agent-core package test suite at its exact committed SHA with isolated writable caches; record pass/skip/fail counts and imported module path.
- [ ] 8.3 Run the complete agent-docs-sync package test suite at its exact committed SHA with isolated writable caches; record pass/skip/fail counts and imported module path.
- [ ] 8.4 Run the complete agent-harness package test suite at its exact committed SHA with isolated writable caches; record pass/skip/fail counts and imported module path.
- [ ] 8.5 Run the complete ai-harness-skills and ai-review package suites at their exact committed SHAs and record pass/skip/fail counts.
- [ ] 8.6 Run each repository's full Ruff and strict mypy gates, plus package/build validation required by that repository; scoped module passes SHALL NOT substitute for full package gates.
- [ ] 8.7 Run cross-repository contract fixtures covering every precedence layer, source provenance, cache/root/file/environment changes, model-chain parity, harness propagation, CLI-provider isolation, and redaction.
- [ ] 8.8 Run static audits for direct dotenv/YAML model reads, undeclared LLM environment keys, literal secrets, unsafe TDT paths, legacy harness paths, repo-local LLM fields, and private model imports; retain searched roots and patterns.
- [ ] 8.9 Reconfirm current Graphify and GitNexus freshness; query only fresh indexes and explicitly attribute direct-source fallback where indexes are stale.
- [ ] 8.10 Run strict validation for this change and `openspec validate --all --strict --no-interactive`; attribute any unrelated full-store failure separately.
- [ ] 8.11 Verify the implementation diff against every task, capture a credential-safe evidence manifest, and complete an independent fresh-frame review before any archive or integration claim.
- [ ] 8.12 Run a downstream `code-daily-scan` import/config smoke probe against the integrated agent-core and tdt-core revisions; verify deterministic Phase 3 behavior remains non-LLM and configuration still resolves.
- [ ] 8.13 Run OpenSpec store doctor against the exact integration checkout and require healthy root/metadata resolution without changing the registered default checkout.

## 9. Live LLM and Operational Hard Gates

- [ ] 9.1 Preflight the configured provider routes and registered environment-key availability without printing values; record each provider/model as reachable, unavailable, or blocked.
- [ ] 9.2 Run real agent-core CLI prompts through valid configured Anthropic Messages, OpenAI Chat Completions, and OpenAI Responses model identifiers; require successful nested completion and non-zero token usage, not construction alone.
- [ ] 9.3 Run a real docs-sync full generation operation in a disposable clean target; separately record process exit, nested report completion, provider error, compliance, generated artifacts, approval state, and original-target preservation.
- [ ] 9.4 Run a real agent-backed harness stage from production service composition; verify the propagated model, stage completion, token usage, bounded artifact location, and no source-target mutation.
- [ ] 9.5 Run real ai-harness Claude and Codex adapter smoke operations and enabled ai-review reviewer smoke operations where native authentication is available; report prerequisite-aware pass, skip, or provider failure per adapter.
- [ ] 9.6 Repeat one live path with an intentionally unavailable registered credential key and verify fail-closed redacted diagnostics with no fallback to another provider credential.

## 10. Rollback and Integration

- [ ] 10.1 Rehearse per-repository rollback from the implementation commits in disposable worktrees and verify generated fixtures/artifacts are removed while pre-existing dirty and target files remain byte-identical.
- [ ] 10.2 Commit each repository slice with the repository-configured human `Co-authored-by` and `Signed-off-by` trailers, verify the trailers, and record full SHAs without exposing credentials.
- [ ] 10.3 Integrate in dependency order: tdt-core, agent-core, agent-docs-sync and agent-harness, then ai-harness-skills and ai-review; rerun downstream contracts after each dependency move.
- [ ] 10.4 Rerun deterministic and live acceptance against the integrated SHAs and update the evidence manifest with exact commands, exit codes, counts, dirty inventories, and rollback results.
- [ ] 10.5 Mark the v2 change implementation-complete only after all applicable hard gates pass; any provider-prerequisite skip remains explicitly unresolved unless the requirement permits that environment to omit the provider.
- [ ] 10.6 Sync and archive only the v2 change after implementation verification, then perform separately authorized cleanup of the superseded untracked drafts without reapplying already synchronized requirements.
