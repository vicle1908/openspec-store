## Why

The current per-epic tab in the Google Sheets report shows a flat list of child tasks without platform (iOS/Android/QA) breakdown. For cross-platform epics like RMD-4160 (DLC Visibility), each story has iOS and Android subtasks, but the report doesn't show which platform each subtask belongs to or its progress. This makes it impossible to answer "how is iOS doing vs Android?" without manually checking each subtask in Jira.

## What Changes

- **Add platform columns** (iOS, Android, QA) to the per-epic tab showing subtask status + key for each parent task
- **Compute per-platform progress** using the existing weighted status mapping (Done=100, Code Review=75, In Progress=70, etc.)
- **Add summary section** at the top of the per-epic tab showing iOS/Android/QA progress breakdown
- **QA column** included only for tickets that have QA subtasks

### Data Flow

```
Jira API → Collector (Phase 1: child_tasks) → Reporter (per-epic tab)
                         ↓
              Fetch subtasks for each parent task
                         ↓
              Parse summary to detect platform ([IOS], [Android], [QA])
                         ↓
              Populate iOS, Android, QA columns
                         ↓
              Compute per-platform weighted progress
                         ↓
              Add summary rows at top of tab
```

### Before/After

**Before:**
```
Key      | Type  | Summary           | Status    | Assignee | ...
RMD-4161 | Story | Global Search     | In Progress | Dev_VuVuong | ...
```

**After:**
```
iOS Progress: 44%  |  Android Progress: 69%  |  Overall: 56%

Key      | Summary           | Status    | iOS           | Android       | QA
RMD-4161 | Global Search     | In Progress | CODE REVIEW (RMD-4555) | CODE REVIEW (RMD-4556) | —
RMD-4456 | DLCs Column Set   | In Progress | To do (RMD-4576) | CODE REVIEW (RMD-4575) | —
```

## Capabilities

### Modified Capabilities

- `spreadsheet-export-enhancement`: Per-epic tab now includes platform columns (iOS, Android, QA) with subtask status+key, and platform progress summary at top. Existing tab structure extended, not broken.

### New Capabilities

None — this is an enhancement to existing spreadsheet output.

## Impact

- **Code:** `epic_report/reporters/spreadsheet_reporter.py` — per-epic tab rendering logic
- **Data:** Requires fetching subtasks for each parent task (additional Jira API calls during report generation)
- **Performance:** ~23 additional API calls per epic (one per parent task with subtasks). Acceptable for single-epic reports.
- **Backward compatibility:** Existing column structure extended (new columns added, not replaced). Old spreadsheet layouts remain compatible.
