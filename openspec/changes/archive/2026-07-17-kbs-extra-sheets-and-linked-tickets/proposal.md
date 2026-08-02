## Why

The `kbs` sprint board pipeline currently extracts issue keys only from a fixed
set of bucket tabs and includes only the keys literally listed in those tabs.
Sprint planning now also tracks scope in additional tabs (e.g. `Ewallet Scope`,
`related-to-items-work-in-sprint`) and the team needs the PUB board to also pull
in tickets linked to planned PUB issues (split/block/blocked-by and other link
types) without manually copying them into the sheet. Cloned tickets are
duplicates and must stay out.

## What Changes

- Extend sheet extraction so additional tabs can be configured by their Google
  Sheets **URL** (gid), with the tab title resolved at runtime from spreadsheet
  metadata. This keeps configuration stable when tab titles are renamed and lets
  "sheet details be derived from the spreadsheet links."
- Merge rows from these URL-derived tabs into the existing bucket-tab extraction,
  preserving the current issue-key dedup and parse-error reporting.
- Add an opt-in linked-ticket expansion step for the PUB board: for planned
  issues in the configured source project (default `PUB`), include their linked
  issues via the Jira `issuelinks` field.
- Linked-ticket expansion SHALL include **all** link types except `Cloners`
  (clones / is cloned by), and SHALL include linked targets in **any** project.
- Add a board-mode config option so that, after the reporting filter is
  resolved, the pipeline can create an **agile scrum sprint** instead of (or in
  addition to) the board. The sprint is created on a scrum board backed
  by the resolved filter, named from the workbook title (`Sprint N`), with
  title-derived dates, and the planned issues are moved into it on a live run.
- Make `kbs sync` an end-to-end pipeline: resolve spreadsheet (config or link) →
  extract required sheets → extract ticket scope → build JQL → resolve filter →
  create/update board or sprint (default kanban) → refresh sprint report and
  person capacity. Each stage consumes the prior stage's output, and the report
  refresh consumes the resolved filter scope so it reflects the sheet-merged and
  linked-ticket-expanded keys (not a separately recomputed bucket-only scope).
- Give each sprint its own native Jira dashboard: the report refresh path
  find-or-creates a per-sprint dashboard (`Sprint N Dashboard`) backed by the
  resolved filter, and the sprint report header renders filter, board, sprint,
  and dashboard links when their ids are available.
- All new behavior is opt-in via config/env and preserves existing dry-run
  semantics (no Jira writes in dry-run).

## Capabilities

### New Capabilities

- `sprint-extra-sheets`: configure additional sprint-scope tabs by Google Sheets
  URL, resolve gid→tab-title from spreadsheet metadata, and merge their issue
  rows into the extracted sprint scope.
- `sprint-linked-ticket-expansion`: optionally expand the planned issue-key set
  with Jira-linked issues of source-project issues, excluding clone links, with
  targets allowed in any project.
- `sprint-agile-creation`: as a configurable alternative to the existing board,
  find-or-create an agile scrum sprint (on a scrum board backed by the resolved
  filter) after filter resolution, and move the planned issues into it on a live
  run.
- `sprint-end-to-end-orchestration`: run the full pipeline from one `kbs sync`
  invocation (spreadsheet → sheets → scope → JQL → filter → board/sprint →
  report + capacity refresh), with the report refresh consuming the resolved
  filter scope and gated behind live mode.
- `sprint-report-links`: find-or-create a per-sprint native Jira dashboard in
  the report refresh path, backed by the resolved filter, and render the sprint
  report header with filter, board, sprint, and dashboard hyperlinks (each
  rendered when its id is available).

### Modified Capabilities

<!-- No requirement changes to sprint-spreadsheet-ssot: title parsing,
     filter/board find-or-create, dry-run gating, and report contract are
     unchanged. This change only widens how the issue-key set is gathered
     before JQL is built. -->

## Impact

- **Code (`jira-kanban-from-spreadsheet`)**:
  - `src/kbs/config.py`: new opt-in fields (`sheet_links`, `expand_linked`,
    `link_expand_project`, `excluded_link_types`, `board_mode`,
    `refresh_reports`) + env parsing (`SHEET_LINKS`, `EXPAND_LINKED`,
    `LINK_EXPAND_PROJECT`, `EXCLUDED_LINK_TYPES`, `BOARD_MODE`,
    `REFRESH_REPORTS`).
  - `src/kbs/sheets/tdt_backend.py` + `src/kbs/sheets/reader.py`: gid→title
    resolver using existing `tdt_sheets` metadata (`SheetMetadata.gid`,
    `get_sheet_by_gid`).
  - `src/kbs/jira/link_expander.py` (new): `issuelinks`-based expansion.
  - `src/kbs/jira/sprint_sync.py` (new): find-or-create scrum board + sprint,
    move planned issues into the sprint (live only).
  - `src/kbs/cli.py`: merge URL-derived tabs in `_read_sheets`; run link
    expansion before JQL build; after filter resolution, run sprint creation
    when board mode selects it; and generalize `_run_post_sync_reports` to hand
    the resolved expanded key set, filter id, board id, sprint id, and project
    key to the report refresh. kbs does not create dashboards because it has no
    `jira_skill` dependency.
- **Code (`jira-daily-reports`, cross-repo)**:
  - `src/jira_daily_reports/reports/sprint_report_sheet.py` +
    `delivery/tdt_sheet.py`: accept an optional caller-provided resolved scope
    (keys + filter id). When provided, `write_sheet()` SHALL NOT overwrite it by
    re-reading bucket scope, and `run()` SHALL seed `issuekey in (<resolved>)`
    from it. Absent a caller scope, bucket-derived behavior is unchanged. This
    is required because the original filter-fallback parity path is unreachable
    (validated: `write_sheet()` always re-reads bucket scope; `run()` prefers
    bucket keys over `filter = {id}`).
  - `src/jira_daily_reports/reports/sprint_report_sheet.py`: read
    `RESOLVED_BOARD_ID`, `RESOLVED_SPRINT_ID`, and `RESOLVED_PROJECT_KEY`,
    find-or-create the per-sprint dashboard (`Sprint N Dashboard`) in the report
    path using jdr's `delivery/jira_dashboard` helper, and render the sprint
    report header with filter, board, sprint, and dashboard hyperlinks. The
    dashboard id is produced by jdr itself; each link is rendered only when its
    id is present.
  - `config/workflow.yaml`, `README.md`, `OPERATOR_RUNBOOK.md`: document the
    new opt-in inputs.
- **APIs/Dependencies**: uses existing `tdt_core` `PatchedJira.jql()` with the
  `issuelinks` field and `tdt_sheets` metadata; **adds** sprint/scrum-board
  methods to `tdt_core` `PatchedJira` (`create_sprint`, `search_sprints`,
  `move_issues_to_sprint`, scrum board search/create via existing
  `create_board(board_type="scrum")`); reuses the existing
  `jira_skill.dashboard` find-or-create helper (via jdr's
  `delivery/jira_dashboard.build_dashboard`) for the per-sprint dashboard; no
  new third-party dependencies.
- **Config/Env**: `~/.tdt/.env` gains optional `SHEET_LINKS`, `EXPAND_LINKED`,
  `LINK_EXPAND_PROJECT`, `EXCLUDED_LINK_TYPES`, a board-mode selector
  (`BOARD_MODE` = `kanban` | `sprint` | `both`, default `kanban`), and
  `REFRESH_REPORTS` (opt-in report + person-capacity refresh). Defaults keep
  current behavior unchanged.
- **Skills/Docs**: `board-from-spreadsheet` skill documents extra sheets,
  linked-ticket expansion, and the agile sprint option.
- **Non-Goals**:
  - No change to filter/board naming or find-or-create logic.
  - No allow-list link filtering (exclude-`Cloners` only).
  - No recursive/transitive link walking (one hop from planned issues).
  - No change to `jira-daily-reports` report calculations or reconciliation
    rules. The orchestration adds an optional resolved-scope handoff to the
    `sprint-sheet` write path (so expanded keys are honored) but does not alter
    how rows/capacity are computed, and standalone report runs keep their
    bucket-derived scope unchanged. The only sheet-layout change is the header
    link row (filter/board/sprint/dashboard), which renders each link only when
    its id is available and is otherwise backward compatible.
  - No sprint completion/closing or velocity automation (create + populate only).
