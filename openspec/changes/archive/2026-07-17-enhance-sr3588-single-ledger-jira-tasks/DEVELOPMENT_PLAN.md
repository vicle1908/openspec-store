# P3 Mobile Single Ledger - Frontend Development Plan

**Version:** 4.0
**Date:** June 11, 2026
**Epic:** SR-3588 - USSO Single Ledger
**Scope:** Frontend Only (Backend APIs Ready)
**Team:** 10 Android + 10 iOS + 15 QA

---

## 1. Overview

| Sprint | Focus | Duration | Key Deliverables |
|--------|-------|----------|------------------|
| **Sprint 1** | Solution & Design | Weeks 1-2 | Clarified requirements, finalized architecture, resolved open questions |
| **Sprint 2** | Implementation | Weeks 3-4 | 20 frontend tasks built, integrated, tested |

### Jira Tasks Summary

| Category | Count | Status |
|----------|-------|--------|
| Backend Tasks (Epic Level) | 5 | ✅ Ready |
| Android Subtasks | 10 | ⏳ To Build |
| iOS Subtasks | 10 | ⏳ To Build |
| **Total** | **25** | |

---

## 2. Backend Tasks (SR-3775 to SR-3779)

These are **already done** - backend has implemented:

| Jira | Task | Priority | Status |
|------|------|----------|--------|
| SR-3775 | [Critical] CIS Flag API Contract | Highest | ✅ Done |
| SR-3776 | [Phase 1 Blocker] M2 Platform Access Control | High | ✅ Done |
| SR-3777 | [Phase 1] Options Activation Flow | High | ✅ Done |
| SR-3778 | [Phase 1] Realized P/L Merged View | Medium | ✅ Done |
| SR-3779 | [Phase 1] Error Handling & Graceful Degradation | Medium | ✅ Done |

---

## 3. Frontend Tasks (SR-3780 to SR-3799)

All frontend tasks are grouped under 3 parent tasks:

### Trade Tab Updates (SR-3755)

| Jira | Task | Platform | Sprint |
|------|------|----------|--------|
| SR-3780 | CIS Flag Integration for Trade Tab | Android | Sprint 2 |
| SR-3781 | Securities Renaming | Android | Sprint 2 |
| SR-3782 | Options Tab Removal from Trade | Android | Sprint 2 |
| SR-3783 | Merged Positions View | Android | Sprint 2 |
| SR-3784 | Realized P/L Integration | Android | Sprint 2 |
| SR-3790 | CIS Flag Integration for Trade Tab | iOS | Sprint 2 |
| SR-3791 | Securities Renaming | iOS | Sprint 2 |
| SR-3792 | Options Tab Removal from Trade | iOS | Sprint 2 |
| SR-3793 | Merged Positions View | iOS | Sprint 2 |
| SR-3794 | Realized P/L Integration | iOS | Sprint 2 |

### Market Tab Updates (SR-3756)

| Jira | Task | Platform | Sprint |
|------|------|----------|--------|
| SR-3785 | CIS Flag Integration for Market Tab | Android | Sprint 2 |
| SR-3786 | Outstanding Positions Merged View | Android | Sprint 2 |
| SR-3787 | Market Tab Filter/Sort Enhancements | Android | Sprint 2 |
| SR-3795 | CIS Flag Integration for Market Tab | iOS | Sprint 2 |
| SR-3796 | Outstanding Positions Merged View | iOS | Sprint 2 |
| SR-3797 | Market Tab Filter/Sort Enhancements | iOS | Sprint 2 |

### Global Search Enhancement (SR-3762)

| Jira | Task | Platform | Sprint |
|------|------|----------|--------|
| SR-3788 | Options Symbol Search | Android | Sprint 2 |
| SR-3789 | Combined Search Results | Android | Sprint 2 |
| SR-3798 | Options Symbol Search | iOS | Sprint 2 |
| SR-3799 | Combined Search Results | iOS | Sprint 2 |

---

## 4. Sprint 1: Solution & Design (Weeks 1-2)

**Theme:** Clarify, Design, Align before Build

### Goals
- Resolve all open questions
- Finalize architecture decisions
- Lock API contract understanding
- Complete design alignment

### Team Activities

#### Android Team (5 developers)
- Architecture review and planning
- Module structure design
- Stub API setup
- Figma design review and feedback

#### iOS Team (5 developers)
- Architecture review and planning
- Module structure design
- Stub API setup
- Figma design review and feedback

### Discussions Needed

| Topic | Question | Impact | Owner |
|-------|----------|--------|-------|
| CIS Flag | Edge case handling (network error, delayed response) | **Critical** | Backend + Mobile |
| M2 Accounts | Show merged or legacy UX? | **Critical** | Backend |
| Figma | Finalized specs for all Phase 1 screens? | **Critical** | Design |
| Merged View | Sorting strategy (alphabetical, by value, by type)? | High | Design + Mobile |
| Options Search | Only symbol or include company name? | High | Backend + Mobile |
| Realized P/L | Per position or aggregated display? | Medium | Design |

### Sprint 1 DoD
- [ ] All Critical open questions resolved
- [ ] Architecture decisions documented
- [ ] API contract fully understood
- [ ] Figma designs aligned
- [ ] Sprint 2 tasks ready for implementation

---

## 5. Sprint 2: Implementation (Weeks 3-4)

**Theme:** Full Feature Build

### Android Tasks (10 tasks)

| Jira | Task | Parent | Priority |
|------|------|--------|----------|
| SR-3780 | CIS Flag Integration (Trade) | SR-3755 | High |
| SR-3781 | Securities Renaming | SR-3755 | Medium |
| SR-3782 | Options Tab Removal | SR-3755 | High |
| SR-3783 | Merged Positions View | SR-3755 | High |
| SR-3784 | Realized P/L Integration | SR-3755 | Medium |
| SR-3785 | CIS Flag Integration (Market) | SR-3756 | High |
| SR-3786 | Outstanding Positions Merged | SR-3756 | High |
| SR-3787 | Filter/Sort Enhancements | SR-3756 | Medium |
| SR-3788 | Options Symbol Search | SR-3762 | High |
| SR-3789 | Combined Search Results | SR-3762 | High |

### iOS Tasks (10 tasks)

| Jira | Task | Parent | Priority |
|------|------|--------|----------|
| SR-3790 | CIS Flag Integration (Trade) | SR-3755 | High |
| SR-3791 | Securities Renaming | SR-3755 | Medium |
| SR-3792 | Options Tab Removal | SR-3755 | High |
| SR-3793 | Merged Positions View | SR-3755 | High |
| SR-3794 | Realized P/L Integration | SR-3755 | Medium |
| SR-3795 | CIS Flag Integration (Market) | SR-3756 | High |
| SR-3796 | Outstanding Positions Merged | SR-3756 | High |
| SR-3797 | Filter/Sort Enhancements | SR-3756 | Medium |
| SR-3798 | Options Symbol Search | SR-3762 | High |
| SR-3799 | Combined Search Results | SR-3762 | High |

### Sprint 2 DoD
- [ ] CIS Integration working (Trade + Market)
- [ ] Options Tab removed
- [ ] Positions Merged View complete
- [ ] Options Search with combined results
- [ ] Realized P/L merged display
- [ ] Filter/Sort enhancements done
- [ ] QA integration tests passing
- [ ] No critical bugs

---

## 6. Timeline

```
Week 1: Solution Design
├── Kickoff meeting
├── Solution walkthrough
├── Requirements review
└── Architecture planning

Week 2: Decisions Lock
├── Open questions resolved
├── Architecture finalized
├── Figma aligned
└── Sprint 2 planning

Week 3: Core Build
├── CIS Integration (Trade + Market)
├── Options Tab removal
├── Positions Merged View
└── Options Search

Week 4: Polish & Test
├── Realized P/L
├── Filter/Sort
├── Integration testing
└── Bug fixes
```

---

## 7. Dependencies

```
Backend Ready (SR-3775-3779)
│
├── SR-3780/3790: CIS Integration (Trade) ← Depends on SR-3775
├── SR-3785/3795: CIS Integration (Market) ← Depends on SR-3775
│
├── SR-3783/3793: Merged Positions ← After CIS ready
├── SR-3786/3796: Outstanding Positions ← After SR-3783/3793
│
├── SR-3784/3794: Realized P/L ← Depends on SR-3778
├── SR-3788/3798: Options Search ← Depends on SR-3777
└── SR-3789/3799: Combined Results ← After SR-3788/3798
```

---

## 8. Open Questions (Must Resolve in Sprint 1)

| # | Question | Impact | Owner | Status |
|---|----------|--------|-------|--------|
| 1 | CIS Flag edge cases? | **Critical** | Backend + Mobile | ⏳ |
| 2 | M2 feature flag behavior? | **Critical** | Backend | ⏳ |
| 3 | Figma designs finalized? | **Critical** | Design | ⏳ |
| 4 | Merged View sorting? | High | Design + Mobile | ⏳ |
| 5 | Options Search scope? | High | Backend + Mobile | ⏳ |
| 6 | Realized P/L display format? | Medium | Design | ⏳ |

---

## Summary

| Metric | Value |
|--------|-------|
| Backend Tasks | 5 (Done) |
| Frontend Tasks | 20 (Sprint 2) |
| Total Tasks | 25 |
| Sprints | 2 (4 weeks) |
| Team | 10 Android + 10 iOS + 15 QA |

✅ **Sprint 1: Clarify before build**
✅ **Sprint 2: Full implementation**
✅ **Production ready by Week 4**

**Jira Epic:** https://psplit.atlassian.net/browse/SR-3588
