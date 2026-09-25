# Proposal: Reorganize Workspace Domains and Clean Legacy Artifacts

## Why

The workspace root at `~/Developer/` currently contains 109 items (76 visible, 33 hidden), creating severe navigational friction, command ambiguity, and risk of accidental mutations. Recent content migrations from iCloud, Google Drive, and VDS alongside historical test runs placed dozens of disparate repositories, temporary test scratch folders, dead Python virtual environments, and unreferenced backups flat at the root alongside the 24 active production services. Establishing a structured domain hierarchy (`legacy/`, `apps/`, `study/`, `ai-tooling/`, `migration-archives/`) and purging obsolete scratch directories restores workspace cleanliness and aligns root layout with `AGENTS.md`.

## What Changes

1. **Purge Root Caches and Ephemeral Scraps**: Remove root-level `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.infinity_cache/`, `.knowledge-refresh-test-*/`, `.phase6-field-audit/`, `.workspace-lifecycle-dryrun-*/`, empty `vds/`, `.tmp/`, `tmp/`, `tdt-v2-accept/`, `recovery-pilot/`, and orphaned backups (`mcp-router-backup-20260722/`, `.claude.json.backup`, `.claude-server-commander*`).
2. **Prune Dead Internal Virtualenvs and Stale Worktrees**: Delete obsolete 948 MB `mcp-servers/Code-Index-MCP/venv/` and 1.3 GB `vds-content-migration/WHO-project/worktrees/` checkouts.
3. **Establish Logical Domain Namespaces**: Create dedicated parent directories matching the existing `mobile/`, `infra/`, and `ops-tools/` model:
   - `legacy/`: Group inactive historical checkouts (`ghtk/` 6 repos, `kafka-microservices/` [renamed from `microservices/` to eliminate name collision with `go-microservices`], `ascend-configs/`).
   - `apps/`: Group standalone tools and clients (`camunda/`, `airbridge/`, `invest-bots/`, `githubusers/`, `viettel-excel-updater/`, `tmz-case-challenge/`).
   - `study/`: Group training code and reference materials (`study-examples/`, `ai-training-materials/`).
   - `ai-tooling/`: Group supplemental agent utilities (`mcp-servers/`, `mcp-suite/`, `wiki-mcp-server/`, `claudia/`, `rules/`, `workspace-python-template/`).
   - `migration-archives/`: Group historical migration receipts and tooling (`vds-content-migration/`, `content-migration-manifests/`, `icloud-migration-tools/`).
4. **Relocate Loose Root Configuration Files**:
   - Move `qi_config.yaml` to `~/Developer/qi-bridge/qi_config.yaml` and update stale iCloud paths.
   - Move `skills-lock.json` to `~/Developer/.agents/skills-lock.json`.
   - Relocate `.worktree-execution-contracts-*.md` to `~/Developer/docs/contracts/`.
5. **Update Workspace Documentation**: Update `~/Developer/AGENTS.md`, `CLAUDE.md`, and workspace path maps to reflect the new directory structure.

## Capabilities

### New Capabilities
- `workspace-topology-and-hygiene`: Defines the canonical workspace root domain structure, prohibits bare root cache generation, enforces kebab-case naming, and specifies placement rules for shared configuration and legacy archives.

### Modified Capabilities
(none)

## Impact

- **Affected Paths**: `~/Developer/` root items, `~/Developer/AGENTS.md`, `~/Developer/CLAUDE.md`.
- **Preserved Core Repos**: The 24 active workspace repositories documented in `AGENTS.md` (e.g. `go-microservices`, `openspec-store`, `mcp-router`, `qi-bridge`, and the 19 core Python `tdt-*` / `agent-*` / `jira-*` repositories) remain at their canonical root paths.
- **Rclone & GDrive**: Zero impact on `rclone bisync` loops, which are strictly locked to the 19 Python repo paths in `~/.config/rclone/tdt-filters.txt`.
- **Knowledge Refresh**: Zero disruption to `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`, which tracks only the 20 approved root repos.
- **Storage Yield**: Reclaims ~2.5 GB of dead virtualenv and cache storage; reduces root visible clutter from 76 items down to canonical production roots.
