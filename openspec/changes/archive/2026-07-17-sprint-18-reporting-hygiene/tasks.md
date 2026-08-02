# Tasks: Sprint 18 Reporting Hygiene

## Task Checklist

### Freshness State Fix ✅
- [x] Add error handling to `_write_freshness_state()` in `tdt_sheet.py`
- [x] Add logging for write success/failure
- [x] Ensure parent directory exists before write
- [x] Run linter: `ruff check jira-daily-reports/ --fix`
- [x] OpenSpec spec created and validated

### Reminder Policies Path Fix ✅
- [x] Update `remind` command in `cli.py` to use `tdt_state_path()` for policies file
- [x] Copy `reminder-policies.yaml` to `~/.tdt/state/jira-daily-reports/`
- [x] Run linter
- [x] OpenSpec spec created and validated

### SHEET_LINKS Cleanup ✅
- [x] Clean up invalid gid entries from `~/.tdt/.env`
- [x] Keep only valid entry: gid=1772255915
- [x] Verified in logs

### Person Capacity Role Fix ✅
- [x] Add `classify_role()` call in `_build_person_capacity()` to populate Role column
- [x] Import `classify_role` and `load_role_config` from person_capacity module
- [x] Role now correctly shows QA, AOS, iOS, etc. based on member_key prefix
- [x] BA_HA_USSO correctly maps to QA via override
- [x] OpenSpec spec created and validated

### Deployment ✅
- [x] Restart scheduler container (code is bind-mounted)
- [x] Copy reminder-policies.yaml to container
- [x] Verify freshness state writes (confirmed working)
- [x] Verify scheduler running without errors

### Verification ✅
- [x] OpenSpec validates: `openspec validate --strict sprint-18-reporting-hygiene`
- [x] Freshness state file updates confirmed
- [x] No scheduler errors in logs
