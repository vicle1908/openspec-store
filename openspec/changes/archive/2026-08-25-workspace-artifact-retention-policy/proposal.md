## Why

Workspace cleanup keeps colliding with categories that have different owners, so the same sweep keeps mixing safe caches, active index state, persistent databases, and retained evidence into one ambiguous cleanup problem.

## What Changes

- Define reviewed protected classes for workspace state:
  - active index state
  - generated index or cache
  - tracked permanent fixture
  - temporary or ephemeral test fixture
  - runtime state or database
  - retained evidence or report
  - retained rollback or snapshot
  - operator-owned preserved file
- Define policy states consistently across proposal, spec, and inventory: `PROTECTED`, `REVIEW_REQUIRED`, `RECLAIMABLE`, and `RECLAIMED`.
- Add a retention inventory contract for exact path membership, owner, justification, provenance, last-observed reference, and policy state.
- Store the operational inventory at `~/Developer/.workspace-retention/retention-inventory.json`; the OpenSpec artifacts remain the normative contract.
- Add review gate and future reclamation rules for candidate state so any later cleanup depends on evidence, age, owner consent, and service status rather than naming conventions.
- Make `workspace-artifact-retention-policy` a prerequisite input to `workspace-lifecycle-gated-cleanup`; lifecycle cleanup SHALL consume protected retention classes as exclusions.
- Consume the existing reviewed workspace inventory, Graphify/GitNexus ownership, and freshness contracts rather than duplicating them.
- Explicitly exclude branch/worktree retirement, OpenSpec archive operations, index mutation, and any immediate deletion.

## Capabilities

### New Capabilities

- `workspace-artifact-retention-policy`: Reviewed classification, ownership, and reclamation gates for the eight retention classes: active index state, generated index or cache, tracked permanent fixtures, temporary or ephemeral test fixtures, runtime state or databases (including retained logs), retained evidence or reports, retained rollback or snapshots, and operator-owned preserved files.

### Modified Capabilities

- None. Existing index-freshness and generated-artifact ownership contracts remain authoritative.

## Non-Goals

- No branch or worktree deletion.
- No OpenSpec archive or change completion.
- No Graphify/GitNexus mutation, refresh, repair, or version upgrade.
- No removal of files, folders, databases, logs, backups, credentials, or test fixtures in the first version.
- No reading, copying, hashing, or exposing credential values.
- No filesystem sweep heuristics based only on name or age.

## Ownership Boundaries

- Index owners own Graphify, GitNexus, and generated state ownership.
- Runtime owners own persistent databases, state stores, logs, LaunchAgents, and rollback copies.
- Evidence owners own retained reports and verification records.
- The retention policy defines classification and protection, not deletion authority.

## Risks

- Some generated state overlaps with active index ownership, so conservative classification will leave more items review-required than reusable today.
- Reclamation without runtime coverage could break active services; the initial policy therefore remains protective and manual.
- Overprotective classification may slow cleanup velocity, but it prevents accidental evidence or state loss.

## Open Questions

- Policy storage and mandatory runtime/state owners are resolved in `design.md` under “Resolved Decisions”.
