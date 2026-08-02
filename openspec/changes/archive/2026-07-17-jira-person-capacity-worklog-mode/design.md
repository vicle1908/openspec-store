# Jira Person Capacity Worklog Mode - Design

## Context

`jira-daily-reports` currently produces a ticket-centric sprint sheet. It is strong for status and risk, but weak for person-level capacity tracking. Live workspace data (from the v1 spec, 2026-05-28) showed that assignee and worklog author diverge 77% of the time on a 65-issue scope, so one-dimensional person attribution creates incorrect conclusions. The ticket-first `_build_person_capacity` only captures worklog activity on issues already in the bucket, which is a small subset of the team's actual effort.

This change replaces that calculation with a person-first JQL query keyed by `worklogAuthor`. The roster of people is loaded from the existing `Person Capacity Mapping` sheet tab; the fetcher then asks Jira for all worklogs authored by that roster inside a date window.

Constraints:

- Jira board behavior may be Kanban-like (`Sprint: N/A`), so date windows cannot always depend on sprint metadata. Workbook-title parsing, sprint window derivation, and daily column layout logic MUST stay unchanged.
- Jira Cloud documented max for `in (...)` clauses is 150 ids. Larger rosters MUST be chunked and the results merged.
- JQL and `issue_get_worklog` may hit HTTP 429 (rate limit) and timeout. The fetcher MUST retry with exponential backoff, max 3 attempts.
- Worklogs can be sparse and/or paginated. Existing pagination checks (`total > len(worklogs)`) MUST be preserved.
- Existing sprint report semantics (`missing` vs `unavailable`) and stable sheet writing behavior MUST be preserved. The `Sprint Report` tab is unchanged.
- `JIRA_FILTER_ID` is no longer required for the activity-only flow. The legacy error message for a missing `JIRA_FILTER_ID` is removed.

Stakeholders:

- Engineering managers and tech leads tracking team capacity.
- Individual contributors validating workload and logged activity.
- Program managers requiring a daily person-level effort view.

## Module Layout (changes scoped to `jira-daily-reports`)

```
jira-daily-reports/
├── src/jira_daily_reports/
│   ├── person_worklog_source.py            [NEW] JQL-first worklog fetcher; public API updated: display-name key, account_ids field, concurrency, report_timezone, _normalize_display_name, _parse_report_timezone, find_jira_display_name_collisions
│   ├── planning_sheet_fields.py            [UNCHANGED]
│   ├── reports/sprint_report_sheet.py      [MODIFIED] _build_person_capacity rewritten
│   ├── delivery/tdt_sheet.py               [UNCHANGED for tab writing; consumes new row shape]
│   ├── work_item_fields.py                 [UNCHANGED] format_seconds, worklog_started_date, person_identity reused
│   └── cli.py                              [UNCHANGED] sprint-sheet CLI surface preserved
└── tests/
    ├── test_person_worklog_source.py       [NEW] unit tests
    └── test_sprint_report_sheet_person_capacity.py   [REWRITTEN] integration tests
```

## Runtime Data Flow

```
Person Capacity Mapping tab  ─┐
                              ├─► load_roster_display_names()  ──► fetch_person_worklogs(jira, display_names, window)
JQL: worklogAuthor in (names)│                                       │
  AND worklogDate in window  │                                       │
        ────────────────────►─┘                                       │
                                                                      ▼
                                              PersonWorklogAggregate (per-display-name)
                                                                      │
                                                                      ▼
                                                  Person Capacity sheet rows
                                                  (No., Person, Worked Tickets, Logged Total, daily × N)
                                                                      │
                                                                      ▼
                                                  unmapped_worklog_authors reconciliation block
```

## The Boundary: `PersonWorklogAggregate`

The fetcher module exposes a small dataclass pair:

```python
@dataclass(frozen=True)
class PersonWorklogEntry:
    issue_key: str
    started: datetime      # tz-aware, in report timezone
    seconds: int

@dataclass
class PersonWorklogAggregate:
    display_name: str                           # from roster or worklog author; primary key
    account_id: str = ""              # first non-empty author.accountId observed (never None)
    account_ids: tuple[str, ...] = ()         # all distinct author.accountIds observed
    entries: list[PersonWorklogEntry] = field(default_factory=list)

    @property
    def worked_ticket_keys(self) -> set[str]: ...
    @property
    def logged_total_seconds(self) -> int: ...
    @property
    def daily_seconds(self) -> dict[date, int]: ...
```

Two companion dataclasses:

- `RosterLoadResult`: holds the validated list of `display_names` (deduplicated, ordered) plus the structured reconciliation payload (`missing_display_name_rows`, `duplicate_member_key_rows`, `display_name_collisions`).
- `UnmappedWorklogAuthor`: holds display name, optional accountId enrichment, total seconds, and first/last seen dates for worklog authors that are not in the roster.

## Public API of `person_worklog_source.py`

- `load_roster_display_names(sheet_client, spreadsheet_id) -> RosterLoadResult`
  - Returns the deduplicated, ordered list of display names plus a structured reconciliation payload (`missing_display_name_rows`, `duplicate_member_key_rows`, `display_name_collisions`).
  - Reads the `Dropdown Keys - Do Not Delete -` tab by default; overridable via `PERSON_CAPACITY_MAPPING_SHEET_NAME`.
- `fetch_person_worklogs(jira, display_names, window_start, window_end, *, concurrency=None, report_timezone=None) -> list[PersonWorklogAggregate]`
  - Performs the JQL + per-issue worklog fetch and returns one aggregate per display name that had any worklog.
  - Internal JQL: `worklogAuthor in ("name1", "name2", ...) AND worklogDate >= "YYYY-MM-DD" AND worklogDate <= "YYYY-MM-DD"` (all names NFC-normalized before JQL emission).
  - JQL is paginated with `startAt`. Each returned issue is fetched with `issue_get_worklog()` and entries are filtered to roster display names and to `[window_start, window_end]` on `started` (converted to report timezone when `report_timezone` is provided).
  - JQL is chunked at 150 display names (Jira Cloud documented max). Results are merged.
  - JQL and `issue_get_worklog` calls retry with exponential backoff (1s, 2s, 4s, cap 30s), max 3 attempts.
  - Concurrency (default 8 via `WORKLOG_FETCH_CONCURRENCY`) parallelizes per-issue worklog fetches (v1.4).
  - `report_timezone` (default None → UTC) converts each `started` to the report's local timezone before window filtering and per-day bucketing (v1.4.5).
- `find_unmapped_worklog_authors(aggregates, roster_names) -> list[UnmappedWorklogAuthor]`
  - Surfaces display names that appeared in worklogs but are not in the roster. Defensive — the JQL is already roster-scoped, but this catches API-side drift.
- `find_jira_display_name_collisions(aggregates) -> list[tuple[str, tuple[str, ...]]]`
  - Returns one `(display_name, (account_id, ...))` per aggregate whose `account_ids` has more than one entry. Used for the `jira_display_name_collision` reconciliation row.

## Outputs — the New `Person Capacity` Tab

| Column | Source | Behavior |
|---|---|---|
| `No.` | row index (1-based) | Sequential |
| `Person` | roster `member_key` (preferred) → `jira_nick_name` → `account_id` | Resolved by roster order |
| `Jira Account ID` | roster `jira_account_id` | Surfaced for reconciliation |
| `Role` | roster `role` | Surfaced for ops |
| `Worked Tickets` | count of distinct `issue_key` in aggregate | Same as today |
| `Logged Total` | sum of `seconds` for all entries | Formatted as `Xh Ym` |
| `Worked Ticket Links` | plain-text issue keys, one per line (sorted) | Copy/paste-able; the clickable surface is the report header links (filter + board) |
| `Daily Ticket Details` | human-readable per-day text: `YYYY-MM-DD: K1 (Xs), K2 (Ym), ...` | Diagnostic, plain text. Days sorted ascending, issues sorted by key, seconds summed per (day, issue) |
| Daily columns (one per day in window) | `K1 (Xs), K2 (Ym), ...` — issue keys (sorted) with time labels per (day, issue), comma-separated; or ` ` (single space) for days with zero worklogs | The "daily logged tickets" diagnostic. Same timezone, same column count. Matches the v1.0 legacy contract where each per-day cell showed the issues worked on that day with their time totals |

**Removed columns** (relative to v2 planning-alignment spec):
- `Assigned Tickets`
- `Original Estimation Total`
- All `Planned` columns (these were planning-merged, not part of v1)

## Identity Resolution Order for the `Person` Column

1. `member_key` from mapping tab (preferred — matches existing sheet semantics).
2. `jira_nick_name` (display name in mapping).
3. `account_id` (last resort, opaque).

If a mapping row has a `member_key` but an empty `jira_nick_name`, that row is **skipped from the roster** and a `roster_row_missing_display_name` reconciliation entry is emitted.

## Row Ordering

1. Roster members with worklogs, sorted by `Logged Total` desc, then by `Worked Tickets` desc, then by `Person` asc.
2. Roster members without worklogs, sorted by `Person` asc (separate visual block).
3. Reconciliation rows (single block, fixed order: `roster_row_missing_display_name`, `roster_row_duplicate_member_key`, `roster_display_name_collision`, `jira_display_name_collision`, `unmapped_worklog_authors`, `roster_without_worklogs`).

## Pre-Flight Checks (run before fetcher)

1. `load_roster_display_names` returns at least 1 valid display name → otherwise fail fast with `person_capacity_roster_unavailable`.
2. `window_start <= window_end` → otherwise fail fast with `person_capacity_window_invalid`.
3. `window_days <= 90` (soft cap) → warn if exceeded (`person_capacity_window_oversized`).

## Error Handling and Edge Cases

| Failure mode | Detection | User-visible behavior |
|---|---|---|
| Mapping tab missing or unreadable | `load_roster_display_names()` returns empty `display_names` | Fail with `person_capacity_roster_unavailable` log + actionable error pointing at the Dropdown Keys tab name |
| Mapping tab has rows missing `jira_nick_name` | Detected during roster build | Each missing row → `roster_row_missing_display_name` reconciliation entry. Roster still proceeds with valid rows. |
| `JIRA_FILTER_ID` set but unreferenced in v1 | Pre-flight check | Spec clarifies it is no longer required. The legacy error message is removed. |
| JQL `worklogAuthor in (...)` exceeds 150 display names | `len(display_names) > 150` | Split into chunks of 150, run sequentially, merge results. Log `worklog_jql_chunked chunk=N total=M`. |
| Jira rate limit (HTTP 429) on JQL pagination or `issue_get_worklog` | Retryable HTTP exception | Retry with exponential backoff (1s, 2s, 4s, cap 30s), max 3 attempts. Log `worklog_jira_retry` on each retry. |
| Two Jira users share the same `displayName` | `aggregate.account_ids` has > 1 entry | `find_jira_display_name_collisions` surfaces the collision as a `jira_display_name_collision` reconciliation row. |
| `issue_get_worklog` returns partial results | Existing pagination check | Existing behavior: if `total > len(worklogs)`, follow up. No change. |
| Worklog `started` is null or unparseable | `worklog_started_date()` returns "" | Entry excluded from daily columns but counted in `Logged Total` and `Worked Tickets`. Log `worklog_started_missing issue_key=X count=N`. |
| `timeSpentSeconds` is 0 or null | `int(entry.get("timeSpentSeconds") or 0)` | Counted as 0 seconds. Existing behavior. |
| Empty display name from Jira | `_worklog_author_display_name` returns "" | Roster display name is used as the label; `accountId` is used as a fallback label if both are empty. |
| Mapping `member_key` duplicates | Detected during roster build | First occurrence wins; subsequent duplicates → `roster_row_duplicate_member_key` reconciliation entry. |
| Report timezone is invalid | `_parse_report_timezone` receives an unrecognized name | Falls back to UTC and logs `worklog_invalid_timezone tz=<name>` warning. |
| Report timezone missing | `report_timezone=None` passed to `fetch_person_worklogs` | `_parse_report_timezone(None)` returns UTC; behavior is backward-compatible with v1.4.3. |

## Migration

No data migration is required (the output is a sheet tab, not a database).

1. **Day 0:** Spec approved. `person_worklog_source.py` added. Tests added. Sheet writer rewired.
2. **Day 0:** `sprint-sheet` runs against the team workbook. The new tab overwrites the old one. Operators see:
   - Old tab had: `Assigned Tickets`, `Original Estimation Total`, `Worked Tickets`, `Logged Total`.
   - New tab has: `Worked Tickets`, `Logged Total`.
   - Reconciliation rows appear at the bottom.
3. **Day 1 (if no rollback signal):** Promote to default. Document the change in `.agents/skills/jira-daily-reports/SKILL.md` lines 147-186.
4. **Day 7 (post-deploy review):** Verify reconciliation rows are empty or have a known population. If `unmapped_worklog_authors` is non-empty, decide whether to update the mapping tab or accept the gap.

### Rollback

If the new mode breaks a workflow, the rollback is a one-line revert of `_build_person_capacity()` to the legacy implementation. The legacy implementation is **not** kept as a fallback mode in v1. If a rollback is needed, the spec is updated to revisit.

## Out of Scope (deferred)

- Re-adding ownership dimensions as a layered second query.
- A separate `planned` view driven purely by the sheet.
- `CapacitySignal` wiring (the `jira-skill` model is unaffected by this change).


## v1.4.5 Design Notes — Unicode NFC + Report-timezone Fixes

### Rationale for NFC normalization

A live probe on 2026-06-16 revealed that `Vũ Văn Tuân` (and potentially
other Vietnamese-named members) was missing from the Person Capacity
report despite having 16 worklogs in the window. The root cause was a
Unicode encoding mismatch:

- The roster in the `Dropdown Keys - Do Not Delete -` sheet stores
  the name in **NFC** form: `Vũ Văn Tuân` (11 characters, with
  precomposed Vietnamese diacritics `ũ`, `ă`, `â`).
- Jira Cloud's `author.displayName` for the same person was in **NFD**
  form: `V` + `u` + `U+0303` (combining tilde) + ... (12 characters,
  with decomposed Vietnamese diacritics).

This is a classic macOS-vs-Windows/Android difference: the macOS
Vietnamese input method (VNI, Telex) produces NFD by default, while
Windows/Android Vietnamese keyboards typically produce NFC. When the
roster entry was pasted into Google Sheets from a different source
than the Jira account creation, the two forms differ byte-for-byte but
are semantically identical (Unicode `unicodedata.normalize("NFC", x) ==
unicodedata.normalize("NFC", y)`).

Python's `str.__eq__` is byte-exact and returns `False` for these two
forms, so `_merge_issue_worklogs`'s `author_name in roster_names`
filter silently dropped 44h of worklogs for one member.

**Decision:** Apply NFC normalization at every boundary:

1. `load_roster_display_names` normalizes the sheet value when reading.
2. `_worklog_author_display_name` normalizes the Jira-returned value.
3. `_build_worklog_jql` normalizes the value before inserting into JQL.
4. A single helper, `_normalize_display_name`, encapsulates the rule
   (`unicodedata.normalize("NFC", value).strip()` + whitespace collapse).

This is **defense in depth** — even if a future code path bypasses one
boundary, the other two still catch the mismatch. It is also a no-op
for any name that is already in NFC (or pure ASCII), so there's no
performance cost.

The longer-term recommendation (out of scope for v1.4.5) is to also
update the roster sheet to use NFC consistently, so a single source of
truth holds the canonical form.

### Rationale for report-tz windowing

The v1.4.3 fix changed `daily_secs` keys from `datetime.date` objects
to ISO strings, fixing a silent key-mismatch bug. But the v1.4.3 fix
did not address a related, more fundamental issue: the window filter
in `_merge_issue_worklogs` used `started_dt.date()` directly, which
for an offset-aware datetime returns the date **in the offset of the
datetime, not the report's local timezone**.

Worked example:

- A worklog at `2026-06-10 17:00:00 +00:00` (= `2026-06-11 00:00 +07`)
  in a window `2026-06-10 → 2026-06-19` (window dates in `+07`):
  - The old filter: `started.date() = 2026-06-10` (in `+00:00` offset),
    so `2026-06-10 <= 2026-06-10 <= 2026-06-19` → **included**, but
    the entry is bucketed under `2026-06-10` (UTC date) instead of
    `2026-06-11` (the +07 date the team expects to see).
  - The new filter (v1.4.5): `started.astimezone(+07).date() = 2026-06-11`,
    so the entry is **correctly bucketed** under `2026-06-11`.

The bug was masked in the v1.4.3 verification probe because the
team's worklogs all fell in business hours where the 1-hour shift
between UTC+7 and UTC+8 didn't cross a day boundary. But for any
member who logs work at the local-day boundary (e.g. late evening), the
bucketing would have been wrong.

**Decision:**

- Add a `report_timezone: str | None` parameter to
  `fetch_person_worklogs`. When provided, parse it via
  `zoneinfo.ZoneInfo` and pass the resulting `ZoneInfo` to
  `_merge_issue_worklogs`.
- The merge path uses `started_dt.astimezone(report_tz).date()` for the
  window filter and stores the local-tz datetime as `effective_started`.
- The `daily_secs` and `daily_issue_seconds` buckets in
  `_build_person_capacity` then naturally use the local date because
  `entry.started.date()` returns the local date (the datetime is
  already in the report's tz after the merge step).
- Default `report_timezone=None` → falls back to UTC, preserving
  backward compatibility for callers that don't pass it.
- `sprint_report_sheet.py` threads `self.person_timezone` (which was
  already resolved from `PERSON_CAPACITY_TIMEZONE` env var) into
  `fetch_person_worklogs`.

**Out of scope for v1.4.5:** Per-member timezone. The team is
geographically distributed and a single report timezone is a
simplification. A future v1.5 change should add a per-member timezone
column to the roster and pass it through. Tracked as a separate
work item.

### What did NOT change

- `PersonWorklogEntry.started` still has the same dataclass shape
  (`tz-aware datetime`). The docstring was already correct
  (`# tz-aware, in report timezone`); the implementation now matches
  the docstring.
- The JQL chunk size, the JQL pagination logic, the retry behavior,
  the concurrency model — none of these changed.
- The `Person Capacity` tab layout, columns, and formatting — none
  of these changed. The fix is purely in the data layer that
  populates the tab.
- Backward compatibility: callers that don't pass `report_timezone`
  get UTC semantics, matching the v1.4.3 behavior.

## References

- `tdt-meta/docs/superpowers/specs/2026-06-15-person-capacity-mode-design.md` — full design rationale and live research.
- `tdt-meta/docs/superpowers/plans/2026-06-15-person-capacity-mode-plan.md` — TDD implementation plan.
- `openspec/changes/jira-person-capacity-report/specs/person-capacity-report/spec.md` — v1 spec for the existing Person Capacity tab.
- `openspec/changes/jira-person-capacity-planning-alignment/specs/person-capacity-planning-alignment/spec.md` — v2 spec adding planning-merged rows.
- `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py:560-800` — current `_build_person_capacity()` (activity-only, roster-driven, v1.1+).
- `jira-daily-reports/src/jira_daily_reports/work_item_fields.py:100-175` — `worklog_started_date()` and `issue_worklog_details()` (reused as-is).
- `jira-skill/src/jira_skill/analysis/signals.py:254-291` — `CapacitySignal` model (unaffected by this change).
