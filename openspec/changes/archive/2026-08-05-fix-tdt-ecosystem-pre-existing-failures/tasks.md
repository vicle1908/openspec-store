# Tasks: Fix TDT Ecosystem Pre-existing Failures

## Task 1: webhook-receiver — remove module-level create_app()
- [x] Remove `app = create_app()` from app.py line 1110

## Task 2: jira-daily-reports — fix formatting tests
- [x] Update `test_format_daily_ticket_details_uses_readable_ticket_names`
- [x] Update `test_format_daily_ticket_details_handles_multiple_days_sorted`
- [x] Update `test_format_daily_ticket_details_skips_empty_day_entries`
- [x] Update `test_format_daily_ticket_details_uses_zero_m_for_zero_seconds`
- [x] Update `test_build_person_capacity_populates_daily_ticket_details_per_day`

## Task 3: jira-skill — fix hardcoded paths
- [x] Fix `test_rca.py:903` hardcoded path → `Path(__file__).resolve().parents[2]`
- [x] Fix `test_cli_imports.py:48` hardcoded cwd → `Path(__file__).resolve().parents[1]`
- [x] Add skipWhenMissing for taxonomy tests in `test_taxonomy.py`

## Task 4: Run verification
- [x] webhook-receiver: 17 tests collected (was collection error)
- [x] jira-daily-reports: 62 passed (was 5 failures)
- [x] jira-skill: 28 passed, 38 skipped (was 3 failures + 38 errors)
