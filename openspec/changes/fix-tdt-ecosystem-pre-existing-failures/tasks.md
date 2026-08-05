# Tasks: Fix TDT Ecosystem Pre-existing Failures

## Task 1: webhook-receiver — remove module-level create_app()
- [ ] Remove `app = create_app()` from app.py line 1110

## Task 2: jira-daily-reports — fix formatting tests
- [ ] Update `test_format_daily_ticket_details_uses_readable_ticket_names`
- [ ] Update `test_format_daily_ticket_details_handles_multiple_days_sorted`
- [ ] Update `test_format_daily_ticket_details_skips_empty_day_entries`
- [ ] Update `test_format_daily_ticket_details_uses_zero_m_for_zero_seconds`
- [ ] Update `test_build_person_capacity_populates_daily_ticket_details_per_day`

## Task 3: jira-skill — fix hardcoded paths
- [ ] Fix `test_rca.py:903` hardcoded path
- [ ] Fix `test_cli_imports.py:48` hardcoded cwd
- [ ] Add skipWhenMissing for taxonomy tests in `test_taxonomy.py`

## Task 4: Run verification
- [ ] webhook-receiver: test collection succeeds
- [ ] jira-daily-reports: formatting tests pass
- [ ] jira-skill: no more hardcoded path failures
