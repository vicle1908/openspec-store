# kbs extra sheets and linked tickets

## Context

`kbs sync` builds the per-sprint Jira filter/board scope from a sprint workbook.
Today `_read_sheets` iterates a fixed `WorkflowConfig.sheet_names` list (the
three bucket tabs), parses rows with `parse_rows`, dedups by `issue_key`, and
`build_cross_project_jql` turns the keys into `key in (...)`. Sprint planning now
also tracks scope in extra tabs, and the PUB board needs to include tickets
linked to planned PUB issues without hand-copying them.

Two facts in the existing stack make this low-risk:

- `tdt_sheets` already exposes per-sheet gid via `SheetMetadata.gid` and
  `SpreadsheetMetadata.get_sheet_by_gid(gid)`, and `parse_url()` returns
  `(spreadsheet_id, gid)`. The `kbs` backend currently keeps only tab titles.
- `tdt_core.clients.jira.PatchedJira.jql()` accepts a `fields` argument, so the
  `issuelinks` field can be fetched in the same key-batched query pattern used
  for the board JQL.
- The canonical board host space defaults to `PUB` (`WorkflowConfig.project_key = "PUB"`),
  so user-facing board links and default linked-ticket expansion must stay aligned
  to the PUB board surface unless explicitly overridden.
- `PatchedJira` already has `create_filter`, `search_boards`, and `create_board`
  (the latter accepts `board_type="scrum"`), but has **no** sprint methods. Agile
  sprints require a scrum board as `originBoardId` plus
  `POST rest/agile/1.0/sprint`, then `POST rest/agile/1.0/sprint/{id}/issue` to
  populate. These methods must be added to `PatchedJira`.

No linked-ticket expansion or sprint creation exists anywhere in the ecosystem
today; both are new. Sprint creation is requested as a configurable alternative
to the existing board, running after filter resolution.

## Goals / Non-Goals

**Goals:**

- Configure additional sprint-scope tabs by Google Sheets URL (gid), resolving
  the tab title at runtime so config survives tab renames.
- Merge URL-derived tab rows into the existing extraction with the same dedup
  and parse-error reporting.
- Keep the default board host surface aligned to the `PUB` Jira space for
  canonical board links and board creation.
- Optionally expand the planned key set with Jira-linked issues of source-project
  (default `PUB`) issues, excluding `Cloners`, targets in any project.
- Offer an agile scrum sprint as a configurable alternative to the existing board,
  created after filter resolution and populated with the resolved scope.
- Keep all new behavior opt-in and preserve dry-run (no Jira writes).
- Provide an opt-in end-to-end run that, after filter/sprint resolution, refreshes
  the `Sprint Report` and `Person Capacity` sheets from the resolved scope.

**Non-Goals:**

- No change to filter/board naming, find-or-create, or report layout.
- No allow-list link filtering (exclude-`Cloners` only).
- No recursive/transitive link traversal (one hop only).
- No sprint state automation beyond create + populate (no auto-start/close,
  no velocity/board column config).
- No change to `jira-daily-reports` report/capacity layout or reconciliation
  rules (the orchestration invokes the existing `sprint-sheet` path).

## Decisions

### D1: Configure extra sheets by URL+gid, resolve title at runtime

Tab titles get renamed; gids are stable. `SHEET_LINKS` (comma-separated Google
Sheets URLs) is parsed via `tdt_sheets.utils.parse_url` to extract gids, and a
new `TdtSheetsBackend.resolve_gids_to_titles()` maps gids→titles using the
metadata it already fetches. Resolved titles are appended to `sheet_targets` in
`_read_sheets` with an order-preserving dedup, then flow through the unchanged
`parse_rows` path.

_Alternative considered:_ configure by tab title (`sheet_names`). Rejected —
breaks on rename and the user explicitly wants sheet details derived from the
links.

### D2: Linked-ticket expansion via `issuelinks`, not JQL `linkedIssues()`

Jira Cloud has no native `linkedIssues()` JQL operator (that is a ScriptRunner
extension). The portable path is to fetch `fields=issuelinks` for the planned
source-project keys (same ≤50-key batching as `build_cross_project_jql`), then
walk `outwardIssue`/`inwardIssue` on each link. A new
`src/kbs/jira/link_expander.py` owns this logic.

### D3: Exclude `Cloners`, include all other link types, targets any project

Filtering is by link-type **name**. `excluded_link_types` defaults to
`{"Cloners"}` (the clone link type, whose names are "clones" / "is cloned by").
Every other link type (Split, Blocks/Blocked, Relates, etc.) is included. No
project filter is applied to the linked **targets** — the board is cross-project.
The source side is filtered to `link_expand_project` (default `PUB`) so only
planned PUB issues seed the expansion.

### D4: Opt-in, expansion before JQL build

`expand_linked` defaults `False`; existing runs are unchanged. When enabled,
expansion runs in `sync` after `issue_keys` is gathered and before
`build_cross_project_jql`, so linked keys participate in the same JQL, filter
update, and board verification. The Jira client (`JiraClientFactory.from_env()`)
is hoisted ahead of the JQL build; reads are safe in dry-run.

### D5: Board mode selector; sprint as an alternative after filter resolution

A `board_mode` config (`BOARD_MODE` = `kanban` | `sprint` | `both`, default
`kanban`) selects how the resolved filter is surfaced. `kanban` preserves today's
behavior exactly. `sprint` and `both` run agile sprint creation after the filter
is resolved, reusing the resolved key scope. In `sprint` mode the kanban board is
neither found nor created (`resolve_sprint_scope(create_board=False)`), so scope
is surfaced only via the scrum board; `both` keeps the kanban board in addition
to the scrum sprint. The mode lives on `WorkflowConfig` so it is set per-workflow
via YAML or env.

_Alternative considered:_ a single boolean `create_sprint`. Rejected — `both` is
a real need (keep the existing board while also seeding a scrum sprint), and a
tri-state mode reads more clearly than two booleans.

### D6: Sprint on a scrum board backed by the resolved filter

Agile sprints require an origin scrum board. A new `src/kbs/jira/sprint_sync.py`
finds-or-creates a scrum board (canonical name, e.g. `Sprint N Board (Scrum)` to
avoid colliding with the main board name) backed by the resolved filter via
the existing `create_board(board_type="scrum")`, then find-or-creates the sprint
by canonical name on that board, then moves the resolved keys into it. New
`PatchedJira` methods: `create_sprint(name, origin_board_id, start, end, goal=None)`,
`search_sprints(board_id, state)`, `move_issues_to_sprint(sprint_id, keys)`
(chunked, agile API caps moves at 50 keys/call).

_Alternative considered:_ reuse the existing board's id as origin. Rejected —
sprints require a scrum board; a kanban board cannot host sprints.

### D7: Sprint dates from the workbook title, year inferred

Sprint name/dates come from the same workbook title parse used for filter/board
naming. The title range (e.g. `08 Jun - 19 Jun`) omits a year, so the year is
inferred (current year, rolling to next year only if that would place the sprint
wholly in the past) to produce valid ISO start/end datetimes. Created sprints
start in the `future` state; the pipeline does not auto-start them.

**Pipeline semantics:**

- Report and capacity refresh runs only on a live run when `refresh_reports=True`; dry-run reports the intended refresh without writing.
- Each stage is classified as required (fail-stop, non-zero exit) or non-required (fail-soft, recorded in `SyncResult.errors`):
  - **Required:** spreadsheet resolution, scope extraction yielding a usable key set, JQL build, reporting-filter resolve/update.
  - **Non-required:** individual extra-tab reads, linked-ticket expansion, board count verification, report/capacity refresh.

### D8: End-to-end orchestration drives report + capacity refresh on resolved scope

`kbs sync` is the single end-to-end entry point: read spreadsheet → extract
required sheets → extract tickets → resolve filter (JQL) → resolve board/sprint
→ refresh sprint report + person capacity. The report/capacity refresh runs only
on a live run after the filter and board/sprint are resolved, reusing the
existing `jira-daily-reports sprint-sheet` path (which writes both `Sprint
Report` and `Person Capacity` from one snapshot). The existing
`_run_post_sync_reports` hook is generalized: it is invoked as the final
orchestration step and SHALL pass the resolved spreadsheet so the report targets
the same workbook.

**Scope-parity reality (validated against code):** the filter-fallback parity
plan does NOT work as originally written. Two facts in
`jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py`
defeat it:

- `write_sheet()` unconditionally calls `read_sprint_ticket_scope(spreadsheet_id)`
  and `report.set_bucket_keys(...)`, **overwriting** any keys a caller set
  beforehand. Passing the resolved spreadsheet alone cannot inject kbs-expanded
  keys — they are discarded on the next line.
- `SprintReportSheetReport.run()` branches `if self._bucket_keys:` →
  `jql = "issuekey in (<bucket_keys>)"` and only uses `filter = {id}` when bucket
  keys are empty. Since bucket keys are essentially never empty, the
  filter-fallback path is unreachable, and the resolved filter JQL is never
  consulted.

**Revised mechanism — explicit key-set handoff:** the orchestration SHALL pass
the resolved expanded key set to the report path, and `jira-daily-reports` SHALL
be modified so an explicit caller-provided scope is honored instead of being
overwritten by a bucket re-read:

- Add an optional resolved-scope parameter (resolved keys + resolved filter id)
  threaded into `write_sheet()` / `SprintReportSheetReport`.
- When a caller scope is provided, `write_sheet()` SHALL NOT re-read bucket
  scope, and `run()` SHALL seed `issuekey in (<resolved_keys>)` from it.
- When no caller scope is provided, the bucket-derived behavior is preserved
  exactly (standalone `sprint-sheet` and the hourly refresh are unchanged).
- The report's own `_expand_issue_graph` is independent from kbs `expand_linked`
  and is seeded from the resolved keys, so it can only widen, never narrow, the
  resolved scope.

This is a real cross-repo change (`jira-kanban-from-spreadsheet` →
`jira-daily-reports`), not a config flag, and the Impact/tasks reflect it.

_Alternative considered:_ have kbs write the report sheets directly. Rejected —
`jira-daily-reports` owns the report/capacity contract; duplicating it would
fork the layout and reconciliation rules.

_Alternative considered:_ make `sprint-sheet` natively read `SHEET_LINKS` /
`EXPAND_LINKED`. Rejected — duplicates kbs extraction/expansion logic in a second
repo and re-introduces the divergence this change removes; the explicit handoff
keeps one source of truth (kbs) for scope.

### D9: Per-sprint dashboard + four-link report header

Each sprint gets its own dashboard, created in the pipeline (option B), and the
sprint report header renders filter, board, sprint, and dashboard hyperlinks.

**Dashboard creation home (jdr report path, live only):** kbs depends only on
`tdt-core[jira]`; the canonical dashboard builder lives in `jira_skill.dashboard`
and is already wired into jdr via `delivery/jira_dashboard.build_dashboard`.
Forcing kbs to import `jira_skill` (or jdr) would be a bad new coupling, so the
per-sprint dashboard is find-or-created **in the jdr report path** that the
orchestration already invokes (`sprint-sheet`). jdr has the resolved filter id
(via `RESOLVED_FILTER_ID`) and the sprint number/name, so it find-or-creates a
per-sprint dashboard named `Sprint N Dashboard` (distinct from the shared
`TDT Sprint Reports`) backed by that filter. This still runs inside the
end-to-end pipeline (the sync's report-refresh stage), satisfying the spec
requirement. Creation is gated behind live mode; dry-run reports the intended
dashboard only. Dashboard failure is non-required (fail-soft): it is recorded
and does not abort the report.

**ID handoff:** kbs passes the ids it already resolves to the report subprocess
as `RESOLVED_SPRINT_ID`, `RESOLVED_BOARD_ID`, and `RESOLVED_PROJECT_KEY`,
alongside the existing `RESOLVED_FILTER_ID` / `RESOLVED_SCOPE_KEYS`. The
dashboard id is produced by jdr itself (it creates the dashboard) and rendered
directly, so it is not handed off from kbs. This mirrors the established
explicit-handoff pattern from D8 rather than having the report re-derive ids by
title search.

**Report header (jdr):** `build_sheet_rows` renders a link per resolved id:

- Filter — `{site}/issues/?filter={filter_id}` (existing)
- Board — `{site}/jira/software/c/projects/{project}/boards/{board_id}` (existing)
- Sprint — `{site}/jira/software/c/projects/{project}/boards/{board_id}?sprint={sprint_id}` (new)
- Dashboard — `{site}/jira/dashboards/{dashboard_id}` (new)

Each link is rendered only when its id is present; absent ids fall back to the
current text-only rendering, so standalone `sprint-sheet` runs (no handoff) are
unchanged. The markdown header gains the same links additively.

_Alternative considered (A — render-if-exists):_ have the report find a dashboard
by name and link it without the pipeline creating one. Rejected per user
decision — each sprint should own its dashboard, so creation belongs in the
pipeline (B) to guarantee the link resolves.

_Alternative considered (create dashboard in kbs):_ Rejected — kbs has no
`jira_skill`/jdr dependency and the dashboard builder + report rendering both
live in jdr; creating it in jdr's report path avoids a new cross-package import
and keeps dashboard lifecycle next to the report that links it.

_Alternative considered:_ create the dashboard in `jira-daily-reports`
`sprint-bootstrap` instead of `kbs sync`. Rejected — `kbs sync` is the
end-to-end entry point (D8) and already owns filter/board/sprint creation;
colocating dashboard creation keeps one orchestrator.

## Risks / Trade-offs

- [Large planned set → many `issuelinks` fetches] → Reuse ≤50-key batching;
  expansion is opt-in and one-hop only, bounding API calls.
- [Link-type name drift in Jira] → `excluded_link_types` is configurable; default
  targets the standard `Cloners` type. Document the exact names.
- [gid URL points to a tab with a different row schema] → `parse_rows` already
  skips rows without a valid `issue_key` and collects parse errors per tab, so
  non-conforming tabs degrade gracefully rather than failing the run.
- [Cross-project linked targets inflate board count] → Expected; board is
  cross-project and `verify_count` compares against the expanded key count.
- [Sprint date year inference is wrong near year boundary] → Inference rolls to
  next year only when the sprint would otherwise be wholly past; document and
  allow an explicit override via title if needed.
- [Scrum board name collides with existing board] → Use a distinct scrum board
  name (`Sprint N Board (Scrum)`); find-or-create matches exact name.
- [Move-to-sprint API 50-key cap] → Chunk `move_issues_to_sprint` in ≤50-key
  batches, mirroring the JQL batching.
- [Report scope diverges from kbs-expanded scope] → sprint-sheet recomputes own scope; orchestration SHALL pass resolved key set + filter id explicitly via resolved_scope param, and report SHALL honor caller-provided scope when present instead of re-reading bucket tabs. Document that report parity is handoff-driven, not filter-driven.
- [Per-sprint dashboard creation fails or is slow] → Dashboard creation is non-required (fail-soft): recorded in `SyncResult.errors`, never aborts the sync. Find-or-create is idempotent (reuses an existing `Sprint N Dashboard`), and writes are live-only.
- [Sprint/dashboard link ids absent at report time] → Each header link renders only when its id is present in the handoff; absent ids fall back to text-only, so standalone `sprint-sheet` runs are unchanged.

## Migration Plan

1. Land code behind defaults-off config; existing cron runs unchanged.
2. Set `SHEET_LINKS` and `EXPAND_LINKED=true` in `~/.tdt/.env` for the PUB
   workflow once verified in dry-run.
3. Optionally set `BOARD_MODE=sprint` (or `both`) once sprint creation is
   verified in dry-run; default `kanban` keeps current behavior.
4. Roll back by unsetting the env vars — no schema or Jira state migration.

## Open Questions

None — link-type policy (exclude `Cloners`) and target scope (any project) are
confirmed. Sprint defaults (scrum-board-backed, future state, title-derived
dates with inferred year, populate on live run) are chosen autonomously and can
be revised on review.
