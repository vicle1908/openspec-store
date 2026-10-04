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
    executed inventory (32 entries) is treated as accurate because every entry
    resolves to a directory that exists; only the stale recorded copy changes.
  - Not fixing the unrelated defect that `kilo update` exits zero while reporting
    an error, nor the `docfork/docs` upstream path ambiguity; both are recorded in
    the `automate-skill-content-refresh` change.
  - Not addressing the hardcoded repository list in `workspace-worktree-scan.sh`,
    which `workspace-index-freshness` already forbids elsewhere. Recording the
    script does not license the pattern; correcting it is a separate change.
  - Not relocating or renaming any executed script, and not changing the LaunchAgent
    schedules or program paths.
  - Not introducing a new synchronization daemon.
