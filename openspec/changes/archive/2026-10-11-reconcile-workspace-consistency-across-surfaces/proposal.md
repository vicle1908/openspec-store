# Proposal: Reconcile Workspace Consistency Across Surfaces

## Why

Comprehensive audits across workspace specifications, agent guides, repository checkouts, and skills revealed lingering legacy references, scrap files, and documentation drift following the first-class organization namespaces migration:
1. **Spec Path Drift**: `gdrive-ios-and-deployments` and `workspace-topology-and-hygiene` still reference superseded `mobile/` and `ops-tools/` paths rather than canonical `tdt/` and `fpt/` organization namespaces.
2. **Agent Documentation Drift**: `AGENTS.md` and `CLAUDE.md` retain legacy category headers (`### Mobile (1 app, 1 docs)`, `### Operations & Infrastructure`) and legacy path prefixes (`mobile/poems-mobile3-*`, `ops-tools/*`, `infra/fpt-ingenico`).
3. **Workspace Ephemeral Scrap**: 62 `.DS_Store` files exist across top-level workspace directories, causing noise and potential git churn.
4. **Skills Alignment**: Verify that all 96 canonical workspace skills under `.agents/skills/` remain synchronized with `.agents/skills-lock.json` and zero broken symlinks exist.

Reconciling these surfaces guarantees end-to-end consistency across specifications, code checkouts, agent guidance documents, and skill discovery registries.

## What Changes

1. **OpenSpec Spec Harmonization**:
   - Update `gdrive-ios-and-deployments` to target canonical `~/Developer/tdt/poems-mobile3-ios/`.
   - Update `workspace-topology-and-hygiene` to reference canonical organization subtrees (`tdt/`, `fpt/`) rather than superseded `mobile/` and `ops-tools/` categories.

2. **Agent Documentation Synchronization**:
   - Update `AGENTS.md` and `CLAUDE.md` to reference canonical paths:
     - `tdt/poems-mobile3-android/`
     - `tdt/poems-mobile3-docs/`
     - `tdt/tdt-tools/`
     - `tdt/bootstrap-nexus/`
     - `fpt/fpt-ingenico/`
   - Keep `CLAUDE.md` in byte-for-byte synchronization with `AGENTS.md`.

3. **Workspace Hygiene & Junk Purge**:
   - Recursively remove all `.DS_Store` files across `~/Developer/` top-level directories and meta-roots.

4. **Skill Synchronization Verification**:
   - Assert zero drift via `sync-workspace-agent-skills.py --check`.

## Capabilities

### Modified Capabilities
- `gdrive-ios-and-deployments`: Updates the local iOS ingestion destination from `~/Developer/mobile/poems-mobile3-ios/` to canonical `~/Developer/tdt/poems-mobile3-ios/`.
- `workspace-topology-and-hygiene`: Updates domain taxonomy requirements to reflect first-class organization namespaces.

## Impact
- **Affected Files**: `platform/openspec-store/openspec/specs/gdrive-ios-and-deployments/spec.md`, `platform/openspec-store/openspec/specs/workspace-topology-and-hygiene/spec.md`, `AGENTS.md`, `CLAUDE.md`.
- **System Invariants**: Zero impact on running LaunchAgents or external cloud sync rules.
