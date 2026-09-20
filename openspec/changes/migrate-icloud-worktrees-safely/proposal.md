## Why

The iCloud project tree (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/WHO-project`) contains 46 worktrees and core repository directories (`vds-scripts`, `vds-skills`) with over 107,000 dataless files and 16,139 already-copied hydrated files. Our objective is to fully copy all source code and documents from iCloud to local disk (`~/Developer/vds-content-migration/WHO-project`), preserving exact directory names and hierarchical structure without triggering FileProvider deadlocks. Git history, `.git` pointers, and backing-store reconstruction are explicitly out of scope for this phase per owner direction.

## What Changes

- **Preserve Directory Names and Hierarchy**: Ensure 1:1 structural fidelity so all files retain their exact relative directory paths (e.g. `worktrees/<worktree-name>/...`, `vds-scripts/...`, `vds-skills/...`).
- **Asynchronous Cocoa Hydration Pipeline**: Implement a 3-stage pipeline using Apple's native Cocoa API (`FileManager.default.startDownloadingUbiquitousItem(at:)` via Swift) to asynchronously trigger background downloads of dataless files without blocking kernel I/O, poll non-blockingly via `os.lstat` until materialized (`st_blocks > 0`), and atomically ingest via `content_migration.py`.
- **Exclusion of Git Internals and Build Caches**: Exclude `.git`, `.git_disabled`, `.venv`, `__pycache__`, `.pytest_cache`, and build caches from the local destination.
- **Sensitive File Quarantine**: Automatically divert `.env*` and credential files into a permission-restricted `sensitive-quarantine/` (`0700` dirs, `0600` files).
- **Atomic Installation and Hash Verification**: Every file is staged to a temporary file on the same local filesystem, flushed/fsynced, atomically installed without overwrite, and read-back verified against its SHA-256 digest in `migration-manifest.json`.
- **Fail-Closed Source Preservation**: The iCloud source tree is strictly read-only; no files are modified, moved, or deleted in iCloud (`source_mutations: 0`).
## Capabilities

### New Capabilities

- `icloud-worktree-migration-safety`: Metadata-only inventory, capacity/secret gates, bounded restricted copying, quarantine handling, replacement verification, and deletion authorization for iCloud worktrees.

### Modified Capabilities

None.

## Impact

- Planning artifacts and value-blind evidence live under this change in the registered `openspec-store`.
- Implementation and source data remain outside the OpenSpec store; this change does not authorize moving or deleting iCloud files by itself.
- Existing `remediate-2026-09-06-archive-gaps` remains untouched; its explicit no-iCloud boundary is preserved.
- Existing evidence is referenced by metadata-only artifact paths; sensitive contents and raw sensitive paths are not copied into OpenSpec artifacts.

## Non-Goals

- No iCloud source deletion or move: the iCloud tree is preserved unmutated.
- No Git backing-store or commit-history reconstruction: Git history is decoupled per owner direction ("no need handle git we just need source code fully copied").
- No copying of `.git`, `.git_disabled`, `.venv`, or build caches into the destination.
- No copying of `.env*` or secret keys into the general recovery destination; all sensitive matches are diverted to `sensitive-quarantine/`.
- No archive modification or archive-gap remediation.
