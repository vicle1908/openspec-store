# kbs-resolve-sprint-scope-signature-fix — Tasks

## 1. Fix kbs CLI `resolve_sprint_scope` call sites (source repo)

**File:** `jira-kanban-from-spreadsheet/src/kbs/cli.py`

Remove `filter_id_override=...` and `board_id_override=...` kwargs from both `resolve_sprint_scope()` call sites. The post-call fallback lines below each call are already correct and must be preserved.

- [x] 1.1 **sync command** (line ~408): Remove `filter_id_override=cfg.filter_id or None` and `board_id_override=cfg.board_id or None`
- [x] 1.2 **verify command** (line ~795): Remove `filter_id_override=resolved_filter_id` and `board_id_override=resolved_board_id`
- [x] 1.3 Verify the post-call fallback lines are unchanged after each call
- [x] 1.4 Run `ruff check` — clean
- [x] 1.5 Run `mypy --no-error-summary` — clean
- [x] 1.6 Run pytest — all 23 tests pass

## 2. Fix kbs CLI `resolve_sprint_scope` call sites (ai-review deployment copy)

**File:** `deployments/ai-review/deps/jira-kanban-from-spreadsheet/src/kbs/cli.py`

Apply the same two removals to the shipped deployment copy.

- [x] 2.1 **sync command**: Same removals as task 1.1
- [x] 2.2 **verify command**: Same removals as task 1.2
- [x] 2.3 Verify the post-call fallback lines are unchanged

## 3. Guard jdr board fallback with `has_resolved_scope`

**File:** `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py`

- [x] 3.1 Added `and not self.has_resolved_scope` to the board assignment in `_resolve_scope_from_spreadsheet`
- [x] 3.2 Set `has_resolved_scope = True` when `RESOLVED_BOARD_ID` env var is set, so the guard fires correctly
- [x] 3.3 Run `ruff check` — clean
- [x] 3.4 Run `mypy --no-error-summary` — clean
- [x] 3.5 Run pytest — all 35 tests pass

## 4. Exact-name-match filter/board resolution

**File:** `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py`

Fixed `_resolve_scope_from_spreadsheet` to match filter and board by exact canonical name instead of taking the first search result.

- [x] 4.1 Filter: match by exact `f"Sprint {N} ({dates})"` name — prevents stale filter 10394 ("17-Aug-2024-LiveDeployment") from being picked when many legacy filters contain "Sprint 17"
- [x] 4.2 Board: search by `f"Sprint {N} Board"` name (not spreadsheet title), then match by exact name — prevents board name search returning nothing for full spreadsheet titles
- [x] 4.3 Run pytest — all 35 tests pass including `TestSprintScopeResolution`
- [x] 4.4 Integration: Sprint report terminal output shows `Filter: #15425 | Board: #1206` — correct

## 5. Add targeted tests

### 5.1 kbs: sync and verify complete without TypeError

**File:** `jira-kanban-from-spreadsheet/tests/test_cli.py`

- [x] 5.1.1 `TestResolveSprintScopeSignature.test_sync_no_typeerror_with_current_signature`: mocks `resolve_sprint_scope`, asserts no `filter_id_override`/`board_id_override` kwargs passed
- [x] 5.1.2 `test_sync_live_with_existing_filter_updates_not_creates`: ensures existing filter is updated not re-created
- [x] 5.1.3 `test_verify_no_typeerror_with_current_signature`: same kwargs check for verify command
- [x] 5.1.4 `test_verify_uses_post_call_fallback_for_resolved_ids`: ensures CLI-resolved ids are used when resolve_sprint_scope returns None

### 5.2 jdr: board-guard preserves kbs-resolved board id

**File:** `jira-daily-reports/tests/test_sprint_report_sheet.py`

- [x] 5.2.1 `test_resolved_board_id_preserved_over_spreadsheet_fallback`: sets `RESOLVED_BOARD_ID=1066`, asserts board id is NOT overwritten by spreadsheet fallback
- [x] 5.2.2 `test_no_resolved_board_id_falls_back_to_spreadsheet`: without `RESOLVED_BOARD_ID`, board id IS derived from spreadsheet title
- [x] 5.2.3 `test_has_resolved_scope_true_when_resolved_board_id_set`: asserts `RESOLVED_BOARD_ID` alone sets `has_resolved_scope=True`
- [x] 5.2.4 Fixed pre-existing test `test_build_sheet_rows_renders_all_four_links` for updated sprint label format

## 6. Integration validation

- [x] 6.1 `kbs sync --dry-run` with Sprint 17 spreadsheet — completes without TypeError; confirms 39 keys, would create filter
- [x] 6.2 `kbs sync --live` with Sprint 17 spreadsheet — created filter 15425 "Sprint 17 (22 Jun - 03 July)" and board 1206 "Sprint 17 Board"; board has all 39 issues
- [x] 6.3 `kbs verify` after sync — completes successfully; Filter 15425, Board 1206, 39 issues confirmed
- [x] 6.4 Sprint report terminal run — shows `Filter: #15425 | Board: #1206 | Total: 39` — correct
- [x] 6.5 Scheduler trigger of `jira-sprint-sheet` — rebuilt all packages, wrote Sprint Report + Person Capacity to sheet
- [x] 6.6 Rebuild and deploy `tdt-scheduler:local` Docker image

## 7. Board project association

**Symptom:** Board 1206 showed "Connect this board to a project" warning in Jira.

- [x] 7.1 Add `location_key` kwarg to `tdt_core.clients.jira.create_board()` with body `{"location": {"type": "project", "projectKeyOrId": location_key}}`
- [x] 7.2 Add `board_project_key` param to `tdt_core.sprint_scope.resolve_sprint_scope()`
- [x] 7.3 Pass `board_project_key=cfg.project_key` in `kbs/cli.py` sync command
- [x] 7.4 Fix API field name: `projectKeyOrId` (not `projectKey`)
- [x] 7.5 Rebuild scheduler Docker image
- [x] 7.6 Redeploy scheduler
- [x] 7.7 Verify board 1207 has `location.projectKey: 'PUB'` via Jira API
- [x] 7.8 Verify Sprint Report sheet shows board 1207 with correct HYPERLINK

## Dependencies

- Task 1 must complete before Task 5.1
- Task 3 can proceed independently of Task 1
- Task 2 is independent of Tasks 1 and 3 (but must use the same removal pattern)
- Task 4 (exact-name-match) was discovered during integration validation

## 7. Board project association fix

**Root cause:** `jira.create_board()` was called without a `location` parameter, so boards were created without a project association. Jira shows "Connect this board to a project" warning on the board page.

**Files changed:**
- `tdt-core/src/tdt_core/clients/jira.py` — `create_board()` added `location_key` kwarg
- `tdt-core/src/tdt_core/sprint_scope.py` — `resolve_sprint_scope()` added `board_project_key` param
- `jira-kanban-from-spreadsheet/src/kbs/cli.py` — sync passes `board_project_key=cfg.project_key`

**API fix:** Jira Agile REST API v1 expects `location: { type: "project", projectKeyOrId: "PUB" }`.

**Validation:**
- Board 1207 created with `location_key='PUB'` → Jira API confirms `location.projectKey: 'PUB'`
- Sprint Report terminal: `Filter: #15425 | Board: #1207 | Total: 39` ✓
- Sprint Report sheet D2: `=HYPERLINK(".../PUB/boards/1207","PUB Kanban (#1207)")` ✓
- Scheduler rebuilt and deployed (`tdt-scheduler:local`)

## Notes

- The `filter_id_override`/`board_id_override` removal was intentional in `tdt-core` commit `2437c9f`. Do NOT re-add these params to `resolve_sprint_scope`.
- The fix is in **kbs** (the callers), not **tdt-core** (the callee).
- Task 2 (ai-review deployment) must use identical changes to Task 1 so the deployed copy stays in sync.
- Task 3 (board guard) required setting `has_resolved_scope = True` when `RESOLVED_BOARD_ID` env var is set, so the guard in `_resolve_scope_from_spreadsheet` fires correctly.
- **Task 4** (exact-name-match) was a critical bug discovered during integration: `_resolve_scope_from_spreadsheet` called `search_filters(title)` and took `filters[0]` (oldest-created filter), which for Sprint 17 returned the Aug 2024 "17-Aug-2024-LiveDeployment" filter (#10394) instead of the correct "Sprint 17 (22 Jun - 03 July)" filter (#15425). The fix uses exact name matching.

- **Task 7** (board project association) was reported by user: the Sprint 17 Kanban board showed "Connect this board to a project" warning. Fixed by passing `location: { type: "project", projectKeyOrId: "PUB" }` to the Jira Agile v1 board creation API.
