# Proposal: Migrate and Purge All iCloud Code (Option 3)

## Summary

Execute a comprehensive, fail-closed migration of all identified source code repositories, microservice projects, utility scripts, study code, Android projects, Telegram bots, MCP servers, and sensitive credentials/configs from iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/`) to `~/Developer/`, followed by verified two-way reconciliation and bounded deletion of cloud sources and root packaging debris.

## Motivation & Problem Statement

Development projects and source code repositories hosted in iCloud Drive suffer from several critical issues:
1. **APFS Dataless State:** Over 260,000 files in iCloud Drive are currently in an APFS dataless state (`SF_DATALESS` / `st_blocks == 0`), causing CLI file operations (`cp`, `tar`, `ditto`, `git`) to hang or fail on unmaterialized pointers.
2. **Uncommitted Code Loss Risk:** Critical repositories like `project/microservices` (264 uncommitted changes on branch `feature/temporal-workflow-orchestration`) and `viettel/Nangluc/excel-updater` (58 untracked files, 0 commits) reside solely in iCloud with no local duplicate.
3. **Workspace Fragmentation:** Source code is scattered across `project/`, `viettel/`, `timecompany/`, `books/`, `ghtk/`, `invest/`, `AI/`, `ascend/`, `github/`, `.claude/`, `.vds/`, and `main/`, while root iCloud contains unpacked wheel debris (`_internal/`, `base64/`, `METADATA`, etc.).
4. **iCloud Sync Daemon Throttling:** The macOS `bird` sync daemon frequently throttles and corrupts active Git trees and build caches.

## Proposed Solution (Option 3: Full Migration - Expanded)

Migrate all source code projects, utility scripts, and developer configurations into structured local destinations under `~/Developer/`, preserving directory hierarchy while strictly pruning transient/cache directories (`node_modules`, `.venv`, `.gradle`, `build`, `dist`, `__pycache__`):

### Comprehensive Scope Matrix

| Category | Source Path | Proposed Local Destination | Total Files | Eligible Code Files | Strategy |
|---|---|---|---|---|---|
| **Cat 1: Active / Uncommitted** | `project/microservices` | `~/Developer/microservices` | 5,984 | ~1,698 (19.1 MB) | Cocoa hydrate + manifest copy + git preserve |
| **Cat 1: Active / Uncommitted** | `viettel/Nangluc/excel-updater` | `~/Developer/viettel-excel-updater` | 4,969 | ~84 (0.8 MB) | Cocoa hydrate + manifest copy + git init/commit |
| **Cat 1: Android Project** | `timecompany/test/githubusers` | `~/Developer/githubusers` | 36 | 36 (65.1 KB) | Cocoa hydrate + manifest copy |
| **Cat 1: Database Migrations** | `main` | `~/Developer/main-db-migrations` | 10 | 10 (18.6 KB) | Direct manifest copy |
| **Cat 2: Microservice Monorepos**| `project/camunda7` | `~/Developer/camunda7` | 28,927 | ~1,214 (6.1 MB) | Cocoa hydrate + manifest copy (skip .gradle/build) |
| **Cat 2: Integration Projects** | `project/camunda` | `~/Developer/camunda-loan-approval` | 45,565 | ~212 (1.8 MB) | Cocoa hydrate + manifest copy |
| **Cat 2: Integration Projects** | `project/airbridge` | `~/Developer/airbridge` | 4,417 | ~86 (2.8 MB) | Cocoa hydrate + manifest copy (skip .venv) |
| **Cat 2: Integration Projects** | `project/tmz` | `~/Developer/tmz-case-challenge` | 474 | ~50 (1.8 MB) | Cocoa hydrate + manifest copy (skip node_modules) |
| **Cat 3: Utility Scripts** | `ghtk/project/script/catalog-v2` | `~/Developer/ghtk-catalog-v2` | 47 | ~18 (0.1 MB) | Cocoa hydrate + manifest copy |
| **Cat 3: CI/CD Devops** | `ghtk/training/cicd` | `~/Developer/ghtk-training-cicd` | 3 | 3 (12.4 KB) | Direct manifest copy |
| **Cat 3: Study Source Code** | `books/.../Go by Example Source Code` | `~/Developer/study-examples/go-by-example` | 463 | 463 (1.2 MB) | Cocoa hydrate + manifest copy (isolate from book epubs/pdfs) |
| **Cat 3: Study Source Code** | `books/.../Learning-Spring-Boot-4-main` | `~/Developer/study-examples/spring-boot-4` | 199 | 199 (0.8 MB) | Cocoa hydrate + manifest copy |
| **Cat 3: Telegram Bots** | `invest` | `~/Developer/invest-bots` | 578 | ~578 (381.5 MB) | Cocoa hydrate + manifest copy |
| **Cat 4: MCP Servers & AI** | `AI/mcp/server` | `~/Developer/mcp-servers` | 184,391 | ~4,963 (39.8 MB*) | Cocoa hydrate + manifest copy (skip node_modules/qdrant DB) |
| **Cat 4: AI Projects** | `AI/claudia` | `~/Developer/claudia` | 71,504 | ~369 (7.4 MB) | Cocoa hydrate + manifest copy (skip node_modules) |
| **Cat 5: Root Debris** | `_internal/`, `METADATA`, etc. | *None* | 35 | 0 | Direct verification & unlinking |
| **Cat 6: Utility & Static Analysis** | `ghtk/project/script/` | `~/Developer/ghtk-scripts` | 40 | 40 (108.9 KB) | Cocoa hydrate + manifest copy |
| **Cat 6: Utility & Static Analysis** | `ghtk/detekt/` | `~/Developer/ghtk-detekt` | 3 | 3 (56.5 KB) | Cocoa hydrate + manifest copy |
| **Cat 6: Configs & Credentials** | `ascend/` (code & configs) | `~/Developer/ascend-configs` | 714 | ~20 (0.5 MB) | Cocoa hydrate + manifest copy |
| **Cat 6: Configs & Credentials** | `ascend/` (keys & certs) | `~/Developer/sensitive-quarantine/ascend` | 3 | 3 (15.2 KB) | Cocoa hydrate + quarantine copy (0700/0600) |
| **Cat 6: Configs & Credentials** | `github/github-recovery-codes.txt` | `~/Developer/sensitive-quarantine/github` | 1 | 1 (206 B) | Cocoa hydrate + quarantine copy (0700/0600) |
| **Cat 6: Configs & Credentials** | `.claude/` | `~/Developer/claude-icloud-backup` | 7 | 7 (32.2 KB) | Cocoa hydrate + manifest copy |
| **Cat 6: Configs & Credentials** | `.vds/.env` | `~/Developer/sensitive-quarantine/vds` | 1 | 1 (7.4 KB) | Quarantine copy (0700/0600) |

*\* Note on `AI/mcp/server`: Excludes generated Qdrant vector database (`qdrant_storage/`, ~4 GB) and `node_modules` to protect APFS headroom.*
*\* Note on `books/`: Only code subdirectories are migrated; ePub and PDF documents remain in iCloud Drive.*

## Success Criteria

1. 100% of eligible source code, utility scripts, and configuration files across Categories 1–6 are materialized, copied to `~/Developer/`, and recorded in migration manifests.
2. Read-back verification (`--verify-only`) passes with 0 failures, 0 missing files, and 0 checksum mismatches.
3. Sensitive files (`.env*`, credentials, `.pem`, `.key`, recovery codes) are isolated in `sensitive-quarantine/` with `0700` directory and `0600` file modes.
4. Cloud source directories are deleted bottom-up only after passing the two-way reconciliation audit gate.
5. Root debris in iCloud Drive is purged cleanly without affecting personal documents (`SHB/`, `TDT/`, `candidate/`, `books/*.epub`, etc.).
6. APFS disk headroom remains safely above 30 GB throughout execution.

## Risks & Mitigations

- **Risk: APFS Volume Exhaustion during Hydration.**
  *Mitigation:* Local APFS headroom is currently 56.0 GB free. Pruning `node_modules`, `.gradle`, `.venv`, `qdrant_storage`, and non-code book documents (`.epub`, `.pdf`) limits total ingested payload to <4.5 GB, preserving >50 GB headroom.
- **Risk: Sync Daemon (`bird`) Saturation.**
  *Mitigation:* Use directory-level pruning via Cocoa `enumerator.skipDescendants()` to prevent traversal into excluded directories. Partition hydration into per-project batches with file-level `brctl download` triggers.
- **Risk: Accidental Deletion of Personal Files.**
  *Mitigation:* Strict destination existence checks (`dest.exists()`) immediately prior to unlinking each file. Personal directories (`SHB/`, `TDT/`, `candidate/`, `che/`, `family/`, `fcfc/`, etc.) and non-code assets in `books/` are hard-excluded from deletion scope.
