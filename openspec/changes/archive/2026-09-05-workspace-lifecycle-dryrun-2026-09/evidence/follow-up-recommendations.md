# Follow-up Recommendations — workspace-lifecycle-dryrun-2026-09

Manifest: `evidence/cleanup-manifest.json` (plan identity `dfdc6e33512837dfe0d42d04646815bc66b2dec856fcf0a02585f4a423bfae5e`)
Classifications: 34 paths scanned — 2 PROTECTED, 32 REVIEW_REQUIRED, 0 RECLAIMABLE.

The dry-run fail-closed result is correct per spec: none of the observed paths carry
the provenance (retention entry, merged-ancestry proof, or runtime-owner release)
that the gated-cleanup spec requires before reclaimability can be proposed. The
follow-ups below are what each class needs to become actionable.

## 1. Orca orphaned checkouts — need a retention-inventory amendment

Manifest classification: `REVIEW_REQUIRED` (`reclaimability_not_proven`) for the 6
orphaned checkouts under `~/orca/workspaces/agent-core/` (~139 MB total) and the 2
empty orca dirs.

Why blocked: the retention inventory entry for `~/.orca` covers the Orca application
root as runtime state (PROTECTED). The orphaned checkouts inside it have no entries
of their own, and my observations carry no proof that no Orca agent/terminal/session
still references them — the observation file records git-side facts only.

Recommended follow-up change: extend the observation set with Orca-authority facts
(agent state per workspace, pin status, terminal references — via Orca's own state
under `~/.orca`), then amend the retention inventory with per-path entries carrying
that provenance. After amendment review, a future dry-run would classify these
RECLAIMABLE and an approved-retirement change could act.

## 2. `tdt/` ai-review migration — runtime-owner change, out of cleanup scope

Manifest classification: `PROTECTED` (live runtime service).

`~/Developer/tdt/deployments/ai-review/` hosts the running `com.tdt.ai-review`
LaunchAgent (uvicorn on 127.0.0.1:8090). The sibling deployment root
`~/.tdt/deployments/` (outside the workspace) already hosts webhook-receiver and has
an empty `ai-review/` slot. Migration = redeploy app to `~/.tdt/deployments/ai-review/`,
update the plist paths, restart, verify port 8090 healthy — then `~/Developer/tdt/`
(1.1 GB of stale repo copies) loses its runtime owner and can be re-observed.

Recommended follow-up change: `migrate-ai-review-deployment-home` (skip_specs runtime
change, owned with the service's own tooling). Cleanup only consumes its outcome.

## 3. Root junk files — closest to actionable, still need owner review

Manifest classification: `REVIEW_REQUIRED` for all 15 root files (omniroute review
bundles ×6, git bundle, shell artifacts, stale plans).

None is referenced by a running service or retention entry, so after an owner
review confirms no archival value, these would classify `RECLAIMABLE` in a follow-up
dry-run that adds a `retention_inventory` amendment or owner-release provenance. The
review-evidence bundles (omniroute dialects) relate to changes already archived
(2026-08-24/25 era); the change directories themselves hold the canonical record.

## 4. review-hermes-cron worktree — evidence value decision needed

Manifest classification: `REVIEW_REQUIRED` (8 unmerged commits; unique commits touch
the archived `2026-08-25-repair-hermes-cron-run-reliability` directory).

The underlying change is archived in the main store; the worktree's unique commits are
review-side evidence (provenance corrections, a side-effect incident note). Decision
needed: merge the evidence into the archived record (archive dirs are immutable —
would need an append-only evidence addendum elsewhere) or record the branch tip SHA in
the store and retire the worktree. Not decidable by classification alone.

## 5. Empty dirs and low-risk strays

`deployments/`, `poems-mobile3-*` (0 bytes each) classify REVIEW_REQUIRED only because
unknown-ownership defaults fail closed. An owner confirmation makes them trivially
reclaimable in the next cycle. `wiki-mcp-server/` (38 MB, not a git repo, no config
references — wiki MCP runs via mcp-router), `wiki-cron-validator/`, `ntu-keynote/`
(74 MB), `workspace-python-template/` need owner review for archival or deletion.

## What this change does NOT enable

Per the gated-cleanup spec, no deletion happens in this change. RECLAIMABLE
classifications (0 here) would still be review-only proposals. All actual reclamation
requires a future approved-retirement change referencing a fresh manifest.
