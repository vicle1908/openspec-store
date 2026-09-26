# Proposal: Reconcile Workspace Topology and Knowledge Sync Paths

## Why

Post-migration path drift between actual on-disk directory layouts and workspace governance documentation causes broken synchronization pipelines and inaccurate architectural mapping across development tools.

Following the clean-break reorganization of repositories into first-class organization namespaces (`platform/`, `tdt/`, `vds/`, etc.), `docs/WORKSPACE_TOPOLOGY.md` incorrectly documented a phantom intermediate `~/Developer/shared/` directory, while `scripts/knowledge-refresh/sync-notion-knowledge.sh` continues referencing historical paths (`${WORKSPACE_ROOT}/openspec-store`), preventing automated discovery and Notion catalog synchronization of 422 governed capability specifications. Concurrently, `platform/openspec-store/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` still contains legacy flat repository paths instead of the canonical 20-repo organization paths in `~/Developer/scripts/`, and `knowledge-refresh-approval.sha256` in both locations retains the stale digest `d030ceb6...` instead of the active inventory digest `5a0366fa...`, causing `refresh-knowledge-indexes.sh` to abort with `inventory SHA-256 mismatch` and blocking the `com.developer.index-refresh` LaunchAgent. Furthermore, several top-level organizational and operational directories (`apps/`, `ai-tooling/`, `study/`, `migration-archives/`, `legacy/`) and related wiki concepts lack formal canonical documentation.

## What Changes

1. **Reconcile Workspace Topology Documentation (`docs/WORKSPACE_TOPOLOGY.md`)**:
   - Remove the nonexistent `shared/` directory hierarchy.
   - Formally document the first-class **Workspace Meta-Roots** (`docs/`, `scripts/`, `wiki/`, `data/`, `sensitive-quarantine/`) located directly at `~/Developer/`.
   - Document auxiliary top-level roots (`apps/`, `ai-tooling/`, `study/`, `migration-archives/`, `legacy/`, `cursor-account-manager-build/`, `main-db-migrations/`, `ntu-keynote/`, `.knowledge-refresh/`) and their domain roles.
2. **Fix OpenSpec Path Resolution in Knowledge Sync Script (`sync-notion-knowledge.sh`)**:
   - Update `OPENSPEC_STORE_ROOT` from `${WORKSPACE_ROOT}/openspec-store` to `${WORKSPACE_ROOT}/platform/openspec-store`.
   - Update embedded Python spec catalog discovery snippet `store_specs` from `/Users/androidteam/Developer/openspec-store/openspec/specs` to `/Users/androidteam/Developer/platform/openspec-store/openspec/specs`.
   - Update documentation reference string in generated catalog tables to reflect `platform/openspec-store/openspec/specs/`.
   - Dynamically discover active changes in `platform/openspec-store/openspec/changes/` instead of rendering hardcoded legacy changes.
   - Synchronize edits across both `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh` and its source repository copy in `platform/openspec-store/scripts/knowledge-refresh/sync-notion-knowledge.sh` to maintain zero-diff parity.
3. **Reconcile Knowledge Refresh Inventory and Approval Digest**:
   - Reconcile `knowledge-refresh-inventory.tsv` from `~/Developer/scripts/knowledge-refresh/` to `platform/openspec-store/scripts/knowledge-refresh/` so both source and workstation reflect all 20 canonical repository paths.
   - Recompute and update `knowledge-refresh-approval.sha256` in both locations to the active digest `5a0366fa97474a8acae28546df9054b551fcb5f0143d3582bc5bc501eb469acc`, unblocking the daily `refresh-knowledge-indexes.sh` integrity verification.
4. **Reconcile Stale Workspace Documentation (`wiki/`)**:
   - Update `wiki/concepts/openspec-change-lifecycle.md` to reference `/Users/androidteam/Developer/platform/openspec-store/openspec` instead of the legacy non-namespaced path.
   - Update `wiki/concepts/workspace-domain-topology.md` to reflect the current first-class organization namespaces and workspace meta-roots layout.
5. **Update `organization-namespaces` Specification**:
   - Extend `organization-namespaces` capability to formally specify Workspace Meta-Roots and tooling path resolution invariants.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `organization-namespaces`: Extend requirements to define first-class Workspace Meta-Roots (`docs/`, `scripts/`, `wiki/`, `data/`, `sensitive-quarantine/`), document auxiliary domain roots, and require automated maintenance scripts to resolve canonical repository paths without assuming legacy flat layouts.

## Non-Goals
- Moving on-disk directories into a new `shared/` directory (violates zero-disruption clean-break policy and breaks existing LaunchAgents).
- Modifying repository layouts within `platform/`, `tdt/`, `vds/`, `ascend/`, `ghtk/`, or `fpt/`.
- Changing GitNexus or Graphify indexing engine parameters or schedules.
- Re-architecting the Notion sync payload schema or API authentication.

## Affected Ownership Boundaries
- **Platform Infrastructure**: Governs `docs/WORKSPACE_TOPOLOGY.md`, `scripts/knowledge-refresh/`, and `platform/openspec-store`.
- **Knowledge Base & Wiki**: Governs `wiki/concepts/`.
- **Cross-Agent Tooling**: Affects path resolution for Notion sync and OpenSpec CLI consumers across Claude Code, Codex, OMP, and Hermes.

## Impact
- Restores automated OpenSpec catalog generation in `sync-notion-knowledge.sh` from 0 discovered specs to all 422 governed specifications.
- Resolves `inventory SHA-256 mismatch` failure in `refresh-knowledge-indexes.sh`, restoring clean automated nightly re-indexing by `com.developer.index-refresh`.
- Aligns engineering documentation and repository source copies with verified on-disk reality across all agent sessions.
- Zero breaking changes to existing git worktrees, active LaunchAgents, or developer shell configurations.
