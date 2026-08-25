## Why

Workspace cleanup currently crosses OpenSpec, Git, Orca, running services, and retained evidence without one authoritative safety gate, so a branch or worktree can appear merged while still hosting live terminals, untracked work, or the only copy of an artifact.

## What Changes

- Add a reviewed workspace inventory that correlates:
  - OpenSpec active changes, incomplete tasks, untracked archive moves, and retained evidence.
  - Git branches, worktrees, detached commits, merge ancestry, uncommitted files, and unpushed commits.
  - Orca worktree lifecycle state, host activity, live terminals, attached PTYs, and active agents.
  - Runtime ownership signals for services, LaunchAgents, containers, and index watchers.
- Add deterministic candidate classification: `PROTECTED`, `REVIEW_REQUIRED`, `RECLAIMABLE`, or `RECLAIMED`, with a reason and evidence reference for every path.
- Add a read-only dry-run report as the default operation. It SHALL produce a machine-readable manifest and a human-readable summary without deleting, pruning, resetting, checking out, pushing, archiving, or staging anything.
- Add fail-closed retirement gates for active OpenSpec work, non-generated uncommitted or untracked files, live Orca sessions, running processes, detached commits not proven elsewhere, unpushed history, and unresolved squash-merge equivalence.
- Define ordered retirement: close or retire Orca state first, verify Git content and reachability second, remove worktrees through the owning lifecycle tool third, and delete branches only after the worktree is gone and preservation evidence is recorded.
- Preserve existing Graphify/GitNexus freshness ownership. This change SHALL consume their status where relevant but SHALL NOT mutate indexes or duplicate the canonical refresh path.
- Consume `workspace-artifact-retention-policy` as the artifact-protection source: protected retention classes SHALL be exclusions for lifecycle cleanup, and candidate artifacts SHALL remain review-only.
- Emit an auditable cleanup manifest recording operator intent, evidence timestamps, ownership decisions, selected paths, skipped paths, and final outcomes.

## Capabilities

### New Capabilities

- `workspace-lifecycle-gated-cleanup`: Cross-system inventory, classification, dry-run reporting, and fail-closed retirement of stale Git/Orca/OpenSpec workspace state.

### Modified Capabilities

- None. Existing index-freshness and generated-state contracts remain authoritative and are consumed rather than redefined.

## Non-Goals

- No automatic deletion of files, folders, branches, worktrees, OpenSpec changes, evidence, caches, databases, rollback copies, or credentials.
- No `git push`, force push, reset, clean, checkout, branch deletion, or worktree removal without an explicit approved cleanup action.
- No OpenSpec archive operation or active-change completion; archive integrity remains owned by the OpenSpec lifecycle.
- No Graphify or GitNexus refresh, repair, version upgrade, or generated-index mutation.
- No cleanup of temporary or generated artifacts; protected retention classes and candidate artifacts are governed by `workspace-artifact-retention-policy`, which this change consumes as an exclusion and gating layer.
- No reading, copying, hashing, or exposing credential values.

## Ownership Boundaries

- Orca owns Orca-managed worktree visibility, terminal, agent, and workspace lifecycle state.
- Git owns branch, worktree, ancestry, and uncommitted-content facts.
- OpenSpec owns active-change, task, archive, and canonical-spec state.
- Runtime/service owners own process, LaunchAgent, container, database, and rollback-copy liveness.
- The cleanup report correlates these authorities but does not replace any of them.

## Risks

- Git merge ancestry can miss squash-merged content; branch deletion requires an explicit equivalence check.
- Generated Graphify/GitNexus changes can make a clean worktree appear dirty; generated-only changes still require ownership confirmation.
- Orca can retain active terminals after an agent reports completion; filesystem age and Git cleanliness are insufficient evidence.
- Unpushed local history may have no off-machine backup; cleanup MUST remain blocked until preservation is confirmed.

## Open Questions

- Approval identity, manifest storage, and runtime adapter scope are resolved in `design.md` under “Open Questions (Resolved for Initial Design)”.
