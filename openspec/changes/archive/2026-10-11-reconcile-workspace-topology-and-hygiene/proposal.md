# Proposal: Reconcile Workspace Topology and Hygiene

## Why

Audits of `~/Developer/` reveal drift from the canonical workspace topology (`docs/WORKSPACE_TOPOLOGY.md`) and the `workspace-topology-and-hygiene` specification:
1. **Root Cache & Scratch Sprawl**: Build and test caches (`.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`) and session artifacts (`pi-session-*.html`, `comprehensive_mcp_native_test.log`) exist loose at workspace root, consuming ~88MB and violating zero-root-cache invariants.
2. **Skills Duplication & Lockfile Sprawl**: A redundant `skills/` directory (44 items), `agent/skills/` directory (44 items), and root `skills-lock.json` (10.6 KB) exist at root, shadowing canonical workspace skills in `.agents/skills/` and violating configuration confinement rules.
3. **Unclassified Project Roots**: Ad-hoc directories (`cursor-account-manager-build/`, `main-db-migrations/`, `ntu-keynote/`) sit flatly at root instead of within designated domain subtrees (`apps/`, `legacy/`, `study/`).

Reconciling these items restores strict root hygiene, enforces canonical skill discovery via `.agents/skills/`, and ensures all projects adhere to first-class organization namespaces and established auxiliary subtrees.

## What Changes

1. **Root Hygiene Purge**:
   - Purge root test and linter cache directories (`.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`).
   - Remove stale probe logs (`comprehensive_mcp_native_test.log`) and session exports (`pi-session-*.html`).
   - Clean sub-repo caches (`ntu-keynote/.pytest_cache/`, `wiki/.pytest_cache/`).

2. **Skills Consolidation & Confinement**:
   - Verify that all 44 skills in `skills/` and `agent/skills/` are already present in `.agents/skills/`.
   - Remove the redundant `skills/`, `agent/` directories and the loose root `skills-lock.json`.
   - Re-verify canonical skills via `sync-workspace-agent-skills.py --check`.

3. **Auxiliary Domain Reclassification**:
   - Move `cursor-account-manager-build/` to `apps/cursor-account-manager-build/`.
   - Move `main-db-migrations/` into `legacy/kafka-microservices/db-migrations/` where its `inventory-service` Flyway scripts belong.
   - Relocate standalone presentation `ntu-keynote/` into `study/ntu-keynote/`.

4. **Topology and Documentation Sync**:
   - Update `docs/WORKSPACE_TOPOLOGY.md` and `AGENTS.md` to reflect the clean top-level hierarchy.

## Capabilities

### Modified Capabilities
- `workspace-topology-and-hygiene`: Strengthens root hygiene requirements to explicitly ban loose skill trees, unconfined skill locks, and rogue build outputs at workspace root.

## Impact

- **Affected Directories**: `~/Developer/` root, `apps/`, `legacy/kafka-microservices/`, `study/`, `docs/WORKSPACE_TOPOLOGY.md`.
- **Tooling Invariants**: Zero impact on `rclone bisync` (which only touches 19 Python repos in `tdt/`), LaunchAgents, and GitNexus inventory.
