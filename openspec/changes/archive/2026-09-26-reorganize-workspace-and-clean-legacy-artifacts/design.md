# Technical Design: Reorganize Workspace Domains and Clean Legacy Artifacts

## Context

The `~/Developer/` workspace has evolved from a single monorepo into a multi-repo ecosystem housing active Go services, 19 core Python packages, and multiple mobile and infrastructure projects. Recent batch migrations from iCloud, Google Drive, and VDS brought dozens of historical repositories, scratch directories, and migration artifacts directly into the top-level directory without parent domain clustering. Additionally, command-line runs of `pytest`, `mypy`, and `ruff` at the workspace root left cache artifacts outside individual repository boundaries.

This design establishes a clear, non-destructive migration plan to organize disparate directories into structured domain subtrees (`legacy/`, `apps/`, `study/`, `ai-tooling/`, `migration-archives/`), purge verified ephemeral scratch directories, and relocate loose configuration files while preserving all Git histories and avoiding breaking changes to active development workflows.

## Goals / Non-Goals

**Goals:**
- Eliminate top-level root clutter (reducing visible root items from 76 to canonical production roots).
- Group inactive and historical repositories into clear domain subdirectories with preserved Git history.
- Reclaim ~2.5 GB of dead disk space by deleting abandoned Python venvs (`Code-Index-MCP/venv`), dead worktrees (`WHO-project/worktrees`), and root test/lint caches.
- Eliminate repository name confusion by renaming deprecated `microservices/` to `legacy/kafka-microservices/`.
- Ensure zero breakage to active pipelines: `rclone bisync`, GitNexus index refresh, and active LaunchAgents.

**Non-Goals:**
- Modifying any of the 24 active production repositories (`go-microservices`, `openspec-store`, `mcp-router`, `qi-bridge`, `agent-core`, `tdt-*`, `jira-*`, etc.).
- Modifying or reorganizing `mobile/`, `infra/`, or `ops-tools/` (these were previously migrated and structured cleanly).
- Modifying remote cloud storage (Google Drive or iCloud).
- Deleting any historical source code without an existing archive or backup.

## Decisions

### Decision 1: Domain Subtree Grouping Pattern
- **Choice**: Organize unclustered projects into five dedicated subdirectories:
  1. `legacy/`: For deprecated checkouts (`legacy/ghtk/`, `legacy/kafka-microservices/`, `legacy/ascend-configs/`).
  2. `apps/`: For standalone client applications and automation tools (`camunda/`, `airbridge/`, `invest-bots/`, `githubusers/`, `viettel-excel-updater/`, `tmz-case-challenge/`).
  3. `study/`: For reference implementations and training materials (`study-examples/`, `ai-training-materials/`).
  4. `ai-tooling/`: For supplemental agent tools, rules, and MCP servers (`mcp-servers/`, `mcp-suite/`, `wiki-mcp-server/`, `claudia/`, `rules/`, `workspace-python-template/`).
  5. `migration-archives/`: For historical migration logs, receipts, and migration harnesses (`vds-content-migration/`, `content-migration-manifests/`, `icloud-migration-tools/`).
- **Rationale**: Follows the exact operational pattern established by `mobile/`, `ops-tools/`, and `infra/`. Keeps active project paths clean while retaining fast local access to historical and reference code.
- **Alternatives considered**:
  - *Keep everything flat*: Rejected due to severe cognitive load and navigation friction.
  - *Move all legacy projects to external cold storage*: Rejected because user frequently references historical implementation patterns.

### Decision 2: Disambiguate Legacy `microservices`
- **Choice**: Move and rename `~/Developer/microservices` to `~/Developer/legacy/kafka-microservices`.
- **Rationale**: `microservices` is an old Java/Kafka implementation (`vicle1908/kafka-transactional-microservices`) last touched in 2025. It repeatedly creates cognitive and path collision with `go-microservices`, which is the active greenfield production platform.
- **Alternatives considered**:
  - *Keep `microservices` at root*: Causes tab-completion confusion and risks accidental edits.
  - *Delete `microservices`*: Destructive and loses historical transaction patterns.

### Decision 3: Root Loose File Relocations
- **Choice**:
  - `qi_config.yaml` -> `qi-bridge/qi_config.yaml`: The file configures the Qi hybrid search proxy. Its hardcoded iCloud paths will be updated to point to the local workspace.
  - `skills-lock.json` -> `.agents/skills-lock.json`: The lockfile tracks installed skill hashes for `notion-cli`.
  - `.worktree-execution-contracts-*.md` -> `docs/contracts/`: Historical architectural contract documents.
- **Rationale**: The root directory should only contain foundational meta-files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`). All configuration belongs to specific tools or repos.

### Decision 4: Safe Directory Moves and Preserving Git History
- **Choice**: Use atomic filesystem `mv` operations for directory trees. For directories that are standalone Git repositories (e.g. `viettel-excel-updater`, `wiki-mcp-server`, `icloud-migration-tools`), directory moves preserve the embedded `.git` folder intact.
- **Rationale**: Subtree moves preserve full commit history, branches, and tags.

## Risks / Trade-offs

- **[Risk] Path breakage in local scripts or agent prompts** → *Mitigation:* Audit of `~/.zshrc`, LaunchAgents, and `knowledge-refresh-inventory.tsv` confirmed zero active dependencies on the candidate legacy paths. `AGENTS.md` and `CLAUDE.md` will be updated simultaneously to document the new paths.
- **[Risk] Unintended file loss during scratch purge** → *Mitigation:* The purge list is strictly limited to verified empty directories, ephemeral caches (`.mypy_cache`, `.pytest_cache`), and redundant backups (`mcp-router-backup-20260722`). No unique source code is included in the purge.
- **[Risk] Collision during multi-agent concurrent work** → *Mitigation:* Standard single-writer execution rule applied; operations will be batched sequentially.

## Migration Plan

1. **Phase 1: Verification & Pre-flight Snapshot**: Record pre-migration file listing and disk usage baseline.
2. **Phase 2: Purge Ephemeral Scraps & Root Caches**: Remove confirmed root cache folders and empty directories.
3. **Phase 3: Namespace Scaffolding**: Create parent directories (`legacy/`, `apps/`, `study/`, `ai-tooling/`, `migration-archives/`).
4. **Phase 4: Atomic Relocations**: Move projects and loose files into their designated domain folders.
5. **Phase 5: Internal Bloat Pruning**: Remove dead venvs (`mcp-servers/Code-Index-MCP/venv`) and dead worktrees (`vds-content-migration/WHO-project/worktrees`).
6. **Phase 6: Documentation & Verification**: Update `AGENTS.md` and `CLAUDE.md`, run verification checks, and confirm store validity.
