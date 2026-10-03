# Design

## Context

See `proposal.md` — Why. Constraints that shape the approach:

- Four existing specifications already require archived change files to be immutable: `cleanup-archive-verification`, `archive-integrity-reconciliation`, `archive-closure-audit`, and `ai-review-deployment-state`. The principle is established; this change adds detection and reversion obligations plus a named artifact.
- The `spec-driven` schema defines exactly four artifacts: `proposal → specs → design → tasks`. `evidence.md` is not a schema artifact and `openspec validate` does not check for it.
- `openspec schema fork`/`init` exist, but `schema init --artifacts` accepts only the four built-in artifact IDs, so a first-class `evidence` artifact cannot be declared through the CLI.
- `operations.archive.guidance` in `openspec/config.yaml` already says "record the archived change for downstream verification" without naming an artifact. Guidance is where apply/archive norms already live.
- Evidence usage is measured at 78/619 archives (12.6%), peaked 2026-09 at 57%, regressed 2026-10 to 25%, and two forms coexist (`evidence/` directories and `evidence.md` files).
- The violation being remediated is a single commit, `6f274f8d`, which added one file to one archived change.

## Goals / Non-Goals

**Goals:**

- Record the immutability violation and restore the affected archive to its pre-edit content.
- Preserve the recovered evidence inside the active corrective change.
- Name the evidence artifact in archive guidance, and standardize on one form for new work.
- Keep the remediation verifiable and reversible.

**Non-Goals:**

- Backfilling the 543 archives that carry no evidence.
- Migrating existing `evidence/` directories to `evidence.md`.
- Forking the schema to add a first-class evidence artifact.
- Editing any other archived change.

## Decisions

### Decision: Revert by removing the added file, not by rewriting the archive

The violation is a pure addition, so reversion is a single file removal. The archived directory then matches its pre-edit content exactly.

*Alternatives considered:* rewriting the archive from its archived revision wholesale (rejected — wider blast radius for a one-file defect and risks touching content that was never modified); leaving the file and only recording the violation (rejected — leaves the archive permanently deviating and contradicts the spec's reversion obligation).

### Decision: Preserve recovered evidence inside the active change

The evidence content is not discarded. It moves into the corrective change so the verification record survives without living in an archived directory.

*Alternatives considered:* deleting it as redundant with `tasks.md` (rejected — the evidence contains verification results not recorded elsewhere, including the investigated 401); leaving a pointer in a notes file (rejected — a pointer is not durable evidence).

### Decision: Guidance, not schema fork

Named in `operations.archive.guidance` rather than enforced as a schema artifact.

*Rationale:* guidance is where the store's apply/archive norms already live, the CLI cannot declare a custom artifact, and a convention used by 12.6% of archives should not be imposed at schema level before it is agreed. A schema fork would also make the store diverge from the upstream schema for a young convention.

*Alternatives considered:* schema fork (rejected as above); adding a validation rule (rejected — validation is schema-driven and the artifact is not in the schema).

### Decision: Standardize on `evidence.md`, grandfather `evidence/`

New changes use a single file. Existing `evidence/` directories are left untouched.

*Rationale:* a single file is simpler to create, review, and cite, and the more recent practice already favors it. Migrating 48 existing directories would violate the immutability principle this change upholds.

*Alternatives considered:* standardizing on the directory form (rejected — heavier for the common case and the newer practice moved away from it); allowing either form indefinitely (rejected — that is the current ambiguity being resolved).

### Decision: No backfill

The 543 archives without evidence stay without it.

*Rationale:* backfill would require re-deriving verification for historical work, would be largely unreproducible, and would mean touching hundreds of archived directories — in direct tension with the immutability rule. Recording the norm for new work is the durable fix.

## Risks / Trade-offs

- **Removing a file from an archive is itself a change to archived content** → It is a *reversion to* the archived state, which the spec's reversion obligation expressly requires. The commit message must state that it restores, not alters, the archive.
- **A convention in guidance is not enforced** → Accepted. Guidance over enforcement is the deliberate choice at this adoption level; the specs supply the normative language, guidance supplies the pointer.
- **`evidence.md` may later need to become a schema artifact** → The guidance requirement is written so a later schema fork can supersede it without contradiction.
- **Other sessions may be writing to the store concurrently** → The reversion touches one archived path and must be staged in isolation; verify no other session is mid-operation before committing.
- **Precedent already exists for the directory form** → Grandfathering avoids a destructive migration and keeps the change narrowly scoped.

## Migration Plan

1. Capture the current archived file content and the archived revision reference for the affected archive.
2. Remove the added `evidence.md` from the archived change directory.
3. Place the recovered evidence and this change's own evidence in the active change.
4. Extend `operations.archive.guidance` in `openspec/config.yaml` with the evidence requirement and the standardized form.
5. Validate the store, then commit as a single scoped commit stating the reversion explicitly.

**Rollback:** restore the added file from the recorded commit (`6f274f8d`) and revert the `config.yaml` guidance edit. Both are single-path changes.

## Open Questions

None that affect the specs, the approach, or the task breakdown.
