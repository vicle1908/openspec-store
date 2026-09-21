# Proposal: migrate-remaining-vds-icloud-projects

## Summary
Safely migrate all remaining sibling project trees and shared root assets from iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/`) to local disk (`~/Developer/vds-content-migration/`), verify data integrity with SHA-256 digests, quarantine sensitive configuration files, and cleanly delete verified source files from iCloud Drive.

## Motivation & Context
Following the successful migration, verification, and cleanup of `WHO-project` (121,410 verified files/symlinks, 46 quarantined secrets), multiple sibling projects and shared assets remain in the iCloud `project/vds` root:
- `EKYC-project`
- `SAVING-project`
- `LIB-project`
- `DOPS-project`
- `PAR-project`
- `LEP-project`
- `INSURANCE-project`
- Shared root scripts, documentation, and configuration files

These projects contain substantial APFS dataless files and complex directories. To prevent sync starvation, timeouts, and data loss, migration must proceed project-by-project with bounded hydration, strict quarantine rules, and fail-closed deletion verification.

## Scope
1. Conduct shallow inventory and prioritize sibling projects by size and dependency.
2. Execute staged, bounded hydration and copy for each sibling project.
3. Migrate and organize shared root assets into `vds-root-assets/`.
4. Quarantine all `.env*` and sensitive secrets with `0700` directories and `0600` files.
5. Perform two-way reconciliation and safely delete verified items from iCloud.
