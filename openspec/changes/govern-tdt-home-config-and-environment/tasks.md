# Tasks

## 1. Baseline and safety evidence

- [ ] 1.1 Create one feature worktree per affected repository; record branch, clean baseline, nearest `AGENTS.md`, dependency metadata, and exact verification commands.
- [ ] 1.2 Run GitNexus impact analysis for every symbol to be edited and stop for approval on any HIGH or CRITICAL result.
- [ ] 1.3 Add a redacted inventory test fixture representing the live legacy layout: duplicate scheduler config, literal DSN, broken credential symlink, logs, databases, schedules, and mixed permissions.
- [ ] 1.4 Capture a value-free live baseline manifest (path class, mode, owner, link status, and hashes only) and verify no secret values appear in the artifact.

## 2. tdt-core provider contract (RED)

- [ ] 2.1 Add failing tests that preserve every baseline behavior exactly: selected `.env` is read through python-dotenv for set/unset/empty/tilde roots, absent optional files do not raise, and no import-time root snapshot is used.
- [ ] 2.2 Add a failing precedence matrix covering home/local file present and absent, unset/development/production profiles, process collisions, trusted process-only profile selection, unknown-profile failure, repeated/concurrent calls, failed-load retry, and exact isolation restoration.
- [ ] 2.3 Add failing tests for namespace and filename validation (including extensions/fixed hidden files), absolute-root containment, no-follow behavior, effective-access creation, and concurrent directory creation.
- [ ] 2.4 Add failing doctor tests for duplicate logical settings, literal secrets, permission drift, broken/escaping symlinks, malformed files, and foreign ownership.
- [ ] 2.5 Seed canary secrets and assert they never occur in outputs produced by the governed loader, config parser, doctor, source audit, or migration: stdout, stderr, JSON, their logs, their exceptions, and their manifests.
- [ ] 2.6 Add failing migration tests for dry-run immutability, lock contention, atomic apply, mid-transaction failure, rollback, idempotent rerun, and hash/mode preservation.

## 3. tdt-core implementation (GREEN)

- [ ] 3.1 Implement dynamic config, credentials, schedules, logs, state, and runtime path helpers backed only by `tdt_root()`.
- [ ] 3.2 Implement backward-compatible profiles, process-only profile selection, thread-safe one-time initialization, lock-scoped test isolation, and source provenance while preserving all six baseline scenarios.
- [ ] 3.3 Implement recursive typed config loading, full-scalar `${VAR_NAME}` references, alias normalization, the committed per-key ownership/migration table, deterministic equal/unequal duplicate handling, DSN conflict gates, and redacted errors.
- [ ] 3.4 Add base Typer/PyYAML dependencies, create `tdt_core.cli`, register the `tdt` console script, and verify `tdt --help` from an installed base wheel without scheduler extras.
- [ ] 3.5 Implement workspace-independent `tdt config doctor` text/JSON/strict modes and its stable finding schema.
- [ ] 3.6 Implement `tdt config source-audit --workspace-root` and a versioned manifest enumerating every classified repository/path family/exception; prohibit symlink traversal and exclude secrets, dependencies, caches, generated/runtime artifacts, databases, and logs.
- [ ] 3.7 Implement the path map plus `migrate --dry-run`, durable journal preparation/staging, and quiescence preflight without switching active paths.
- [ ] 3.8 Implement the fixed journal state machine and per-path intent/replace/fsync/completed protocol, reverse rollback oracle, `recover`, and idempotent rerun; test termination at every durability boundary.
- [ ] 3.9 Document layout/access principals, profile trust source, reference grammar, ownership/path maps, doctor/source-audit schemas, quiescence, recovery, compatibility, and rollback.
- [ ] 3.10 Verify `tdt-core` with full pytest, Ruff, format, strict mypy, and CLI tests.
- [ ] 3.11 Bump to `0.3.0`; build provider artifacts; materialize the complete locked runtime/transitive wheel closure into a fresh wheelhouse; record SHA-256 inventory; then install with empty cache, `--no-index --find-links`, no checkout, and no `PYTHONPATH`.
- [ ] 3.12 Probe documented Nexus DNS, credentials presence, and release authority without exposing secrets; publish/install from Nexus only if all pass, otherwise record the conditional release blocker without blocking local wheelhouse consumer verification.

## 4. Direct agent consumers

- [ ] 4.1 **REQUIRES: task 3.11.** In `agent-core`, replace import-time/private root and scratch paths with provider helpers; add runtime re-evaluation and containment tests; run full gates.
- [ ] 4.2 **REQUIRES: task 3.11.** In `agent-docs-sync`, add direct `tdt-core>=0.3,<0.4`, regenerate its lock, replace duplicate paths, add alternate-root tests, and run full gates.
- [ ] 4.3 **REQUIRES: task 3.11.** In `agent-harness`, replace private root resolution while preserving its authority boundary; run full gates.
- [ ] 4.4 **REQUIRES: task 3.11.** Set direct importer floors to `tdt-core>=0.3,<0.4`, regenerate lockfiles, build consumer wheels, and clean-install against the local wheelhouse with editable source mappings and sibling paths excluded.

## 5. Supporting TDT consumers

- [ ] 5.1 **REQUIRES: task 3.11.** In `tdt-observability`, align Python metadata, add the provider floor, migrate paths, and run compatibility/full gates.
- [ ] 5.2 **REQUIRES: task 3.11.** In `tdt-sheets`, add the provider floor, migrate credential fallback, and run link/redaction/full gates.
- [ ] 5.3 **REQUIRES: task 3.11 or the approved adapter decision.** In `ai-harness-skills`, use the provider or implement the contract-vector compatibility adapter while preserving standalone isolation; run conformance/full gates.
- [ ] 5.4 **REQUIRES: task 3.11.** In separate worktrees, add RED tests then migrate `browser-cli` and `code-daily-scan`; run each independently.
- [ ] 5.5 **REQUIRES: task 3.11.** In separate worktrees, add RED tests then migrate `jira-daily-reports` and `jira-kanban-from-spreadsheet`; run each independently.
- [ ] 5.6 **REQUIRES: task 3.11.** In separate worktrees, add RED tests then migrate `jira-skill` and `webhook-receiver`; hand agent-core Compose edits to its owning worktree; run full gates.
- [ ] 5.7 **REQUIRES: task 3.11 for any promotion.** Classify and smoke-test `ai-review` and `jira-epic-report`; if source audit finds an executable bypass, promote it to a separately owned provider-gated source-migration worktree.
- [ ] 5.8 Run full pytest, Ruff, format, strict mypy, and local-wheelhouse clean-install gates for every changed supporting repository.

## 6. Persistent governance

- [ ] 6.1 Add an AST/config-literal cross-repo check that rejects executable `Path.home()/".tdt"`, literal `~/.tdt` defaults (including values passed through config objects), and private `TDT_HOME` parsing outside canonical/approved compatibility sites while distinguishing docs/messages.
- [ ] 6.2 Add source-audit tests for explicit workspace-root discovery, missing registered repositories, owner/reason/expiry validation, expired exceptions, and installed-wheel execution outside a workspace; runtime doctor SHALL remain independent of repository presence.
- [ ] 6.3 Update `SPEC_INDEX.md` and relevant operator/security docs in each changed repository to map the `tdt-env-loader-tdt-home` capability to its modules.
- [ ] 6.4 Run GitNexus `detect_changes` in every changed repository and investigate unexpected flows before commit.

## 7. Synthetic migration verification

- [ ] 7.1 Create a temporary HOME/TDT_HOME legacy tree from the redacted fixture; record hashes and modes.
- [ ] 7.2 Run migration dry-run and prove zero filesystem changes.
- [ ] 7.3 Apply migration, run strict doctor, verify the canonical layout and secret references, and execute consumer smoke commands against the alternate root.
- [ ] 7.4 Roll back and prove original hashes, links, and modes are restored; repeat the full synthetic cycle a second time from a fresh fixture.
- [ ] 7.5 Rehearse release rollback in clean environments: install pre-change consumer wheels/metadata, verify legacy behavior with the locally verified `tdt-core` 0.3 compatibility artifact still available, then reinstall migrated consumers and verify the provider path again.
- [ ] 7.6 Run old and migrated consumers concurrently only in supported compatibility modes against one synthetic tree; verify the path map prevents stale reads/writes.

## 8. Provider-first rollout

- [ ] 8.1 **REQUIRES: Sections 1–7 complete and explicit rollout approval.** Deploy provider-first in dependency order and verify active package versions without switching live paths.
- [ ] 8.2 Deploy/restart downstream consumers in dependency order; verify clean imports, legacy-path compatibility, and exact active versions.
- [ ] 8.3 Inventory every production launchd/Compose process and require inherited `TDT_ENV_PROFILE=production`; fail rollout evidence for unset/development production processes.
- [ ] 8.4 Execute the reverse consumer-first dependency/import rollback rehearsal against deployed artifacts while retaining the provider compatibility artifact, then restore the migrated rollout.

## 9. Live operator migration

- [ ] 9.1 **REQUIRES: Section 8 complete and explicit live-migration approval.** Inventory runtime principals/writers, run live doctor/dry-run, and present redacted access, config/DSN conflicts, quiescence, and ambiguous credential choices.
- [ ] 9.2 Resolve every per-key/config and credential choice; after quiescence preflight passes, create/fsync the journal and backup copies/manifest without switching active paths.
- [ ] 9.3 Quiesce verified writers, apply the journaled migration, simulate/recover one interrupted boundary on a live-copy fixture, then run strict doctor twice.
- [ ] 9.4 Restart and smoke-test Compose, launchd, observability, all consumers, and credential discovery; on failure execute journaled rollback and retain evidence.

## 10. Final verification and archive

- [ ] 10.1 Re-run full tests, Ruff, formatting, and strict mypy in every changed repository from clean worktrees.
- [ ] 10.2 Re-run source audit and strict doctor; require zero ungoverned bypasses and zero expired/invalid exceptions, literal-secret findings, broken links, access errors, or non-terminal journals.
- [ ] 10.3 Run focused and full strict OpenSpec validation and the semantic second-pass review.
- [ ] 10.4 Update Graphify indexes where present and commit each owning repository independently.
- [ ] 10.5 After every marked task has real evidence, archive the change, revalidate the store, and commit the store.
