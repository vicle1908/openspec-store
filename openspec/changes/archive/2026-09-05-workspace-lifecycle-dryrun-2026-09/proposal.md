## Why

The workspace-lifecycle-gated-cleanup tooling (archived 2026-08-25) has only ever run against test fixtures — no real-workspace observations have been collected, so the workspace's own mandated cleanup path has never been exercised on live state. Meanwhile post-cleanup research surfaced ~139MB of orphaned orca checkouts, 1.1GB stale `tdt/` copies hosting a live service, root-level junk files, and an unmerged review-evidence worktree. These need classification through the governed pipeline, not ad-hoc deletion.

## What Changes

- Collect real authority observations (Git, Orca, OpenSpec, runtime) for the workspace's post-cleanup state: orphaned orca checkouts, root-level untracked files, empty directories, the `review-hermes-cron` worktree, and the `tdt/` runtime-hosting copies.
- Run the existing `workspace-lifecycle.py` dry-run against those observations to produce the first real-workspace classification manifest, applying the approved retention inventory as exclusion layer.
- Record classifications per the gated-cleanup spec: RECLAIMABLE candidates stay review-only proposals; PROTECTED paths (orca roots, live runtime state) are documented, not touched.
- Produce a reviewed manifest and summary under `~/Developer/.workspace-lifecycle/` as durable evidence for a future approved-retirement change.
- Normalize `.claude/` gitignore coverage in the 16 repos that lack it, so repo status reads clean (adjacent repo hygiene, not lifecycle-governed deletion).

## Capabilities

### New Capabilities

_(none — this change exercises existing specs; it produces operational evidence, not new behavior)_

### Modified Capabilities

_(none — the gated-cleanup and retention-policy specs already define the contract this change executes against real data; `skip_specs: true`)_


## Impact

- **Affected surfaces**: `~/Developer/.workspace-lifecycle/` (new manifest output), workspace repos' `.gitignore` (one-line additions), research findings documented in the change's evidence.
- **No deletions, no mutations of governed state** — dry-run only, per the read-only spec requirement. The `tdt/` ai-review service migration is explicitly out of scope (runtime-owner change).
- **Risk**: Minimal. The dry-run tool never mutates; `.gitignore` additions are inert. The main risk is producing an incomplete observation set, mitigated by per-authority verification tasks.
