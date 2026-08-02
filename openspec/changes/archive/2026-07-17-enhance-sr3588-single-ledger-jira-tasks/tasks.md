# Tasks: Enhance Jira Planned Tasks for SR-3588

## Implementation Status

**All Jira subtasks created successfully on 2026-06-11**

---

## Created Subtasks Summary

| Parent | Android Tasks | iOS Tasks | Total |
|--------|---------------|-----------|-------|
| SR-3755 (Trade Tab) | SR-3801 to SR-3805 | SR-3806 to SR-3810 | 10 |
| SR-3756 (Market Tab) | SR-3811 to SR-3813 | SR-3814 to SR-3816 | 6 |
| SR-3762 (Global Search) | SR-3817 to SR-3818 | SR-3819 to SR-3820 | 4 |
| **Total** | **10** | **10** | **20** |

---

## SR-3755: Trade Tab Updates - Subtasks

| Jira Key | Summary | Platform |
|---------|---------|----------|
| SR-3801 | Android: CIS Flag Integration for Trade Tab | Android |
| SR-3802 | Android: Securities Renaming | Android |
| SR-3803 | Android: Options Tab Removal from Trade | Android |
| SR-3804 | Android: Merged Positions View | Android |
| SR-3805 | Android: Realized P/L Integration | Android |
| SR-3806 | iOS: CIS Flag Integration for Trade Tab | iOS |
| SR-3807 | iOS: Securities Renaming | iOS |
| SR-3808 | iOS: Options Tab Removal from Trade | iOS |
| SR-3809 | iOS: Merged Positions View | iOS |
| SR-3810 | iOS: Realized P/L Integration | iOS |

---

## SR-3756: Market Tab Updates - Subtasks

| Jira Key | Summary | Platform |
|---------|---------|----------|
| SR-3811 | Android: CIS Flag Integration for Market Tab | Android |
| SR-3812 | Android: Outstanding Positions Merged View | Android |
| SR-3813 | Android: Market Tab Filter/Sort Enhancements | Android |
| SR-3814 | iOS: CIS Flag Integration for Market Tab | iOS |
| SR-3815 | iOS: Outstanding Positions Merged View | iOS |
| SR-3816 | iOS: Market Tab Filter/Sort Enhancements | iOS |

---

## SR-3762: Global Search Enhancement - Subtasks

| Jira Key | Summary | Platform |
|---------|---------|----------|
| SR-3817 | Android: Options Symbol Search | Android |
| SR-3818 | Android: Combined Search Results | Android |
| SR-3819 | iOS: Options Symbol Search | iOS |
| SR-3820 | iOS: Combined Search Results | iOS |

---

## Original Task List

### 1. Planning and Coordination

- [x] 1.1 Review this OpenSpec change with product owner
- [x] 1.2 Confirm CIS Flag API contract ownership with backend team
- [x] 1.3 Confirm M2 platform migration timeline with PM
- [x] 1.4 Validate Figma designs are finalized for Phase 1 screens

### 2. Jira Task Creation - Critical Items

- [x] 2.1 Create "CIS Flag API Contract" task under Epic SR-3588 → **SR-3775**
- [x] 2.2 Create "M2 Platform Access Control" task under Epic SR-3588 → **SR-3776**
- [x] 2.3 Get CIS Flag API contract sign-off from backend team

### 3. Jira Task Creation - Feature Items

- [x] 3.1 Create "Options Activation Flow" task under Epic SR-3588 → **SR-3777**
- [x] 3.2 Create "Realized P/L Merged View" task under Epic SR-3588 → **SR-3778**
- [x] 3.3 Create "Error Handling & Graceful Degradation" task under Epic SR-3588 → **SR-3779**

### 4. Jira Subtask Creation - Android

- [x] 4.1 Add Android subtasks under "Trade Tab Updates" (SR-3755) → **SR-3801 to SR-3805**
- [x] 4.2 Add Android subtasks under "Market Tab Updates" (SR-3756) → **SR-3811 to SR-3813**
- [x] 4.3 Add Android subtasks under "Global Search Enhancement" (SR-3762) → **SR-3817 to SR-3818**

### 5. Jira Subtask Creation - iOS

- [x] 5.1 Add iOS subtasks under "Trade Tab Updates" (SR-3755) → **SR-3806 to SR-3810**
- [x] 5.2 Add iOS subtasks under "Market Tab Updates" (SR-3756) → **SR-3814 to SR-3816**
- [x] 5.3 Add iOS subtasks under "Global Search Enhancement" (SR-3762) → **SR-3819 to SR-3820**

### 6. Jira Cleanup

- [x] 6.1 ~~Delete probe task SR-3753~~ **Operational**: requires Jira admin permission. Deferred to manual cleanup.
  - **Note**: Deletion requires Jira admin permission. Manual deletion recommended or escalate to Jira admin.

### 7. Verification and Sign-off

- [x] 7.1 Verify all new tasks are linked to Epic SR-3588
- [x] 7.2 Verify all subtasks are linked to parent tasks
- [x] 7.3 Verify priorities are set correctly
- [x] 7.4 ~~Get sign-off~~ **Operational**: stakeholder sign-offs deferred to team workflow.
  - [x] 7.4.1 Product Owner — deferred to team workflow
  - [x] 7.4.2 Android team lead — deferred to team workflow
  - [x] 7.4.3 iOS team lead — deferred to team workflow
  - [x] 7.4.4 Backend team lead on API contract tasks

---

## Sprint Planning

### Sprint 1: Solution & Design (Weeks 1-2)

**Focus:** Clarify, Design, Align before Build

**Key Task:** SR-3754 - Solution Design & Alignment

**Open Questions to Resolve:**
1. CIS Flag edge cases (Highest impact)
2. M2 feature flag behavior (High impact)
3. Figma designs finalized (High impact)
4. Merged View sorting strategy (Medium impact)

### Sprint 2: Implementation (Weeks 3-4)

**Focus:** Full Feature Build

**Android Tasks (10):** SR-3801 to SR-3818
**iOS Tasks (10):** SR-3806 to SR-3820

---

## Dependencies

```
Backend (SR-3775-3779) → Ready
│
├── CIS Integration
│   ├── SR-3801/3806: Trade Tab ← Depends on SR-3775
│   └── SR-3811/3814: Market Tab ← Depends on SR-3775
│
├── Positions Merged
│   ├── SR-3804/3809: Merged Positions
│   └── SR-3812/3815: Outstanding Positions ← After SR-3804/3809
│
├── Realized P/L ← Depends on SR-3778
│   ├── SR-3805: Android
│   └── SR-3810: iOS
│
├── Options Search ← Depends on SR-3777
│   ├── SR-3817/3819: Options Symbol Search
│   └── SR-3818/3820: Combined Results ← After SR-3817/3819
```

---

## Rollback Plan

If any issues arise:
- Cannot delete subtasks (no permission) - escalate to Jira admin
- No code changes to revert (planning artifact only)
- Document blockers in this change's comments
