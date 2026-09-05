## Context

The workspace lifecycle dry-run (2026-09-05) classified ~/Developer/tdt/ as PROTECTED due to live ai-review service. That service is now migrated to ~/.tdt/ (change 2026-09-05-migrate-ai-review-deployment). The directory is now unblocked for retirement. Shell artifacts and empty dirs are trivially reclaimable (no retention entry, no owner, no content).

## Decisions

### 1. tdt/ retirement via direct removal, not lifecycle dry-run
The directory's contents are known: 17 stale repo copies (full .git dirs, HEADs matching current repos — confirmed via readlink analysis that these are independent copies, not symlinks) plus the now-empty deployments/ai-review/. A second dry-run is unnecessary; the prior dry-run already classified it PROTECTED-with-justification-now-resolved.

### 2. Shell artifacts: delete without lifecycle involvement
--help and yield are zero-information accidental files (2.2K, 1.2K). No lifecycle ceremony needed.

### 3. Empty dirs: direct deletion
deployments/, poems-mobile3-android/, poems-mobile3-ios/ contain zero files. No lifecycle ceremony needed.

## Risks

- [Risk] tdt/ repo copies contained unpushed work → Mitigation: confirmed HEADs match current repos, no unique commits
- [Risk] orca-workspaces/tdt-core empty dir referenced by 9 DB records → Mitigation: retained, not touched in this change
