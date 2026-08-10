## 1. Runtime configuration boundary

- [ ] 1.1 Add regression coverage for repository-root configuration with an omitted model, explicit `runtime.model`, local iteration/timeout overrides, and `DOCS_SYNC_*` environment precedence against a synthetic `TDT_HOME`.
- [ ] 1.2 Verify the docs-sync consumer imports only the public `agent_core.sdk` settings/model facade and preserves the TDT provider/credential ownership boundary.
- [ ] 1.3 Implement or reconcile the runtime profile merge so effective model, fallback IDs, max iterations, and timeout are the values actually passed to generation.

## 2. Provider and generation behavior

- [ ] 2.1 Add model-resolution tests for ordered fallback construction, constructible primary-only degradation when a fallback credential is absent, and all-route failure without secret values in diagnostics.
- [ ] 2.2 Implement or reconcile generation-agent fallback composition through the SDK factory, including explicit model overrides and redacted logged failures.
- [ ] 2.3 Add generation-result tests covering completed output, max-iterations/timeout/provider failure, approval-needed state, iteration counts, and zero generated updates on incomplete results.
- [ ] 2.4 Ensure the full and canonical workflows preserve generation completion, reason, error, iterations, approval, and write-status fields into the final report.

## 3. CLI and documentation contract

- [ ] 3.1 Normalize nested workflow reports before human-readable and JSON output, with legacy-shape compatibility coverage.
- [ ] 3.2 Select CLI exit codes from the normalized report: execution failure versus documentation/generation non-compliance versus success; add regression tests for each class.
- [ ] 3.3 Update `config.yaml`, `docs/configuration.md`, `docs/cli.md`, README-facing runtime guidance, and the canonical `.agents/skills/doc-sync/SKILL.md` with TDT precedence, supported overrides, secret boundary, fallback warnings, runtime limits, and exit codes.
- [ ] 3.4 Preserve the untracked generic `doc-sync/` scaffold and unrelated Graphify/GitNexus generated state; record the exact dirty inventory before verification.

## 4. Verification and handoff

- [ ] 4.1 Run the full docs-sync pytest suite, Ruff, strict mypy, formatter/diff checks, and relevant OpenSpec validation with isolated writable caches where needed.
- [ ] 4.2 Run a synthetic `TDT_HOME` provider/model construction matrix without printing credential values and retain redacted route/type evidence.
- [ ] 4.3 Run the real LLM-backed `docs-sync sync --full` against a disposable fixture using the committed default TDT resolution; record source HEAD, dirty fingerprint, report counts, generation reason/iterations, exit code, and fixture path.
- [ ] 4.4 Perform a fresh diff/impact review, reconcile every task with implementation/evidence, and publish the integration state, remaining credential warning, rollback boundary, and exact follow-up before archive.
