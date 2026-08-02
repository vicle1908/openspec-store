## 1. Subtask Fetching

- [x] 1.1 Add `fetch_subtasks_for_parent(client, parent_key)` function in `spreadsheet_reporter.py` that fetches subtasks via JQL `key in (subtask_keys)`
- [x] 1.2 Add `classify_platform(summary: str) -> str` function that parses `[IOS`, `[ANDROID`, `[QA`, `[TEST` tags from summary (case-insensitive)
- [ ] 1.3 Add unit tests for `classify_platform` covering iOS, Android, QA, unclassified, and mixed tags

## 2. Per-Epic Tab Columns

- [x] 2.1 Add iOS, Android, QA columns to the per-epic tab header (columns L, M, N)
- [x] 2.2 For each parent task with subtasks, fetch subtasks and populate platform columns with `STATUS (KEY)` format
- [x] 2.3 For parent tasks without subtasks, populate platform columns with "—"
- [ ] 2.4 Add unit tests for platform column population

## 3. Platform Progress Summary

- [x] 3.1 Add `compute_platform_progress(subtasks: list, weights: dict) -> dict` function using existing `COMPLETION_WEIGHTS`
- [x] 3.2 Add summary rows at top of per-epic tab showing iOS/Android/QA progress percentages
- [x] 3.3 Handle edge cases: no subtasks, no QA subtasks, single platform
- [ ] 3.4 Add unit tests for progress computation

## 4. Integration & Verification

- [x] 4.1 Run full test suite — all existing tests must pass
- [x] 4.2 Run ruff check — zero warnings
- [x] 4.3 Generate report for RMD-4160 and verify per-epic tab shows platform columns
- [x] 4.4 Verify summary section shows correct iOS/Android progress
- [x] 4.5 Verify backward compatibility — existing columns A-K unchanged
