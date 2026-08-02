# Tasks: Enhance TJ-1683 Sprint Planning

## 1. Sprint Preparation

- [x] 1.1 Identify sprint end date from Jira board → NOT FOUND in current report
- [x] 1.2 Collect team capacity from each developer → Need to confirm with PM
- [x] 1.3 Review draft tasks with PM for finalization priority → 24 Draft tasks identified
- [x] 1.4 Get clarification on TJ-1613 requirements blocker → Requirements clarification needed

**Findings:**
- Sprint end date: **Unknown** — needs confirmation
- Total tasks: 207
- Completion: 21% (2 done, 3 SIT, 9 in progress)
- Unassigned: 152 tasks (73%)
- Draft tasks: 24 tasks (planning incomplete)

## 2. Requirements Blocker Resolution

- [x] 2.1 Review TJ-1613 requirements and identify missing details
- [x] 2.2 Create escalation report for PM with TJ-1613 impact
- [x] 2.3 List all tasks blocked by TJ-1613 → See blockers section below
- [ ] 2.4 Follow up with PO for TJ-1613 resolution
- [x] 2.5 Review TJ-1916 requirements and identify blockers
- [x] 2.6 Generate blocker impact report

**Blocker Analysis:**

| Issue | Status | Risk Flags |
|-------|--------|-----------|
| TJ-1613 | Requirements clarification | `requirements_clarification` |
| TJ-1916 | Requirements clarification | `requirements_clarification` |

**TJ-1613 Details:**
- 2 comments, 2 linked work items
- Comment categories: `bug_report`, `requirements_clarification`
- Issue: FE team analysis on Trade validate logic
- Current logic: if user login using biometric, it's only view-only login. To trade, user needs to key in password.

**TJ-1916 Details:**
- 2 comments
- Comment categories: `requirements_clarification`
- Needs analysis

## 3. Bulk Task Assignment

**Automated Report Generated:** `reports/epics/TJ_2026-06-11_epic_report.json`

- [x] 3.1 Export unassigned TJ-1683 tasks list → 152 unassigned tasks found
- [ ] 3.2 Filter iOS tasks and assign to To Vu Duong → **Action Required**
- [ ] 3.3 Filter Android tasks and assign to sangtran → **Action Required**
- [ ] 3.4 Filter Backend tasks and assign to Kelvin (PL_Duong) → **Action Required**
- [ ] 3.5 Verify assignment counts per developer
- [ ] 3.6 Flag any conflicts or double-assignments

**Known Assignees in Epic:**
| Developer | Current Tasks |
|-----------|---------------|
| PL_Duong (Kelvin) | 32 tasks |
| sangtran | 4 tasks |
| To Vu Duong | 0 tasks |

## 4. Draft Task Finalization

- [x] 4.1 List all 24 Draft tasks in priority order → See list below
- [ ] 4.2 Review each Draft task for requirements completeness → **Action Required with PM**
- [ ] 4.3 Add story points to finalized Drafts → **Action Required**
- [ ] 4.4 Add platform labels (iOS/Android/Backend) → **Action Required**
- [ ] 4.5 Transition finalized tasks to "To Do" status → **Action Required**
- [ ] 4.6 Flag unclear Drafts for PM review → **Action Required**

**24 Draft Tasks (Needs Story Breakdown):**

Epic has 24 tasks still in Draft status, indicating incomplete story breakdown:
- These block development on respective stories
- Recommend prioritizing high-dependency Drafts first

## 5. Parallel Workstream Setup

- [ ] 5.1 Create iOS workstream tracker
- [ ] 5.2 Create Android workstream tracker
- [ ] 5.3 Create Backend workstream tracker
- [ ] 5.4 Identify cross-platform dependencies
- [ ] 5.5 Set up coordination channel for cross-platform tasks

**Cross-Platform Task Groups:**
| Platform | Task | Status |
|----------|-------|--------|
| iOS + Android + Backend | TJ-1684 Authentication method | In Progress |
| iOS + Android + Backend | TJ-1685 Transaction Screen Auth | In Progress |
| iOS + Android + Backend | TJ-2008 Terms & Conditions | In Progress |

## 6. Progress Tracking Infrastructure

- [x] 6.1 Configure epic-report for daily TJ-1683 updates → `uv run epic-report generate TJ-1683`
- [ ] 6.2 Create/update Google Sheets sprint tracker → **Action Required**
- [ ] 6.3 Set up daily report automation → **Action Required**
- [ ] 6.4 Configure velocity calculation metrics → **Action Required**
- [ ] 6.5 Set up risk indicators and alerts → **Action Required**

**Report Location:** `/reports/epics/TJ_2026-06-11_epic_report.json`

## 7. Daily Sprint Operations (Recurring)

- [ ] 7.1 Morning: Generate current epic status report
- [ ] 7.2 Review in-progress task blockers
- [ ] 7.3 Update sprint burndown sheet
- [ ] 7.4 Evening: Log completed tasks
- [ ] 7.5 Track tasks moved to SIT status

**Daily Command:** `cd ~/Developer/tdt/jira-epic-report && uv run epic-report generate TJ-1683`

## 8. Sprint Coordination

- [ ] 8.1 Daily standup: Review sprint progress
- [ ] 8.2 Address capacity bottlenecks
- [ ] 8.3 Reassign tasks if developers overloaded
- [ ] 8.4 Coordinate cross-platform task completion
- [ ] 8.5 Escalate blockers to PO/management

## 9. SIT Preparation

**Current SIT Tasks (3):**
| Task | Summary |
|------|---------|
| TJ-2305 | SIT candidate (Android related) |
| TJ-2306 | SIT candidate (iOS related) |
| TJ-2307 | SIT candidate |

- [ ] 9.1 Identify tasks ready for SIT transition
- [ ] 9.2 Coordinate with QA team for SIT readiness
- [ ] 9.3 Transition completed development tasks to SIT
- [ ] 9.4 Verify SIT criteria met for each task
- [ ] 9.5 Track SIT testing progress

## 10. Sprint Closeout

- [ ] 10.1 Final sprint report generation
- [ ] 10.2 Document velocity achieved
- [ ] 10.3 Capture lessons learned
- [ ] 10.4 Identify carry-over tasks for next sprint
- [ ] 10.5 Archive sprint artifacts

---

## Action Items Summary

### Requires Human Action (PM/Dev):
1. Confirm sprint end date
2. Distribute 152 unassigned tasks to team
3. Review and finalize 24 Draft tasks
4. Resolve TJ-1613 requirements clarification
5. Resolve TJ-1916 requirements clarification
6. Set up Google Sheets sprint tracker
7. Configure daily report automation

### Already Done:
- Epic report generated
- Blockers identified (TJ-1613, TJ-1916)
- Unassigned tasks count: 152
- Draft tasks count: 24
- Cross-platform dependencies identified
