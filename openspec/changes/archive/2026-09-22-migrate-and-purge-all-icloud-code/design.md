# Design: Migrate and Purge All iCloud Code (Option 3)

## Architecture Overview

The migration utilizes the proven `icloud-migration-tools` framework (`content_migration.py`, `run_hydration_loop.py`, `hydrate_pilot.swift`, `delete_migrated_source.py`) with enhanced partitioned runners for multi-project execution.

```
iCloud Source Trees (com~apple~CloudDocs/)
  ├── project/microservices
  ├── project/camunda7, camunda, airbridge, tmz
  ├── viettel/Nangluc/excel-updater
  ├── timecompany/test/githubusers
  ├── ghtk/project/script/catalog-v2, training/cicd
  ├── books/.../Go by Example Source Code, Learning-Spring-Boot-4-main
  ├── invest/
  ├── AI/mcp/server, claudia
  └── main/
          │
          ▼
   [ Cocoa Hydration Engine (hydrate_pilot.swift) ]
          │  Asynchronous ubiquitous item download trigger
          │  Directory-level pruning of node_modules, .venv, .gradle, book docs (.epub/.pdf)
          ▼
   [ Partitioned Ingestion (content_migration.py) ]
          │  Atomic temporary installation (.dst.tmp -> dst)
          │  Sensitive detection (.env*, *.key -> sensitive-quarantine/)
          │  SHA-256 digestion and manifest recording
          ▼
Local Destinations (~/Developer/)
  ├── microservices/
  ├── viettel-excel-updater/
  ├── githubusers/
  ├── main-db-migrations/
  ├── camunda7/
  ├── camunda-loan-approval/
  ├── airbridge/
  ├── tmz-case-challenge/
  ├── ghtk-catalog-v2/
  ├── ghtk-training-cicd/
  ├── study-examples/
  │   ├── go-by-example/
  │   └── spring-boot-4/
  ├── invest-bots/
  ├── mcp-servers/
  └── claudia/
          │
          ▼
   [ Two-Way Reconciliation Audit Gate ]
          │  Verify 100% of source files exist in destination or quarantine
          │  Assert 0 missing files, 0 size mismatches
          ▼
   [ Fail-Closed Bounded Deletion (delete_migrated_source.py) ]
          │  Per-file destination presence check before unlinking
          │  Bottom-up empty directory pruning
          ▼
   [ Direct Purge of Root Debris ]
          └── Unlink _internal/, base64/, METADATA, .vds, etc.
```

## Directory & Subtree Exclusions

To safeguard the 40.3 GB APFS volume headroom and prevent sync daemon saturation, discovery strictly excludes:
- Package managers & build outputs: `node_modules`, `.gradle`, `build`, `target`, `dist`, `coverage`, `.parcel-cache`
- Virtual environments & Python caches: `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.hypothesis`
- Generated vector & database storages: `qdrant_storage`, `wal`, `segments`
- Editor & index caches: `.idea`, `.vscode`, `.cache`, `cache`, `.gitnexus`
- Non-code documents in book trees: `.epub`, `.pdf`, `.mobi`, `.azw3`, `.rar`, `.zip`
- Legacy AppleDouble sidecars: `._*`

## Sensitive File Handling & Quarantine

1. Any file whose name matches `.env*`, `credentials*`, `secrets*`, `id_rsa*`, `*private_key*` or suffixes (`.pem`, `.key`, `.p12`, `.pfx`, `.crt`, `.cer`) is diverted to `sensitive-quarantine/<project>/`.
2. Normalization sweeps enforce `0700` on quarantine directories and `0600` on quarantined files (`stat.S_ISLNK` guarded).
3. Secret files are never committed to git repositories or placed in world-readable destinations.

## Ingestion & Manifest Pipeline

Each project produces a dedicated manifest at `~/Developer/content-migration-manifests/manifest-<project>.json`:
```json
{
  "project": "microservices",
  "source_root": "/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/microservices",
  "dest_root": "/Users/androidteam/Developer/microservices",
  "quarantine_root": "/Users/androidteam/Developer/sensitive-quarantine/microservices",
  "entries": {
    "relative/path/to/file.ext": {
      "size": 1234,
      "sha256": "abcdef...",
      "quarantined": false
    }
  }
}
```

## Two-Way Reconciliation Gate

Before any source deletion, the reconciler sweeps the iCloud source tree:
- **Verified Regular Files:** Exists in destination with matching size and SHA-256.
- **Verified Symlinks:** Exists in destination with matching `readlink` target.
- **Quarantined Secrets:** Exists in `sensitive-quarantine/` with matching digest and `0600` permissions.
- **Excluded Artifacts:** Matches canonical exclusion patterns (`.venv`, `node_modules`, book documents).
- **Unaccounted Files:** MUST BE ZERO (`assert unaccounted == 0`).

## Fail-Closed Deletion Guardrails

1. `SOURCE_ROOT != DEST_ROOT` and `DEST_ROOT` is not under `SOURCE_ROOT`.
2. Every file unlinked from iCloud must pass `(DEST_ROOT / rel).exists()` or `os.path.lexists(QUARANTINE_ROOT / rel)`.
3. If any single destination file is missing, the deletion process halts immediately (`sys.exit(1)`).
4. After unlinking files, empty parent directories are pruned bottom-up (`topdown=False`).
5. Root debris (`_internal/`, `METADATA`, etc.) is verified as non-source before unlinking.
