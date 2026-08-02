# Tasks: Finalize TJ-1656 Trade Ticket Revamp Epic Planning

This document outlines the implementation tasks to complete epic planning for TJ-1656 Trade Ticket Revamp.

## Progress Summary (Updated: June 11, 2026)

**Completed:**
- ✅ Task 3.3: Reassigned TJ-1979 to Vũ Văn Tuân (load balancing)
- ✅ Task 7.1: Generated fresh epic report

**Remaining: Manual Steps Required**

---

## 1. Draft Story Breakdown

- [ ] 1.1 Review URS document (Functions 3-9) for TJ-1889 breakdown requirements
- [ ] 1.2 Review URS document (Function 9) for TJ-1890 breakdown requirements
- [ ] 1.3 Create iOS subtasks for UI Trade ticket revamp (TJ-1889 breakdown)
- [ ] 1.4 Create Android subtasks for UI Trade ticket revamp (TJ-1889 breakdown)
- [ ] 1.5 Create iOS subtasks for UI Order confirmation revamp (TJ-1890 breakdown)
- [ ] 1.6 Create Android subtasks for UI Order confirmation revamp (TJ-1890 breakdown)
- [ ] 1.7 Add acceptance criteria from URS to each subtask
- [ ] 1.8 Link subtasks to parent stories (TJ-1889, TJ-1890)
- [ ] 1.9 Transition TJ-1889 from Draft to SIT status
- [ ] 1.10 Transition TJ-1890 from Draft to SIT status

## 2. Story Point Estimation

> **NOTE:** TJ project does not have configurable story points field. Story points must be entered manually in Jira.

- [x] 2.1 Review existing task structure and dependencies
- [ ] 2.2 ~~Apply story points to existing tasks~~ - **Manual entry required**
- [ ] 2.3 ~~Apply story points to Counter Quotes subtasks~~ - **Manual entry required**
- [ ] 2.4 ~~Apply story points to Search Counter Screen subtasks~~ - **Manual entry required**
- [ ] 2.5 ~~Apply story points to Display Account Information subtasks~~ - **Manual entry required**
- [ ] 2.6 ~~Apply story points to Architecture Design subtasks~~ - **Manual entry required**
- [ ] 2.7 ~~Apply story points to Navigation subtasks~~ - **Manual entry required**
- [ ] 2.8 ~~Apply story points to Counter details Short direction subtasks~~ - **Manual entry required**
- [ ] 2.9 ~~Apply story points to Navigation Flow Handler (TJ-1979)~~ - **Manual entry required**
- [ ] 2.10 ~~Apply story points to newly created UI subtasks~~ - **Manual entry required**
- [ ] 2.11 Validate total story points with PL_Duong (Tech Lead)
- [ ] 2.12 Update all 23 tasks in Jira with approved story points

## 3. Resource Redistribution

- [x] 3.1 Review PL_Duong's current task load (8 tasks - reduced from 9)
- [x] 3.2 Identify tasks suitable for redistribution
- [x] 3.3 Reassign TJ-1979 (Navigation Flow Handler) from PL_Duong to Vũ Văn Tuân
- [ ] 3.4 Assign new UI subtasks to VietNguyen2 to balance workload
- [ ] 3.5 Update assignee fields in Jira for redistributed tasks
- [ ] 3.6 Verify workload is balanced (no assignee > 6 tasks)

## 4. Stale Task Resolution

- [ ] 4.1 Review TJ-1694 (196 days old) with product/tech lead
- [ ] 4.2 Determine if Counter details - show Short direction for SGX is still required
- [ ] 4.3 If valid: Update task with current requirements, assign fresh
- [ ] 4.4 If outdated: Close task with reason "Feature no longer required"
- [ ] 4.5 If redundant: Merge with other Counter details task
- [ ] 4.6 Review TJ-1888, TJ-1889, TJ-1890 (89 days old) for currency
- [ ] 4.7 Update or close stale tasks as appropriate

## 5. Sprint Allocation

- [x] 5.1 Sprint 16 (08 Jun - 19 Jun) already assigned to 21 tasks
- [ ] 5.2 Assign Sprint 17 to newly created subtasks
- [ ] 5.3 Update sprint field in Jira for all affected tasks
- [x] 5.4 Verify 100% sprint allocation in epic report (91% - 2 Done tasks without sprint)

## 6. Epic Status Update

- [ ] 6.1 Verify no Draft stories remain in epic (2 Draft still present)
- [ ] 6.2 Confirm all tasks have story points assigned
- [x] 6.3 Verify sprint assignments are complete (91%)
- [x] 6.4 Epic status is already "In Progress"
- [ ] 6.5 Add epic planning completion comment documenting final structure

## 7. Documentation & Verification

- [x] 7.1 Generate fresh epic report to verify planning completeness
- [ ] 7.2 Document final task assignments and story points in epic description
- [ ] 7.3 Create summary for sprint planning meeting
- [ ] 7.4 Archive OpenSpec change after verification

---

## Story Points Recommendations

> **MANUAL ENTRY REQUIRED** - Enter these values manually in Jira for each task

| Task | Summary | Recommended SP | Current Owner |
|------|---------|----------------|---------------|
| TJ-1924 | [Planning] Trade Ticket Revamp | 3 | Venkattesan DU |
| TJ-1918 | [Analyze] Trade Ticket Revamp | 3 | Dao Mai Binh Thuy |
| TJ-1981 | Search Counter Screen (parent) | 3 | PL_Duong(Kelvin) |
| TJ-1980 | Counter Quotes (parent) | 5 | PL_Duong(Kelvin) |
| TJ-1979 | Navigation Flow Handler | 5 | Vũ Văn Tuân ✓ |
| TJ-1978 | Display Account Information (parent) | 3 | PL_Duong(Kelvin) |
| TJ-1977 | Architecture Design (parent) | 3 | PL_Duong(Kelvin) |
| TJ-1888 | Navigation to Trade ticket (parent) | 3 | PL_Duong(Kelvin) |
| TJ-1694 | Counter details Short direction (parent) | 3 | PL_Duong(Kelvin) |
| TJ-1889 | UI Trade ticket revamp | 8 | PL_Duong(Kelvin) |
| TJ-1890 | UI Order confirmation revamp | 5 | PL_Duong(Kelvin) |
| TJ-2033 | [iOS] Counter Quotes | 5 | VietNguyen2 |
| TJ-2034 | [Android] Counter Quotes | 5 | Vũ Văn Tuân |
| TJ-2022 | [iOS] Search Counter Screen | 5 | Dev Anh Pham (Henson) |
| TJ-2021 | [Android] Search Counter Screen | 5 | Vũ Văn Tuân |
| TJ-2031 | [iOS] Display Account Information | 3 | Dev Anh Pham (Henson) |
| TJ-2032 | [Android] Display Account Information | 3 | Vũ Văn Tuân |
| TJ-2027 | [iOS] Architecture Design | 3 | Dev Anh Pham (Henson) |
| TJ-2028 | [Android] Architecture Design | 3 | Vũ Văn Tuân |
| TJ-2020 | [iOS] Navigation to Trade ticket | 3 | Dev Anh Pham (Henson) |
| TJ-2019 | [Android] Navigation to Trade ticket | 3 | Vũ Văn Tuân |
| TJ-2029 | [iOS] Counter details Short direction | 2 | Dev Anh Pham (Henson) |
| TJ-2030 | [Android] Counter details Short direction | 2 | Vũ Văn Tuân |

**Total Recommended SP: 82**

---

## New Subtasks to Create

**From TJ-1889 (UI Trade ticket revamp - Functions 3-8):**

iOS:
- [ ] TJ-XXXX: [iOS] UI Trade ticket - Function 3 (Buy/Sell tabs)
- [ ] TJ-XXXX: [iOS] UI Trade ticket - Function 4 (Order type selection)
- [ ] TJ-XXXX: [iOS] UI Trade ticket - Function 5 (Price entry)
- [ ] TJ-XXXX: [iOS] UI Trade ticket - Function 6 (Quantity entry)
- [ ] TJ-XXXX: [iOS] UI Trade ticket - Function 7 (Order review)
- [ ] TJ-XXXX: [iOS] UI Trade ticket - Function 8 (Confirmation)

Android:
- [ ] TJ-XXXX: [Android] UI Trade ticket - Function 3 (Buy/Sell tabs)
- [ ] TJ-XXXX: [Android] UI Trade ticket - Function 4 (Order type selection)
- [ ] TJ-XXXX: [Android] UI Trade ticket - Function 5 (Price entry)
- [ ] TJ-XXXX: [Android] UI Trade ticket - Function 6 (Quantity entry)
- [ ] TJ-XXXX: [Android] UI Trade ticket - Function 7 (Order review)
- [ ] TJ-XXXX: [Android] UI Trade ticket - Function 8 (Confirmation)

**From TJ-1890 (UI Order confirmation revamp - Function 9):**

- [ ] TJ-XXXX: [iOS] UI Order confirmation - Function 9
- [ ] TJ-XXXX: [Android] UI Order confirmation - Function 9

---

## Team Account IDs (for Jira operations)

| Team Member | Account ID |
|------------|------------|
| PL_Duong (Kelvin) | 60b59dc2a547eb0068213613 |
| Vũ Văn Tuân | 712020:c2d112a5-7ac6-4437-9387-4ec6cda915c2 |
| Dev Anh Pham (Henson) | (needs lookup) |
| VietNguyen2 | (needs lookup) |
| Venkattesan DU | 616e849abcb5740068036ff2 |
| Dao Mai Binh Thuy | 712020:8cee580c-91a7-4d08-81e9-7a85f1cbef88 |

---

## Verification Commands

```bash
# Generate epic report to verify completion
cd /Users/lekhanhvinh/Developer/tdt/jira-epic-report
uv run epic-report generate TJ-1656 --output /tmp/verify-TJ-1656.md

# Check task assignments
cd /Users/lekhanhvinh/Developer/tdt/tdt-core
uv run python - <<'PY'
from tdt_core.clients.jira import JiraClientFactory
jira = JiraClientFactory.from_env()
result = jira.jql('"Epic Link" = "TJ-1656"', limit=50)
issues = result if isinstance(result, list) else result.get('issues', [])
for issue in issues:
    if isinstance(issue, str):
        continue
    fields = issue.get('fields', {})
    key = issue.get('key', 'N/A')
    assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'
    status = fields.get('status', {}).get('name', 'N/A')
    print(f"{key}: {status} - {assignee}")
PY
```
