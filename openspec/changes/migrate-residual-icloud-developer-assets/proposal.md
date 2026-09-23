# Proposal

## Why

Following the completion of the VDS multi-project and Category 1–6 migrations, five residual developer assets (393-file historical `mcp-router-src` trial snapshot, production secrets security guide, lending miniapp architecture docs, investing Streamlit code samples, and a Fable-5 setup script) totaling 439 files (~37.4 MB, 435 dataless) remain stranded in iCloud Drive (`com~apple~CloudDocs`), where they risk sync daemon throttling, unmaterialized pointer loss, and workspace fragmentation.

Migrating these final assets into structured local directories under `~/Developer/` completes the consolidation of all code and technical documentation on local storage, enabling a safe, bounded purge of residual cloud source directories while strictly preserving all personal documents, photos, and book PDFs.

## What Changes

- **Migrate Historical MCP Router Snapshot**: Hydrate and atomically copy `Documents/Codex/2026-07-22/try/work/mcp-router-src` (393 files, 391 dataless) to `~/Developer/mcp-router-backup-20260722/`, preserving full internal package and app directory structure (`apps/`, `packages/`, `docs/`, `tools/`).
- **Migrate Security Guide**: Hydrate and copy `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md` to `~/Developer/docs/PRODUCTION_SECRETS_SECURITY_GUIDE.md`.
- **Migrate Lending Miniapp Documentation**: Hydrate and copy `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe` (14 files, 12 dataless) to `~/Developer/lending-miniapp-docs/`, preserving the `diagrams/` subdirectory.
- **Migrate Study Source Code**: Hydrate and copy `books/ai/2025/Investing for Programmers/investing-for-programmers-main` (30 files, 30 dataless) to `~/Developer/study-examples/investing-for-programmers/`.
- **Migrate Setup Script**: Copy `Downloads/setup-fable-5.sh` to `~/Developer/scripts/setup-fable-5.sh`.
- **Asynchronous Cocoa Hydration**: Use `hydrate_pilot.swift` to trigger background materialization via Apple's native `FileManager.default.startDownloadingUbiquitousItem(at:)`, followed by non-blocking `os.lstat` polling (`st_blocks > 0`) and atomic ingestion via `content_migration.py`.
- **Manifest Recording and Digest Verification**: Generate individual JSON manifests for each migrated asset and verify 100% SHA-256 digest and byte-count equality via `--verify-only`.
- **Controlled Fail-Closed Purge**: After two-way reconciliation passes with 0 failures, safely unlink the migrated cloud source files and prune empty parent directories, while strictly protecting all personal non-code files.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `icloud-full-code-migration`: Extend migration, verification, and controlled purge scope to include residual developer assets across `Documents/`, `Desktop/`, `books/`, and `Downloads/`.

## Impact

- **Affected Systems**: macOS iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/`) and local Developer roots (`~/Developer/`).
- **Ownership Boundaries**: Only developer code, configurations, and technical markdown documents are migrated and purged. Personal directories (`SHB/`, `TDT/`, `candidate/`, `che/`, `family/`, `fcfc/`, `interview/`, `loan/`, `pic/`, `thue/`, `timecompany/`) and non-code reading materials (`books/*.pdf`, `books/*.epub`) are completely untouched.
- **Live Projects Protection**: The live `~/Developer/mcp-router` working repository is protected; the historical trial snapshot is routed to `~/Developer/mcp-router-backup-20260722/` without touching active development checkouts.

## Non-Goals

- No migration or modification of personal documents, family media, financial spreadsheets, or ePub/PDF files.
- No overwriting or merging into the active `~/Developer/mcp-router` repository.
- No Git commit history or remote backing-store reconstruction for detached trial snapshots.
- No unbounded or wildcard unlinking; deletion is strictly gated on prior 100% read-back SHA-256 verification.
- No archive modification or retroactive alteration of previously archived migration changes.
