## 1. Read-only inventory

- [x] 1.1 Inventory iCloud candidates (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/`, `microservices/`, and each proposed artifact path) with `du`, `find`, `git status`, and checksums; record exact sizes and timestamps without modifying data. Verify completion by checking `evidence/inventory.json` and `evidence/inventory.md` contain path, owner classification, size, timestamp, and proposed action for every candidate, and confirm no deletion or move commands were run.
- [x] 1.2 Inventory Google Drive candidates (`~/My Drive/TDT (1)/`, `VinID/`, `tdt/`) with `du`, `find`, and rclone metadata; identify duplicates and code mirrors without deleting anything. Verify completion by checking evidence files include Google Drive root and nested keep/delete classifications, and confirm no deletion commands were run.
- [x] 1.3 Inventory Desktop/Documents candidates and classify personal-looking paths as protected by default; verify no deletion commands run. Verify completion by checking evidence files include Desktop and Documents entries with protected-by-default classifications and no destructive commands executed.
- [x] 1.4 Capture pre-action evidence in `evidence/inventory.json` and `evidence/inventory.md`; verify all entries have path, owner classification, size, timestamp, and proposed action. Verify completion by reading both evidence files and confirming required fields exist for every listed path.

## 2. Approval gate

- [x] 2.1 Present exact candidate paths, sizes, classifications, impact, and rollback options; verify no mutation task is marked complete. Verify completion by confirming all mutation tasks 3.1 through 6.2 remain unchecked and the approval list has been presented to the user.
- [ ] 2.2 Obtain explicit approval naming exact paths for iCloud moves, Google Drive deletions, and Desktop/Documents deletions; record approval in evidence. Verify completion by checking evidence files contain exact approved paths and that no mutation commands have been executed.

## 3. Approved iCloud operations

- [ ] 3.1 Move only approved iCloud code projects to `~/Developer/`; verify destination checksums/status and source absence after each move. Verify completion by confirming each approved destination path exists with expected contents and each original iCloud path is absent.
- [ ] 3.2 Delete iCloud build artifacts only when individually approved; verify each approved path is absent and all unapproved paths remain. Verify completion by confirming each approved artifact path is absent and all other artifact candidate paths remain untouched.

## 4. Approved Google Drive operations

- [ ] 4.1 Confirm rclone/bisync implications for approved paths; verify excluded or intentionally propagated paths are documented. Verify completion by checking evidence or notes document the confirmed rclone/bisync implications for the approved targets.
- [ ] 4.2 Delete only approved duplicate/code-mirror paths; verify documentation, rollback, personal, and unknown paths remain. Verify completion by confirming each approved target is absent while protected paths remain present.

## 5. Approved Desktop/Documents operations

- [ ] 5.1 Delete only explicitly approved migration stubs; verify exact paths are absent and protected paths remain. Verify completion by confirming each approved stub path is absent and all protected Desktop/Documents entries remain.

## 6. Final verification

- [ ] 6.1 Re-run destination/source, cloud, Git, and disk-usage checks; record before/after evidence without claiming APFS free-space recovery as deleted bytes. Verify completion by checking updated evidence files contain current source/destination state and measured disk usage.
- [ ] 6.2 Run strict OpenSpec validation and archive only after all approved operations have evidence; verify store is clean except unrelated active changes. Verify completion by running the applicable validation command and confirming the store contains only the expected change artifacts plus any unrelated active changes.
