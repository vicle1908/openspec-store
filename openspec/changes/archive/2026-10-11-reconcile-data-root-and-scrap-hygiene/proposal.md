# Proposal: Reconcile Data Root and Scrap Hygiene

## Why

Audits of `~/Developer/data/` reveal redundant artifacts and ephemeral scrap that violate workspace hygiene boundaries:
1. **Duplicate Skills Sprawl**: `data/skills/` contains 61 skill directories that completely duplicate skills already canonically tracked in `.agents/skills/`. Storing skills inside the shared runtime data store risks version divergence and confuses skill discovery tooling.
2. **Ephemeral Repro Scrap**: `data/harness-prod-repro-qb71_yqg/` (empty) and `data/harness-prod-repro-to792iqu/` are obsolete test reproduction scratchpads that were left uncollected.
3. **Stale Task Artifacts**: Loose markdown and patch files (`tdt-core-agent-config-batch1.patch`, `tdt-observability-integrated-review-task_87be348dd00d.md`) reside loose in `data/` rather than within their respective project repositories or clean capture spools.

Eliminating these items confines all agent skills strictly to `.agents/skills/` and maintains `data/` as a dedicated runtime state store (`state_store.db`, stream stores, spools).

## What Changes

1. **Purge Rogue Data Skills**: Remove `data/skills/` entirely after verifying 100% presence in `.agents/skills/`.
2. **Prune Repro Scrap**: Remove empty and obsolete reproduction test scratchpads (`harness-prod-repro-*`) from `data/`.
3. **Archive Stale Artifacts**: Relocate or prune legacy patch and task markdown dumps from `data/`.
4. **Enforce Hygiene Invariant**: Update `workspace-artifact-retention-policy` and `workspace-topology-and-hygiene` to explicitly prohibit skill checkouts and ad-hoc task patches in `data/`.

## Capabilities

### Modified Capabilities
- `workspace-artifact-retention-policy`: Explicitly mandates immediate pruning of unmanaged ephemeral reproduction runs and prohibits storing skill bundles within runtime data directories.

## Impact
- **Affected Path**: `~/Developer/data/`
- **Zero Regressions**: Active state stores (`state_store.db`, `stream_store`, `capture-spool`, `quarantine`) are preserved untouched.
