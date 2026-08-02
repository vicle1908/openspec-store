# Gap Matrix — Sprint Ecosystem Alignment

## Status Legend
- ✅ **Match** — implementation meets the spec requirement
- ⚠️ **Partial** — implemented but not explicitly labeled or missing one field
- ❌ **Gap** — not implemented or contradicts the spec

## 1. Resolved sprint context is the integration contract

| Requirement | Status | Notes |
|---|---|---|
| Sprint pipeline produces a single resolved context | ✅ | `SprintScope` in `tdt-core` covers spreadsheet_id, sprint_number, dates, filter, board, project_key |
| Downstream consumes the same context | ✅ | `ResolvedScope`, `_resolved_scope_from_env()`, `set_resolved_scope()`, and the `tdt_sheet` handoff now carry keys/filter/board/sprint/dashboard/project through the report path; `RESOLVED_DASHBOARD_ID` is also accepted when present. |
| Context includes spreadsheet id, workbook title, sprint number, dates, issue keys, filter name, filter id, board name, board id, sprint id, dashboard id, project key | ⚠️ | `ResolvedScope` now carries board_id, sprint_id, project_key, and dashboard_id in addition to keys + filter_id. `dashboard_id` is still produced as a link-only shell inside the report path when not pre-supplied, so the full object-id contract is present but not all ids originate from KBS. |
| Missing optional objects are absent rather than faked | ✅ | SprintScope uses `None` consistently; env vars absent → empty string, handled as absent |

## 2. Dashboard behavior: link-only vs configured build

| Requirement | Status | Notes |
|---|---|---|
| Dashboard behavior is explicit | ✅ | `_resolve_sprint_dashboard()` now logs link-only mode and surfaces the canonical `jira-skill dashboard` build command. |
| Configured dashboards use `jira-skill.dashboard` layout engine | ✅ | `jira-daily-reports dashboard` delegates to the shared `jira-skill.dashboard` builder/validator path; the `sprint-sheet` path intentionally remains link-only instead of building gadgets. |
| Link-only dashboards label themselves and surface canonical build command | ✅ | Link-only shell behavior is now logged explicitly, with the canonical `jira-skill dashboard` command shown for full builds. |
| Dry-run does not mutate dashboard state | ✅ | The live refresh path is explicitly gated; the sprint report shell only resolves when a resolved scope is handed off, and dry-run KBS runs do not invoke the refresh. |


## 3. Sprint report links reflect resolved context

| Requirement | Status | Notes |
|---|---|---|
| Links use resolved filter, board, sprint, dashboard ids and project key | ✅ | The report reads all five from env/init and renders via `self.filter_id`, `self.board_id`, `self.sprint_id`, `self.dashboard_id`, `self.link_project_key` |
| Optional links omitted safely | ✅ | Each link is gated behind its id being non-empty |
| Consistent between Sheet and markdown | ✅ | Both output paths check the same ids |

## 4. Docs and skills describe canonical ownership

| Requirement | Status | Notes |
|---|---|---|
| jira-daily-reports is identified as active sprint report output path | ✅ | SKILL.md explicitly states sprint report ownership |
| Spreadsheet-derived context is the sprint scope input | ✅ | SKILL.md states spreadsheet is SSOT |
| jira-skill.dashboard is canonical dashboard builder/validator | ✅ | `jira-dashboard` now states `jira-skill.dashboard` as canonical and distinguishes it from the link-only sprint-report shell path. |
| Board/sprint creation from resolved filter + live gating | ✅ | The `board-from-spreadsheet` skill now documents live-gated board/sprint creation from the resolved spreadsheet scope and the report handoff semantics. |
| Stale manual per-sprint Jira id wording removed | ⚠️ | Not fully audited; some readme/docs still reference manual filter/board creation patterns |

## 5. Validation evidence

| Requirement | Status | Notes |
|---|---|---|
| Dry-run validation evidence | ✅ | KBS dry-run resolved filter 15330/board 1168 from workbook title; no Jira objects created. |
| Live readback evidence | ✅ | `sprint-sheet` completed: 9 met / 65 behind / 0 rejected, freshness run eda1bdcfb5e5a9fa. |
| Temporary-object cleanup evidence | ⚠️ | Live run used the real sprint workbook — no temp objects created that need cleanup. |
