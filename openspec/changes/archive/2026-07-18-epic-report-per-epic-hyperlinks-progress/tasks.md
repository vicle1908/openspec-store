## 1. Hyperlinks in Platform Columns

- [x] 1.1 Update `ios_str`, `android_str`, `qa_str` to use `_link(subtask.key)` with display text `STATUS (KEY)` format
- [x] 1.2 Verify hyperlinks render correctly in Google Sheets

## 2. Progress Column

- [x] 2.1 Add "Progress" column header after QA column (column O)
- [x] 2.2 Compute weighted progress for each parent task using subtask statuses
- [x] 2.3 Fallback to parent task's weighted status when no subtasks exist
- [x] 2.4 Format progress as percentage string (e.g., "73%")

## 3. Integration & Verification

- [x] 3.1 Run full test suite — all existing tests must pass
- [x] 3.2 Run ruff check — zero warnings
- [x] 3.3 Generate report for RMD-4160 and verify hyperlinks in iOS/Android columns
- [x] 3.4 Verify Progress column shows correct percentages
- [x] 3.5 Verify backward compatibility — columns A-K unchanged
