# Design

## Context

See `proposal.md` — Why. The constraints that shape this design are properties of
the current layout, each verified directly:

- Two scheduled jobs execute scripts from outside any repository:
  - `com.developer.workstation-daily-update` (daily 08:00) →
    `~/Developer/scripts/workstation-daily-update.sh`
  - `com.developer.index-refresh` (daily 02:30) →
    `~/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh`
- `~/Developer` is not a Git repository. No LaunchAgent references the copies
  recorded under `openspec-store/scripts/` (verified: no plist contains
  `openspec-store/scripts`).
- The knowledge-refresh files exist as two byte-identical copies with **distinct
  inodes** — 6 of 8 files identical, 2 already diverged. They are duplicated
  files, not links, so editing either one does not update the other.
- The store's own test already reaches past its recorded copy to the installed
  one (`test_process_inventory.sh` line 9 defaults `SCRIPT` to the path under
  `~/Developer/scripts/`), so the recorded copy is neither executed nor
  exercised — it is a stale record.
- A prior reconciliation (`4741f899`) brought the copies back together once and
  the drift returned, so a one-off fix does not hold.
- The existing daily job is a `set -euo pipefail` script with 8 numbered stages
  and exactly one fail-closed exit path (`SYNC_FAILED`, owned by the parity
  stage). Its other failure outcomes (`REFRESH_FAILED`, `AGENT_FAILED`) are
  reported as degradations and do not abort the run.

The relevant precedent is `host-deploy-script-consistency`, which mandates
SHA-256 snapshot-and-diff for scripts copied during deploy and exits non-zero on
a source/runtime mismatch. It is scoped to `ai-review/scripts/deploy.sh`, so the
pattern exists in the workspace but does not cover this script tree.

## Goals / Non-Goals

**Goals:**

- Give every executed maintenance script revision history and a recovery path.
- Make the executed-copy/recorded-copy relationship explicit per script instead
  of leaving independent duplicates.
- Detect content drift between the copies and surface it through the existing
  scheduled job, without rewriting either copy.

**Non-Goals:**

- Deciding by fiat which repositories the knowledge-refresh job should index.
  The executed inventory (32 entries) is treated as accurate because all 32
  resolve to existing directories; only the stale recorded copy is corrected.
- Relocating executing scripts, or changing LaunchAgent program paths or
  schedules. Jobs keep running the same paths they run today.
- Fixing `workspace-worktree-scan.sh`'s hardcoded repository list, which
  `workspace-index-freshness` already forbids elsewhere. This design records the
  script; correcting its content is a separate change.
- Building a synchronization daemon or auto-healing loop.

## Decisions

### Decision: The executed copy is authoritative; the store copy is a recorded mirror

Where a script exists in both places, `~/Developer/scripts/` remains the
executed, authoritative copy and the store's `scripts/` copy is the recorded
mirror. The relationship is declared in a small manifest rather than inferred.

*Alternatives considered:* (a) make the store copy authoritative and install
outward — rejected, because it introduces an install step into a path that
currently has none, and any drift between install and execution becomes an
outage of the scheduled job itself; (b) symlink one location to the other —
considered and not adopted as part of this change, because changing an executed
script into a symlink alters launchd's resolved path and needs its own
verification. Either may be a follow-up; the manifest records the choice so a
future change can change it deliberately rather than by accident.

*Rationale for a manifest:* the requirement is that the declared relationship be
discoverable without inspecting file contents. A manifest listing each script,
its executed path, its recorded path, and which one is authoritative satisfies
that directly and is itself version controlled, so the declaration is reviewable.

### Decision: Record the two unversioned scripts by copying them into the store

`workstation-daily-update.sh` and `workspace-worktree-scan.sh` gain recorded
copies under `openspec-store/scripts/`, matching how `knowledge-refresh/` is
already recorded.

*Rationale:* it is the established convention in this store (13 tracked files
under `scripts/knowledge-refresh/`, `scripts/workspace-lifecycle/`, and
`scripts/archimate/`), so it needs no new mechanism. The recorded copies are not
executed, so adding them cannot change job behavior.

*Risk accepted:* a recorded copy can go stale exactly as the knowledge-refresh
inventory did. That is precisely what the drift-detection requirement addresses;
recording without detection would repeat the original mistake.

### Decision: Drift is detected by content digest, not by timestamp

The check compares content (a SHA-256 over the file, and over the tree where a
script has companions) between the executed and recorded copies, and reports a
script as drifted when the digests differ.

*Alternatives considered:* (a) modification-time comparison — rejected, because
mtime changes without content changing (touch, checkout, restore) and would
produce false drift; (b) byte-length comparison — rejected, insufficient;
(c) reusing the lockfile `computedHash` approach — rejected for the same reason
established in `automate-skill-content-refresh`: that digest is CLI-internal and
not reproducible for multi-file trees.

*Rationale:* `host-deploy-script-consistency` already establishes SHA-256
snapshot-and-diff for copied scripts in this workspace, so this follows an
existing convention rather than inventing one.

### Decision: Drift is a reported degradation, not a fail-closed abort

The drift stage joins the daily job as a new stage after the skills parity check,
reports each drifted script, and sets a `SCRIPT_DRIFT` flag that the run summary
reports as a degradation. It does not trigger the parity stage's fail-closed
`return 1`.

*Rationale:* this mirrors the existing asymmetry in the job. An unresolved skill
link is a correctness defect that must fail the run; a script whose executed copy
is ahead of its recorded copy is a provenance gap that must be *visible* but that
must not stop unrelated maintenance. The spec also requires that drift not be
reported as a silent success, which the summary satisfies.

### Decision: The check neither rewrites nor repairs

The stage reports drift and exits; it never copies one file over the other.

*Rationale:* the spec forbids modifying either copy, and the prior one-off
reconciliation (`4741f899`) demonstrates why an automatic overwrite is
dangerous — if the executed copy held uncommitted operator changes, an automatic
reconciliation would destroy them while reporting success.

### Decision: Correct the conflicting requirement rather than contradict it

The change modifies `organization-namespaces`'s "Tooling and script path
resolution invariants" requirement so its inventory assertion is expressed as the
two copies agreeing, instead of naming a fixed 20-repository count, and so its
freshness assertion reflects the observed non-zero result rather than asserting a
zero exit.

*Rationale:* leaving the requirement unmodified while reconciling the inventory to
32 entries would create a spec that the archived change directly violates, and a
future reader could not tell which statement was authoritative. The alternative —
forcing the inventory back to 20 entries to satisfy the old number — was rejected
because all 32 executed entries resolve to real Git repositories, so truncating
the list would silently drop 12 repositories from indexing to preserve a stale
assertion.

*Note on scope:* only the wording of that one requirement changes. Its other two
scenarios, which constrain path resolution and fail-closed behaviour, are carried
through unmodified.

### Decision: The recorded approval digest is regenerated with its inventory

Reconciling the recorded `knowledge-refresh-inventory.tsv` from 20 to 32 entries
changes its content, so the recorded `knowledge-refresh-approval.sha256` is
recomputed over the reconciled file in the same change.

*Rationale:* the running job verifies its inventory against the digest beside it
and refuses to proceed on a mismatch. Recording a new inventory without its
digest would leave an internally inconsistent pair that appears approved.

## Risks / Trade-offs

- **[A recorded copy becomes stale and nobody notices]** → The drift-detection
  requirement makes staleness a reported outcome of the existing daily job, so it
  surfaces within a day rather than waiting to be discovered.
- **[The drift check produces false positives on line-ending or permission
  differences]** → The comparison is over file content only, not mode or mtime,
  so a permission change does not register as drift. This is stated in the
  requirement's intent and asserted by the agreement scenario.
- **[Recording the workstation script embeds host-specific absolute paths in the
  store]** → Accepted: the store already records scripts containing
  `/Users/androidteam` paths, and `~/Developer` is not portable by design. The
  recorded copy is a recovery artifact, not a distributable.
- **[Reconciling the recorded inventory to 32 entries could be read as approving
  12 new repositories]** → The proposal's non-goals state that this changes only
  the stale record, not what is approved; the executed copy remains the authority
  on what is indexed, and it already indexes all 32.
- **[Adding a 9th stage lengthens the daily run]** → The check is local file
  hashing over a handful of files, with no network access, so its cost is
  negligible next to the existing package-manager stages.

## Migration Plan

1. Add the script manifest declaring each script's executed path, recorded path,
   and authoritative copy.
2. Copy `workstation-daily-update.sh` and `workspace-worktree-scan.sh` into the
   store's `scripts/` tree as recorded mirrors.
3. Reconcile the recorded `knowledge-refresh-inventory.tsv` to the executed
   inventory's 32 entries and regenerate the recorded approval digest over it.
4. Add the drift-detection stage to `workstation-daily-update.sh`, renumbering
   stage banners, and report a `SCRIPT_DRIFT` degradation in the summary.
5. Verify by hand: run the drift stage expecting agreement, confirm it reports no
   drift; then modify a recorded copy and confirm the stage reports that script as
   drifted without rewriting either file.

*Rollback:* remove the drift stage and revert the store's `scripts/` additions;
the scheduled jobs continue to execute the same installed paths throughout, so
rollback carries no job risk.

## Open Questions

None. The authority direction, the comparison method, the failure severity, and
the digest coupling are all resolved above. Whether to later replace the
duplication with a link is explicitly deferred as a separate change and does not
affect these requirements.
