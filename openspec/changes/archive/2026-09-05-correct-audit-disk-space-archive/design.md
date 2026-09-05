## Context

The referenced archive is immutable. Its operational evidence is complete, but three narrative claims need reconciliation: a pre-approval Trash statement, a non-goal that reads broader than the later approved action, and a claim about unrelated workspace modifications.

## Goals / Non-Goals

**Goals:**

- Reconcile claims against the archived evidence without changing archive history.
- Record the authoritative interpretation and scope boundary in value-blind evidence.
- Preserve pre-existing unrelated dirty paths.

**Non-Goals:**

- No edits under `openspec/changes/archive/`.
- No cleanup, restoration, deletion, or filesystem mutation.
- No Git history rewrite or modification of unrelated active changes.

## Decisions

- Use the archived `evidence.md` as the source for later operational facts and the archived proposal/task files as the source for historical wording.
- Classify the Trash sentence as pre-approval inventory state; do not erase or rewrite it.
- Interpret the non-goal as prohibiting unapproved automatic cleanup, with approved execution documented in the evidence section.
- Narrow the workspace claim to modifications made by the audit implementation, rather than all repository dirt.
- Store only claim IDs, statuses, paths, dates, sizes, and hashes where needed; omit contents and credentials.
- Use a final immutable-path check and strict OpenSpec validation before archiving this corrective change.

## Risks / Trade-offs

- A corrective record cannot change how a reader first interprets the archived wording; it provides an explicit authoritative reconciliation.
- Historical source files may contain contradictory statements by design; preserving them maintains audit history.
- Unrelated active changes can change concurrently, so scope checks are point-in-time evidence only.
