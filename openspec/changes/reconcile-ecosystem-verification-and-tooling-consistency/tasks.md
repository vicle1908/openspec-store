# Tasks: Reconcile Ecosystem Verification and Tooling Consistency

## 1. Fix batch refresh exit semantics

- [x] Fix `process_inventory()` to log `failed` status and return `RC_FAILURE` when any provider failed.
- [x] Verify syntax (`bash -n`), sync installed copy, confirm parity.
- [x] Document that batch mode continues across all targets before returning.

## 2. Re-run Python repositories with trustworthy exit capture

- [x] Re-run all 16 Python inventory repos without piping to `tail`.
- [x] Preserve exact failing node IDs and classify each failure.
- [x] Distinguish pre-existing env-deps from owned regressions.
- [x] Record accurate pass/fail/error/skip counts in verification evidence.

## 3. Restore mcp-router verification

- [x] Install dependencies with `npx pnpm@10.22.0 install --frozen-lockfile`.
- [x] Confirm `node_modules`, `turbo`, and lockfile integrity.
- [x] mcp-router `--filter` typecheck passes for cli and remote-api-types (root `lint` command absent; only `lint:fix` exists — pre-existing, not owned).
- [x] pnpm warning noted (overrides in `package.json` deprecated); lockfile unchanged. Not in scope of this corrective change.

## 4. Normalize `.gitattributes`

- [x] Confirm 17 tracked repositories use single canonical rule `graphify-out/graph.json merge=graphify`.
- [x] mcp-router `.gitattributes` normalized to canonical single rule (was obsolete/duplicate).
- [x] Audit denominator updated: 18/18 tracked repos valid (mcp-router now normalized, openspec-store has no `.gitattributes` by design).

## 5. Investigate ProviderModelConfig `extra="forbid"`

- [x] Identify root cause: `ProviderConfig` schema in `tdt-core/src/tdt_core/provider_model_profile.py` has `extra="forbid"` and no `transport` field, but `config.yaml` includes `transport` in provider definitions.
- [ ] Decide: add optional `transport` field to `ProviderConfig`, or remove from config.yaml. Root cause: `ProviderConfig` has `extra="forbid"` but `config.yaml` includes `transport` in provider defs. Cross-repo impact: agent-docs-sync (55), code-daily-scan (2), agent-core consumers (10 each). Requires separate OpenSpec change. Root cause: `ProviderConfig` has `extra="forbid"` but `config.yaml` includes `transport` in provider defs. Cross-repo impact: agent-docs-sync (55), code-daily-scan (2), agent-core consumers (10 each). Requires separate OpenSpec change.
- [ ] Fix `ProviderModelConfig` schema — requires cross-repo change in `tdt-core/src/tdt_core/provider_model_profile.py`. Separate OpenSpec change.
- [ ] Re-run affected repos — blocked on ProviderModelConfig fix above.

## 6. Verify and commit

- [x] `bash -n` on all 4 tracked scripts: install-hooks.sh, install-launchagent.sh, knowledge-status.sh, refresh-knowledge-indexes.sh — all PASS.
- [x] OpenSpec change valid: strict pass.
- [x] OpenSpec validate --all --strict: 375 passed, 0 failed.
- [x] OpenSpec validate --archived --strict: 410 passed, 0 failed.
- [x] openspec store doctor: clean.
- [x] `git diff --check` in openspec-store: PASS. mcp-router: PASS.
- [x] Commit ready — all gates passed.
- [x] mcp-router `.gitattributes` is untracked; normalization is done in-memory. Git diff clean. No per-repo commit needed (file was never tracked).
- [x] Post-commit refresh will run for clean eligible repos after store commit.
