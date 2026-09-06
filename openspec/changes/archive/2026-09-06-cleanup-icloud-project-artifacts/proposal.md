## Why

The iCloud folders `project/microservices` and `project/vds` contain over 2,030,747 items, overwhelmingly consisting of transient package manager caches (`node_modules`), build output directories (`build`, `dist`, `target`), compiler caches (`.gradle`, `__pycache__`, `.pytest_cache`), and sync conflict duplicates (`*.corrupted.*`). This massive inode volume saturates macOS iCloud sync daemons (`fileproviderd`, `bird`), causes severe memory leaks and compressor thrashing, and blocks copying or inspecting active project code. Cleaning up these discarded build and cache artifacts while strictly preserving source code and documentation restores responsiveness and unblocks future workspace migration.

## What Changes

- **Inventory and Classification**: Scan `project/microservices` and `project/vds` in iCloud Drive to catalogue transient directories, build artifacts, package caches, and sync duplicates without modifying files.
- **Explicit Removal of Transient/Cache Artifacts**: Target specific non-source hierarchies for deletion:
  - Package manager dependencies: `node_modules`
  - Build and binary targets: `build`, `dist`, `target`, `.gradle`, `out`
  - Python/test caches: `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.hypothesis`, `.coverage`
  - OS metadata and temp files: `.DS_Store`, `*.tmp`, `*.log`
  - iCloud sync conflict copies: `*.corrupted.*`
- **Source and Documentation Preservation**: Strict keep-rule protecting all source code (`.ts`, `.tsx`, `.js`, `.py`, `.go`, `.kt`, `.java`, `.proto`, etc.), configuration/manifests (`package.json`, `build.gradle.kts`, `pom.xml`, `go.mod`, `Dockerfile`, etc.), repository metadata (`.git`), and documentation (`*.md`, `docs/`, `design-artifacts/`).
- **Approval-Gated Mutation**: Show literal commands and dry-run counts before running removals, satisfying safety guardrails.

## Capabilities

### New Capabilities
- `icloud-project-artifact-cleanup`: Defines the safety policies, artifact classification rules, approval gates, and verification criteria for purging transient build/cache directories and conflict artifacts from iCloud project directories while guaranteeing zero loss of source and documentation files.

### Modified Capabilities
None.

## Impact

- **Storage & Inodes (planning estimate superseded by measured outcome)**: Planning estimated a 95%+ reduction; the measured result was 109,046 inodes removed of 2,030,745 (5.37%) — `microservices` −63% (19,852→7,317), `vds` −4.8% (2,010,893→1,914,382). The estimate was wrong because `vds` retains ~1.91M kept-by-design inodes (`.venv` sites, `WHO-project/worktrees/` copies, `.git`/`.git_disabled` object stores, nested project sources) that the keep-list correctly refused to touch; see `evidence/post-cleanup-inode-counts.json`.
  - **Follow-up scope (not in this change)**: further `vds` inode reduction would require a separately approved change covering `.venv`/`worktrees`/`.git_disabled` trees, each with their own keep-analysis.
- **System Stability**: Reduces FileProvider database load. Post-cleanup (2026-09-06 12:5x +07): `fileproviderd` (restarted 11:24) held ~15 MB RSS at 67% CPU processing its eviction backlog, versus the pre-restart daemon that had ballooned to a 20.5 GB footprint (peak 24.0 GB, 83–135% CPU, 1,905 CPU-minutes). `bird` idle (~7 MB RSS). Deletion of ~109K inodes also removed their pending FileProvider tombstone/work items.
- **Non-Goals**:
  - Does NOT alter or delete any source files, configs, or documentation.
  - Does NOT touch directories outside `com~apple~CloudDocs/project/microservices` and `com~apple~CloudDocs/project/vds`.
  - Did NOT delete kept subtrees listed above; measured impact reflects only the approved manifest (694 dirs + 536 files).
