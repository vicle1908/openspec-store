# kbs-resolve-sprint-scope-signature-fix — Design

## Context

The sprint ecosystem pipeline has two layers:

1. **kbs sync** (`jira-kanban-from-spreadsheet`): Reads spreadsheet scope, builds JQL, resolves/creates filter + board, optionally creates scrum sprint, optionally refreshes reports
2. **jdr sprint-sheet** (`jira-daily-reports`): Reads spreadsheet bucket tabs, builds sprint report + person capacity, writes to Google Sheets

The two layers communicate across a subprocess boundary via environment variables (`RESOLVED_FILTER_ID`, `RESOLVED_BOARD_ID`, `RESOLVED_SPRINT_ID`, `RESOLVED_PROJECT_KEY`, `RESOLVED_SCOPE_KEYS`). When kbs completes successfully, jdr reads these env vars to render accurate links in the report header.

## Root Cause

On 2026-06-11, `tdt-core` refactored `resolve_sprint_scope()`:

```diff
-    filter_id_override: int | None = None,
-    board_id_override: int | None = None,
+    # (removed)

-    filter_id = filter_id_override or _find_filter_id(jira, filter_name)
+    filter_id = _find_filter_id(jira, filter_name)
```

The `filter_id_override`/`board_id_override` params were replaced by a post-call fallback in kbs CLI:

```python
resolved_filter_id = scope.filter_id or cfg.filter_id   # line 423
resolved_board_id = scope.board_id or cfg.board_id     # line 424
```

This fallback is correct — it handles pre-seeded ids from `~/.tdt/.env` or CLI flags without needing them as function kwargs. However, the kbs CLI call site was never updated.

## Decision 1: Fix the call sites, not the callee

The post-call fallback pattern is semantically equivalent to the override-params pattern and is simpler. Rather than re-adding the removed params to `resolve_sprint_scope`, we fix the call sites to match the new signature.

**Two call sites are affected:**

1. **`sync` command** (`cli.py:409-410`): Used when bootstrapping a new sprint. Calls with `filter_id_override=cfg.filter_id or None` and `board_id_override=cfg.board_id or None`.

2. **`verify` command** (`cli.py:797-798`): Used for dry-run alignment checks. Calls with `filter_id_override=resolved_filter_id` and `board_id_override=resolved_board_id` (where resolved ids come from CLI flags or config).

## Decision 2: Board-id guard in jdr fallback

In `SprintReportSheetReport._resolve_scope_from_spreadsheet`, the filter assignment is gated:

```python
if filters and not self.has_resolved_scope:
    self.filter_id = str(...)
```

But the board assignment is **unconditional**:

```python
if boards:
    self.board_id = str(...)
```

This means even when `RESOLVED_BOARD_ID` was set by kbs, the spreadsheet fallback can overwrite it with the wrong board. Add the same guard:

```python
if boards and not self.has_resolved_scope:
    self.board_id = str(...)
```

## Changes

### 1. kbs CLI: Remove stale kwargs from both `resolve_sprint_scope` call sites

**File:** `jira-kanban-from-spreadsheet/src/kbs/cli.py`

#### Call site A — `sync` command (~line 403)

```python
# BEFORE (crashes):
scope = resolve_sprint_scope(
    jira,
    spreadsheet_id=cfg.spreadsheet_id,
    title=metadata.title,
    jql=jql,
    dry_run=cfg.dry_run,
    filter_id_override=cfg.filter_id or None,      # ← unknown kwarg
    board_id_override=cfg.board_id or None,        # ← unknown kwarg
    sprint_number_override=metadata.sprint_number,
    create_board=cfg.board_mode != "sprint",
)

# AFTER (correct):
scope = resolve_sprint_scope(
    jira,
    spreadsheet_id=cfg.spreadsheet_id,
    title=metadata.title,
    jql=jql,
    dry_run=cfg.dry_run,
    sprint_number_override=metadata.sprint_number,
    create_board=cfg.board_mode != "sprint",
)
# Post-call fallback handles pre-seeded cfg.filter_id / cfg.board_id:
resolved_filter_id = scope.filter_id or cfg.filter_id
resolved_board_id = scope.board_id or cfg.board_id
```

#### Call site B — `verify` command (~line 791)

```python
# BEFORE (crashes):
scope = resolve_sprint_scope(
    jira,
    spreadsheet_id=cfg.spreadsheet_id,
    title=metadata.title,
    jql=jql,
    dry_run=True,
    filter_id_override=resolved_filter_id,         # ← unknown kwarg
    board_id_override=resolved_board_id,           # ← unknown kwarg
    sprint_number_override=metadata.sprint_number,
)

# AFTER (correct):
scope = resolve_sprint_scope(
    jira,
    spreadsheet_id=cfg.spreadsheet_id,
    title=metadata.title,
    jql=jql,
    dry_run=True,
    sprint_number_override=metadata.sprint_number,
)
resolved_filter_id = scope.filter_id or resolved_filter_id
resolved_board_id = scope.board_id or resolved_board_id
```

In both call sites, the post-call fallback lines are **already present** and correct — they just never execute because the function call crashes first.

#### Deployment note

The `ai-review` deployment ships its own copy of kbs at
`deployments/ai-review/deps/jira-kanban-from-spreadsheet/src/kbs/cli.py`
(lines 409-410 and 797-798). Apply the same two-kwargs removal there.

### 2. jdr: Guard board fallback with `has_resolved_scope`

**File:** `jira-daily-reports/src/jira_daily_reports/reports/sprint_report_sheet.py`, `_resolve_scope_from_spreadsheet` method

```python
# BEFORE:
if boards:
    self.board_id = str(as_dict(boards[0]).get("id") or self.board_id)

# AFTER:
if boards and not self.has_resolved_scope:
    self.board_id = str(as_dict(boards[0]).get("id") or self.board_id)
```

This matches the filter assignment pattern immediately above it and prevents kbs-resolved board ids from being overwritten.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Post-call fallback doesn't handle edge case | Low | Medium | The fallback logic was always present in both call sites; only the crash blocked it |
| Other call sites of `resolve_sprint_scope` use old signature | Low | Low | Only kbs CLI calls `resolve_sprint_scope`; `sprint_sync.py` imports only date-parse helpers; jdr/cli.py uses correct signature; tdt-core tests use correct signature |
| `ai-review` deployment copy not updated | High | High | Shipped copy at `deployments/ai-review/deps/jira-kanban-from-spreadsheet/` must be updated alongside source repo |
| Board guard breaks existing standalone behavior | Low | Low | Standalone runs have `has_resolved_scope=False`, so guard is a no-op |

## Testing Strategy

1. **Unit test (kbs):** Call `resolve_sprint_scope` with current signature (no override kwargs) and verify it returns a valid `SprintScope` without crashing
2. **Integration test (kbs):** Run `kbs sync --dry-run` and `kbs verify --spreadsheet <id>` against Sprint 17 spreadsheet and verify both complete without `TypeError`; assert the Sprint 17 filter is not the old "17-Aug-2024-LiveDeployment" (id 10394)
3. **Unit test (jdr):** When `RESOLVED_BOARD_ID=1066` env is set, assert `board_id` is `"1066"` after `_resolve_scope_from_spreadsheet` even if Jira search finds a different board
4. **Manual validation:** Run `kbs sync --refresh-reports --live` for Sprint 17 and verify report header shows Sprint 17 filter, Sprint 17 board, and dashboard links

## Rollback Plan

Revert the two-line removal of kwargs in `kbs/cli.py` restores the pre-fix state (crash). The jdr board-guard change is additive and has no rollback risk beyond removing one condition.
