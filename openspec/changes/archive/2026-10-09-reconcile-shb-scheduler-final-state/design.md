# Design

## Context

See proposal.md for motivation. The completed scheduler archive is immutable, while the live implementation advanced through additional hardening commits. The corrective change spans the central OpenSpec store, the scheduler and skill repositories, curated wiki entities, and two exact local cleanup targets.

## Goals / Non-Goals

**Goals:**
- Establish source precedence: live repository state and command output are authoritative for final implementation claims; archived artifacts remain authoritative historical records.
- Reconcile the canonical scheduler specification without changing runtime behavior.
- Update only the two named wiki entities and only the two named cleanup targets.
- Produce value-blind evidence with paths, commit IDs, statuses, exit codes, counts, and hashes where useful.

**Non-Goals:**
- No edits under the completed archive.
- No scheduler runtime or dependency changes.
- No broad wiki rewrite, LaunchAgent sweep, cache sweep, or generated Graphify changes.

## Decisions

### 1. Immutable archive and corrective record
Create a new active change rather than editing the archived scheduler change. The corrective change records discrepancies as historical-vs-final evidence and cites the final live revisions. Before commit, verify `git diff --name-only -- openspec/changes/archive` is empty.

### 2. Canonical specification split
Refactor only the overlong first requirement in `openspec/specs/shb-schedule-engine/spec.md` into shorter normative requirements and scenarios. Preserve all existing behavior, scenario meaning, and container/local backend distinction. Validate both the corrective change and the canonical spec with strict JSON validation.

### 3. Evidence precedence and test-count reconciliation
Use the current repository HEADs and fresh command outputs for final-state claims. Treat archived evidence counts and review-plan statements as historical snapshots; do not overwrite them. Record the discrepancy and the exact final verification command/result in corrective evidence.

### 4. Documentation scope
Update only `wiki/entities/shb-schedule.md` and `wiki/entities/shb.md`. Replace obsolete host-service wording with Compose/PostgreSQL/advisory-lock wording while retaining the local SQLite fallback. Do not alter the already-correct scheduler README or skill unless validation finds a concrete contradiction.

### 5. Host cleanup safety
Before removing the plist, verify the exact path, inspect whether it is currently loaded, and check for an active scheduler process. If loaded or active, unload/stop only that exact scheduler target before unlinking it; if state is ambiguous, leave it and record the blocker. Remove the residual `service/__pycache__` only after confirming no source file remains in that directory. Use exact-path unlink/rmdir operations; never recursive deletion.

### 6. External execution evidence
For each external root, record root path, pre-change revision/status, bounded command, timestamp, exit code, changed paths, and post-change read-back. Exclude `.git`, credentials, generated Graphify files, unrelated active OpenSpec changes, and all other LaunchAgents.

## Risks / Trade-offs

- The canonical spec split may create a broader diff than the stale evidence corrections; strict validation and scenario comparison are required to avoid semantic drift.
- The plist may be loaded or referenced by a stale launchd state; fail closed and leave it untouched if exact ownership cannot be established.
- Wiki edits can conflict with concurrent knowledge synchronization; preserve unrelated edits and inspect status before commit.
- Historical archive evidence cannot be corrected in place, so the final state will be represented by a new corrective record rather than a single self-contained archive.
