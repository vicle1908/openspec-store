# Tasks: TDT Home Synthetic Migration Engine

Each task is one focused work session with a verification gate. Depends on
`govern-tdt-home-config-and-environment` (provider foundation) and
`govern-tdt-home-source-conformance` (manifests) being complete.

## 1. Plan compilation

- [x] 1.1 Implement source inventory scanner that reads provider manifests and produces a typed migration plan (source path, target path, kind, hash, backup flag).
- [x] 1.2 Implement plan validation: verify all source paths exist, all target paths are contained under TDT_HOME, and no conflicts exist.
- [x] 1.3 Implement plan digest computation (SHA-256 of canonical JSON) for journal binding.
- [x] 1.4 Add tests for plan compilation with fixtures covering: clean migration, missing sources, conflicting targets, unsafe paths.

## 2. Journaled apply

- [ ] 2.1 Implement journal lifecycle: `prepared → staged → switching → intent → completed → switched → committed` using existing `JournalHeader`, `JournalRecord` schemas from `control_plane_schema.py`.
- [ ] 2.2 Implement `prepared → staged`: snapshot each DESTINATION target with `BackupMetadata` before mutation, record backup paths in journal.
- [ ] 2.3 Implement staging: create staging copies under TDT_HOME, verify identity hashes match plan, verify BOTH backups and staged payloads BEFORE writing the `staged` journal record.
- [ ] 2.4 Implement `switching → intent`: atomically rename staging copies to final locations using descriptor-relative operations from `fs_kernel.py`.
- [ ] 2.5 Implement `intent → completed`: verify all final locations, write completion marker.
- [ ] 2.6 Implement `completed → switched → committed`: update symlinks/pointers, persist journal to durable storage.
- [ ] 2.7 Add tests for each state transition including partial apply scenarios.

## 3. Recovery and rollback

- [ ] 3.1 Implement crash recovery: read journal, determine last committed state, resume from next valid transition.
- [ ] 3.2 Implement rollback from each supported recoverable journal state back
  to `rolled_back`, restoring from verified backup metadata; a committed
  generation requires a separately approved plan rather than implicit reverse
  mutation.
- [ ] 3.3 Implement idempotent retry: same journal replay produces identical result.
- [ ] 3.4 Add tests for recovery from each journal state boundary.

## 4. Backup and restore

- [ ] 4.1 Implement pre-migration snapshot using `BackupMetadata` schema (hash, mode, ownership, link count).
- [ ] 4.2 Implement backup verification: re-read backed-up file, compare hash and metadata.
- [ ] 4.3 Implement backup restore for rollback path.
- [ ] 4.4 Add tests for backup integrity under normal and adversarial conditions.

## 5. Synthetic interruption testing

- [ ] 5.1 Implement interruption harness: run apply in a subprocess, send SIGTERM at each journal state boundary, verify recovery.
- [ ] 5.2 Add tests for interruption at: after prepared, after staged, during switching, after intent, after completed, after switched.
- [ ] 5.3 Verify no partial mutations survive after recovery from each interruption point.

## 6. Isolated test root verification

- [ ] 6.1 Create isolated test root fixtures (value-free, no real credentials).
- [ ] 6.2 Run full apply → verify → rollback cycle against isolated test root.
- [ ] 6.3 Run `tdt config doctor` against migrated test root and verify healthy.
- [ ] 6.4 Run provider contract tests against migrated test root.

## 7. Verification and documentation

- [ ] 7.1 Run complete pytest suite, Ruff, strict mypy on the migration engine code.
- [ ] 7.2 Document the migration engine API, journal states, recovery semantics, and operator-facing CLI.
- [x] 7.3 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until all migration engine tasks pass, interruption tests green,
isolated root verification passes, and documentation is complete.

## Evidence boundary

Tasks 1.1–1.4 are implemented and verified in canonical `tdt-core` commit
`3db6623` and the safe compatibility facade in `tdt-core` commit `ebc545c`.
`ManifestMapping` requires an explicit absolute repository root,
manifest-declared source scope, and relative target prefix; the scanner uses
the provider no-follow descriptor kernel and emits only relative paths, object
kinds, metadata facts, hashes, and backup flags. Preflight reopens and
identity/digest-checks every source, rejects root overlap, unsafe or missing
sources, hard links, unsupported objects, duplicate targets, and overlapping
targets. Canonical JSON is deterministic and its SHA-256 digest is available
for journal binding. The compatibility `compile_plan` surface is read-only;
its apply, backup, rollback, and journal persistence entry points fail closed
until their successor tasks are implemented. Focused planner coverage is 19
passed; full provider pytest reports 487 passed and 16 skipped, with Ruff,
formatting, and strict mypy gates passed. GitNexus MCP could not
index `tdt-core` in this session, so no live impact/detect evidence is claimed;
manual scope review was performed and `graphify update .` refreshed the local
code graph. Tasks 2.1–7.2 remain open: the canonical checkout still has no
journal executor, backup/apply/recovery/rollback implementation, interruption
harness, or isolated end-to-end migration evidence. Task 7.3 remains the only
other completed task. This predecessor is not green and cannot satisfy rollout
or live-cutover gates.
