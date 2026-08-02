# Tasks — Release 3.3.54 Bug Classification

## Priority 1: Critical Blockers (Fix Immediately)

### TASK-001: Fix AM-2287 — Realized PL bottom sheet
- **Priority:** Highest
- **Platform:** Android
- **Status:** In Progress
- **Assignee:** Dao Mai Binh Thuy
- **Commits in worktree:** 0
- **Action:** Verify fix is on correct branch. If not, escalate to assignee for merge into `release/v3.3.54_develop_27_06_2026`.
- **Success:** Commit merged + SIT passed

### TASK-002: Verify TJ-2328 — Wrong Payment Type
- **Priority:** Highest
- **Platform:** Android
- **Status:** SIT
- **Assignee:** Nguyen Minh Duc
- **Commits in worktree:** 0
- **Action:** SIT status suggests fix exists. Find the correct branch/PR and merge to release worktree.
- **Success:** Fix verified in worktree + SIT passed

### TASK-003: Fix SR-3689 — API Orders history inconsistency
- **Priority:** High
- **Platform:** API (Backend)
- **Status:** In Progress
- **Assignee:** ITMobile - Bui Quoc Toan Tony
- **Commits in worktree:** 0
- **Action:** This is a backend API blocker — both iOS and Android depend on it. Escalate for immediate fix.
- **Success:** API fixed + both mobile platforms re-test

## Priority 2: High-Risk Unmerged (Fix This Week)

### TASK-004: AU-482 — iOS OTP navigation after CAPTCHA
- **Priority:** High | **Platform:** iOS | **Status:** In Progress | **Commits:** 0
- **Action:** Assignee Tuyen Vuong Xuan to merge fix

### TASK-005: AM-2300 — iOS cash balance frame loading
- **Priority:** High | **Platform:** iOS | **Status:** In Progress | **Commits:** 0
- **Action:** Assignee Dao Mai Binh Thuy to merge fix

### TASK-006: PDS-484 — iOS remark tooltip
- **Priority:** High | **Platform:** iOS | **Status:** In Progress | **Commits:** 0
- **Action:** Assignee Dev Tuan Anh(Finn) to merge fix

### TASK-007: PDS-383 — iOS decimal input on Trade Ticket
- **Priority:** High | **Platform:** iOS | **Status:** SIT | **Commits:** 0
- **Action:** Fix exists but not in worktree. Find and merge.

### TASK-008: AM-2268 — Both platforms API not called (Outstanding Positions)
- **Priority:** High | **Platform:** Both | **Status:** In Progress | **Commits:** iOS: 3
- **Action:** iOS has commits, Android needs merge.

### TASK-009: PDS-514 — Android disclaimer blinks
- **Priority:** High | **Platform:** Android | **Status:** To Do | **Commits:** 0
- **Action:** Start development immediately

### TASK-010: PDS-508 — Android Open Account background
- **Priority:** High | **Platform:** Android | **Status:** To Do | **Commits:** 0
- **Action:** Start development immediately

### TASK-011: PDS-507 — iOS Open Account wrong step
- **Priority:** High | **Platform:** iOS | **Status:** To Do | **Commits:** 0
- **Action:** Start development immediately

### TASK-012: SR-3706 — Android Condition option no response
- **Priority:** High | **Platform:** Android | **Status:** To Do | **Commits:** 0
- **Action:** Start development immediately

### TASK-013: AU-471 — Android Caps Lock warning
- **Priority:** High | **Platform:** Android | **Status:** In Progress | **Commits:** 0
- **Action:** Assignee QA Nguyen Thi Ha to merge fix

## Priority 3: Code Review (Quick Wins)

### TASK-014: Merge SR-3705 — Stop Price Trigger default
- **Priority:** High | **Platform:** Android | **Status:** Code Review | **Commits:** 1
- **Action:** Approve and merge

### TASK-015: Merge SR-3704 — Stop Price Trigger button type
- **Priority:** Medium | **Platform:** Android | **Status:** Code Review | **Commits:** 0
- **Action:** Approve and merge

### TASK-016: Merge PDS-510 — Community icons enabled
- **Priority:** Medium | **Platform:** Android | **Status:** Code Review | **Commits:** 1
- **Action:** Approve and merge

### TASK-017: Merge PDS-488 — CFD Analytics cutoff
- **Priority:** Medium | **Platform:** Android | **Status:** Code Review | **Commits:** 1
- **Action:** Approve and merge

### TASK-018: Merge PDS-440 — iOS Trade/Me
- **Priority:** Medium | **Platform:** iOS | **Status:** Code Review | **Commits:** 1
- **Action:** Approve and merge

### TASK-019: Merge PDS-340 — Both platforms
- **Priority:** Medium | **Platform:** Both | **Status:** Code Review | **Commits:** 1
- **Action:** Approve and merge

### TASK-020: Merge AU-424 — Android UI/UX
- **Priority:** Medium | **Platform:** Android | **Status:** Code Review | **Commits:** 1
- **Action:** Approve and merge

### TASK-021: Merge RMD-4333 — iOS Watchlist
- **Priority:** Medium | **Platform:** iOS | **Status:** Code Review | **Commits:** 1
- **Action:** Approve and merge

### TASK-022: Merge TJ-2333 — Android UI
- **Priority:** Medium | **Platform:** Android | **Status:** Code Review | **Commits:** 3
- **Action:** Approve and merge

## Priority 4: SIT Verification (Confirm Merged Fixes)

### TASK-023: Verify all 242 SIT bugs have corresponding commits in worktrees
- **Action:** Cross-reference SIT bugs with worktree git log
- **Success:** 100% of SIT bugs have matching commits

## Priority 5: To Do Triage (Plan & Assign)

### TASK-024: Triage 38 To Do bugs
- **Action:** Assign owners, set deadlines, move to In Progress
- **Target:** All To Do bugs have assignees and ETAs within 1 week

## Priority 6: Systemic Improvements

### TASK-025: Android/iOS UI parity audit
- **Trigger:** 70 cross-platform bugs + 223 UI/UX bugs (67.8%)
- **Action:** Implement visual regression testing for next release

### TASK-026: Auth/Signup module focus
- **Trigger:** 56.5% of Auth bugs unmerged
- **Action:** Dedicated sprint for Auth module cleanup
