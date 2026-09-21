# Proposal: finalize-vds-icloud-migration-and-purge

## Why
All 8 primary VDS projects (`WHO-project`, `DOPS-project`, `EKYC-project`, `PAR-project`, `SAVING-project`, `LIB-project`, `LEP-project`, `INSURANCE-project`) and root assets have been migrated to `~/Developer/vds-content-migration/`, with 145,782 entries and 96 sensitive items verified locally. However, 38 residual items remain in the iCloud `project/vds/` directory, including shared agent directories, loose files like `CLAUDE.md`, empty directory shells, and gitignored runtime dumps (`data/`, `reports/`). To fully complete the migration and deletion as requested, these remaining items must be audited, any remaining legitimate assets copied and verified, and all residual artifacts cleanly purged from iCloud Drive.

## What Changes
1. Audit all 38 remaining items in `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` and inspect the broader `com~apple~CloudDocs/project/` container.
2. Complete the copy of any remaining legitimate files (such as `CLAUDE.md` and active agent configs) into `~/Developer/vds-content-migration/vds-root-assets/` and update `migration-manifest-root-assets.json`.
3. Quarantine any remaining sensitive files with `0700` directory permissions and `0600` file permissions.
4. Safely purge all residual directories, empty shells, agent caches, and gitignored runtime dumps from `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/`.
5. Remove the `project/vds/` directory from iCloud Drive upon confirming zero unmigrated source assets remain.
6. Perform global verification across all manifests and archive the change in `openspec-store`.
