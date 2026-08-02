# Sprint Sheet P1 Scope Filter — Design

## Problem

The sprint report (`sprint-sheet`) extracts all tickets from the sprint workbook's bucket tabs. There is currently no way to restrict the report to Priority 1 (Highest) tickets only. The report processes every ticket in scope, using priority only for a summary counter, not as a filter.

## Decision

Filter at the **sheet-reading layer**, not the JQL layer. This ensures:
- Jira is never queried for tickets outside scope (cost, latency)
- No changes needed to JQL construction (`sprint_report_sheet.py`)
- The scope object (`SprintTicketScope`) carries the authoritative filtered set from the start

## Changes

### 1. `delivery/tdt_sheet.py`

**New module-level constants:**
```python
_PRIORITY_1_ONLY_ENABLED = os.getenv("PRIORITY_1_ONLY", "").strip().lower() in {"1", "true"}
_P1_PRIORITY_VALUES: frozenset[str] = frozenset({"1", "highest"})
```

**`HEADER_VARIANTS` update** (in `sprint_report_sheet.py`):
```python
"Priority": ["Priority", "PRIORITY"],
```
`_find_col(headers, "Priority")` is already used in `tdt_sheet.py` via the shared import — no additional import needed.

**`read_sprint_ticket_scope()` changes:**

| Location | Change |
|----------|--------|
| Standard bucket tab loop | Find `priority_col` via `_find_col(headers, "Priority")`. When `_PRIORITY_1_ONLY_ENABLED` and `priority_col` is not `None`: read `row[priority_col]`, strip, lower-case, check membership in `_P1_PRIORITY_VALUES`. Skip (count as skipped) if not a match. |
| Headerless tab | When filter is enabled, emit `p1_filter_skip_headerless_tab` WARNING; include keys as-is (cannot filter without header row). |
| Extra tabs (`SHEET_LINKS`) | Change range from `A1:B500` to `A1:Z500` to capture Priority column. Apply same Priority=1 filter logic. For headerless extra tabs, emit `p1_filter_skip_headerless_extra_tab` WARNING. |
| Return value | Attach `warnings: list[str]` to `SprintTicketScope` when filter is active. |
| Logger output | Add `priority_filter` and `skipped` fields to `bucket_scope_read_done` log line. |

**`write_sheet()` changes:**

After `read_sprint_ticket_scope()`, attach `scope.warnings` to the report object:
```python
report.scope_warnings = scope.warnings
```

### 2. `reports/sprint_report_sheet.py`

Add `"Priority"` to `HEADER_VARIANTS` so `_find_col` can locate it in any tab.

### 3. `cli.py`

After the successful sheet write, iterate `report.scope_warnings` and print each in yellow:
```python
for warning in getattr(report, "scope_warnings", []):
    console.print(f"[yellow]   {warning}[/yellow]")
    logger.info("cli_scope_warning %s", warning)
```

### 4. `SprintTicketScope` dataclass

The `warnings: list[str]` field (already defined in the dataclass) is populated with the P1 skip message.

## Priority Value Matching

The Jira `priority.name` field uses `"Highest"` for P1. The sheet's `Priority` column may contain either `1`, `Highest`, or other variants. Matching is done case-insensitively against the frozenset `{"1", "highest"}`. Empty cells when the filter is active are excluded (treated as unknown priority, not P1).

## Rollout

The feature is **opt-in** via `PRIORITY_1_ONLY=1`. Default behavior is unchanged. Operators can test without affecting other users.
