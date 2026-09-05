# Proposal: Cloud Drive Migration

## Summary

Migrate confirmed code projects from iCloud Drive to `~/Developer`, then clean only explicitly approved cloud duplicates and migration artifacts. The change is split into a read-only inventory/approval gate and a separately approved mutation phase; no deletion is performed without path-level approval and rollback evidence.

## Problem

Development projects and generated artifacts are scattered across iCloud Drive, Google Drive, Desktop, and Documents. iCloud-hosted Git trees risk filesystem corruption; Google Drive contains possible duplicates; personal folders and rollback bundles require explicit ownership decisions.

## Proposed Solution

### Phase 0: Read-only inventory and approval gate

- Record exact paths, sizes, Git status, remotes, checksums where practical, and active-process references.
- Compare iCloud code trees with existing `~/Developer` destinations before any move.
- Compare Google Drive candidates against canonical workspace repositories.
- Classify every candidate as `PROTECTED`, `REVIEW_REQUIRED`, or `APPROVED_FOR_ACTION`.
- Stop unless the user explicitly approves the exact paths for each destructive operation.

### Phase 1: iCloud code migration (approval required)

- Move only approved code projects from `~/Library/Mobile Documents/com~apple~CloudDocs/project/` to `~/Developer/`.
- Verify destination integrity and source absence after each move.
- Do not delete build artifacts until individually approved.

### Phase 2: Google Drive cleanup (approval required)

- Delete only explicitly approved duplicate or code-mirror paths.
- Preserve documentation, rollback bundles, personal data, and unknown ownership by default.
- Coordinate with rclone before deleting paths that may propagate through bisync.

### Phase 3: Desktop/Documents cleanup (approval required)

- Inventory and classify migration stubs.
- Delete only exact approved paths; personal-looking paths remain protected unless explicitly approved.

## Success Criteria

1. Every mutation has a recorded path-level approval and pre-action evidence.
2. Approved code projects are present in `~/Developer/` and verified after migration.
3. No protected or unknown-ownership data is deleted.
4. Post-action verification records actual source/destination state and disk usage.

## Risks

- Cloud deletions may propagate to synced services; mitigation: dry-run, exact approvals, and rclone state review.
- Moves may expose duplicate or conflicting Git histories; mitigation: compare status, remotes, and revisions first.
- Personal data may be misclassified; mitigation: personal-looking paths are protected by default.
