## Context

The per-epic tab currently shows iOS/Android/QA columns with plain text status+key. The `_link()` helper already generates clickable HYPERLINK formulas for Jira keys. The `COMPLETION_WEIGHTS` dict maps statuses to progress percentages (Done=100, Code Review=75, etc.).

## Goals / Non-Goals

**Goals:**
- Make all ticket cells clickable hyperlinks
- Add Progress column with weighted subtask completion
- Fallback to parent task status when no subtasks

**Non-Goals:**
- Change the underlying data model
- Modify other tabs (Executive Summary, Sprint Report, etc.)

## Decisions

### D1: Hyperlink format for platform columns

**Decision:** Use `=HYPERLINK(url, "STATUS (KEY)")` format.

**Implementation:**
```python
def _platform_cell(subtask, jira_url_fn):
    """Create hyperlink cell for a platform subtask."""
    if not subtask:
        return "—"
    url = jira_url_fn(subtask.key)
    display = f"{subtask.status} ({subtask.key})"
    return f'=HYPERLINK("{url}", "{display}")'
```

### D2: Progress computation

**Decision:** Weighted average of subtask statuses using `COMPLETION_WEIGHTS`. Fallback to parent status when no subtasks.

**Logic:**
```
if subtasks exist:
    progress = sum(weight(status) for subtasks) / len(subtasks)
else:
    progress = weight(parent_task.status)
```

### D3: Column placement

**Decision:** Progress column goes after QA (column O), before existing columns.

**Layout:**
```
A:Key | B:Type | C:Summary | D:Status | E:Assignee | F:Sprint | G:Story Points
H:Blocked By | I:Blocks | J:Chain Depth | K:Impact Radius
L:iOS | M:Android | N:QA | O:Progress
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| HYPERLINK formula may break if URL contains special chars | Use `jira_url()` which handles encoding |
| Progress shows 0% for tasks with all-ToDo subtasks | Correct behavior — reflects actual progress |
| Column width may be too narrow for hyperlinks | Auto-fit or use 25-char truncation |
