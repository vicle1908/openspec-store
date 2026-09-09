## Context

See `proposal.md` and `specs/icloud-worktree-migration-safety/spec.md`. The current evidence contains unresolved Git backing state, metadata-level dataless entries, sensitive-name matches, and a quarantined pilot. The design must preserve iCloud sources while producing independently verifiable local evidence.

## Goals / Non-Goals

**Goals:**

- Make each bounded source-to-destination copy an independently verifiable transaction.
- Record evidence before advancing any readability, secret, replacement, or deletion gate.
- Keep sensitive pilot content quarantined and excluded from the general recovery destination.
- Make deletion authorization exact-path, evidence-backed, and fail closed.
- Preserve metadata-only and value-blind evidence in OpenSpec while keeping per-file restricted evidence external.

**Non-Goals:**

- No implementation or iCloud mutation is authorized by this design alone.
- No assumption that iCloud deletion is reversible; rollback is not promised.
- No reuse of the quarantined destination as a non-secret source.
- No bulk or all-worktree operation.
- No attempt to authorize an external writable repository through this central OpenSpec change.

### External implementation boundary

OpenSpec 1.10 resolves `actionContext.allowedEditRoots` to the planning root and does not authorize linked writable roots. The central change therefore accepts evidence from external orchestration but does not edit an external migration repository or the iCloud source itself. Any copy/recovery utility SHALL be implemented in a separately authorized external repository or worktree, with its own permissions, commit, and focused verification. The external implementation identity, commit, evidence manifest, and validation result must be supplied before corresponding central tasks advance.

The central change may define the contract and record externally produced evidence. A scoped subagent or external command may perform read-only work only when its own target root and permissions are explicitly established; the central `allowedEditRoots` value is not treated as authorization for that work.

### Backing-store research evidence

The first research artifact, `backing_store_research.json`, is classified as **mixed local/cloud metadata**, not local-only: its recorded traversal includes a `Library/CloudStorage/GoogleDrive-…` hit and a FileProvider timeout. It must not be used as proof of a local-only search.

The corrected artifact, `backing_store_research_allowlisted.json`, uses positively allowlisted local roots, prunes `Library/CloudStorage` before traversal, performs metadata-only inspection, and does not open unresolved iCloud `.git` bodies. It still establishes no independent backing-store identity; task 3.1 remains unresolved.

### External execution packet

Before any pending task can be accepted centrally, the external operator must provide a value-blind execution packet under the authorized research/evidence root containing: the exact external repository/worktree path; commit or immutable source identity; command and bounded source/destination scope; start/end timestamps; exit status; per-operation result counts; source-preservation result; collision/error result; destination read-back result; manifest and evidence hashes; and explicit confirmation that `.git`, sensitive paths, and iCloud source deletion were excluded unless separately authorized by an exact-path record. The packet must identify whether evidence is local-only, mixed cloud metadata, or restricted, and must never include secret contents.

The packet is an acceptance prerequisite, not proof of completion. Negative searches, empty directories, capacity projections, or successful planning validation do not establish replacement, readability, backing-store identity, or deletion authorization.

## Decisions

### 1. Separate evidence surfaces

OpenSpec stores only aggregate counts, gate states, timestamps, and references to restricted external evidence. Per-file paths, hashes, modes, and read errors remain in access-restricted evidence outside OpenSpec. Sensitive contents are never emitted.

The pilot manifest is the source for the bounded-copy result: 18 allowlisted candidates, 7 copied and destination-verified, 11 not copied, and 0 read failures. A read-only lstat audit of the original `WHO-project-worktrees/` destination confirms the seven files remain, including `vds-scripts-phase128/AGENTS.md`; the root and child directories are `0755`, and files are `0644`. The separate reconciliation evidence records four quarantined files from `restricted-nonsecret/`. The original pilot destination and the later quarantine destination are distinct dispositions: quarantine does not empty or clear the original pilot. The retained pilot destination is unavailable for further generalized batches until independently dispositioned; the secret gate remains blocked.

### 2. Atomic bounded-copy transaction

A bounded copy operates on one exact source path at a time. Before writing, the process records source metadata and confirms the path is outside `.git`, cache exclusions, and sensitive-name matches. It writes to a temporary destination on the same local filesystem, flushes and closes it, and atomically renames it into a destination path that does not already exist. Existing destination paths are never overwritten: an existing target is a verification conflict, requiring comparison against restricted evidence and an explicit resolution before any replacement attempt. A failed read, write, rename, collision check, or verification leaves the iCloud source untouched, removes only the uncommitted temporary destination, and does not advance any gate.

A batch is complete only when every member has a successful evidence record. Partial batches remain explicitly partial and cannot authorize source cleanup.

### 3. Quarantine boundary

Sensitive-name or content matches are diverted to a separately permission-restricted quarantine. The quarantine is not a migration destination, is never used as evidence of a clean batch, and is excluded from future non-secret scans. Its permission state is recorded as a point-in-time observation; content matches keep the secret gate blocked.

### 4. Gate advancement order

Gates advance in order: metadata inventory, capacity projection, bounded readability evidence, sensitive-file classification, replacement verification, exact deletion authorization. Evidence is persisted before the next gate is considered. Capacity is never treated as readability, and a non-dataless pointer is never treated as backing-store proof.

### 5. Replacement and deletion transaction boundary

Replacement verification is per exact source path. It must cover the declared readable scope, local changes, and either a preserved local snapshot, recovered Git store, or verified remote clone. Deletion authorization names exactly one source path and references the independently recorded replacement evidence. A missing, stale, or mismatched authorization rejects the operation.

Deletion has no assumed rollback: the original remains untouched until the authorization gate passes, but once deletion executes the design does not promise recovery. Glob, directory, all-worktree, and unbounded requests are rejected before mutation.

## Risks / Trade-offs

- Per-file atomic transactions increase metadata and verification overhead but prevent an unverified partial copy from masquerading as a complete replacement.
- Excluding `.git` avoids unsafe hydration and backing-store assumptions but delays history reconstruction.
- Quarantine preserves potentially sensitive material for controlled review while preventing accidental inclusion; it consumes local space and does not clear the secret gate.
- No rollback assumption makes exact authorization and pre-deletion evidence mandatory; it is safer than pretending iCloud deletion can be reversed reliably.
- Logical-size capacity projections can understate operational cost when dataless files require hydration, so bounded batches and repeated free-space checks remain mandatory.
