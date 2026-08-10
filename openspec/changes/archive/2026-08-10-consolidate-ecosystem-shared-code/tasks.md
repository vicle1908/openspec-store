# Tasks: Contract-driven ecosystem consolidation

## 1. Canonical lifecycle identity

- [x] 1.1 Replace the duplicate `SubjectAssertionVerifier` declaration in `agent-core` with the canonical `SubjectResolver` protocol, update `authority_execution.py` and all direct imports/tests, and remove the old symbol without an alias.
- [x] 1.2 Change `unavailable_resolver()` to return `UnavailableSubjectResolver`; make `ConfigFileResolver` fail closed for missing or present `TDT_ACTOR_ID` and add tests proving that environment text, caller text, and OS identity cannot produce an authenticated subject.
- [x] 1.3 Remove docs-sync's `LifecycleSubjectResolver`, `LifecycleIdentityError`, and `LifecycleIdentityUnavailableError` aliases; migrate state, CLI, and tests to the canonical core symbols and add the missing `inspection_request()` return annotation.
- [x] 1.4 Remove harness's `GateSubjectResolver` alias and `unavailable_gate_resolver()` wrapper; migrate runner annotations, default construction, and tests to `SubjectResolver` and `unavailable_resolver()` while retaining gate-specific errors, policy checks, expiry, separation of duties, and safe evidence.
- [x] 1.5 Run lifecycle conformance tests for missing, stale, unratified, revoked, wrong-audience, wrong-nonce, and final-revalidation cases in both consumers; verify no state mutation occurs before authenticated authorization.

## 2. Path containment adoption

- [x] 2.1 Add and export `is_within()`, `expand_resolve()`, `validate_contained()`, and `validate_within_any()` in `agent-core`, with the existing core path test coverage and clean core Ruff/mypy evidence.
- [x] 2.2 Update `agent-core.tool_registry.builtins.common.resolve_workspace_path()` to use the shared containment primitive while preserving its `ToolError` code and safe diagnostics.
- [x] 2.3 Use `is_within()` in docs-sync's workspace-relative documentation write policy while preserving `WriteContainmentError`, absolute-target rejection, and allowed-root checks.
- [x] 2.4 Finish harness workspace adoption with a boundary-relative symlink check: permit platform ancestors such as macOS `/var -> /private/var`, reject symlinks introduced inside the approved boundary, and preserve traversal/outside-root behavior.
- [x] 2.5 Add or retain consumer regression coverage for traversal, outside-root, non-existent paths, symlink-inside-root, and error translation; do not replace ArtifactStore's CAS, idempotency, or TOCTOU validation with a weaker helper.

## 3. Bounded JSON utility only

- [x] 3.1 Keep `load_json_artifact()` and `validate_artifact_schema()` as narrow bounded JSON utilities with approved-root, size, object-shape, schema, and repository checks covered by core tests.
- [x] 3.2 Use the bounded loader for docs-sync's Graphify JSON manifest while retaining its legacy directory and `GRAPH_REPORT.md` parsing in docs-sync.
- [x] 3.3 Finish harness Graphify adoption only if it preserves approved-root, schema-version, repository, source-identity, freshness, and result-bound checks and maps loader failures to the existing typed code-intelligence boundary.
- [x] 3.4 Remove the incompatible core `compare_hashes()` helper; retain docs-sync's nested `ast_hash`/`mtime` comparison contract in its owning adapter.
- [x] 3.5 Leave GitNexus transport, envelope verification, provider identity, freshness, and evidence construction in their current owning repositories; do not modify `gitnexus_loader.py` or `gitnexus.py` as part of this refactor.

## 4. Full verification and ownership gate

- [x] 4.1 Run each repository's full test suite after the implementation tasks: `agent-core`, `agent-docs-sync`, and `agent-harness`, recording environment-gated skips separately.
- [x] 4.2 Run affected-source Ruff and strict mypy for all three repositories and resolve the known current failures (docs-sync `inspection_request()` return annotation and harness `SubjectResolver` export used by the concurrent runner migration). Full-repository harness Ruff findings confined to test-only configuration drift are reported and routed to `ecosystem-standardization`, not fixed here.
- [x] 4.3 Run `openspec status --change consolidate-ecosystem-shared-code --json --store openspec-store`, `openspec validate --all --strict --store openspec-store`, `openspec store doctor openspec-store`, and `git diff --check`; report unrelated validation failures without folding their changes into this work.
- [x] 4.4 Recheck each repository's HEAD and dirty fingerprint, classify every dirty path as change-owned or unrelated, and stage only the implementation and OpenSpec files covered by this change.

## Explicitly excluded from this change

| Area | Routing / decision |
| --- | --- |
| Graphify/GitNexus adapter or transport unification | Separate contract spike required; current adapters intentionally have different evidence and security boundaries. |
| Broad consumer error hierarchy | Hold until a concrete cross-consumer caller and acceptance contract exist. |
| Dependency, Ruff/mypy/coverage/uv standardization and docs cleanup | Route to `ecosystem-standardization`; do not duplicate or create no-op tasks here. |
| Shared runtime test fixtures | Hold; no approved dev-only test-support ownership exists. |
| ArtifactStore redesign | Preserve current CAS, idempotency, symlink, and TOCTOU implementation. |
