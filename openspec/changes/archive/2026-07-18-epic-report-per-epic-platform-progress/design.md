## Context

The per-epic tab in the Google Sheets report currently shows a flat list of child tasks with columns: Key, Type, Summary, Status, Assignee, Sprint, Story Points, Blocked By, Blocks, Chain Depth, Impact Radius.

For cross-platform epics (like RMD-4160 DLC Visibility), each story has iOS and Android subtasks. The current flat view doesn't show:
- Which platform each subtask belongs to
- Per-platform progress (iOS vs Android)
- QA status for tickets with QA subtasks

The collector already fetches child tasks (Phase 1) but subtasks are excluded when `include_subtasks=false` (current config). Subtasks need to be fetched separately for the per-epic tab.

## Goals / Non-Goals

**Goals:**
- Show iOS, Android, QA columns with subtask status + clickable key
- Compute per-platform weighted progress using existing status mapping
- Add summary section at top showing platform breakdown
- Maintain backward compatibility (existing columns preserved)

**Non-Goals:**
- Change the collector's subtask fetching behavior
- Modify the Blocking Bugs tab
- Change the Executive Summary or other tabs
- Add new Jira API endpoints

## Decisions

### D1: Subtask fetching approach

**Decision:** Fetch subtasks on-demand per parent task during per-epic tab rendering, not during collection.

**Rationale:** The collector already has `include_subtasks=false` config. Fetching subtasks during rendering keeps the collection phase unchanged and only adds API calls when the per-epic tab is actually generated.

**Implementation:**
```python
# In per-epic tab rendering, after getting filtered_epic_tasks:
for task in filtered_epic_tasks:
    if task.subtasks:  # Has subtask references
        subtasks = fetch_subtasks(task.subtasks)
        ios, android, qa = classify_subtasks(subtasks)
```

### D2: Platform detection from summary

**Decision:** Parse subtask summary for platform tags: `[IOS]`, `[Android]`, `[QA]`, `[TEST]`.

**Rationale:** The existing Jira convention uses these tags in subtask summaries. No need for custom fields or labels.

**Classification logic:**
```python
def classify_platform(summary: str) -> str:
    s = summary.upper()
    if '[IOS' in s:
        return 'ios'
    elif '[ANDROID' in s:
        return 'android'
    elif 'QA' in s or 'TEST' in s:
        return 'qa'
    return 'other'
```

### D3: Progress computation

**Decision:** Use the existing `COMPLETION_WEIGHTS` mapping (Done=100, Code Review=75, In Progress=70, etc.) for per-platform progress.

**Rationale:** Consistent with the epic-level completion calculation. No new mapping needed.

**Per-platform progress:**
```
iOS progress = sum(weight(subtask.status) for ios_subtasks) / len(ios_subtasks) * 100
```

### D4: Column layout

**Decision:** Add iOS, Android, QA columns after the existing Status column. Each cell shows `STATUS (KEY)` format.

**Layout:**
```
Key | Summary | Status | iOS | Android | QA | Assignee | Sprint | ...
```

**Cell format:** `CODE REVIEW (RMD-4555)` — status + clickable key in parentheses.

### D5: Summary section placement

**Decision:** Add summary rows at the top of the per-epic tab, between the metadata header and the task table.

**Layout:**
```
[Title]
[Status: X | Priority: Y]
[Completion: Z% | Tasks: N]
[Unassigned: U | Blocked: B]
[Sprint Alloc: S% | Stale: T]
[EMPTY ROW]
[Platform Summary]                    ← NEW
[iOS: X% | Android: Y% | QA: Z%]    ← NEW
[EMPTY ROW]
[Task Table Header]
[Task Rows...]
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Additional API calls (23 per epic) | Acceptable for single-epic reports; batch if needed later |
| Subtask summary parsing may miss platforms | Fallback to "—" for unclassified subtasks |
| Column width may be too narrow | Use 30-char truncation for status+key display |
| Existing layouts break | New columns appended, not inserted — backward compatible |
