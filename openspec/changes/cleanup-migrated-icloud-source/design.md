# Design: cleanup-migrated-icloud-source

## Overview
This design outlines the architecture, invariants, and procedures for safely deleting migrated project files from the iCloud Drive source root (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/WHO-project`).

## Invariants
1. **Local Destination Inviolability**: No deletion command may reference or touch any path under `~/Developer/vds-content-migration/`.
2. **Pre-Flight Verification**: Deletion is blocked unless `content_migration.py --verify-only` reports `{"failed": 0, "verified": 121699}` immediately prior to execution.
3. **Quarantine Inviolability**: All 47 sensitive `.env*` items must remain secured in `~/Developer/vds-content-migration/sensitive-quarantine/` with `0700`/`0600` permissions.
4. **Bounded Scope**: Only paths explicitly confirmed by user authorization and dry-run audits may be deleted.

## Deletion Approaches
1. **Option A: Full Source Tree Removal (`rm -rf WHO-project`)**:
   - Removes the entire `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/WHO-project` directory in iCloud.
   - Recommended because 100% of real code, documents, worktrees, and quarantined secrets are preserved locally, and remaining iCloud files are only transient build/cache artifacts or AppleDouble sidecars.
2. **Option B: Granular Manifest Deletion**:
   - Deletes only the 121,699 files matching entries in `migration-manifest.json`.
   - Leaves behind empty directory hierarchies, cache files, and AppleDouble sidecars.
