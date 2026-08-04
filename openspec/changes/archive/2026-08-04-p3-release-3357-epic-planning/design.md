# Design: P3 Mobile Release 3.3.57 — Epic Planning & Sprint Capacity Alignment

## Context

The P3 Mobile team operates across two platforms (iOS + Android) and three sub-teams (Kelvin's, Andrew's, VuVuong's) with a shared Chennai QA pool. **Release 3.3.57** consolidates 12 Jira Epics into a coordinated release plan. The existing Sprint 16 capacity spreadsheet (`1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`) has the infrastructure for capacity tracking (`Capacity of Resource`, `Person Capacity`) and sprint reporting (`Sprint Report`, `Bucket (New Feature)`), but lacks a dedicated **Epic Planning** view that maps:

- Each Epic to its team owner and sub-team capacity band
- URS document links and readiness state
- Child story breakdown and platform effort estimates
- Sprint window assignment (FINISH / DEVELOP / VERIFY phases) with explicit dates
- Cross-team blockers and dependencies
- Tech-tasks and API-dependency buffer lanes

The release plan is structured as **4 phases × 2-week sprints**, with each phase having a distinct goal. Each sprint is **10 workdays (5 workdays × 2 weeks)**, not 2 full weeks of dev time:

1. **FINISH (Sprint 16: 2026-06-08 → 2026-06-19)**: Lock down solution design, API contracts, and URS gaps. USSO Single Ledger is the focus. Limited capacity (~50h/team) due to v3.3.54 UAT regression (PUB-39, 576h) and v3.3.55 biometric work competing.
2. **DEVELOP (Sprints 17-18: 2026-06-22 → 2026-07-17)**: Code, unit test, and internal verification of all v3.3.57 epics. Two full sprints because 1358h of feature work cannot fit in a single 10-day sprint.
3. **VERIFY (Sprint 19: 2026-07-20 → 2026-07-31)**: SIT, regression, UAT readiness. Dedicated sprint (not overlap with dev) so QA can complete full coverage.
4. **BUFFER + RELEASE (Sprint 20: 2026-08-03 → 2026-08-14)**: Final bug fix, soft release, UAT sign-off, **Public Release 3.3.57 cut on 2026-08-14**.
5. **SEPTEMBER+ (Sprint 22+)**: Defer epics to next release cycle (TJ-1635, RMD-4160, TJ-1773, TJ-1960, RMD-4148). RMD-4148 was already in progress and continues; the others start fresh.

## Goals / Non-Goals

**Goals:**
- Provide a single source of truth in the Sprint 16 workbook for all 12 v3.3.57 Epic readiness
- Align Epic ownership with the 3 sub-team capacity bands visible in `Capacity of Resource`
- Surface URS document availability and estimation completion per Epic
- Enable sprint-over-sprint tracking of Epic progress toward release
- Anchor the release grouping (Public Release 3.3.57 in Aug vs. downstream)

**Non-Goals:**
- This does NOT create or modify Jira sub-tasks under the 12 Epics
- This does NOT produce implementation code in poems-mobile3-ios or poems-mobile3-android
- This does NOT reassign team ownership — ownership is derived from Epic reporter + current sprint bucket assignments
- This does NOT replace the `Bucket (New Feature)` tab — the Epic Planning tab is additive, focused on the planning horizon

## Decisions

### Decision 1: Additive Tab vs. In-Place Addition

**Choice:** Add a new tab "Epic Planning" to the existing Sprint 16 workbook, not modify existing tabs.

**Rationale:**
- The `Bucket (New Feature)` tab is already at capacity with ~50 rows and is used by PMs for sprint planning. Augmenting it would risk breaking existing formulas.
- A separate tab keeps the Epic Planning view self-contained and easy to archive at sprint-end.
- The Epic Planning tab is readable by the same stakeholders (PM, PL, QA) who use the existing tabs.

**Alternatives considered:**
- Adding columns to `Bucket (New Feature)` — rejected; that tab is Jira-key-centric (individual ticket rows), not Epic-centric (group rows).
- Creating a separate workbook — rejected;分散es the source of truth and requires stakeholders to check two sheets.

---

### Decision 2: Manual Refresh from Jira via Agent, Not Auto-Sync

**Choice:** The Epic Planning tab is refreshed manually (agent-assisted) rather than auto-synced via Apps Script or API polling.

**Rationale:**
- Jira data (child stories, status, assignee) changes frequently during a sprint. Auto-sync would create churn in the sheet.
- The tab is primarily a **planning artifact** — it records the planned state at sprint planning time, not the live execution state (which `Sprint Report` covers).
- Agent-assisted refresh (this agent, on-demand) is consistent with how the team already uses the Sprint 16 workbook — it is a living document updated by the operator.
- Apps Script API polling adds fragility (Jira auth token expiry, quota limits) with little benefit for a planning artifact.

**Alternatives considered:**
- Apps Script with time-driven triggers — rejected; Jira OAuth token management is complex and the sheet is operator-maintained, not auto-pushed.
- Daily `jira-skill` pipeline write-back — rejected for same reason; `jira-skill analyze-filter` is for intelligence analysis, not capacity planning.

---

### Decision 3: One Row Per Epic, Not Per Story

**Choice:** The Epic Planning tab has one row per Epic, with effort and children columns aggregated, rather than one row per child story.

**Rationale:**
- The target audience (PM + PL leads) needs a **release-level** view, not a sprint-level story list.
- Sprint-level story tracking already lives in `Sprint Report` and `RawData`.
- The Epic Planning tab answers "where are we on the 12 epics" not "which stories are in today's sprint".
- Aggregation keeps the tab compact (12 rows + header) and scannable.

**Alternatives considered:**
- One row per child story — rejected; would produce ~100+ rows, defeating the purpose of a release overview.
- Drill-down with grouping — rejected; Google Sheets grouping is fragile across collaborators.

---

### Decision 4: Effort Estimates from P3AP Estimation Tickets + Epic Child Stories

**Choice:** Platform effort (iOS hours, AOS hours) is sourced from the P3AP estimation ticket comments where available, supplemented by Epic child story counts.

**Rationale:**
- The `ForEstimation` label on all 12 Epics indicates a paired `P3AP-xxxx` estimation ticket exists. These tickets contain the actual hour estimates from the team.
- Child story counts serve as a proxy for effort complexity when P3AP comments are unavailable.
- Story point estimates from `RawData` are unreliable (only 10.7% coverage per Sprint Report) so they are not used directly.

**Data sources in priority order:**
1. P3AP estimation ticket (e.g., P3AP-1064 for HK Advanced Orders) — contains PM-provided hours
2. Epic child story count × average story weight (use 8h/story as a conservative default)
3. Epic description text (for URS scope)

---

### Decision 5: Release Grouping as a Column, Not Separate Tabs

**Choice:** Release grouping (Public 3.3.57 / Sep / TBD) is a column in the Epic Planning tab, not separate sub-tabs.

**Rationale:**
- A single tab with a filter/sort by release group is more usable than navigating multiple tabs.
- Google Sheets built-in filter views allow each stakeholder to focus on their team's epics without creating tab sprawl.
- The column approach is consistent with how `Bucket (New Feature)` already has a `Target version` column.

---

## Epic Planning Tab Structure

**Sheet name:** `Epic Planning`

| Column | Header | Source / Logic |
|--------|--------|----------------|
| A | `Epic Key` | Direct from Epic Jira key (e.g., TJ-1635) |
| B | `Summary` | Epic summary (from Jira) |
| C | `Team` | Kelvin's / Andrew's / VuVuong's |
| D | `Platform` | iOS + AOS / P2+P3 / etc. |
| E | `Priority` | High / Medium (from Jira priority field) |
| F | `Status` | Jira status (To Do / In Progress / Done) |
| G | `Release Group` | Public 3.3.57 (Aug) / Sep+ / TBD |
| H | `Phase` | **FINISH / DEVELOP / VERIFY / BUFFER / SEPTEMBER+ / TBD** |
| I | `Sprint Target` | e.g., "Sprint 17", "Sprint 21" |
| J | `Sprint Start` | Date — first day of sprint |
| K | `Sprint End` | Date — last day of sprint |
| L | `URS Link` | SharePoint URL extracted from Epic description |
| M | `URS Available` | Yes / No / Partial (URS present but ITSR placeholder) |
| N | `P3AP Estimation` | Yes / Partial / No |
| O | `Children (Total)` | Count of Jira child issues (stories + tasks) |
| P | `Children (Stories)` | Count of child stories only |
| Q | `Children (Tasks)` | Count of child tasks only |
| R | `Est iOS Hours` | Estimated iOS effort (from P3AP or child stories × 8h) |
| S | `Est AOS Hours` | Estimated AOS effort |
| T | `Est QA Hours` | Estimated QA effort (verification phase) |
| U | `Key Blocker` | Critical blocker description or "None" |
| V | `Figma Link` | Figma URL from Epic description |
| W | `PC Case Link` | Phillip Connect case URL |
| X | `Notes` | Planning notes: e.g., "URS placeholder [XXXX]", "P3AP blocked by backend", "Phase 1 only" |

---

## Sprint Calendar (2-week sprints, 5 workdays/week = 10 workdays/sprint)

| Sprint | Start | End | Workdays | Phase | Goals |
|--------|-------|-----|----------|-------|-------|
| 16 | 2026-06-08 | 2026-06-19 | 10 | FINISH | v3.3.54 UAT regression (PUB-39) + USSO Single Ledger solution design, CIS flag contract, M2 access control + v3.3.55 biometric SIT |
| 17 | 2026-06-22 | 2026-07-03 | 10 | DEVELOP (1/2) | All v3.3.57 epics coding start; ~50% stories reach "In QA" by end |
| 18 | 2026-07-06 | 2026-07-17 | 10 | DEVELOP (2/2) | Coding complete + dev internal verification; all stories to "In QA" by end |
| 19 | 2026-07-20 | 2026-07-31 | 10 | VERIFY | SIT, regression, UAT readiness, cross-platform parity |
| 20 | 2026-08-03 | 2026-08-14 | 10 | BUFFER + RELEASE | Bug fix, soft release, UAT sign-off, **Public Release 3.3.57 cut (2026-08-14)** |
| 21 | 2026-08-17 | 2026-08-28 | 10 | BUFFER | Post-release monitoring + Sep planning |
| 22+ | 2026-08-31+ | TBD | 10/sprint | SEPTEMBER+ | Defer epics: RMD-4160, TJ-1635, TJ-1773, TJ-1960, RMD-4148 |

> **Why 4 phases, not 3:**
> 1. **10 workdays/sprint, not 14.** Each dev has 80h/sprint of available time. The original 3-phase plan (Finish + Develop + Verify in 3 sprints) packed too much work into Sprint 16 (which is already loaded with v3.3.54 UAT).
> 2. **v3.3.57 effort = 1358h feature dev + 650h QA verification.** Two 10-day sprints of development (1818h available after 40% overhead) cover this with 25% buffer.
> 3. **Verification needs its own sprint.** Combined dev+verify in 2 sprints creates the "throw-it-over-the-wall" anti-pattern; QA starts late and has no time for proper cross-platform parity.

## Capacity Per Sprint (10 workdays × 8h)

| Team | Gross | Fixed Deductions | Total Net | DEV Ratio | DEV Net | QA Net |
|------|-------|------------------|-----------|-----------|---------|--------|
| **Kelvin** | 924h | 60h | 864h | 67% (8 dev / 12 total) | **576h** | 288h |
| **Andrew** | 800h | 60h | 740h | 70% (7 dev / 10 total) | **518h** | 222h |
| **VuVuong** | 622h | 60h | 562h | 75% (6 dev / 8 total) | **422h** | 140h |
| **TOTAL** | 2346h | 180h | 2166h | — | **1516h** | **650h** |

**Fixed deductions per sprint:** Adhoc (30h) + Other meeting (20h) + AI study (10h) = **60h/team/sprint**.

**After 25% tech-tasks lane + 15% buffer lane:** 1516h × 0.60 = **909h available per sprint for feature dev**.

## Per-Epic Sprint Mapping (v3.3.57 Public Release — Aug 2026)

| Epic | Team | Stories | Effort (h) | Sprint 16 | Sprint 17-18 | Sprint 19 | Sprint 20 |
|------|------|---------|------------|-----------|--------------|-----------|-----------|
| **SR-3588** USSO Single Ledger | Kelvin | 20 | 320 | **FINISH** | DEVELOP | VERIFY | Bug fix |
| **AM-1244** Live Positions | Kelvin | 8 | 128 | (in prog) | DEVELOP | VERIFY | Bug fix |
| **AU-348** Transaction Notifications | VuVuong | 29 | 350 | setup | DEVELOP | VERIFY | Bug fix |
| **GAMI-1596** OOE | Andrew | 2 | 48 | — | DEVELOP | VERIFY | Bug fix |
| **SR-3391** CFD Market Discovery | Andrew | 50 | 200 | — | DEVELOP | VERIFY | Bug fix |
| **TJ-1893** Recurring Order Plan | Andrew | 9 | 144 | — | DEVELOP | VERIFY | Bug fix |
| **PWM-1778** SMART Portfolio Revamp | Andrew | 7 | 168 | — | DEVELOP | VERIFY | Bug fix |
| **TOTAL** | — | **125** | **1358h** | — | — | — | — |

## Per-Team Load Check (Sprint 17-18 combined, 2 sprints)

| Team | v3.3.57 Effort (h) | Available (S17-18) | Buffer |
|------|--------------------|---------------------|--------|
| **Kelvin** | 448h (USSO 320 + AM 128) | 1152h (576h × 2) | **704h / 61%** |
| **Andrew** | 560h (OOE + CFD + Recurring + SMART) | 1036h (518h × 2) | **476h / 46%** |
| **VuVuong** | 350h (AU-348) | 844h (422h × 2) | **494h / 59%** |
| **TOTAL** | 1358h | 3032h | **1674h / 55%** |

> **Verdict:** 55% total buffer across all teams, but Andrew's team is the bottleneck at 46% buffer (4 of 7 v3.3.57 epics). If any of Andrew's 4 epics slips, the timeline tightens.

## Per-Epic Sprint Mapping (September+ — Sprint 22+)

> These epics are deferred from v3.3.57 because they would have made the August cut infeasible.

| Epic | Team | Stories | Effort (h) | Sprint 22 | Sprint 23 | Sprint 24+ |
|------|------|---------|------------|-----------|-----------|------------|
| **RMD-4148** CBOE GY/UK | Kelvin | 9 | ~120 | DEVELOP (continues) | VERIFY | Bug fix |
| **RMD-4160** DLC Visibility | Kelvin | 6 | ~80 | DEVELOP | VERIFY | Bug fix |
| **TJ-1635** US 24 | Kelvin | 6 | ~80 | — | DEVELOP | VERIFY |
| **TJ-1773** HK Advanced Orders | Kelvin | 4 | ~50 | — | DEVELOP | VERIFY |
| **TJ-1960** Pre-Trade Fees | Kelvin | 1 | TBD | — | — | DEVELOP (ITSR-blocked) |

---

## Per-Epic Data Sheet (Epic Detail Annex)

For epics with significant complexity, a second section ("Epic Detail Annex") on the same tab provides:

| Column | Header | Notes |
|--------|--------|-------|
| A | `Child Key` | Direct Jira key of child story/task |
| B | `Parent Epic` | Maps to Epic Key |
| C | `Child Summary` | From Jira |
| D | `Type` | Story / Task / Sub-task |
| E | `Status` | Current Jira status |
| F | `iOS Hours` | Estimated (from `RawData` story points × 1h/point if available) |
| G | `AOS Hours` | Same |
| H | `QA Hours` | Same |
| I | `Feature Flag?` | Yes / No |
| J | `API Dependency?` | Backend API needed? |

This annex is collapsible to keep the main Epic view clean.

---

## Risks / Trade-offs

### Risk: SR-3588 FINISH Phase Must Complete by 2026-06-19

**[Risk]** USSO Single Ledger (SR-3588) has 5 Phase 1 blockers that must be closed by end of Sprint 16: CIS Flag API contract, M2 Platform Access Control, Options Activation Flow design, Realized P/L Merged View Figma, Error Handling patterns. Without these, DEVELOP phase (Sprint 17) cannot start cleanly and all 20 subtasks stall.

**[Mitigation]** SR-3588 FINISH phase is the priority for Kelvin's team in Sprint 16. 25% tech-tasks lane of Kelvin's DEV capacity is reserved for CIS flag contract work. Escalate to backend team by 2026-06-15 if M2 access logic is not aligned.

### Risk: v3.3.54 UAT Regression Eats Sprint 16 Capacity

**[Risk]** Sprint 16 already allocates 288h iOS + 288h AOS + 864h QA to PUB-39 (v3.3.54 UAT regression) and 200h each for PUB-45 (Beta regression). This consumes Kelvin's team DEV net (514.67h) significantly, leaving less room for SR-3588 FINISH.

**[Mitigation]** The 15% buffer lane absorbs UAT regression overflow. If PUB-39 extends into Sprint 17, USSO FINISH extends by 1 week (dev starts 2026-06-29, ends 2026-07-10).

### Risk: Backend API SLA for Sprint 17 Start (2026-06-22)

**[Risk]** Multiple epics depend on backend APIs that must be ready by Sprint 17 start: CIS flag (SR-3588), M2 access control (SR-3588), real-time positions API (AM-1244), CBOE EU feed (RMD-4148), BO pre-trade fees (TJ-1960).

**[Mitigation]** Tech-tasks lane (25% of DEV capacity) absorbs the API dependency tracking. Each team PL has explicit API-ready check in their Sprint 17 kickoff. If an API is not ready, the affected Epic moves to Sprint 18 and the team reassigns to another Epic.

### Risk: CBOE EU Feed (RMD-4148) — Third-Party Dependency

**[Risk]** GY, UK - Switch Feed to CBOE EU Sources (RMD-4148) requires CBOE EU to provide a price feed for German and UK markets. If CBOE doesn't have coverage, the epic scope changes.

**[Mitigation]** Mark `Key Blocker` as "CBOE EU feed availability" for RMD-4148. Coordinate with product to get CBOE confirmation by 2026-06-15. RMD-4148 is on the September release track (Sprint 21+), giving more time.

### Risk: TJ-1960 and PWM-1778 URS Have ITSR Placeholders

**[Risk]** TJ-1960 (Pre-Trade Fees) and PWM-1778 (SMART Portfolio Revamp) URS documents use placeholder ITSR numbers (`[XXXX]`, `[1234]`). These URS may not be approved for development.

**[Mitigation]** Mark `URS Available` as "Partial" for these two epics. PWM-1778 is on v3.3.57 track (Sprint 17-18) — escalate ITSR approval to BA/PM by 2026-06-15. TJ-1960 is on September track — extra time to resolve.

### Risk: OOE (GAMI-1596) Blocks Larger Project

**[Risk]** GAMI-1596 is a sub-epic that blocks P3AP-1152 (the full Online Offline Experiences project). Starting OOE late risks delaying P3AP-1152.

**[Mitigation]** GAMI-1596 starts DEVELOP phase in Sprint 17 (2026-06-22) and finishes in Sprint 18. Plan team assigns 1 dev + 1 QA dedicated to OOE.

### Risk: Chennai QA Onboarding for v3.3.57

**[Risk]** 7 Chennai QA resources are on the HA+ project through mid-June. They need to be on-boarded to v3.3.57 epics by Sprint 18 (2026-07-06) for VERIFY phase. Onboarding takes ~3 days for context switch.

**[Mitigation]** Start Chennai QA onboarding in Sprint 17 (2026-06-22) with parallel learning (URS reading, Figma review). Have them shadow Kelvin/Andrew QAs during Sprint 17.

---

## Migration Plan

### Tab Creation

1. Agent (this process) reads all 12 Epics via `tdt_core.clients.jira.JiraClientFactory`
2. Agent fetches child stories/tasks per Epic via `jql('parent = <epic>')`
3. Agent writes the "Epic Planning" tab to the Sprint 16 workbook via `gspread` (service account auth using `GOOGLE_SERVICE_ACCOUNT_PATH`)
4. Tab is shared with the same editors as the existing Sprint 16 workbook

### Sprint-End Archive

- At sprint-end (Sprint 16 = 19 Jun), the Epic Planning tab is archived by copying the workbook and appending `_sprint16_archive` to the sheet title
- A fresh Epic Planning tab for Sprint 17 is created with updated Jira data

### Rollback

- If the Epic Planning tab is not used, it can be deleted without affecting other tabs
- The `Capacity of Resource`, `Person Capacity`, `Sprint Report` tabs are untouched

---

## Open Questions

1. **Backend API Owners for SR-3588:** Who owns the CIS flag API and M2 access control contracts? Need backend PL assignment **by 2026-06-15** before Sprint 16 ends.
2. **CBOE EU Feed Confirmation:** Has CBOE confirmed they can provide price feeds for GY and UK markets? Need confirmation **by 2026-06-15** to confirm RMD-4148 Sep release commitment.
3. **OOE Scope Finalization:** The GAMI-1596 URS covers "OOE Journey Criteria" and "Coin History Pagination" — are there additional OOE screens planned under P3AP-1152? Need PM clarification **by 2026-06-19** to finalize Sprint 17 plan.
4. **TJ-1960 ITSR Approval:** When will the ITSR for Pre-Trade Fees Charges (TJ-1960) be formally raised and approved? URS is ready but has placeholder reference. Need approval **by 2026-08-01** for Sprint 23 start.
5. **PWM-1778 ITSR Number:** SMART Portfolio Revamp New (PWM-1778) ITSR is `[XXXX]` — when will this be assigned? Affects development start date. Need assignment **by 2026-06-15** for Sprint 17 plan.
6. **Chennai QA Onboarding Date:** When do 7 Chennai QA resources complete HA+ project? Need availability from **2026-07-06** (Sprint 18 start) for VERIFY phase.
7. **v3.3.54 UAT Regression Status:** Will PUB-39 v3.3.54 UAT regression complete by 2026-06-19? If not, USSO FINISH extends and Sprint 17 dev start slips.
