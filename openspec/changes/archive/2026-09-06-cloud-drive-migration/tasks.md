# Tasks: Cloud Drive Migration

## 1. Read-only inventory

- [x] 1.1 Inventory iCloud candidates (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/`, `microservices/`, and each proposed artifact path) with `du`, `find`, `git status`, and checksums; record exact sizes and timestamps without modifying data.
- [x] 1.2 Inventory Google Drive candidates (`~/My Drive/TDT (1)/`, `VinID/`, `tdt/`) with `du`, `find`, and rclone metadata; identify duplicates and code mirrors without deleting anything.
- [x] 1.3 Inventory Desktop/Documents candidates and classify personal-looking paths as protected by default; verify no deletion commands run.
- [x] 1.4 Capture pre-action evidence in `evidence/inventory.json` and `evidence/inventory.md`; verify all entries have path, owner classification, size, timestamp, and proposed action.

## 2. Approval gate

- [x] 2.1 Present exact candidate paths, sizes, classifications, impact, and rollback options; verify no mutation task is marked complete.
- [x] 2.2 Obtain explicit approval naming exact paths for iCloud moves, Google Drive deletions, and Desktop/Documents deletions; record approval in evidence.

## 3. Approved iCloud operations

- [ ] 3.1 Move only approved iCloud code projects to `~/Developer/`; verify destination checksums/status and source absence after each move.
- [ ] 3.2 Delete iCloud build artifacts only when individually approved; verify each approved path is absent and all unapproved paths remain.

## 4. Approved Google Drive operations

- [x] 4.1 Confirm rclone/bisync implications for approved paths; verify excluded or intentionally propagated paths are documented.
- [x] 4.2 Delete only approved duplicate/code-mirror paths; verify documentation, rollback, personal, and unknown paths remain.

## 5. Approved Desktop/Documents operations

- [x] 5.1 Delete only explicitly approved migration stubs; verify exact paths are absent and protected paths remain.

## 6. Final verification

- [ ] 6.1 Re-run destination/source, cloud, Git, and disk-usage checks; record before/after evidence without claiming APFS free-space recovery as deleted bytes.
- [ ] 6.2 Run strict OpenSpec validation and archive only after all approved operations have evidence; verify store is clean except unrelated active changes.
