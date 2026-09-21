# Proposal: cleanup-migrated-icloud-source

## Summary
Safely clean up and remove migrated project artifacts from the iCloud Drive source directory (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/WHO-project`) following the 100% verified migration of all source code, worktrees, skills, documents, and quarantined secrets to local disk (`~/Developer/vds-content-migration/WHO-project` and `~/Developer/vds-content-migration/sensitive-quarantine`).

## Motivation
- The complete `WHO-project` codebase (121,699 verified files across 46 worktrees, all skills, and all core orchestrators) and 47 sensitive items have been fully transferred and verified on local disk with 0 checksum or size discrepancies.
- Keeping redundant, dataless, and partially hydrated trees in iCloud Drive consumes cloud storage quota, incurs background CPU and network sync overhead from macOS `bird`, and creates confusion regarding the canonical location of active project code.
- Removing the migrated items from iCloud completes the transition to local workspace storage.

## Proposed Changes
1. **Pre-Deletion Safety Gate**: Assert that local destination (`~/Developer/vds-content-migration/WHO-project`) passes full SHA-256 and byte-count verification (121,699 files, 0 failures) and quarantine contains 47 verified items.
2. **Dry-Run Audit**: Compute exact candidate deletion lists, disk space to be reclaimed, and confirm zero overlap with local destination paths.
3. **Phased & Bounded Deletion**: Execute removal of verified source items from iCloud Drive with rate and path controls to avoid overwhelming the macOS `bird` sync daemon.
4. **Post-Deletion Verification**: Re-verify that local destination remains 100% intact and confirm iCloud source tree is cleanly removed or trimmed.

## Risks & Mitigations
- **Risk**: Accidental deletion of local destination.
  - **Mitigation**: Absolute path guardrails; destination (`~/Developer/...`) is on a completely separate local APFS volume from iCloud (`~/Library/Mobile Documents/...`).
- **Risk**: macOS `bird` sync lockup or API throttling on mass file deletion.
  - **Mitigation**: Phased batch deletion or top-level directory removal with pauses if needed.
