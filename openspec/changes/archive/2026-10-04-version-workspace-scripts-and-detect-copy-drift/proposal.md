# Version workspace scripts and detect installed-copy drift

## Why

The scripts that run this workstation's scheduled jobs live only in an
unversioned directory that no Git repository tracks, and where a tracked copy
does exist in the OpenSpec store it has silently fallen behind the copy that
actually executes, so a script can be lost with no revision history and a
"source of truth" can disagree with reality without anyone noticing.

## What Changes

- Record the workstation's executed scripts under version control in the OpenSpec
  store, so each has revision history and a recovery path:
  - `workstation-daily-update.sh` and `workspace-worktree-scan.sh` are currently
    tracked by **no** repository at all.
  - The `scripts/knowledge-refresh/` files have a tracked copy, which this change
    brings back in line with the executed copy.
- Define a single, explicit source of truth for each script and make the
  relationship checkable, rather than leaving two independent copies that drift.
- Add a drift check that compares an executed script against its recorded copy
  and reports a mismatch, so divergence is detected by the scheduled maintenance
  job instead of being discovered by accident.
- Reconcile the remaining drifted knowledge-refresh script
  (`sync-notion-knowledge.sh`), whose executed copy is newer and lists two wiki
  entity paths the recorded copy lacks, so the recorded tree matches what runs.
- Fix a latent defect in `refresh-knowledge-indexes.sh` single-repository mode:
  it formats the Graphify state as `STALE (<rev> != <rev>)` but then tests for the
  bare string `STALE`, so a repository whose Graphify index is stale while its
  GitNexus index is fresh is reported fresh and the check exits `0`. The check
  must classify staleness correctly in both modes while still showing which
  revisions differ.
- Report drift as a degradation in the daily job rather than silently, and
  without rewriting either copy on its own initiative.
- **BREAKING**: the recorded copy of `knowledge-refresh-inventory.tsv` currently
  lists 20 repositories while the executed copy lists 32. Reconciling the
  recorded copy changes which repositories the recorded approval digest covers,
  and the digest must be regenerated in the same step or the approval gate fails.

## Capabilities

### New Capabilities

None. This change extends requirements already owned by an existing capability.

### Modified Capabilities

- `ecosystem-tooling-and-skills-upgrade`: this capability already owns the
  workstation's scheduled maintenance job — its requirement "Unified daily
  scheduled maintenance and check-and-update automation" mandates
  `~/Developer/scripts/workstation-daily-update.sh`, its `--check` mode, and the
  daily 08:00 LaunchAgent, and its "Check mode does not mutate" requirement
  constrains what that mode may do. What it does **not** own is the *durability*
  or *provenance* of that script: nothing in the capability requires the script
  to be under version control, requires a recorded copy to match the executed
  copy, or requires drift between them to be detected. That absence is why an
  unversioned script can be lost and why the recorded `knowledge-refresh`
  inventory can disagree with the executed one. New requirements are needed for
  versioned provenance, an explicit source of truth, and drift detection.

- `organization-namespaces`: its requirement "Tooling and script path resolution
  invariants" states that the inventory and approval digest "SHALL match with
  identical canonical 20-repo paths" across both copies, and that
  `refresh-knowledge-indexes.sh --check` "SHALL exit successfully with return
  code 0". The count assertion is stale: it described a snapshot of the workspace
  on 2026-09-26 (the origin change's own text reads "both source and workstation
  reflect all 20 canonical repository paths"), while the executed inventory has
  listed 32 repositories since 2026-09-27. The exit assertion is a different kind
  of problem: `--check` **is** a real, first-class flag with a documented contract
  ("Exit code: 0=all fresh, 1=any stale or missing"), and it correctly returns
  `1` today because 25 of the 32 indexed repositories are genuinely stale
  (observed `Total: 32 FRESH: 7 STALE: 25`). So the requirement asserts a
  workspace condition that is currently false, not a flag that is broken. Both
  assertions must be restated: the count as agreement between the copies rather
  than a fixed number, and the exit as a freshness outcome rather than an
  unconditional zero.

## Impact

- **Not under version control today** (`~/Developer` is not a Git repository and
  no other repository tracks these paths):
  - `~/Developer/scripts/workstation-daily-update.sh`
  - `~/Developer/scripts/workspace-worktree-scan.sh`
- **Duplicated and already drifted** — executed copy vs. the copy recorded in the
  store, as different files (distinct inodes) that are byte-identical for 6 of 8
  files:
  - `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`:
    executed copy lists **32** repositories, recorded copy lists **20**; the
    recorded copy is missing 12 `shb/*` repositories and contains no extra
    entries, so it is behind rather than contradictory.
  - `~/Developer/scripts/knowledge-refresh/knowledge-refresh-approval.sha256`:
    the two copies carry different digests (executed `c855c50d…`, recorded
    `5a0366fa…`); each is self-consistent with its own inventory, so no job is
    currently failing.
- **A conflicting existing requirement must be reconciled, not silently overwritten**:
  the capability `organization-namespaces` requires, in its requirement "Tooling
  and script path resolution invariants", that `knowledge-refresh-inventory.tsv`
  and `knowledge-refresh-approval.sha256` "match with identical canonical
  **20-repo** paths" across both copies, and that
  `refresh-knowledge-indexes.sh --check` exit `0`. Both claims are false today:
  the executed inventory lists **32** repositories, and the script's freshness
  check returns `1` (reported `Total: 32 FRESH: 7 STALE: 25`). Reconciling the
  recorded copy therefore requires correcting that requirement and its scenario
  in the same change, rather than contradicting it silently.
- **Scheduled jobs affected**: `com.developer.workstation-daily-update` (daily
  08:00) and `com.developer.index-refresh` (daily 02:30) both execute the
  installed copies under `~/Developer/scripts/`, not the recorded copies. The
  recorded copies are not executed by any LaunchAgent.
- **Precedent used**: `host-deploy-script-consistency` already establishes the
  snapshot-and-fail pattern for copied scripts, but it is scoped to
  `ai-review/scripts/deploy.sh` alone and does not cover the workstation script
  tree. Prior art for reconciliation also exists as a one-off
  (`4741f899 fix(knowledge-refresh): reconcile source scripts, inventory, and
  approval digest with installed copy`, 2026-09-19) which did not hold, because
  the duplication itself was never removed.
- **Ownership boundaries**:
  - Workstation tooling and its recorded copy: `~/Developer/scripts/` and
    `openspec-store/scripts/`.
  - The daily maintenance job's behavior: owned by
    `ecosystem-tooling-and-skills-upgrade` (extended here).
  - The knowledge-refresh inventory and its approval digest: owned by the
    knowledge-refresh mechanism, whose approved-repository list is consumed by
    `workspace-index-freshness`; this change aligns the recorded copy with the
    executed one rather than changing which repositories are approved.
- **Non-goals**:
  - Not changing which repositories the knowledge-refresh job indexes. The
    direction of reconciliation is settled by evidence rather than assumption:
    every one of the 32 installed entries resolves to an existing Git repository,
    all 12 entries missing from the recorded copy (the `shb/*` set) carry live
    `.gitnexus` and `graphify-out` indexes exactly as the non-`shb` entries do,
    and the installed inventory was edited (2026-09-27) after the recorded copy
    was last reconciled (2026-09-26). Taking the recorded 20-entry copy as
    authoritative would therefore drop 12 actively indexed repositories. Only the
    stale recorded copy changes; deciding whether the shb ecosystem *should* be
    indexed is not reopened here.
  - Not implementing a freshness or refresh capability in
    `refresh-knowledge-indexes.sh`, and not making its freshness check exit `0`.
    The corrected requirement records the freshness outcome; refreshing the 25
    stale indexes so the check can pass is separate work.
  - Not fixing the unrelated defect that `kilo update` exits zero while reporting
    an error, nor the `docfork/docs` upstream path ambiguity; both are recorded in
    the `automate-skill-content-refresh` change.
  - Not addressing the hardcoded repository list in `workspace-worktree-scan.sh`,
    which `workspace-index-freshness` already forbids elsewhere. Recording the
    script does not license the pattern; correcting it is a separate change.
  - Not relocating or renaming any executed script, and not changing the LaunchAgent
    schedules or program paths.
  - Not introducing a new synchronization daemon.
