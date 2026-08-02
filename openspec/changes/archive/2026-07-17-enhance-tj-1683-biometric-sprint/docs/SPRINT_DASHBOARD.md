# TJ-1683 Sprint Tracking Dashboard

**Epic:** Allow biometric verification in trade submission  
**Generated:** 2026-06-11  
**Last Updated:** 2026-06-11 14:45

## Current Status

| Metric | Value | Trend |
|--------|-------|-------|
| Total Tasks | 207 | - |
| Completion % | 21% | ⚠️ Slow |
| In Progress | 9 | 🔄 |
| SIT Testing | 3 | ✅ |
| To Do | 165 | 🚨 |
| Draft | 24 | 🚨 |
| Unassigned | 152 | 🚨 Critical |

## Sprint Velocity

| Day | Tasks Done | Cumulative | On Track? |
|-----|-----------|------------|-----------|
| Target | ~30/day | 207 | - |

**Required Velocity:** ~30 tasks/day to complete by sprint end

## Risk Dashboard

| Risk | Severity | Tasks Affected | Status |
|------|----------|---------------|--------|
| Unassigned tasks | HIGH | 152 | 🚨 |
| Draft tasks (planning incomplete) | HIGH | 24 | 🚨 |
| Requirements blocker TJ-1613 | MEDIUM | Multiple | 🔄 |
| Requirements blocker TJ-1916 | MEDIUM | Multiple | 🔄 |
| Single developer bottleneck (Kelvin) | MEDIUM | 32 | ⚠️ |

## Workstream Status

| Platform | Assigned | In Progress | Done | Total |
|----------|----------|-------------|------|-------|
| iOS | ~0 | 4 | 0 | ~50 |
| Android | ~4 | 4 | 0 | ~50 |
| Backend | ~32 | 5 | 2 | ~107 |

## Blockers Requiring PM Action

### 1. TJ-1613 - Requirements Clarification (HIGH PRIORITY)
**Issue:** Trade validate logic - biometric vs password authentication
**Current Logic:** Biometric login = view-only. To trade, user must enter password.
**Question:** Is this the intended behavior for biometric verification?
**Action:** Get PO confirmation on authentication flow

### 2. TJ-1916 - Requirements Clarification
**Issue:** Needs requirements clarification
**Action:** Review and clarify with stakeholders

### 3. 24 Draft Tasks
**Impact:** Cannot begin development on affected stories
**Action:** Complete story breakdown with PM

## Recommended Actions

### Immediate (Today)
1. Assign all 152 unassigned tasks to team members
2. Schedule meeting with PO for TJ-1613 clarification
3. Review Draft tasks with PM

### This Week
1. Resolve TJ-1613 and TJ-1916 blockers
2. Finalize 24 Draft tasks
3. Move all development tasks to SIT

### Metrics to Track
- Daily: Tasks assigned, tasks completed
- Weekly: Velocity (tasks/day), blocker count
- Sprint end: SIT completion rate

---

**Report Command:** `cd ~/Developer/tdt/jira-epic-report && uv run epic-report generate TJ-1683`
