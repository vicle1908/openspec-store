# Tasks: P3 Mobile Release 3.3.57 — Epic Planning & Sprint Capacity Alignment

## Sprint Calendar (2-week sprints, 5 workdays/week = 10 days/sprint)

| Sprint | Start | End | Workdays | Phase | Focus |
|--------|-------|-----|----------|-------|-------|
| 16 | 2026-06-08 | 2026-06-19 | 10 | **FINISH** | USSO solution design + v3.3.54 UAT regression cleanup + v3.3.55 biometric SIT |
| 17 | 2026-06-22 | 2026-07-03 | 10 | **DEVELOP** (1/2) | All v3.3.57 epics: coding + unit tests (~50% complete) |
| 18 | 2026-07-06 | 2026-07-17 | 10 | **DEVELOP** (2/2) | Coding complete + internal verification by dev |
| 19 | 2026-07-20 | 2026-07-31 | 10 | **VERIFY** | QA SIT execution + cross-platform parity + bug fix |
| 20 | 2026-08-03 | 2026-08-14 | 10 | **VERIFY + BUFFER** | UAT + bug fix + soft release + release cut |
| 21 | 2026-08-17 | 2026-08-28 | 10 | **BUFFER** | Post-release monitoring + Sep planning |
| 22+ | 2026-08-31+ | TBD | — | **SEPTEMBER+** | Defer TJ-1635, RMD-4160, TJ-1773, TJ-1960, RMD-4148 |

> **Why 4 phases, not 3?**
> 1. Each sprint has only 10 workdays × 8h = 80h per dev. The original 3-phase plan (Finish + Develop + Verify in 3 sprints) assumes 100% of capacity goes to v3.3.57 work, but v3.3.54 UAT regression (PUB-39, 576h) competes in Sprint 16.
> 2. Total v3.3.57 feature work: **1358h** across 7 epics. Available across Sprints 17-18 (DEVELOP): **2 × 909h = 1818h** (after 25% tech lane + 15% buffer). That's 25% slack — sufficient for unknowns.
> 3. Verification (Sprint 19-20) needs its own dedicated time. Pushing verify into Sprint 18 along with dev created the "throw-it-over-the-wall" delay.

---

## Phase Definitions

### Phase 1: FINISH (Sprint 16, 2026-06-08 → 2026-06-19) — IN PROGRESS
**Goal:** Lock down solution design and resolve open questions before development starts.
**Allocated capacity:** 50h per team for FINISH work (rest is v3.3.54 UAT + v3.3.55 biometric)

- USSO Single Ledger architecture sign-off
- CIS Flag API contract sign-off (SR-3775)
- M2 Platform Access Control logic finalized (SR-3776)
- Backend API readiness checklist for all v3.3.57 epics
- Story point re-estimation
- Figma sign-off

### Phase 2: DEVELOP (Sprint 17-18, 2026-06-22 → 2026-07-17)
**Goal:** Code, unit test, and internal verification of all v3.3.57 epics.
**Allocated capacity:** 60% × 1516h = 909h/sprint for feature dev

- Sprint 17: Coding starts for all 7 epics; ~50% stories reach "In QA" by end of sprint
- Sprint 18: Coding complete; dev internal verification; all stories to "In QA" by end of sprint
- Devs write unit tests as part of each PR (not QA's job)
- Code review SLA: < 1 business day per PR

### Phase 3: VERIFY (Sprint 19, 2026-07-20 → 2026-07-31)
**Goal:** Full SIT, regression, and bug fix.
**Allocated capacity:** 650h QA for SIT execution + 25% of dev time for bug fixes

- QA executes SIT test cases
- Regression vs. v3.3.55 baseline
- Cross-platform parity testing (iOS vs AOS)
- Backend integration testing
- All critical/high severity bugs resolved before Sprint 20

### Phase 4: BUFFER (Sprint 20, 2026-08-03 → 2026-08-14)
**Goal:** Final UAT, soft release, and release cut.
**Allocated capacity:** QA final pass + dev bug fixes + release engineering

- UAT sign-off
- Soft release to 5% of users
- Release notes finalized
- **Public Release 3.3.57 cut: 2026-08-14**

---

## Capacity Allocation Per Sprint

Each sub-team splits their capacity into 3 lanes (consistent across all phases):

| Lane | % Capacity | Purpose |
|------|-----------|---------|
| **Feature Development** | 60% | Story implementation per Epic |
| **Tech Tasks + Dependencies** | 25% | API contracts, feature flags, performance, build, dev tools, dependency upgrades |
| **Buffer (incidents, ad-hoc, learning)** | 15% | Production bugs, code review, tech training, meetings |

### Per-Sprint DEV Net Capacity (10 workdays)

| Team | Gross | Fixed Deductions | Total Net | DEV Ratio | **DEV Net** |
|------|-------|------------------|-----------|-----------|-------------|
| **Kelvin** | 924h | 60h | 864h | 67% (8/12 dev) | **576h** |
| **Andrew** | 800h | 60h | 740h | 70% (7/10 dev) | **518h** |
| **VuVuong** | 622h | 60h | 562h | 75% (6/8 dev) | **422h** |
| **TOTAL** | 2346h | 180h | 2166h | — | **1516h** |

After tech-tasks (25%) and buffer (15%): **909h available per sprint for feature dev**

### Per-Sprint QA Net Capacity

| Team | QA Net | SIT Capacity |
|------|--------|--------------|
| Kelvin | 288h | 28.8h/day for SIT |
| Andrew | 222h | 22.2h/day for SIT |
| VuVuong | 140h | 14.0h/day for SIT |
| **TOTAL** | **650h** | 65h/day across 3 teams |

---

## Per-Epic Sprint Plan (v3.3.57 Public Release — Aug 2026)

### v3.3.57 Epics — 4-Sprint Plan

| Epic | Team | Stories | Est. Effort (h) | FINISH (S16) | DEVELOP (S17-18) | VERIFY (S19) | BUFFER (S20) |
|------|------|---------|-----------------|---------------|------------------|--------------|--------------|
| **SR-3588** USSO Single Ledger | Kelvin | 20 | 320 | **FINISH** | DEVELOP | VERIFY | Bug fix |
| **AM-1244** Live Positions | Kelvin | 8 | 128 | (in prog) | DEVELOP | VERIFY | Bug fix |
| **AU-348** Transaction Notifications | VuVuong | 29 | 350 | setup | DEVELOP | VERIFY | Bug fix |
| **GAMI-1596** OOE | Andrew | 2 | 48 | — | DEVELOP | VERIFY | Bug fix |
| **SR-3391** CFD Market Discovery | Andrew | 50 | 200 | — | DEVELOP | VERIFY | Bug fix |
| **TJ-1893** Recurring Order Plan | Andrew | 9 | 144 | — | DEVELOP | VERIFY | Bug fix |
| **PWM-1778** SMART Portfolio Revamp | Andrew | 7 | 168 | — | DEVELOP | VERIFY | Bug fix |
| **TOTAL** | — | **125** | **1358h** | — | — | — | — |

### Per-Team Load Check (Sprint 17-18 combined)

| Team | v3.3.57 Effort (h) | Available (S17-18) | Buffer |
|------|--------------------|---------------------|--------|
| **Kelvin** | 448h (USSO 320 + AM 128) | 1152h (576h × 2) | **704h / 61%** |
| **Andrew** | 560h (OOE 48 + CFD 200 + Recurring 144 + SMART 168) | 1036h (518h × 2) | **476h / 46%** |
| **VuVuong** | 350h (AU-348) | 844h (422h × 2) | **494h / 59%** |
| **TOTAL** | 1358h | 3032h | **1674h / 55%** |

**Verdict:** 4-sprint plan has **55% buffer** for unknowns (10 workdays × 3 teams = 30 days × 8h × 3 = 720h just for tech + buffer lanes).

---

## Phase 1: FINISH (Sprint 16 — in progress by 2026-06-19)

- [ ] 1.1 **USSO Single Ledger (SR-3588) — FINISH by end of Sprint 16**
  - [ ] 1.1.1 CIS Flag API contract signed off (SR-3775)
  - [ ] 1.1.2 M2 Platform Access Control logic finalized (SR-3776)
  - [ ] 1.1.3 Options Activation Flow (SR-3777) — design sign-off
  - [ ] 1.1.4 Realized P/L Merged View (SR-3778) — Figma locked
  - [ ] 1.1.5 Error Handling & Graceful Degradation (SR-3779) — patterns defined
  - [ ] 1.1.6 Subtasks SR-3801 to SR-3820 (created by `enhance-sr3588-single-ledger-jira-tasks`) reviewed by Kelvin

- [ ] 1.2 **AM-1244 (Live Positions) — already In Progress**
  - [ ] 1.2.1 All 8 stories have updated acceptance criteria
  - [ ] 1.2.2 Real-time API contract with BO confirmed

- [ ] 1.3 **AU-348 (Transaction Notifications) — Sprint 16 setup**
  - [ ] 1.3.1 All 29 stories triaged (which P2, which P3)
  - [ ] 1.3.2 Push notification service contract confirmed

- [ ] 1.4 **Tech Tasks Lane — Phase 1 (Sprint 16)**
  - [ ] 1.4.1 Feature flag library version alignment (US 24 + Live Positions + Single Ledger)
  - [ ] 1.4.2 Dependency update audit: `tdt_core`, `tdt-sheets`, Gradle, CocoaPods
  - [ ] 1.4.3 CBOE EU feed integration spec for RMD-4148 (later sprint)
  - [ ] 1.4.4 BO Pre-Trade Fee Charges API contract for TJ-1960 (later sprint)

## Phase 2: DEVELOP (Sprint 17-18 — 2026-06-22 → 2026-07-17)

### Sprint 17: Coding starts (~50% complete by end of sprint)

- [ ] 2.1 **USSO Single Ledger (SR-3588) — Develop iOS** (Sprint 17)
  - [ ] 2.1.1 iOS: CIS Flag integration (SR-3806) → Code Review
  - [ ] 2.1.2 iOS: Securities renaming (SR-3807) → merge
  - [ ] 2.1.3 iOS: Options tab removal (SR-3808) → merge
  - [ ] 2.1.4 iOS: Merged positions view (SR-3809) → Code Review
  - [ ] 2.1.5 iOS: Realized P/L integration (SR-3810) → Code Review

- [ ] 2.2 **USSO Single Ledger (SR-3588) — Develop AOS** (Sprint 17)
  - [ ] 2.2.1 AOS: CIS Flag integration (SR-3801) → Code Review
  - [ ] 2.2.2 AOS: Securities renaming (SR-3802) → merge
  - [ ] 2.2.3 AOS: Options tab removal (SR-3803) → merge
  - [ ] 2.2.4 AOS: Merged positions view (SR-3804) → Code Review
  - [ ] 2.2.5 AOS: Realized P/L integration (SR-3805) → Code Review

- [ ] 2.3 **AM-1244 (Live Positions) — Develop** (Sprint 17)
  - [ ] 2.3.1 iOS + AOS: Rearrange Live Cash Balance (AM-2111) → Code Review
  - [ ] 2.3.2 iOS + AOS: Update field names (AM-2106) → merge
  - [ ] 2.3.3 iOS + AOS: Feature flag (AM-2004) → Code Review
  - [ ] 2.3.4 iOS + AOS: Real-time Realized PL API (AM-2001) → Code Review
  - [ ] 2.3.5 iOS + AOS: Real-time Cash mgmt API (AM-2000) → Code Review
  - [ ] 2.3.6 iOS + AOS: Position tab changes (AM-1999) → Code Review
  - [ ] 2.3.7 iOS + AOS: Settled Positions rename (AM-2003) → merge
  - [ ] 2.3.8 iOS + AOS: Outstanding Positions rename (AM-2002) → merge

- [ ] 2.4 **AU-348 (Transaction Notifications) — Develop starts** (Sprint 17)
  - [ ] 2.4.1 iOS + AOS: Push Notification Triggers (AU-391) → Code Review
  - [ ] 2.4.2 iOS + AOS: Notification Centre (AU-392) → Code Review
  - [ ] 2.4.3 iOS + AOS: Notification Settings toggle (AU-393) → Code Review
  - [ ] 2.4.4 iOS + AOS: P2/P3 Cross-app deep link (AU-388) → Code Review

- [ ] 2.5 **GAMI-1596 (OOE) — Develop** (Sprint 17)
  - [ ] 2.5.1 iOS + AOS: OOE Journey Criteria (GAMI-1597) → Code Review
  - [ ] 2.5.2 iOS + AOS: OOE Pagination for Poems Coin History (GAMI-1595) → Code Review

- [ ] 2.6 **SR-3391 (CFD Market Discovery) — Develop starts** (Sprint 17)
  - [ ] 2.6.1 iOS + AOS: Multi-language Summary view (SR-3457) → Code Review
  - [ ] 2.6.2 iOS + AOS: Multi-language List view (SR-3458) → Code Review
  - [ ] 2.6.3 iOS + AOS: In-App Deep Link (SR-3459) → Code Review

- [ ] 2.7 **TJ-1893 (Recurring Order Plan) — Develop starts** (Sprint 17)
  - [ ] 2.7.1 iOS + AOS: Recurring Order Plan feature (TJ-1899) → Code Review
  - [ ] 2.7.2 iOS + AOS: Status in main order status (TJ-1900) → Code Review

- [ ] 2.8 **PWM-1778 (SMART Portfolio Revamp) — Develop starts** (Sprint 17)
  - [ ] 2.8.1 iOS + AOS: Landing Page (PWM-1779) → Code Review
  - [ ] 2.8.2 iOS + AOS: New Client Journey (PWM-1780) → Code Review
  - [ ] 2.8.3 iOS + AOS: Existing Client Journey (PWM-1781) → Code Review

### Sprint 18: Coding complete + dev internal verification

- [ ] 2.9 **USSO Single Ledger (SR-3588) — Continue + Complete** (Sprint 18)
  - [ ] 2.9.1 iOS: Market tab updates (SR-3814, SR-3815, SR-3816) → Code Review
  - [ ] 2.9.2 iOS: Global search (SR-3819, SR-3820) → Code Review
  - [ ] 2.9.3 iOS: Error handling (SR-3779) → Code Review
  - [ ] 2.9.4 AOS: Market tab updates (SR-3811, SR-3812, SR-3813) → Code Review
  - [ ] 2.9.5 AOS: Global search (SR-3817, SR-3818) → Code Review
  - [ ] 2.9.6 Dev internal verification: iOS runs feature on real device, smoke test
  - [ ] 2.9.7 Dev internal verification: AOS same

- [ ] 2.10 **AM-1244 (Live Positions) — Complete dev internal verification** (Sprint 18)
  - [ ] 2.10.1 iOS + AOS: All 8 stories to "In QA" status
  - [ ] 2.10.2 Dev internal verification

- [ ] 2.11 **AU-348 (Transaction Notifications) — Continue** (Sprint 18)
  - [ ] 2.11.1 iOS + AOS: 25 more stories (out of 29) → Code Review
  - [ ] 2.11.2 iOS + AOS: All 29 stories to "In QA" status

- [ ] 2.12 **SR-3391 (CFD Market Discovery) — Continue** (Sprint 18)
  - [ ] 2.12.1 iOS + AOS: 47 more stories (out of 50) → Code Review
  - [ ] 2.12.2 iOS + AOS: All 50 stories to "In QA" status

- [ ] 2.13 **TJ-1893 (Recurring Order Plan) — Continue** (Sprint 18)
  - [ ] 2.13.1 iOS + AOS: Fractional Shares (TJ-1901) → Code Review
  - [ ] 2.13.2 iOS + AOS: Fractional/Whole Toggle (TJ-1902) → Code Review
  - [ ] 2.13.3 iOS + AOS: All 9 stories to "In QA" status

- [ ] 2.14 **PWM-1778 (SMART Portfolio Revamp) — Continue** (Sprint 18)
  - [ ] 2.14.1 iOS + AOS: Deposit/Withdrawal/Internal Transfer (PWM-1782-PWM-1785) → Code Review
  - [ ] 2.14.2 iOS + AOS: SRS Deposit (PWM-1785) → Code Review
  - [ ] 2.14.3 iOS + AOS: All 7 stories to "In QA" status

- [ ] 2.15 **Tech Tasks Lane — Phase 2** (Sprint 17-18)
  - [ ] 2.15.1 Feature flag A/B testing framework for Single Ledger
  - [ ] 2.15.2 Backend API mocks for parallel frontend dev (CIS flag, M2 access, real-time positions)
  - [ ] 2.15.3 Build pipeline: parallel iOS + AOS CI for fast feedback
  - [ ] 2.15.4 Code review SLA: < 1 business day per PR

## Phase 3: VERIFY (Sprint 19 — 2026-07-20 → 2026-07-31)

- [ ] 3.1 **USSO Single Ledger (SR-3588) — Verify**
  - [ ] 3.1.1 iOS SIT execution (12h dev + 16h QA per platform)
  - [ ] 3.1.2 AOS SIT execution
  - [ ] 3.1.3 Regression vs. v3.3.55 baseline
  - [ ] 3.1.4 UMO integration test (with MO team)
  - [ ] 3.1.5 Cross-platform parity check (iOS vs AOS)
  - [ ] 3.1.6 Edge case: M2 access denial UX
  - [ ] 3.1.7 Edge case: CIS flag false/true switching

- [ ] 3.2 **AM-1244 (Live Positions) — Verify**
  - [ ] 3.2.1 iOS + AOS SIT execution
  - [ ] 3.2.2 Field rename UX validation with PM
  - [ ] 3.2.3 Real-time data freshness SLA validation (< 5s)
  - [ ] 3.2.4 Feature flag A/B test in UAT

- [ ] 3.3 **AU-348 (Transaction Notifications) — Verify**
  - [ ] 3.3.1 iOS + AOS push notification delivery test
  - [ ] 3.3.2 Notification Centre UX test
  - [ ] 3.3.3 P2 + P3 cross-app consistency
  - [ ] 3.3.4 Permission prompts (iOS 17+, Android 13+)

- [ ] 3.4 **GAMI-1596 (OOE) — Verify**
  - [ ] 3.4.1 iOS + AOS offline/online transition tests
  - [ ] 3.4.2 Coin History pagination edge cases

- [ ] 3.5 **SR-3391 (CFD Market Discovery) — Verify**
  - [ ] 3.5.1 iOS + AOS multi-language rendering
  - [ ] 3.5.2 Deep link routing validation
  - [ ] 3.5.3 Analytics event firing validation

- [ ] 3.6 **TJ-1893 (Recurring Order Plan) — Verify**
  - [ ] 3.6.1 iOS + AOS fractional share test
  - [ ] 3.6.2 Recurring plan status flow test
  - [ ] 3.6.3 Toggle button UX

- [ ] 3.7 **PWM-1778 (SMART Portfolio Revamp) — Verify**
  - [ ] 3.7.1 iOS + AOS client journey E2E test
  - [ ] 3.7.2 Deposit/Withdrawal flow test
  - [ ] 3.7.3 SRS deposit flow test

- [ ] 3.8 **Tech Tasks Lane — Phase 3** (Sprint 19)
  - [ ] 3.8.1 Performance profiling: app launch time, memory, crash rate
  - [ ] 3.8.2 Security review of new APIs (CIS flag, M2 access)
  - [ ] 3.8.3 Release notes draft (per Epic)

## Phase 4: BUFFER (Sprint 20 — 2026-08-03 → 2026-08-14)

- [ ] 4.1 **Sprint 20: Bug Fix + Soft Release + Release Cut**
  - [ ] 4.1.1 Address all P0/P1 SIT bugs
  - [ ] 4.1.2 Soft release to 5% of users
  - [ ] 4.1.3 Monitor crash analytics
  - [ ] 4.1.4 UAT sign-off
  - [ ] 4.1.5 Release notes finalized
  - [ ] 4.1.6 **Public Release 3.3.57 cut: 2026-08-14**

## Phase 5: SEPTEMBER+ (Sprint 22+)

> **These epics are deferred from v3.3.57** because they were not feasible in 4 sprints given the team load. RMD-4148 was already in progress and continues.

- [ ] 5.1 **RMD-4148 (CBOE GY/UK) — Continue in Sprint 22** (already In Progress)
  - [ ] 5.1.1 iOS + AOS: Display GY/UK via CBOE EU (RMD-4149)
  - [ ] 5.1.2 iOS + AOS: Acknowledgment dialog (RMD-4150)
  - [ ] 5.1.3 iOS + AOS: Trade support (RMD-4151)
  - [ ] 5.1.4 iOS + AOS: Counter Detail (RMD-4152)
  - [ ] 5.1.5 iOS + AOS: Price alert (RMD-4154)
  - [ ] 5.1.6 iOS + AOS: Chart (RMD-4155)

- [ ] 5.2 **RMD-4160 (DLC Visibility) — Develop in Sprint 22-23**
  - [ ] 5.2.1 iOS + AOS: Global Search DLC ranking (RMD-4161)
  - [ ] 5.2.2 iOS + AOS: Market→Stock→SG (RMD-4162)
  - [ ] 5.2.3 iOS + AOS: Main Stock Counter Detail (RMD-4163)
  - [ ] 5.2.4 iOS + AOS: SGs DLC Counter Detail (RMD-4164)

- [ ] 5.3 **TJ-1635 (US 24) — Develop in Sprint 23-24**
  - [ ] 5.3.1 iOS + AOS: Trade ticket changes (TJ-1695)
  - [ ] 5.3.2 iOS + AOS: Order management (TJ-1776)
  - [ ] 5.3.3 iOS + AOS: Watchlist updates (TJ-1906)
  - [ ] 5.3.4 iOS + AOS: Feature flag (TJ-1777)

- [ ] 5.4 **TJ-1773 (HK Advanced Orders) — Develop in Sprint 24-25**
  - [ ] 5.4.1 iOS + AOS: GTC order support (TJ-1904)
  - [ ] 5.4.2 iOS + AOS: GTD order support (TJ-1903)

- [ ] 5.5 **TJ-1960 (Pre-Trade Fees Charges) — Develop in Sprint 26+** (blocked by ITSR approval)
  - [ ] 5.5.1 iOS + AOS: Trade Ticket fee preview
  - [ ] 5.5.2 iOS + AOS: POEMS Calculator pre-trade fees

## Phase 6: Jira Data & Sheet Maintenance

- [ ] 6.1 Verify Jira connectivity: run `jira.jql('project IN (TJ, SR, AM, RMD, AU, GAMI, PWM) AND issuetype = Epic AND key IN (TJ-1635, SR-3588, AM-1244, RMD-4160, AU-348, TJ-1773, TJ-1960, GAMI-1596, SR-3391, TJ-1893, RMD-4148, PWM-1778)')`, confirm all 12 return
- [ ] 6.2 For each of the 12 epics, fetch child issues via `jql('parent = <epic> OR "Epic Link" = <epic>', limit=50)` and count: total children, stories, tasks
- [ ] 6.3 Authenticate to Google Sheets: load service account from `~/.tdt/philip-project-1-496009-aecd4c291640.json`
- [ ] 6.4 Update the "Epic Planning" tab with revised Phase / Sprint Target / Sprint Start / Sprint End columns reflecting 4-phase model
- [ ] 6.5 Add `Phase` column with values: FINISH / DEVELOP / VERIFY / BUFFER / SEPTEMBER+ / TBD
- [ ] 6.6 Add `Sprint Start` and `Sprint End` columns with dates

## Phase 7: Sign-off and Handoff

- [ ] 7.1 Share the updated workbook with all team PLs (read access): Kelvin, Andrew, VuVuong
- [ ] 7.2 Post summary to the sprint channel: "Epic Planning tab updated for v3.3.57 — USSO FINISH Sprint 16, dev Sprints 17-18, verify Sprint 19, release Aug 14 2026"
- [ ] 7.3 Save this OpenSpec change (proposal.md, design.md, tasks.md) to `tdt-meta` repo — commit from `tdt-meta/` directory, not `~/Developer/tdt/`
- [ ] 7.4 Resolve open questions before Sprint 17 kickoff (2026-06-22):
  - [ ] 7.4.1 Backend API owners for SR-3588 (CIS flag + M2) — by 2026-06-15
  - [ ] 7.4.2 CBOE EU feed confirmation for RMD-4148 — by 2026-06-15
  - [ ] 7.4.3 ITSR numbers for TJ-1960 and PWM-1778 — by 2026-06-15
  - [ ] 7.4.4 Chennai QA availability for v3.3.57 — from 2026-07-20 (Sprint 19)

## Phase 8: (Optional) Automation — Epic Planning Refresh Script

- [ ] 8.1 Create `jira-kanban-from-spreadsheet/src/kbs/refresh_epic_planning.py` CLI command: `kbs refresh-epic-planning --spreadsheet-id 1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg --tab "Epic Planning"`
  - Re-fetches all 12 epics from Jira and re-writes the tab, preserving the header structure
  - Supports `--incremental` flag to only update rows whose status changed since last run
- [ ] 8.2 Add `refresh_epic_planning` to the Sprint 17+ cron schedule (every Monday 6 AM)
  - Depends on `jira-kanban-from-spreadsheet` venv; use `UV_PROJECT_ENVIRONMENT=/Users/lekhanhvinh/.tdt/venvs/jira-kanban-from-spreadsheet`

---

## Rollback Plan

- **Tab deletion**: If the "Epic Planning" tab causes issues, any editor can delete it via Sheets UI. All other tabs are unaffected.
- **No Jira changes**: This change only reads from Jira, never writes. No Jira rollback needed.
- **No code changes**: The `refresh_epic_planning` script (task 8) is optional and additive.
- **OpenSpec commit**: If the change artifacts need to be reverted, `git revert` in `tdt-meta/` restores the previous state.

## Dependencies

```
Phase 1 (Sprint 16)  ──→  Phase 2 (Sprint 17-18)  ──→  Phase 3 (Sprint 19)  ──→  Phase 4 (Sprint 20)
FINISH                       DEVELOP                    VERIFY                     BUFFER + RELEASE
   │                            │                           │                          │
   ├─ USSO solution design      ├─ All 7 v3.3.57 epics     ├─ All 7 v3.3.57 SIT        ├─ Bug fix
   ├─ API contracts             ├─ Sprint 17: ~50%         ├─ Regression vs v3.3.55    ├─ UAT sign-off
   ├─ URS gap analysis          ├─ Sprint 18: complete     ├─ Cross-platform parity    ├─ Soft release
   └─ Figma sign-off            └─ Internal verification   └─ Edge cases               └─ Public Release cut
                                                                          2026-08-14
                                                                                ↓
                                                                Phase 5 (Sprint 22+)
                                                                RMD-4148, RMD-4160, TJ-1635,
                                                                TJ-1773, TJ-1960
```

## Key Risks

1. **Backend API SLA**: SR-3588 needs CIS flag + M2 access APIs by 2026-06-19 (Sprint 16 end). If missed, USSO dev blocks at Sprint 17 start.
2. **CBOE EU Feed**: RMD-4148 depends on third-party feed availability — confirm by 2026-06-15.
3. **ITSR Approvals**: TJ-1960 and PWM-1778 use placeholder ITSR numbers. PWM-1778 URS may not be approved for development.
4. **Chennai QA Onboarding**: 7 resources from Chennai on HA+ project through mid-June. Confirm availability for v3.3.57 from 2026-07-20 (Sprint 19 start).
5. **v3.3.54 UAT Carries into Sprint 17**: PUB-39 v3.3.54 UAT regression is high-effort. If not done by 2026-06-19, Sprint 17 has reduced DEV net capacity.
6. **Sprint 18 Overlap Risk**: If 50% of stories don't reach "In QA" by end of Sprint 17, Sprint 18 becomes a continuation of Sprint 17 work, not verification. This shifts the entire timeline by 1 sprint.
7. **Andrew's Team Load**: 4 of the 7 v3.3.57 epics (OOE, CFD, Recurring, SMART) are Andrew's. 560h over 2 sprints is 280h/sprint vs. 311h available per sprint (518h × 0.6). Buffer is only 11% — thin.
