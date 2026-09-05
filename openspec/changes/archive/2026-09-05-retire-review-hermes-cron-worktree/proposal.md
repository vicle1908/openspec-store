## Why

Follow-up research to the `workspace-lifecycle-dryrun-2026-09` change corrected two findings: the "139MB orphaned orca checkouts" are actually 0-byte symlinks to canonical repos (PROTECTED Orca registrations — observation data had followed the links), and the `review-hermes-cron` worktree's 8 unmerged commits are content-identical to main's archived `2026-08-25-repair-hermes-cron-run-reliability` record (the complete evidence, including the side-effect incident note, is already on main). The worktree is therefore the only real orca-space reclaimable (~139 MB, mostly generated `graphify-out/`), and its evidence value is preserved without it.

## What Changes

- Record corrected evidence: the six `~/orca/workspaces/agent-core/*` paths are symlinks (PROTECTED aliases), not orphaned checkouts — amending the prior dry-run's findings.
- Retire the `review-hermes-cron` worktree following the gated-cleanup spec's transaction order: (1) verify no live Orca terminal/process, (2) `git worktree remove` from openspec-store, (3) delete the `review-hermes-cron` branch.
- Record the branch tip SHA (`69bf758`) and the identity proof (evidence == main archive) in the change evidence so the retirement is auditable against the archived record.
- Remove the two empty orca dirs (`~/orca/workspaces/tdt-core/`, `~/orca/workspaces/tdt-scheduler/` including its empty `.orca-worktree-trash/`) only if they hold no Orca DB references — checked against `orchestration.db`.

## Capabilities

### New Capabilities

_(none — operational retirement within existing gated-cleanup contract)_

### Modified Capabilities

_(none — `skip_specs: true`; the gated-cleanup spec already defines the retirement transaction this change executes)_

## Impact

- **Affected surfaces**: openspec-store git (worktree + branch removal), `~/orca/workspaces/openspec-store/` directory removal, evidence records in this change.
- **Reclaim**: ~139 MB (97M generated graphify-out, 40M duplicated openspec tree).
- **Risk**: Minimal — evidence identity proven by diff (0 substantive diff lines vs main archive); branch deletion is recoverable from the recorded SHA until git gc.
- **Non-goals**: No changes to the 6 orca symlinks (live registrations), no `tdt/` migration, no root-file reclamation (separate owner review), no retention-inventory amendment.
