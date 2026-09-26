# Design: Reconcile Workspace Topology and Knowledge Sync Paths

## Context

See `proposal.md` for motivation and background.

The workstation operates under a clean-break policy established during the organization namespace reorganization (`organize-workspace-by-organization-namespaces`). Repositories were moved into flat organization directories (`platform/`, `tdt/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`). Universal meta-roots (`docs/`, `scripts/`, `wiki/`, `data/`, `sensitive-quarantine/`) and auxiliary domain roots (`apps/`, `ai-tooling/`, `study/`, `migration-archives/`, `legacy/`) were retained directly at `~/Developer/`.

However, two categories of documentation and automation defects remain:
1. `docs/WORKSPACE_TOPOLOGY.md` documented a fictional `~/Developer/shared/` tree that was never created on disk.
2. `scripts/knowledge-refresh/sync-notion-knowledge.sh` hardcodes `${WORKSPACE_ROOT}/openspec-store`, which ceased to exist when `openspec-store` became `platform/openspec-store`.

## Goals / Non-Goals

**Goals:**
- Align `docs/WORKSPACE_TOPOLOGY.md` with verified on-disk reality across all directories.
- Fix `scripts/knowledge-refresh/sync-notion-knowledge.sh` to resolve `openspec-store` at `${WORKSPACE_ROOT}/platform/openspec-store` and discover all 422 specs.
- Update outdated wiki concepts (`wiki/concepts/openspec-change-lifecycle.md` and `wiki/concepts/workspace-domain-topology.md`).
- Add a runtime preflight assertion in `sync-notion-knowledge.sh` so future path relocations fail fast rather than silently publishing 0 specs.
- Reconcile `knowledge-refresh-inventory.tsv` (20 canonical organization paths) from `~/Developer/scripts/knowledge-refresh/` to `platform/openspec-store/scripts/knowledge-refresh/`.
- Recompute and update `knowledge-refresh-approval.sha256` (`5a0366fa97474a8acae28546df9054b551fcb5f0143d3582bc5bc501eb469acc`) across both directories to unblock `refresh-knowledge-indexes.sh --check`.
**Non-Goals:**
- Creating a `~/Developer/shared/` directory or moving any files on disk.
- Modifying GitNexus index structures or Graphify schemas.
- Changing `com.developer.index-refresh` LaunchAgent schedules or behavior.

## Decisions

### 1. Reconcile Documentation to Reality (No Directory Relocation)
*Decision*: Update `docs/WORKSPACE_TOPOLOGY.md` and wiki documentation to reflect the actual flat meta-roots at `~/Developer/`, rather than creating a `shared/` directory.
*Rationale*: Creating a `shared/` directory would break hardcoded paths across active LaunchAgents (`com.developer.workstation-daily-update`, `com.developer.index-refresh`), shell profiles, and existing git worktrees. Reflecting verified on-disk reality honors the zero-disruption invariant.
*Existing Pattern*: `scripts/workstation-daily-update.sh` already references `export STORE_DIR="${HOME}/Developer/platform/openspec-store"`.

### 2. Parameterize, Synchronize, and Assert OpenSpec Store Path in `sync-notion-knowledge.sh`
*Decision*:
1. Update `readonly OPENSPEC_STORE_ROOT="${WORKSPACE_ROOT}/platform/openspec-store"`.
2. Update the embedded Python catalog generator to read from `${OPENSPEC_STORE_ROOT}/openspec/specs`.
3. Add a fail-closed preflight check: if `len(all_specs) == 0`, exit with non-zero status code and descriptive error log, preventing silent Notion page truncation.
4. **Bidirectional Source Reconciliation**: Reconcile both `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh` and the source repository copy in `platform/openspec-store/scripts/knowledge-refresh/sync-notion-knowledge.sh` simultaneously so future syncs or checkouts do not reintroduce stale paths.
*Rationale*: Fail-closed validation catches path drift immediately, and dual-file reconciliation prevents source repository divergence.

### 3. OpenSpec Specification Delta Isolation Invariant
*Decision*: Delta specifications under `changes/<change>/specs/<capability>/spec.md` strictly utilize `## ADDED Requirements` or `## MODIFIED Requirements`. Main specifications under `openspec/specs/` SHALL remain entirely untouched during active planning and implementation.
*Rationale*: Prematurely creating or modifying main specs in `openspec/specs/` prior to archiving causes collision errors during `openspec validate` and violates the OpenSpec change lifecycle contract. Main specs are synthesized exclusively at `openspec archive` time.
### 4. Reconcile Approved Knowledge Inventory and SHA-256 Digest
*Decision*: Copy the canonical 20-repository `knowledge-refresh-inventory.tsv` from `~/Developer/scripts/knowledge-refresh/` to `platform/openspec-store/scripts/knowledge-refresh/`, then write the verified SHA-256 digest (`5a0366fa97474a8acae28546df9054b551fcb5f0143d3582bc5bc501eb469acc`) to `knowledge-refresh-approval.sha256` in both directories.
*Rationale*: `refresh-knowledge-indexes.sh` strictly enforces that `shasum -a 256 "$INVENTORY_FILE"` equals the first field of `"$APPROVAL_FILE"`. Both files currently hold the obsolete digest `d030ceb6...` from prior to the namespace migration, causing `com.developer.index-refresh` to fail with `inventory SHA-256 mismatch`. Reconciling both copies ensures identical source repository tracking and unblocks automated indexing.

### 5. Transaction Boundaries
- All edits are documentation, script, and specification updates.
- Edits in `scripts/knowledge-refresh/sync-notion-knowledge.sh` (both in `~/Developer/` and `platform/openspec-store/`) must maintain execution compatibility under macOS Bash 3.2+ and POSIX subshells.
- Main specs in `openspec/specs/` must remain clean and unmodified until archive.
- The change is validated via read-only dry-run (`sync-notion-knowledge.sh --dry-run --section specs`) and `refresh-knowledge-indexes.sh --check` before committing.
## Risks / Trade-offs

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Notion sync overwrites remote page with altered markdown formatting | Low | Dry-run validation confirms spec counts and markdown generation match expectations prior to execution. |
| Incomplete path coverage across obscure scripts | Low | Grep verification across all files in `scripts/` and `docs/` confirms no other dangling `${WORKSPACE_ROOT}/openspec-store` references exist. |
| Inventory digest mismatch blocks index refresh | High | Synchronize inventory files first, recompute digest, write to approval files, and run `refresh-knowledge-indexes.sh --check` to verify exit code 0. |
