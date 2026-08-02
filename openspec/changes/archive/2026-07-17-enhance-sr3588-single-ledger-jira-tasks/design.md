# Design: Enhance Jira Planned Tasks for SR-3588

## Context

This change enhances the Jira Epic SR-3588 "USSO Single Ledger" by adding missing sub-tasks identified in the URS document "P3 system enhancements - Single ledger project v1.0 20042026.pdf". The current Jira planning has 13 high-level tasks but lacks:

1. **Critical cross-cutting tasks** (CIS Flag API Contract)
2. **Platform access control** (M2 Platform Blocking)
3. **User experience flows** (Options Activation)
4. **Platform-specific breakdowns** (Android/iOS subtasks)
5. **Cross-cutting features** (Realized P/L, Error Handling)

This is a **Jira planning enhancement**, not an implementation change. The output is new/enhanced Jira sub-tasks under Epic SR-3588.

## Goals / Non-Goals

**Goals:**
- Ensure complete task coverage for Phase 1 implementation
- Define clear dependencies and blockers
- Provide acceptance criteria for each task
- Establish API contracts needed before implementation

**Non-Goals:**
- This does NOT implement any Single Ledger features
- This does NOT modify the URS document
- This does NOT write code in poems-mobile3-ios or poems-mobile3-android

## Decisions

### Decision 1: Use Jira sub-tasks instead of Stories

**Choice:** Create sub-tasks under existing Jira Tasks, not new Epic-level Stories.

**Rationale:**
- Existing 13 tasks under SR-3588 form the feature groupings
- Sub-tasks allow proper hierarchy and assignment
- Easier to track completion and dependencies

**Alternatives considered:**
- Creating new Stories at Epic level - rejected to maintain existing structure
- Creating parallel Epics - rejected as over-fragmentation

### Decision 2: CIS Flag as Critical Blocker

**Choice:** Define CIS Flag API Contract as the first and highest priority task.

**Rationale:**
- All UI features depend on knowing which UX to render
- Backend contract must be agreed before mobile implementation
- Sets precedent for other API contracts

### Decision 3: M2 Platform as Access Control Feature

**Choice:** Model M2 platform blocking as a feature task, not a bug.

**Rationale:**
- M2 accounts need explicit handling per URS
- Feature task allows proper rollout coordination
- Easier to track and disable after migration

### Decision 4: Platform-Specific Subtasks Required

**Choice:** Require Android and iOS subtasks for every feature task.

**Rationale:**
- Current tasks are platform-agnostic
- Development team uses separate Android/iOS branches
- Clear ownership and parallel development

## Risks / Trade-offs

### Risk: Backend API Contract Dependencies

**[Risk]** Backend team may not prioritize CIS flag API contract work.

**Mitigation:** Escalate through product owner; document dependency in Epic description.

### Risk: M2 Migration Timeline Unknown

**[Risk]** M2 platform migration timeline is uncertain, may block Phase 1.

**Mitigation:** Design M2 blocking as feature flag, not hard-coded; allow toggling after migration.

### Risk: Scope Creep

**[Risk]** Adding detailed subtasks may expand scope beyond Phase 1.

**Mitigation:** Strictly limit to Phase 1 features per URS; defer Phase 2+ items to separate planning.

### Risk: Task Creation Overhead

**[Risk]** Creating many subtasks may slow sprint planning.

**Mitigation:** Use task templates; batch-create related tasks; prioritize CIS flag and M2 first.

## Migration Plan

This is a planning artifact, not a code change. No migration needed.

### Rollback

If this planning change is rejected:
- Discard this OpenSpec change
- Continue with existing Jira task structure
- Proceed with implementation as-is

## Open Questions

1. **Backend API Owner:** Who owns the CIS flag API contract? Need backend team assignment.
2. **M2 Migration Timeline:** When is M2 platform migration expected? Need PM confirmation.
3. **Testing Strategy:** Are there automated API contract tests? Need QA input for test tasks.
4. **Figma Design Status:** Are Figma designs finalized for all Phase 1 screens? Need design team confirmation.

## Jira Task Creation Plan

Based on this design, the following Jira sub-tasks will be created:

| Task | Parent | Priority | Type |
|------|--------|----------|------|
| Define CIS Flag API Contract | SR-3588 | Critical | Task |
| Implement M2 Platform Access Control | SR-3588 | High | Task |
| Design Options Activation Flow | SR-3588 | High | Task |
| Android: CIS Flag Integration | (new) | High | Subtask |
| Android: Trade Tab Enhancement | SR-3755 | High | Subtask |
| Android: Market Tab Enhancement | SR-3756 | High | Subtask |
| iOS: CIS Flag Integration | (new) | High | Subtask |
| iOS: Trade Tab Enhancement | SR-3755 | High | Subtask |
| iOS: Market Tab Enhancement | SR-3756 | High | Subtask |
| Realized P/L Merged View | SR-3588 | Medium | Task |
| Error Handling & Graceful Degradation | SR-3588 | Medium | Task |
| Delete SR-3753 (probe task) | N/A | Low | Cleanup |
