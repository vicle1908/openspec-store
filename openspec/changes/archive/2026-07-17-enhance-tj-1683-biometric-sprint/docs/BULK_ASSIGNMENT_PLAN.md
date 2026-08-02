# TJ-1683 Bulk Assignment Plan

**Generated:** 2026-06-11  
**Total Unassigned Tasks:** 154

## Assignment Distribution (Recommended)

Based on platform labels and task types:

| Developer | Target Tasks | Platform | Current Load |
|-----------|-------------|----------|--------------|
| To Vu Duong | ~50-60 | iOS | 0 |
| sangtran | ~50-60 | Android | 4 |
| PL_Duong (Kelvin) | ~40-50 | Backend | 32 |

## Assignment Command Template

For bulk assignment in Jira, use:

```
# Example: Assign iOS tasks to To Vu Duong
# Filter: project = TJ AND issuetype in (Story, Subtask) AND "Epic Link" = TJ-1683 AND labels = iOS AND assignee is EMPTY
```

## Task Lists by Platform

### iOS Tasks (Need Labels)
Tasks that likely need iOS platform assignment:
- TJ-2279 to TJ-2303 (iOS authentication-related)

### Android Tasks
Tasks currently assigned to sangtran:
- TJ-2280, TJ-2286, TJ-2304

### Backend Tasks
Tasks currently assigned to PL_Duong:
- TJ-1684, TJ-1685, TJ-2008

## Execution Steps

### Step 1: Label Platform (if not already labeled)
Add labels: `ios`, `android`, `backend` to tasks

### Step 2: Bulk Assign by Label

**iOS:**
```
project = TJ AND "Epic Link" = TJ-1683 AND labels = ios AND assignee is EMPTY
→ Assign to: To Vu Duong
```

**Android:**
```
project = TJ AND "Epic Link" = TJ-1683 AND labels = android AND assignee is EMPTY
→ Assign to: sangtran
```

**Backend:**
```
project = TJ AND "Epic Link" = TJ-1683 AND labels = backend AND assignee is EMPTY
→ Assign to: PL_Duong
```

### Step 3: Verify Assignments
```bash
cd ~/Developer/tdt/jira-epic-report && uv run epic-report generate TJ-1683
```

## Conflict Resolution

If a task appears on multiple platform lists:
- Default to the platform with fewer total tasks
- Escalate complex cases to PM

## Notes

- 24 Draft tasks should be finalized BEFORE bulk assignment
- Some tasks may not have platform labels yet
- Consider story points when distributing workload
