# Design: Finalize TJ-1656 Trade Ticket Revamp Epic Planning

## Context

The TJ-1656 Trade Ticket Revamp epic is the parent initiative for modernizing the Trade Ticket screens in POEMS Mobile 3 (iOS and Android). The epic has:

- **23 tasks** organized in a 2-level hierarchy (parent stories + platform-specific subtasks)
- **2 Draft stories** (TJ-1889, TJ-1890) that reference URS but lack subtask breakdown
- **0/23 story points** assigned - no estimation exists
- **Resource imbalance** - PL_Duong has 9 tasks while VietNguyen2 has only 1
- **4 stale tasks** including TJ-1694 at 196 days old

### Current Task Structure
```
Epic: TJ-1656 (Trade Ticket Revamp)
├── Planning (Done)
├── Analysis (Done)
├── Counter Quotes (3 subtasks)
├── Search Counter Screen (2 subtasks)
├── Display Account Information (2 subtasks)
├── Architecture Design (2 subtasks)
├── Navigation to Trade ticket (2 subtasks)
├── Counter details - Short direction for SGX (2 subtasks)
├── Navigation Flow Handler (To Do)
├── UI Trade ticket revamp (Draft - BLOCKING)
└── UI Order confirmation revamp (Draft - BLOCKING)
```

### Stakeholders
- **PL_Duong (Kelvin)**: Tech Lead, overloaded with 9 tasks
- **Vũ Văn Tuân**: Android developer, 6 tasks
- **Dev Anh Pham (Henson)**: iOS developer, 5 tasks
- **VietNguyen2**: iOS developer, 1 task

## Goals / Non-Goals

**Goals:**
1. Break down 2 Draft stories (TJ-1889, TJ-1890) into platform-specific subtasks
2. Add story points to all 23 tasks for sprint planning
3. Redistribute workload to balance team capacity
4. Clear stale tasks (TJ-1694) with review decision
5. Document final task assignments and sprint allocation

**Non-Goals:**
- Implementation of Trade Ticket features (not code changes)
- Bug fixes (separate backlog)
- URS revision or requirements changes
- Code changes to poems-mobile3-ios or poems-mobile3-android

## Decisions

### Decision 1: Draft Story Breakdown Approach

**Decision:** Break down TJ-1889 and TJ-1890 using the referenced URS document structure (Functions 3-9) and create iOS/Android subtasks.

**Rationale:**
- Maintains traceability to URS document
- Follows existing pattern where other parent stories have iOS/Android subtasks
- Enables parallel development by platform

**Alternatives Considered:**
- Keep as single cross-platform story: Rejected - inconsistent with existing structure
- Create separate epics per platform: Overkill for this scope

### Decision 2: Story Points Estimation Method

**Decision:** Use Fibonacci sequence (1, 2, 3, 5, 8, 13) based on complexity tiers.

**Recommended Points:**
| Tier | Points | Description |
|------|--------|-------------|
| Simple | 1-2 | Minor UI tweaks, accessibility updates |
| Medium | 3-5 | Standard component work, screen updates |
| Complex | 8-13 | New screens, complex navigation, API changes |

### Decision 3: Resource Redistribution

**Decision:** Redistribute based on current capacity and task affinity.

**Recommendations:**
| Task | Current Owner | Recommended Owner | Reason |
|------|---------------|------------------|--------|
| TJ-1979 (Navigation Flow Handler) | PL_Duong | Vũ Văn Tuân | Android-focused, Tuân has capacity |
| Subtasks of TJ-1889/TJ-1890 | PL_Duong | VietNguyen2 | Lighten Kelvin's load |

### Decision 4: Stale Task Resolution

**Decision:** Review TJ-1694 (196 days) to determine if still valid or should be closed/merged.

**Options:**
1. Keep open if feature still required
2. Close as outdated if SGX Short direction no longer needed
3. Merge with other Counter details task if redundant

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| URS not accessible to break down stories | Low | High | SharePoint link provided; if fails, use Trade ticket matrix.xlsx |
| Story points disagreement | Medium | Medium | Use tier-based estimation, review in sprint planning |
| Redistribution rejected by team | Low | Medium | Document rationale, allow reassignment |
| Draft stories still incomplete after planning | Low | High | Add acceptance criteria from URS to unblock |

## Open Questions

1. **TJ-1694 Status**: Should this 196-day-old task be closed, kept, or merged?
2. **Sprint Target**: Which sprint should completed tasks target - Sprint 16 (current) or Sprint 17?
3. **Story Points Approval**: Who approves the estimation - Tech Lead (PL_Duong) or Product Owner?
4. **Figma Access**: Do all team members have Figma access for UI specs reference?

## Implementation Approach

### Phase 1: Draft Story Breakdown
1. Review URS document for Functions 3-9
2. Create iOS subtask for each function
3. Create Android subtask for each function
4. Add acceptance criteria from URS

### Phase 2: Estimation
1. Apply story points using tier system
2. Validate with team (async or sync)
3. Update all 23 tasks in Jira

### Phase 3: Resource Rebalance
1. Move 1-2 tasks from PL_Duong
2. Assign to available team members
3. Update sprint assignments

### Phase 4: Stale Task Cleanup
1. Review TJ-1694 with product/tech lead
2. Document decision in task comments
3. Update or close as appropriate

## Dependencies

- **URS Document**: https://phillipgroupsg.sharepoint.com/.../URS_Trade_Ticket_Revamp_Mobile_v1.3.docx
- **Trade Ticket Matrix**: https://phillipgroupsg.sharepoint.com/.../Trade%20ticket%20matrix.xlsx
- **Figma Design**: https://www.figma.com/design/dARit1smv40LvsvhF16cah/Trade---Counter-Details---Stocks

## Tools Used

- **Jira API**: Via `tdt_core.clients.jira.PatchedJira`
- **Epic Report**: `uv run epic-report generate TJ-1656`
- **Manual Review**: URS and Figma for acceptance criteria
