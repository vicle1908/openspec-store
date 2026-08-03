# Tasks

## 1. Baseline and safety evidence

- [ ] 1.1 Create one feature worktree per affected repository; record branch, clean baseline, nearest `AGENTS.md`, dependency metadata, and exact verification commands.
- [ ] 1.2 Run GitNexus impact analysis for every symbol to be edited and stop for approval on any HIGH or CRITICAL result.
- [ ] 1.3 Add a redacted inventory test fixture representing the live legacy layout: duplicate scheduler config, literal DSN, broken credential symlink, logs, databases, schedules, and mixed permissions.
- [ ] 1.4 Capture a value-free live baseline manifest (path class, mode, owner, link status, and hashes only) and verify no secret values appear in the artifact.

## 2. tdt-core provider contract (RED)

- [ ] 2.1 Add failing tests that preserve every baseline behavior exactly: selected `.env` is read through python-dotenv for set/unset/empty/tilde roots, absent optional files do not raise, and no import-time root snapshot is used.
- [ ] 2.2 Add failing tests for development and production precedence profiles, unknown-profile rejection, idempotency, and isolated test reset.
- [ ] 2.3 Add failing tests for typed path helpers, path containment, private creation modes, and concurrent directory creation.
- [ ] 2.4 Add failing doctor tests for duplicate logical settings, literal secrets, permission drift, broken/escaping symlinks, malformed files, and foreign ownership.
- [ ] 2.5 Seed canary secrets and assert they never occur in outputs produced by the governed loader, config parser, doctor, source audit, or migration: stdout, stderr, JSON, their logs, their exceptions, and their manifests.
- [ ] 2.6 Add failing migration tests for dry-run immutability, lock contention, atomic apply, mid-transaction failure, rollback, idempotent rerun, and hash/mode preservation.

## 3. tdt-core implementation (GREEN)

- [ ] 3.1 Implement dynamic config, credentials, schedules, logs, state, and runtime path helpers backed only by `tdt_root()`.
- [ ] 3.2 Implement explicit environment profiles and source-provenance reporting while preserving all six existing loader scenarios.
- [ ] 3.3 Implement typed shared-config loading, environment-reference resolution, duplicate ownership detection, and redacted validation errors.
- [ ] 3.4 Implement workspace-independent `tdt config doctor` text/JSON/strict modes and separate `tdt config source-audit --workspace-root` modes with a versioned cross-repo conformance manifest.
- [ ] 3.5 Implement `tdt config migrate --dry-run|--apply|--rollback` with locking, backup manifest, temporary files, fsync, atomic replace, and no source deletion.
- [ ] 3.6 Document the canonical layout, precedence, secret-reference syntax, profile selection, doctor reason codes, migration, and rollback.
- [ ] 3.7 Verify `tdt-core` with `uv run pytest`, `uv run ruff check src tests`, `uv run ruff format --check src tests`, and `uv run mypy src/tdt_core --strict`.
- [ ] 3.8 Bump `tdt-core` to `0.3.0`, build wheel/sdist, inspect metadata, publish to the configured internal distribution channel, and install by version into a clean environment with no sibling source path; if no channel or release authority exists, stop before consumer migration.

## 4. Direct agent consumers

- [ ] 4.1 In `agent-core`, replace import-time/private root and scratch paths with provider helpers; add runtime re-evaluation and containment tests; run its full pytest, Ruff, format, and strict mypy gates.
- [ ] 4.2 In `agent-docs-sync`, replace duplicate state and overrides paths with provider helpers; add alternate-`TDT_HOME` tests; run its full pytest, Ruff, format, and strict mypy gates.
- [ ] 4.3 In `agent-harness`, replace private root resolution in config and artifact storage; preserve the authority boundary that confines writes below its artifact root; run its full pytest, Ruff, format, and strict mypy gates.
- [ ] 4.4 Set each direct consumer runtime floor to `tdt-core>=0.3,<0.4`, regenerate lockfiles, then build/install provider and consumer wheels from the configured distribution channel and verify imports and smoke commands without editable sibling paths.

## 5. Supporting TDT consumers

- [ ] 5.1 In `tdt-observability`, raise `requires-python` and mypy/runtime targets to `>=3.14,<3.15`, add `tdt-core>=0.3,<0.4`, regenerate the lock, document the breaking floor, migrate PID/config/database/log-source/log paths, test alternate roots/no snapshots, and assert its metadata is rejected on Python 3.12/3.13.
- [ ] 5.2 In `tdt-sheets`, add `tdt-core>=0.3,<0.4`, regenerate the lock, resolve the fallback credential through `credentials/` with the legacy compatibility link, and test missing/broken/valid link behavior without exposing credential content.
- [ ] 5.3 In `ai-harness-skills`, add conformance tests for the shared root semantics while preserving standalone `$TDT_HOME/ai-harness` isolation; adopt the provider only if dependency review confirms no prohibited runtime coupling.
- [ ] 5.4 Run full pytest, Ruff, format, strict mypy, and clean-install gates for every changed supporting repository.

## 6. Persistent governance

- [ ] 6.1 Add an AST-based cross-repo check that rejects direct `Path.home()/".tdt"`, literal `~/.tdt`, and private `TDT_HOME` parsing outside approved provider/fallback sites.
- [ ] 6.2 Add source-audit tests for explicit workspace-root discovery, missing registered repositories, owner/reason/expiry validation, expired exceptions, and installed-wheel execution outside a workspace; runtime doctor SHALL remain independent of repository presence.
- [ ] 6.3 Update `SPEC_INDEX.md` and relevant operator/security docs in each changed repository to map the `tdt-env-loader-tdt-home` capability to its modules.
- [ ] 6.4 Run GitNexus `detect_changes` in every changed repository and investigate unexpected flows before commit.

## 7. Synthetic migration verification

- [ ] 7.1 Create a temporary HOME/TDT_HOME legacy tree from the redacted fixture; record hashes and modes.
- [ ] 7.2 Run migration dry-run and prove zero filesystem changes.
- [ ] 7.3 Apply migration, run strict doctor, verify the canonical layout and secret references, and execute consumer smoke commands against the alternate root.
- [ ] 7.4 Roll back and prove original hashes, links, and modes are restored; repeat the full synthetic cycle a second time from a fresh fixture.
- [ ] 7.5 Rehearse release rollback in clean environments: install pre-change consumer wheels/metadata, verify legacy behavior with `tdt-core` 0.3 compatibility exports still present, then reinstall migrated consumers and verify the provider path again.

## 8. Live operator migration

- [ ] 8.1 **REQUIRES: Sections 1–7 complete and explicit implementation approval.** Run live doctor and migration dry-run; present redacted findings and any ambiguous credential source for operator selection.
- [ ] 8.2 Create the timestamped live backup manifest, verify it contains no values, and apply the migration without deleting legacy sources.
- [ ] 8.3 Run strict doctor twice, then smoke-test scheduler settings, agent-core settings, docs-sync state, harness config/artifacts, observability stores, and Sheets credential discovery.
- [ ] 8.4 Verify launchd/scheduled processes after restart where applicable; if any check fails, execute rollback and retain evidence.

## 9. Final verification and rollout

- [ ] 9.1 Re-run full tests, Ruff, formatting, and strict mypy in every changed repository from clean worktrees.
- [ ] 9.2 Re-run the AST conformance audit and strict doctor; require zero unexpired bypasses, literal secret findings, broken links, and permission errors.
- [ ] 9.3 Run `openspec validate govern-tdt-home-config-and-environment --strict` and `openspec validate --strict --all`.
- [ ] 9.4 Update Graphify indexes where present, commit each owning repository independently, and execute—not merely record—the provider-first rollout and consumer-first dependency/import rollback rehearsal.
- [ ] 9.5 Mark tasks complete only with real command output, perform the semantic second-pass review, archive the change, validate the store again, and commit the store.