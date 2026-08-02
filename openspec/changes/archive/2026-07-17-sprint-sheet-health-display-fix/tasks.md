## 1. Code Changes

- [x] 1.1 Add health row to Sprint Summary in `build_sheet_rows()`
  - **File:** `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py`
  - **Location:** After line 1334 (Narrative row), before empty row
  - **Change:** Added `rows.append(["Sprint Health", s["health"]])`
  - **Verification:** All 26 sprint report tests pass

- [x] 1.2 Run existing unit tests to verify no regressions
  - **Command:** `cd jira-daily-reports && uv run pytest tests/ -q`
  - **Result:** 208 tests pass

## 2. Documentation Updates

- [x] 2.1 Fix SKILL.md health attribution
  - **File:** `.agents/skills/jira-daily-reports/SKILL.md`
  - **Change:** Updated health description to state it applies to Sprint Report, not Person Capacity
  - **Verification:** Lines 288-295 now correctly describe Sprint Report health

- [x] 2.2 Add Person Capacity sort behavior documentation
  - **File:** `.agents/skills/jira-daily-reports/SKILL.md`
  - **Location:** In Person Capacity section, after planning data description
  - **Change:** Documented conditional sort behavior (mapping order vs logged_total sort)
  - **Verification:** Lines 173-176 document the conditional sort

## 3. Test Updates

- [x] 3.1 Add test for health row in sheet output
  - **File:** `jira-daily-reports/tests/test_sprint_report_sheet.py`
  - **Change:** Added `test_build_sheet_rows_includes_health_in_summary`
  - **Verification:** Test passes

## 4. Verification

- [x] 4.1 Run linter on modified files
  - **Command:** `cd jira-daily-reports && uv run ruff check src/`
  - **Result:** All checks passed

- [x] 4.2 Run full test suite
  - **Command:** `cd jira-daily-reports && uv run pytest tests/ -q`
  - **Result:** 208 tests pass

- [x] 4.3 Verify OpenSpec is complete
  - **Command:** `openspec status --change sprint-sheet-health-display-fix`
  - **Result:** All 4 artifacts show status "done"
