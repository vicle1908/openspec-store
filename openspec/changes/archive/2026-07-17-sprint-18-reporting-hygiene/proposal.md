# Sprint 18 Reporting Hygiene Fixes

## Summary

Fixes four issues discovered during Sprint 18 deployment validation:

1. **Freshness State Not Persisting**: The `_write_freshness_state()` function silently fails when `tdt_core.paths.tdt_state_path()` returns an unexpected path inside the Docker scheduler container
2. **Reminder Policies Path**: The `remind` command defaults to relative path `config/reminder-policies.yaml` which fails when run from non-project directories (e.g., `/workspace/agent-core/src`)
3. **Invalid SHEET_LINKS GIDs**: Two gid entries in `SHEET_LINKS` env point to deleted/moved tabs
4. **Formula Drift Warnings**: 5 spreadsheet formula errors detected in team activity tabs

## Problem Statement

### Issue 1: Freshness State Silent Failure
The freshness state file for Sprint 18 (`1f7T...json`) hasn't been updated since 2026-07-06 despite successful hourly sheet writes. The `write_sheet()` function logs success but the state file remains stale.

Root cause: `_write_freshness_state()` uses `tdt_state_path()` which may return `/home/agent/.tdt/...` inside the container, but the file's parent directory (`freshness/`) might not exist or be writable.

### Issue 2: Reminder Policies Path
```
FileNotFoundError: [Errno 2] No such file or directory: 'config/reminder-policies.yaml'
```
The CLI defaults to a relative path that only works when run from the project root.

### Issue 3: Invalid SHEET_LINKS
```
WARNING sheet_link_gid_not_found gid=864130195
WARNING sheet_link_gid_not_found gid=1938671458
```

### Issue 4: Formula Drift
5 formula errors in team activity tabs (non-blocking but generates warnings).

## Proposed Solution

1. **Freshness State**: Add explicit error handling and logging to `_write_freshness_state()`, plus verify directory existence
2. **Reminder Path**: Use `tdt_core.paths.tdt_state_path()` to resolve to `~/.tdt/` for the policies file
3. **SHEET_LINKS**: Clean up invalid gid entries from `~/.tdt/.env`
4. **Formula Drift**: Surface as a warning in the report reconciliation section (no code change needed, spreadsheet cleanup)

## Success Criteria

- [ ] Freshness state file updates on each successful sprint sheet write
- [ ] Reminder workflow completes without FileNotFoundError
- [ ] No `sheet_link_gid_not_found` warnings in logs
- [ ] Formula drift count documented and acknowledged
