## 0. Implementation surface and policy inputs

Resolved implementation surface (task 0.1):

- Owning repository: `openspec-store` (`~/Developer/openspec-store`, git-tracked store).
- Tool directory: `~/Developer/openspec-store/scripts/workspace-lifecycle/` with `tests/fixtures/`, beside the existing `scripts/knowledge-refresh/` tooling.
- Entry command: `python3 ~/Developer/openspec-store/scripts/workspace-lifecycle/workspace-lifecycle.py` (default: read-only dry-run scan).
- Runtime manifest/approval/retirement records: `~/Developer/.workspace-lifecycle/`.
- Read-only inputs: `openspec ... --store openspec-store --json`; read-only `git -C <repo>` queries; read-only `orca` CLI queries; `bash ~/Developer/scripts/knowledge-refresh/knowledge-status.sh --json` (reviewed inventory: `~/Developer/openspec-store/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`); retention inventory `~/Developer/.workspace-retention/retention-inventory.json` (upstream dependency, task 0.2).

- [x] 0.1 Name the implementation surface and owning repository for the inventory, manifest, and retirement adapters. Verify: design.md and tasks.md identify concrete target paths and commands rather than only abstract components.
- [x] 0.2 Declare `workspace-artifact-retention-policy` as a required policy input. Verify: a fixture with a protected retention class is excluded from lifecycle candidates and a candidate class remains review-only.

## 1. Authority adapters and inventory

- [x] 1.1 Define read-only observations for OpenSpec, Git, Orca, and runtime/index ownership, including canonical path, repository/worktree identity, branch or detached revision, activity, and observation timestamp. Verify: fixture inventory covers each authority and preserves conflicting observations.
- [x] 1.2 Implement deterministic classification precedence: `PROTECTED`, `REVIEW_REQUIRED`, `RECLAIMABLE`, `RECLAIMED`, with unknown ownership failing closed. Verify: focused tests cover active OpenSpec, live Orca terminal, runtime ownership unknown, detached unique revision, proven ancestor snapshot, and protected retention class exclusion from candidates.
- [x] 1.3 Integrate the approved workspace/index inventory and `knowledge-status.sh --json` as read-only inputs. Verify: dry-run does not invoke Graphify/GitNexus mutation and skips dirty, watcher-owned, or non-default targets according to existing contracts.

## 2. Dry-run and evidence manifest

- [x] 2.1 Define the machine-readable cleanup manifest schema with path identity, authority observations, classification, blockers, evidence timestamps, proposed owner action, and secret-redaction rules. Verify: schema validation rejects missing identity, stale evidence, and credential-shaped fields.
- [x] 2.2 Implement the default dry-run report and stable repeated-scan behavior. Verify: `git status --porcelain` and an in-scope file-list checksum are identical before and after two consecutive dry-runs.
- [x] 2.3 Record operator approval against an exact plan identity and require a fresh pre-action observation. Verify: stale or mismatched approval is rejected before any lifecycle mutation.

## 3. Ordered retirement gates

- [x] 3.1 Add Orca retirement preconditions for connected/orphaned terminal state, agent state (`working`/`interrupted`), `isPinned`, active child worktrees, host activity, attached PTYs, and file-handle release. Verify: fixtures cover pinned, orphaned, interrupted, child-before-parent, and released-handle transitions.
- [x] 3.2 Add Git preservation gates for clean status, generated-only dirt classification, merge ancestry or squash-equivalence evidence, remote/backup reachability, and detached revision preservation. Verify: unpushed, unique, dirty, and ambiguous candidates remain `REVIEW_REQUIRED`.
- [x] 3.3 Implement ordered transition recording: child Orca worktrees, parent Orca workspace/file handles, Git worktree removal, then branch deletion; defer OpenSpec paths to OpenSpec lifecycle commands. Verify: simulated failure at each transition leaves completed/pending steps auditable and performs no compensating direct deletion.

## 4. Runtime safety and verification

- [x] 4.1 Add bounded runtime ownership checks for processes, LaunchAgents, containers, databases, rollback copies, and index watchers, with unavailable checks reported as `UNKNOWN`. Verify: unknown runtime ownership blocks reclaimability without exposing secrets or request bodies.
- [x] 4.2 Add end-to-end dry-run fixtures for active OpenSpec changes, untracked archive moves, active Orca workspaces, merged deployment snapshots, detached unique worktrees, pinned/child/orphaned Orca records, protected evidence, and secret-containing observations. Verify: each fixture produces the expected classification, blocker, and redacted manifest.
- [x] 4.3 Run strict OpenSpec validation, focused lifecycle tests, manifest schema checks, and a final read-only workspace scan. Verify: no branch, worktree, OpenSpec artifact, runtime state, or generated index is modified by verification.
