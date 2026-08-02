# Release 3.3.54 Bug Classification — Detailed Report

**Generated:** 2026-06-04
**Source:** Jira Filter 15269 (https://psplit.atlassian.net/issues/?filter=15269)
**Total Issues:** 329 (328 Bugs + 1 Task)
**Worktrees Analyzed:**
- `poems-mobile3-android-3.3.54` (branch: 3.3.54_develop_27_06_2026 → tracking origin/release/v3.3.54_develop_27_06_2026)
- `poems-mobile3-ios-3.3.54` (branch: 3.3.54_develop_27_06_2026 → tracking origin/release/v3.3.54_develop_27_06_2026)

---

## Quick Stats

| Category | Count |
|----------|-------|
| Total Issues | 329 |
| Bugs | 328 |
| Tasks | 1 |
| Highest Priority | 3 |
| High Priority | 23 |
| Medium Priority | 209 |
| Low Priority | 90 |
| Lowest Priority | 4 |
| Already in SIT | 242 (73.6%) |
| In Progress | 36 (11.0%) |
| Code Review | 13 (4.0%) |
| To Do | 38 (11.6%) |
| Merged in Android Worktree | 136 |
| Merged in iOS Worktree | 88 |
| Merged in Both | 4 |
| Not Merged in Either | 109 |

---

## Platform Distribution

| Platform | Count | % |
|----------|-------|---|
| Android-only | 153 | 46.5% |
| iOS-only | 98 | 29.8% |
| Both platforms | 70 | 21.3% |
| API/Backend | 4 | 1.2% |
| Other/General | 4 | 1.2% |

---

## Module Distribution (Top 10)

| Module | Count | Merged | Unmerged |
|--------|-------|--------|----------|
| UI/UX | 223 | 170 | 53 |
| Trade/TradeTicket | 94 | 62 | 32 |
| Market | 83 | 55 | 28 |
| Me (Portfolio/History) | 83 | 58 | 25 |
| Auth/Signup | 46 | 20 | 26 |
| CFD | 24 | 12 | 12 |
| UnitTrust | 24 | 15 | 9 |
| Community | 18 | 8 | 10 |
| Settings | 17 | 12 | 5 |
| Analytics | 16 | 10 | 6 |

---

## Unmerged Critical Issues (109 total)

### Highest Priority (2 unmerged)
- **AM-2287** — Android: Realized PL bottom sheet does not open (In Progress, 0 commits)
- **TJ-2328** — Android: Incorrect Payment Type submitted (SIT, 0 commits — fix may be on different branch)

### High Priority (12 unmerged)
- **PDS-484** — iOS: Remark tooltip not displayed (In Progress, 0 commits)
- **AU-482** — iOS: Not navigated to OTP after CAPTCHA (In Progress, 0 commits)
- **AM-2300** — iOS: Live cash balance frame fails to load (In Progress, 0 commits)
- **SR-3689** — API: Options Orders history inconsistent (In Progress, 0 commits)
- **AM-2268** — Both: API not called for Outstanding Positions (In Progress, iOS: 3 commits)
- **AU-471** — Android: Caps Lock warning not shown (In Progress, 0 commits)
- **PDS-383** — iOS: Quantity field allows decimal (SIT, 0 commits)
- **PDS-514** — Android: Disclaimer bottomsheet blinks (To Do, 0 commits)
- **PDS-508** — Android: Open Account background missing (To Do, 0 commits)
- **PDS-507** — iOS: Wrong step after account open (To Do, 0 commits)
- **SR-3706** — Android: No response tapping Condition (To Do, 0 commits)
- **RMD-4352** — iOS: (To Do, 0 commits)

### Medium Priority — Code Review (6 unmerged)
- SR-3704, PDS-509, PDS-506, PDS-505, PDS-504, PDS-503, AM-2316, RMD-4346, RMD-4343, RMD-4341, SR-3700, TJ-2332, TJ-2330, SR-3685, AU-479, TJ-2324, AM-2274, AM-2270, AM-2263, SR-3678, AM-2255

### Medium Priority — In Progress (17 unmerged)
- PDS-509, PDS-506, PDS-505, PDS-504, PDS-503, AM-2316, RMD-4346, RMD-4343, RMD-4341, SR-3700, TJ-2332, TJ-2330, SR-3685, AU-479, TJ-2324, AM-2274, AM-2270, AM-2263, SR-3678, AM-2255

### Medium/Low — To Do (38+ unmerged)
- RMD-4351, RMD-4350, RMD-4349, AM-2316, PDS-515, AM-2315, RMD-4348, RMD-4347, RMD-4346, RMD-4345, RMD-4344, AU-484, AM-2311, PDS-506, SR-3704, PDS-505, PDS-504, AM-2285, SR-3690, AM-2080, PDS-516, PDS-500, PDS-499, SR-3709, SR-3708, SR-3707, COM-1806, COM-1804, AM-2071

---

## Release Readiness Scorecard

| Category | Score | Status |
|----------|-------|--------|
| Highest bugs fixed | 1/3 (33%) | ❌ BLOCKED |
| High bugs fixed | 14/23 (61%) | ⚠️ AT RISK |
| Medium bugs in SIT | 130+/209 (62%) | ✅ ON TRACK |
| Low bugs in SIT | 70+/90 (78%) | ✅ ON TRACK |
| Android worktree health | 136/153 (89%) | ✅ GOOD |
| iOS worktree health | 88/98 (90%) | ✅ GOOD |
| Code Review backlog | 7 items | ⚠️ NEEDS ATTENTION |
| API blocker | 1 (SR-3689) | ❌ BLOCKING |

**Overall Release Readiness: 58% — NOT READY**

### Blockers to Release
1. AM-2287 — Highest, In Progress, no commits
2. TJ-2328 — Highest, SIT, no commits in worktree
3. SR-3689 — High API, In Progress, no commits

### At Risk
1. AU-482 — High iOS auth blocker
2. AM-2300 — High iOS portfolio blocker
3. 9 High bugs in To Do status
4. 38 Medium To Do bugs (volume risk)
