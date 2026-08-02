# Proposal: Finalize Trade Ticket Revamp Epic Planning

## Why

The TJ-1656 Trade Ticket Revamp epic is blocked at 9% completion due to 2 Draft stories (TJ-1889, TJ-1890) that lack proper breakdown and estimation. Resource overload on PL_Duong (9 tasks) and missing story points (0/23) prevent accurate sprint planning. This change will complete the epic planning to enable development to proceed.

## What Changes

- **Finalize Draft Stories**: Break down TJ-1889 (UI Trade ticket revamp) and TJ-1890 (UI Order confirmation revamp) into subtasks with proper acceptance criteria
- **Assign Story Points**: Add estimation to all 23 tasks using planning poker
- **Redistribute Workload**: Reassign tasks from overloaded PL_Duong to available team members
- **Clear Stale Tasks**: Resolve or close 4 tasks older than 30 days (TJ-1694 at 196 days is most critical)
- **Update Epic Status**: Move epic to proper In Progress state with complete planning

## Capabilities

### New Capabilities

- `jira-epic-finalization`: Process to complete epic planning, including story breakdown, estimation, and resource balancing for mobile app development epics

### Modified Capabilities

- `tj-1656-trade-ticket-revamp`: Epic currently in Draft/In Progress state with 91% sprint allocation but 0% story point coverage

## Impact

### Jira Issues Affected
- **TJ-1656** (Epic): Trade Ticket Revamp - primary epic being finalized
- **TJ-1889**: UI Trade ticket revamp - Draft story to be broken down
- **TJ-1890**: UI Order confirmation revamp - Draft story to be broken down
- **TJ-1979**: Navigation Flow Handler - To Do task to be assigned
- **TJ-1694**: Counter details Short direction (196 days old) - needs review

### Team Members
| Assignee | Current Tasks | Recommended Action |
|----------|---------------|-------------------|
| PL_Duong (Kelvin) | 9 | Redistribute 2-3 tasks |
| Vũ Văn Tuân | 6 | Can accept 1-2 more |
| Dev Anh Pham (Henson) | 5 | OK |
| VietNguyen2 | 1 | Available for more |

### Jira Fields to Update
- Status transitions for Draft → SIT (after breakdown)
- Story Points for all 23 tasks
- Assignee redistribution
- Sprint assignment for unassigned tasks

## Non-Goals

- This does NOT implement the Trade Ticket features (that's a separate epic phase)
- This does NOT modify code in poems-mobile3-ios or poems-mobile3-android
- This does NOT address bugs (TJ-2328, TJ-2345, etc.) - separate backlog management
