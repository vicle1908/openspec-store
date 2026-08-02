# TJ-1683 Draft Task Finalization Workflow

**Date:** 2026-06-11  
**Status:** BLOCKED - Draft status requires completion before transition

## Discovery

**24 Draft tasks** found in TJ-1683 epic with **NO available transitions**.

This means the workflow requires Draft tasks to be **completed** before they can move forward.

## Required Actions to Exit Draft

### 1. Story Points
Each Draft task needs story point estimation added.

### 2. Platform Labels
- `ios` - iOS platform tasks
- `android` - Android platform tasks
- `backend` - Backend platform tasks

### 3. Requirements Check
- Clear acceptance criteria
- No "TBD" in description
- All subtasks created

## Draft Task List

| Task | Summary | Current Assignee |
|------|---------|-----------------|
| TJ-2007 | TBD | PL_Duong(Kelvin) |
| TJ-2006 | TBD | PL_Duong(Kelvin) |
| TJ-2005 | TBD | PL_Duong(Kelvin) |
| TJ-2004 | TBD | PL_Duong(Kelvin) |
| TJ-2003 | TBD | PL_Duong(Kelvin) |
| TJ-2002 | TBD | PL_Duong(Kelvin) |
| TJ-2001 | TBD | PL_Duong(Kelvin) |
| TJ-2000 | TBD | PL_Duong(Kelvin) |
| TJ-1999 | TBD | PL_Duong(Kelvin) |
| TJ-1998 | TBD | PL_Duong(Kelvin) |
| ... | (14 more) | ... |

## Workflow Path

```
Draft → To Do → In Progress
   ↑         ↓
   └─────────┘ (via PM/Lead)
```

## Recommended Actions

1. **PM:** Review all 24 Draft tasks and finalize requirements
2. **Dev Lead:** Add story points and platform labels to each task
3. **Once Draft is complete:** Tasks auto-move to "To Do"
4. **Then:** Transition to "In Progress"

## Alternative: Bulk Operations

If the Draft tasks need story points/labels added, we can do this via:
```python
# Bulk update story points and labels via REST API
jira.put(f"rest/api/3/issue/{key}", data={...})
```

## Current Blockers

| Blocker | Severity | Resolution |
|---------|----------|------------|
| Draft tasks cannot transition | HIGH | PM needs to finalize requirements |
| TJ-1613 requirements unclear | MEDIUM | PO clarification needed |
| TJ-1916 requirements unclear | MEDIUM | PO clarification needed |
