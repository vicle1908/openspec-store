# Tasks

## 1. Baseline and safety evidence

- [ ] 1.1 Create one feature worktree per affected repository; record branch, clean baseline, nearest `AGENTS.md`, exact runtime/import, build/package, release/deployment, editable-only, and rollback edges, dependency metadata, and exact verification commands. Commit a deterministic graph checker; prove `tdt-core` has no consumer dependency and all five graphs are acyclic before task 3.11 and after every consumer metadata change.
- [ ] 1.2 Run GitNexus impact analysis for every symbol to be edited and stop for approval on any HIGH or CRITICAL result.
- [ ] 1.3 Add a redacted inventory test fixture representing the live legacy layout: duplicate scheduler config, literal DSN, broken credential symlink, logs, databases, schedules, and mixed permissions.
- [ ] 1.4 Capture a value-free live baseline manifest (path class, mode, owner, link status, and hashes only) and verify no secret values appear in the artifact.

## 2. tdt-core provider contract (RED)

- [ ] 2.1 Add failing tests that preserve every baseline behavior exactly: selected `.env` is read through python-dotenv for set/unset/empty/tilde roots, absent optional files do not raise, and no import-time root snapshot is used.
- [ ] 2.2 Add a failing precedence matrix covering home/local file present and absent, unset/development/production profiles, process collisions, trusted process-only profile selection, unknown-profile failure, repeated/concurrent calls, failed-load retry, and exact isolation restoration.
- [ ] 2.3 Add failing tests for namespace and filename validation (including extensions/fixed hidden files), absolute-root containment, existing-root anchoring, secure first-run root bootstrap from the verified default-home or explicit approved parent anchor, anchor/ancestor replacement, no-follow behavior, effective-access creation, and concurrent directory creation.
- [ ] 2.4 Add failing doctor tests for duplicate logical settings, literal secrets, permission drift, broken/escaping symlinks, malformed files, and foreign ownership.
- [ ] 2.5 Seed canary secrets and assert they never occur in outputs produced by the governed loader, config parser, doctor, source audit, or migration: stdout, stderr, JSON, their logs, their exceptions, and their manifests.
- [ ] 2.6 Add failing migration tests for dry-run immutability, lock contention, atomic apply, mid-transaction failure, rollback, idempotent rerun, and hash/mode preservation.
- [ ] 2.7 Reproduce every fail-closed review blocker as a minimal adversarial test before further provider edits: non-string secret values; credential mode/owner/principal access; root-symlink replacement; descendant symlink and hard-link races; journal traversal/schema/root/plan/generation/hash-chain tampering; backup type/link-count/digest tampering; lock-before-read recovery; post-switch verifier failure; mandatory packaged manifest failure; alias-aware AST and unrelated `.get`; exception validation without scan findings; governed scheduler reads; runtime/package version agreement; and complete schema fields.
- [ ] 2.8 Add a positive target-platform capability matrix test on the supported macOS/Python build: require `dir_fd` support for open/mkdir/rename/unlink/stat/chmod/readlink/symlink, `O_NOFOLLOW|O_NOFOLLOW_ANY|O_DIRECTORY|O_CLOEXEC`, descriptor-relative create/rename/link/unlink behavior, directory `fsync`, and `F_FULLFSYNC` journal barriers; record results value-free. Also test safe component rejection and fail mutation closed when a required baseline primitive is unavailable. Tests SHALL forbid pathname-based `Path.resolve`, `rglob`, `shutil.copy*`, `symlink_to`, `replace`, and arbitrary journal paths inside mutation/recovery.

## 3. tdt-core implementation (GREEN)

- [ ] 3.1 Implement dynamic config, credentials, schedules, logs, state, and runtime path helpers backed only by `tdt_root()`, plus a reusable descriptor-relative filesystem kernel that anchors existing root identity or bootstraps a missing root only from the verified default-home/explicit approved parent anchor, walks validated components no-follow, creates/opens/renames/unlinks through retained descriptors, enforces regular/single-link policies, and performs file/parent fsync plus post-open identity/digest checks.
- [ ] 3.2 Implement backward-compatible profiles, process-only profile selection, thread-safe one-time initialization, lock-scoped test isolation, and source provenance while preserving all six baseline scenarios.
- [ ] 3.3 Implement recursive typed config loading that classifies secret-shaped keys before accepting any scalar/container type, full-scalar `${VAR_NAME}` references, alias normalization, the complete scheduler ownership/migration table (including app name/version and defaults), deterministic normalized duplicate handling, DSN conflict gates, default provenance, redacted errors, and scheduler consumption through this governed parser.
- [ ] 3.4 Add base Typer/PyYAML dependencies, create `tdt_core.cli`, register the `tdt` console script, and verify `tdt --help` from an installed base wheel without scheduler extras.
- [ ] 3.5 Implement workspace-independent `tdt config doctor` text/JSON/strict modes on the descriptor kernel. It SHALL validate credential type/link-count/mode/owner, prove only the current host principal directly, consume typed external principal attestations, keep one stable root descriptor throughout traversal, and never claim access for an unmapped principal.
- [ ] 3.6 Implement `tdt config source-audit --workspace-root` with mandatory `importlib.resources` provider registry/rule data and registered repository-owned concrete manifests; validate both layers, the exact closed-world fifteen-participant inventory/identity markers, independent exceptions, scope/shadowing-aware AST, module-snapshot and sink-aware literal rules, bounded strict-UTF-8 Python/YAML/TOML/plist/shell parsing, value-free findings with lines, and all exclusions. Provider release tests use synthetic concrete manifests; real workspace audit remains operationally unhealthy until every participant commits its manifest. Operational failures always exit non-zero; strict mode additionally fails on policy findings.
- [ ] 3.7 Implement and test strict schemas for consumer path manifests, deployment/principal manifests, writer/quiescence adapters, verifier adapters, macOS metadata adapters, immutable migration plans, attestations, journal headers/records, backup metadata, and state transitions. Reject placeholders, wildcards, shell strings, arbitrary executable paths, unsafe relative components, unknown adapters/versions/fields, and incomplete ownership. Detect ACL/xattr/flags and block plans when exact restoration lacks a tested adapter.
- [ ] 3.8 Implement a synthetic-plan compiler and descriptor-relative migration/recovery engine against test manifests only: canonical JSON/digest, lock-before-plan/journal read, UUID-only generation selection, root/plan/generation binding, private single-linked plan/journal/backup/staging files, hash-chained records, source identity recheck, state-specific recovery, durable reverse restoration, typed verifier callbacks, and idempotent terminal states. Do not embed guessed consumer paths or runtime-writer PID files.
- [ ] 3.9 Document layout/access principals, profile trust source, reference grammar, ownership/path maps, doctor/source-audit schemas, quiescence, recovery, compatibility, and rollback.
- [ ] 3.10 Verify `tdt-core` with every task 2 adversarial test, full pytest, Ruff, format, strict mypy, CLI tests, added-lines secret/security scan, and a fresh fail-closed independent review whose security and logic lists are empty.
- [ ] 3.11 **REQUIRES: dependency graph checker green and task 3.10 approved.** Bump package metadata and `tdt_core.__version__` to `0.3.0`; build provider artifacts from the reviewed commit; inspect mandatory provider registry/rule package data; materialize the complete locked runtime/transitive wheel closure into a fresh wheelhouse; record SHA-256 inventory; then install with empty cache, `--no-index --find-links`, no checkout, and no `PYTHONPATH`. Require distribution/runtime version equality, `tdt --help` without scheduler extras, and installed-wheel doctor, missing/invalid concrete-manifest failure, synthetic concrete-manifest source audit, plan-schema, and synthetic recovery smokes outside a workspace.
- [ ] 3.12 Probe documented Nexus DNS, credentials presence, and release authority without exposing secrets; publish/install from Nexus only if all pass, otherwise record the conditional release blocker without blocking local wheelhouse consumer verification.

## 4. Direct agent consumers

- [ ] 4.1 **REQUIRES: task 3.11.** In `agent-core`, replace import-time/private root and scratch paths with provider helpers; add runtime re-evaluation and containment tests; run full gates.
- [ ] 4.2 **REQUIRES: task 3.11.** In `agent-docs-sync`, add direct `tdt-core>=0.3,<0.4`, regenerate its lock, replace duplicate paths, add alternate-root tests, and run full gates.
- [ ] 4.3 **REQUIRES: task 3.11.** In `agent-harness`, replace private root resolution while preserving its authority boundary; run full gates.
- [ ] 4.4 **REQUIRES: task 3.11.** Set direct importer floors to `tdt-core>=0.3,<0.4`, regenerate lockfiles, build consumer wheels, and clean-install against the local wheelhouse with editable source mappings and sibling paths excluded.
- [ ] 4.5 **REQUIRES: task 3.11.** In each direct agent consumer worktree, commit a concrete consumer/deployment manifest containing every executable old/new path, helper, compatibility policy, reader/writer principal ID, launch adapter ID, lock participation, value-free verifier argv/registered ID, access operation, and removal milestone. Validate it with the installed provider schema; no placeholder or wildcard row is allowed.
- [ ] 4.6 In the `agent-core` owning worktree, enumerate Compose project/services and app/scheduler/backup writers, container users, bind mounts, lock participation, principal probes, and verifier adapters from `compose.yaml`; unresolved interpolation or unknown users block its manifest.

## 5. Supporting TDT consumers

- [ ] 5.1 **REQUIRES: task 3.11.** In `tdt-observability`, align Python metadata, add the provider floor, migrate paths, and run compatibility/full gates.
- [ ] 5.2 **REQUIRES: task 3.11.** In `tdt-sheets`, add the provider floor, migrate credential fallback, and run link/redaction/full gates.
- [ ] 5.3 **REQUIRES: task 3.11 or the approved adapter decision.** In `ai-harness-skills`, use the provider or implement the contract-vector compatibility adapter while preserving standalone isolation; run conformance/full gates.
- [ ] 5.4 **REQUIRES: task 3.11.** In separate worktrees, add RED tests then migrate `browser-cli` and `code-daily-scan`; run each independently.
- [ ] 5.5 **REQUIRES: task 3.11.** In separate worktrees, add RED tests then migrate `jira-daily-reports` and `jira-kanban-from-spreadsheet`; run each independently.
- [ ] 5.6 **REQUIRES: task 3.11.** In separate worktrees, add RED tests then migrate `jira-skill` and `webhook-receiver`; hand agent-core Compose edits to its owning worktree; run full gates.
- [ ] 5.7 **REQUIRES: task 3.11 for any promotion.** Classify and smoke-test `ai-review` and `jira-epic-report`; if source audit finds an executable bypass, promote it to a separately owned provider-gated source-migration worktree.
- [ ] 5.8 Run full pytest, Ruff, format, strict mypy, and local-wheelhouse clean-install gates for every changed supporting repository.
- [ ] 5.9 **REQUIRES: task 3.11.** Each supporting consumer/deployment owner SHALL commit and validate the same concrete manifest fields as task 4.5, including Compose/launchd ownership where applicable. Verification-only repositories either emit an explicit no-path manifest with evidence or are promoted to migration ownership.
- [ ] 5.10 In `tdt-observability`, enumerate and validate both owned launchd labels/plists and writer/access contracts. In `code-daily-scan`, classify each owned launchd plist as active or retired with evidence because scheduling is also centralized in agent-core; unresolved or contradictory deployment artifacts block plan compilation.

## 6. Persistent governance

- [ ] 6.1 Add an AST/config-literal cross-repo check that rejects executable `Path.home()/".tdt"`, literal `~/.tdt` defaults (including values passed through config objects), and private `TDT_HOME` parsing outside canonical/approved compatibility sites while distinguishing docs/messages.
- [ ] 6.2 Add source-audit tests for explicit workspace-root discovery, missing registered repositories, owner/reason/expiry validation, expired exceptions, and installed-wheel execution outside a workspace; runtime doctor SHALL remain independent of repository presence.
- [ ] 6.3 Update `SPEC_INDEX.md` and relevant operator/security docs in each changed repository to map the `tdt-env-loader-tdt-home` capability to its modules.
- [ ] 6.4 Run GitNexus `detect_changes` in every changed repository and investigate unexpected flows before commit.
- [ ] 6.5 Compile the exact fifteen-participant manifest set (`tdt-core` plus fourteen non-provider repositories) into one canonical migration plan. Require participant identity, complete operation, deployment owner, principal, writer, metadata adapter, verifier, config-choice, and credential-choice coverage; reject duplicates, missing/misidentified/symlinked participants, placeholders, unsafe components, or unresolved choices while ignoring unrelated sibling repositories. Commit only a redacted synthetic plan fixture; the live plan remains operator-owned.
- [ ] 6.6 Execute every registered writer-discovery, lock-participation, principal-access, and value-free smoke adapter against synthetic deployments. Attestations SHALL be typed, time-bounded, and bound to root identity plus plan digest; PID existence or caller assertions SHALL not satisfy the gate.

## 7. Synthetic migration verification

- [ ] 7.1 Create a temporary HOME/TDT_HOME legacy tree from the redacted fixture; record hashes and modes.
- [ ] 7.2 Compile the synthetic manifest set, run migration dry-run with fresh typed attestations, and prove zero filesystem metadata/content/link changes plus exact canonical plan/digest stability.
- [ ] 7.3 Apply the compiled synthetic plan, run descriptor-based strict doctor, verify canonical layout/secret references, and execute every typed consumer verifier. Terminate before/after each journal header, backup/staging fsync, intent, replace, parent fsync, completion, switched verification, rollback replacement, and terminal state.
- [ ] 7.4 Recover each interruption from only its generation UUID; reject traversal/schema/root/plan/hash-chain/backup tampering without mutation; prove original hashes, links, owners, modes, and sizes after rollback; repeat the complete successful apply/verify/rollback cycle a second time from a fresh fixture.
- [ ] 7.5 Rehearse release rollback in clean environments: install pre-change consumer wheels/metadata, verify legacy behavior with the locally verified `tdt-core` 0.3 compatibility artifact still available, then reinstall migrated consumers and verify the provider path again.
- [ ] 7.6 Run old and migrated consumers concurrently only in supported compatibility modes against one synthetic tree; verify the path map prevents stale reads/writes.

## 8. Provider-first rollout

- [ ] 8.1 **REQUIRES: Sections 1–7 complete and explicit rollout approval.** Deploy provider-first in dependency order and verify active package versions without switching live paths.
- [ ] 8.2 Deploy/restart downstream consumers in dependency order; verify clean imports, legacy-path compatibility, and exact active versions.
- [ ] 8.3 Inventory every production launchd/Compose process and require inherited `TDT_ENV_PROFILE=production`; fail rollout evidence for unset/development production processes.
- [ ] 8.4 Execute the reverse consumer-first dependency/import rollback rehearsal against deployed artifacts while retaining the provider compatibility artifact, then restore the migrated rollout.

## 9. Live operator migration

- [ ] 9.1 **REQUIRES: Section 8 complete and explicit live-migration approval.** Re-discover live principals/writers through registered adapters, resolve every config/DSN/credential choice, compile the operator-owned live plan, run descriptor-based doctor/dry-run, and present only redacted plan digest, root identity, access, conflict, and fresh attestation evidence.
- [ ] 9.2 Revalidate plan ownership/mode/link count/digest, root identity, complete writer quiescence/lock participation, principal probes, and verifier availability immediately before apply; then create/fsync the generation journal and verified backup/staging metadata without switching active paths.
- [ ] 9.3 Quiesce verified writers, apply the journaled migration, simulate/recover one interrupted boundary on a live-copy fixture, then run strict doctor twice.
- [ ] 9.4 Restart and smoke-test Compose, launchd, observability, all consumers, and credential discovery; on failure execute journaled rollback and retain evidence.

## 10. Final verification and archive

- [ ] 10.1 Re-run full tests, Ruff, formatting, and strict mypy in every changed repository from clean worktrees.
- [ ] 10.2 Re-run source audit and strict doctor; require zero ungoverned bypasses and zero expired/invalid exceptions, literal-secret findings, broken links, access errors, or non-terminal journals.
- [ ] 10.3 Run focused and full strict OpenSpec validation and the semantic second-pass review.
- [ ] 10.4 Update Graphify indexes where present and commit each owning repository independently.
- [ ] 10.5 After every marked task has real evidence, archive the change, revalidate the store, and commit the store.
