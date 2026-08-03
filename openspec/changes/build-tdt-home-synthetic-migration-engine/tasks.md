# Tasks: TDT Home Synthetic Migration Engine

Each task is one focused work session with a verification gate. Depends on
`govern-tdt-home-config-and-environment` (provider foundation) and
`govern-tdt-home-source-conformance` (manifests) being complete.

## 1. Plan compilation

- [ ] 1.1 Implement source inventory scanner that reads provider manifests and produces a typed migration plan (source path, target path, kind, hash, backup flag).
- [ ] 1.2 Implement plan validation: verify all source paths exist, all target paths are contained under TDT_HOME, and no conflicts exist.
- [ ] 1.3 Implement plan digest computation (SHA-256 of canonical JSON) for journal binding.
- [ ] 1.4 Add tests for plan compilation with fixtures covering: clean migration, missing sources, conflicting targets, unsafe paths.

## 2. Journaled apply

- [ ] 2.1 Implement journal lifecycle: `prepared → staged → switching → intent → completed → switched → committed` using existing `JournalHeader`, `JournalRecord` schemas from `control_plane_schema.py`.
- [ ] 2.2 Implement `prepared → staged`: backup each source file with `BackupMetadata`, record backup paths in journal.
- [ ] 2.3 Implement `staged → switching`: create staging copies under TDT_HOME, verify identity hashes match plan.
- [ ] 2.4 Implement `switching → intent`: atomically rename staging copies to final locations using descriptor-relative operations from `fs_kernel.py`.
- [ ] 2.5 Implement `intent → completed`: verify all final locations, write completion marker.
- [ ] 2.6 Implement `completed → switched → committed`: update symlinks/pointers, persist journal to durable storage.
- [ ] 2.7 Add tests for each state transition including partial apply scenarios.

## 3. Recovery and rollback

- [ ] 3.1 Implement crash recovery: read journal, determine last committed state, resume from next valid transition.
- [ ] 3.2 Implement rollback: reverse journal from any state back to `rolled_back`, restoring from backup.
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
- [ ] 7.3 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until all migration engine tasks pass, interruption tests green,
isolated root verification passes, and documentation is complete.
