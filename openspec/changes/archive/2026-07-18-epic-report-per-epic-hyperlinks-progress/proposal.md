## Why

The per-epic tab now shows iOS/Android/QA platform columns, but they display plain text (`CODE REVIEW (RMD-4555)`) instead of clickable hyperlinks. Users cannot click through to subtasks in Jira. Additionally, there's no progress percentage per ticket — users must mentally calculate progress from the iOS/Android status columns.

## What Changes

- **Standardize hyperlinks** in iOS/Android/QA columns — each cell becomes a clickable Jira link with `STATUS (KEY)` display text
- **Add Progress column** showing weighted subtask completion percentage per parent ticket
- **Fallback logic** — when no subtasks exist, progress falls back to the parent task's weighted status

### Before/After

**Before:**
```
Key      | Status    | iOS                | Android           | ...
RMD-4161 | In Prog   | CODE REVIEW (4555) | In Progress (4574)| ...
```

**After:**
```
Key      | Status    | iOS                      | Android                 | Progress | ...
RMD-4161 | In Prog   | =LINK(CODE REV,4555)     | =LINK(In Prog,4574)    | 73%      | ...
```

## Capabilities

### Modified Capabilities

- `per-epic-platform-progress`: iOS/Android/QA columns now use hyperlinks; new Progress column added after QA column; progress uses weighted subtask completion with parent fallback.

## Impact

- **Code:** `epic_report/reporters/spreadsheet_reporter.py` — platform column rendering, progress computation
- **No new dependencies** — uses existing `_link()` helper and `COMPLETION_WEIGHTS`
- **Backward compatible** — new column appended, existing columns unchanged
