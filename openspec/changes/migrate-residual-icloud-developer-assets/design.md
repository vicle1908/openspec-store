# Design

## Context

See `proposal.md` for problem motivation and scope.

Previous migration phases successfully transferred and purged the VDS multi-project tree (147,315 files) and Categories 1–6 (microservices, camunda, airbridge, tmz, study examples, MCP servers, invest bots; over 12,000 files). A whole-account audit across `~/Library/Mobile Documents/com~apple~CloudDocs/` identified exactly five residual developer assets containing code, configurations, or technical documentation:

1. `Documents/Codex/2026-07-22/try/work/mcp-router-src`: 393 files (391 dataless, 31.16 MB)
2. `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md`: 1 file (dataless, 5.5 KB)
3. `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe`: 14 files (12 dataless, 0.12 MB)
4. `books/ai/2025/Investing for Programmers/investing-for-programmers-main`: 30 files (30 dataless, 6.09 MB)
5. `Downloads/setup-fable-5.sh`: 1 file (hydrated, 6.3 KB)

Total remaining scope: **439 files (~37.4 MB, 435 dataless)**.

## Goals / Non-Goals

**Goals:**
- Completely materialize and transfer all 439 files into structured local destinations under `~/Developer/`, preserving internal package and directory hierarchy.
- Generate dedicated JSON migration manifests in `~/Developer/content-migration-manifests/` and verify 100% read-back SHA-256 digests.
- Execute fail-closed bounded unlinking of the migrated cloud sources and prune empty parent directories without traversing or mutating personal folders.
- Protect the live `~/Developer/mcp-router` working repository by routing the historical snapshot to a distinct backup path.

**Non-Goals:**
- No modification or deletion of personal directories (`SHB/`, `TDT/`, `candidate/`, `che/`, `family/`, `fcfc/`, `interview/`, `loan/`, `pic/`, `thue/`, `timecompany/`).
- No mutation of non-code book assets in `books/` (PDFs, ePubs, mobi files).
- No git commit-history reconstruction for detached trial snapshots.
- No in-place modification of existing local checkouts.

## Decisions

### 1. Dedicated Target Mapping & Collision Isolation

To ensure clear separation between active working repositories and historical snapshots, assets are routed to distinct local destinations:

| Residual Asset | iCloud Source Path | Local Destination | Manifest / Verification Type |
|---|---|---|---|
| MCP Router Trial Snapshot | `Documents/Codex/2026-07-22/try/work/mcp-router-src` | `~/Developer/mcp-router-backup-20260722` | `manifest-mcp-router-backup-20260722.json` |
| Security Guide | `Documents/PRODUCTION_SECRETS_SECURITY_GUIDE.md` | `~/Developer/docs/PRODUCTION_SECRETS_SECURITY_GUIDE.md` | `manifest-production-secrets-guide.json` |
| Lending Miniapp Docs | `Desktop/Desktop - Cuong’s iMac - 1/lending-miniapp-fe` | `~/Developer/lending-miniapp-docs` | `manifest-lending-miniapp-docs.json` |
| Investing Code Samples | `books/.../investing-for-programmers-main` | `~/Developer/study-examples/investing-for-programmers` | Git repository / Directory manifest |
| Docker Study Code | `books/.../code.zip` | `~/Developer/study-examples/docker-in-a-month-of-lunches` | Zip extraction / Directory manifest |
| Kotlin Study Code | `books/.../sckotlin-code.zip` | `~/Developer/study-examples/kotlin-coroutine-confidence` | Zip extraction / Directory manifest |
| Setup Script (Quarantined) | `Downloads/setup-fable-5.sh` | `~/Developer/sensitive-quarantine/downloads/setup-fable-5.sh` | Quarantine `0600` / SHA-256 verified |
| Charles Proxy License | `ghtk/soft/charles/charlesKey.rtf` | `~/Developer/sensitive-quarantine/ghtk/charlesKey.rtf` | Quarantine `0600` / SHA-256 verified |
| GHTK Shell Config | `ghtk/zshrc/.zshrc` | `~/Developer/ghtk-scripts/zshrc/.zshrc` & `sensitive-quarantine/ghtk/.zshrc` | Quarantine `0600` / Scripts verified |
| Ascend Configs | `ascend/PH/localize`, `MM/LoyaltyApp/config` | `~/Developer/ascend-configs/` | Directory verified |

*Rationale:* The active checkout of `mcp-router` at `~/Developer/mcp-router` is currently dirty and under active development. Storing the 2026-07-22 trial snapshot at `~/Developer/mcp-router-backup-20260722` prevents file collisions and maintains complete historical provenance.

### 2. Asynchronous Cocoa Hydration with Paced Subtree Triggering

Materialization will leverage the established Swift Cocoa helper:
```swift
FileManager.default.startDownloadingUbiquitousItem(at: url)
```
- **Pacing & Queue Management:** Download requests are triggered per asset directory with metadata-only `lstat` polling (`st_blocks > 0` and `SF_DATALESS` cleared) before reading bytes.
- **Symlink & Collision Protection:** Symlinks (`.nosync`, `.venv 2`) are excluded from ubiquitous download triggering to prevent polling stalls.

### 3. Atomic Local Ingestion & Value-Blind Manifesting

`content_migration.py` will ingest materialized files:
- Each file is staged to a temporary sibling file on the same local filesystem, flushed and fsynced, and atomically linked/renamed into position without overwriting existing files.
- SHA-256 digests and file sizes are recorded in dedicated manifest JSON files under `~/Developer/content-migration-manifests/`.

### 4. Two-Way Verification and Controlled Cloud Purge

Cloud deletion is strictly gated on prior verification:
1. `content_migration.py --verify-only` must report `failed: 0` across all 5 manifests.
2. The purge routine iterates each cloud source file, asserts `dest_path.exists()` and `dest_path.stat().st_size == src_size`, then unlinks the cloud file.
3. Empty parent directories (`mcp-router-src`, `work`, `try`, `2026-07-22`, `Codex`, `lending-miniapp-fe`, `investing-for-programmers-main`) are pruned bottom-up.
4. If a parent directory contains non-code files (e.g. `books/ai/2025/Investing for Programmers/` containing the book PDF), the parent directory is left intact.

## Risks / Trade-offs

- **Risk: Sync Daemon Throttling on Mass Downloads.**
  - *Mitigation:* The total file count is small (439 files, ~37.4 MB). Paced batch triggering with 1-second settle delays ensures `fileproviderd` operates within its optimal throughput without queue saturation.
- **Risk: Unintended Deletion of Personal Files.**
  - *Mitigation:* The deletion script requires exact path matches against the verified manifest keys. Personal root directories (`SHB/`, `TDT/`, `family/`, `books/*.pdf`, etc.) are completely excluded from the unlinking path.
