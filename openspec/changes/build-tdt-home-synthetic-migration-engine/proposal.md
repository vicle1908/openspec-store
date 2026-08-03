# Build TDT_HOME Synthetic Migration Engine

## Why

The archived `govern-tdt-home-config-and-environment` change established the secure `tdt-core` provider boundary, but it deliberately stopped before moving any data. A future TDT_HOME rollout needs a migration mechanism whose plan is reviewable before mutation, whose progress survives process interruption, and whose rollback can be demonstrated without risking operator data.

This change builds and verifies that mechanism entirely against synthetic, isolated filesystem roots. It turns the already-implemented `JournalHeader`, `JournalRecord`, and `BackupMetadata` control-plane schemas into an executable migration lifecycle before any consumer repository or the real `~/.tdt` tree is eligible for migration.

## What Changes

- Add typed, immutable migration plans that identify each source and destination as validated root-relative components and declare the expected pre-migration object state.
- Canonically serialize and digest each plan so apply, recovery, backup, and rollback remain bound to the same plan, generation, and anchored root identity.
- Preflight a complete plan before mutation, rejecting unsafe paths, duplicate or conflicting destinations, unsupported object types, changed source state, cross-root operations, and incomplete recovery prerequisites.
- Implement journaled apply using the existing `JournalHeader` and `JournalRecord` schemas, durable state transitions, and hash-chain validation.
- Create and verify per-object backups using the existing `BackupMetadata` schema before an original object can be replaced, removed, or otherwise made unavailable at its old location.
- Recover deterministically after interruption by validating the journal, plan digest, generation identifier, root identity, backup metadata, and current filesystem state before continuing forward or rolling back.
- Make apply, recovery, and rollback idempotent: repeating a command after success or interruption either converges on the same verified terminal state or fails closed without unjournaled mutation.
- Add synthetic interruption tests that terminate a worker at controlled apply boundaries, restart recovery in a new process, and verify content, metadata, journal integrity, and absence of partial artifacts.
- Add rollback rehearsals that restore the exact synthetic pre-migration state from verified backups and prove that a second rehearsal is harmless.
- Expose only redacted diagnostics and evidence. Plans and journals may identify bounded relative object paths and hashes, but must not contain credential values, file contents, arbitrary command strings, or unbounded absolute paths.

## Capabilities

### New Capabilities

- `tdt-home-migration-engine`: compile and validate typed root-relative migration plans; execute durable, journaled migrations; recover from interrupted apply; and restore verified backups against explicitly isolated roots.

### Modified Capabilities

- None. The existing `tdt-env-loader-tdt-home` provider contract and control-plane schemas are prerequisites, not redefined by this change.

## Ownership Boundaries

- `tdt-core` owns the typed plan model, canonical plan digest, preflight validator, backup/restore implementation, journal state machine integration, recovery logic, synthetic test harness, and redacted migration diagnostics.
- The existing `tdt-core` `JournalHeader`, `JournalRecord`, and `BackupMetadata` schemas remain the normative wire boundary; this change consumes them rather than introducing incompatible duplicate schemas.
- `openspec-store` owns the normative planning and verification artifacts only. It does not own runtime migration data.
- Consumer repositories continue to own their real path inventories, compatibility behavior, deployment writers/readers, dependency floors, and acceptance evidence. No consumer repository is modified by this change.
- Operators retain ownership of the real `~/.tdt` tree and any future live-cutover approval. This change grants no authority to inspect or mutate it.

## Safety and Isolation

- Every mutating test or rehearsal SHALL require an explicit isolated root created for that run; production defaults and implicit `Path.home() / ".tdt"` resolution are forbidden in the migration test harness.
- The engine SHALL bind a generation to one anchored root identity and reject absolute paths, parent traversal, symlink-mediated escape, root substitution, and plan or journal reuse against another root.
- No mutation SHALL begin until the complete plan passes validation and required backups can be created and verified.
- Journal and backup writes SHALL use the provider-owned private filesystem primitives and durability boundary established by the predecessor change. Unsupported security or synchronization primitives cause a fail-closed result.
- Recovery SHALL never infer success from filenames alone. It must validate trusted invocation context, the complete hash chain, durable intent/completion records, object digests, and backup metadata.
- Corrupt, truncated, reordered, forked, or context-mismatched journals are diagnostic failures; they do not authorize best-effort continuation.
- Synthetic kill points SHALL be enabled only by an explicit test interface and SHALL not be available as an ambient production behavior.

## Explicit Non-Goals

- Reading, backing up, repairing, migrating, or deleting anything under the real `~/.tdt` or any effective operator `TDT_HOME`.
- Modifying consumer source code, manifests, dependency metadata, deployment configuration, launch agents, containers, or running services.
- Defining real consumer path maps or guessing which files belong to a consumer.
- Performing provider release, downstream adoption, deployment rollout, live cutover, or rollback of deployed consumers.
- Supporting cross-device moves, remote filesystems, directories as opaque recursive payloads, special files, or arbitrary filesystem metadata without an approved adapter and explicit schema support.
- Executing plan-supplied shell commands, hooks, scripts, or arbitrary adapter paths.
- Changing the existing control-plane wire schemas merely to simplify the executor. Any required incompatible schema evolution must be proposed separately.

## Dependencies and Preconditions

- The provider boundary from `govern-tdt-home-config-and-environment` must remain green, including bounded path handling, private mutation primitives, packaged contracts, and installed-wheel verification.
- The implemented `JournalHeader`, `JournalRecord`, and `BackupMetadata` schemas and their validators are mandatory inputs to the engine.
- Synthetic fixtures must cover regular files, symlinks where policy permits them, prior absence, metadata representable by `BackupMetadata`, destination conflicts, stale preconditions, and malformed recovery artifacts.
- Test roots must be disposable, independently identifiable, and located outside the real `~/.tdt` tree and consumer repositories.

## Success Criteria

- A reviewed typed plan can be serialized canonically, independently digested, and rejected if its root binding or preconditions change.
- A clean synthetic apply reaches `committed` with every intended destination verified and no untracked staging or backup artifact affecting the migrated view.
- For every supported interruption boundary, a hard-killed apply can be reopened in a fresh process and deterministically recovered to a verified committed or rolled-back state.
- Tampering with a plan, journal header, record sequence, hash link, backup payload, metadata document, generation selector, or root identity is detected before further mutation.
- Rollback from every supported nonterminal apply state restores the exact representable pre-migration content, object kind, permissions, ownership policy, link target, and absence state described by `BackupMetadata`.
- Repeated apply, recovery, and rollback requests are idempotent and never create divergent journal histories.
- Focused and full `tdt-core` tests, Ruff, formatting, strict mypy, security/redaction checks, and strict OpenSpec validation pass with recorded evidence.
- Verification demonstrates by path and root-identity assertions that neither the real `~/.tdt` nor any consumer repository was touched.

## Impact

- Primary implementation repository: `tdt-core` (Python 3.14, `uv`, pytest, Ruff, strict mypy).
- Primary implementation surfaces: migration plan models/compiler, transaction coordinator, journal persistence/recovery, backup/restore services, CLI or internal command boundary, and synthetic subprocess tests.
- Existing provider consumers see no path or configuration behavior change from this work; the engine remains unconnected to consumer deployment flows.
- The main operational risk is an executor claiming recoverability without durable evidence. The design therefore favors fail-closed validation and complete rollback rehearsal over permissive repair.

## Rollout

1. Specify the typed plan, canonical digest, preflight, journal, backup, recovery, and rollback behavior as delta requirements.
2. Implement plan validation and dry-run inspection against disposable roots, with no mutating command enabled until negative safety tests pass.
3. Implement verified backup creation and journal durability using the existing provider schemas and private filesystem primitives.
4. Implement apply and recovery as an explicit state machine, then exercise every legal transition and malformed-chain rejection path.
5. Run synthetic subprocess termination at each supported mutation boundary and verify fresh-process recovery.
6. Rehearse rollback repeatedly against isolated roots and compare the restored tree with the captured pre-migration state.
7. Run full provider quality gates and strict OpenSpec verification, then retain the engine as a prerequisite for later provider-gated rollout and live-cutover changes.
8. Do not connect the engine to real consumer manifests or a live TDT_HOME in this change.

## Rollback

The implementation can be rolled back by removing the synthetic migration command surfaces and restoring the pre-change `tdt-core` artifact. Test generations and backups live only under disposable isolated roots and may be deleted after evidence is captured. Because this change neither modifies consumer repositories nor touches the real `~/.tdt`, rollback requires no operator data rewrite, deployment restart, or consumer compatibility action.

If an implementation defect is found during synthetic apply, recovery, or rehearsal, preserve the affected isolated root and journal as redacted test evidence, disable the mutating engine entry point, and restore the pre-change provider artifact. Any future rollback of deployed consumers or live operator data remains owned by `release-and-roll-out-tdt-home-provider` and `cut-over-live-tdt-home`, respectively.
