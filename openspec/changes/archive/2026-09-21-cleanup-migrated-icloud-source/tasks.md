# Tasks: cleanup-migrated-icloud-source

## 1. Pre-Deletion Verification & Safety Gates

- [x] 1.1 Run pre-deletion verification `content_migration.py --verify-only` against `migration-manifest.json` ensuring 100% of local files pass SHA-256 and byte-count checks with zero errors (121,699 verified files).
- [x] 1.2 Verify that all 47 quarantined sensitive items exist in `sensitive-quarantine/` with compliant permissions (`0700` directories, `0600` files).
- [x] 1.3 Verify that no external Git repositories outside iCloud are linked to worktrees under `WHO-project/worktrees/`.

## 2. Dry-Run Audit & Plan Presentation

- [x] 2.1 Execute a dry-run audit calculating total files and disk bytes to be removed from iCloud Drive.
- [x] 2.2 Present deletion options (Option A: Full tree removal vs. Option B: Granular manifest deletion) and dry-run accounting to user for confirmation.

## 3. Deletion Execution & Post-Deletion Verification

- [x] 3.1 Execute approved deletion on the iCloud Drive source path (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/WHO-project`).
- [x] 3.2 Re-verify that local destination `~/Developer/vds-content-migration/WHO-project` and `sensitive-quarantine/` remain 100% intact with 121,699 verified files.
- [x] 3.3 Confirm iCloud source path removal and verify macOS `bird` stability.
