# Proposal: P3 Mobile Release 3.3.57 — Epic Planning & Sprint Capacity Alignment

## Why

The P3 Mobile team (iOS + Android) is preparing for **Release 3.3.57**, which consolidates 12 Jira Epics across 5 sub-teams (Kelvin's, Andrew's, VuVuong's, plus Chennai QA). These epics span the full POEMS Mobile 3 feature surface — from trading workflow (HK Advanced Orders, US 24, USSO Single Ledger) to portfolio UX (Live Positions, SMART Portfolio Revamp) to platform improvements (DLC Visibility, Transaction Notifications, OOE, CFD Market Discovery). The current sprint capacity sheet (`Sprint 16 - 08 Jun - 19 Jun`) is overloaded with v3.3.54 UAT regression work (288h iOS / 288h AOS / 864h QA per PUB-39 alone), leaving ambiguous room for v3.3.57 development. This change produces an **Epic Planning tab** in the capacity sheet and a structured sprint roadmap to align dev/test effort against the 12 epics.

## What Changes

- **Create an "Epic Planning" tab** in the Sprint 16 capacity spreadsheet (`1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`) with one row per Epic:
  - Jira key, summary, team owner, URS link, estimated children breakdown
  - Per-platform effort (iOS/Android API + FE hours) — sourced from Epic descriptions, child stories, and P3AP estimation tickets
  - Sprint window targeting (Aug release, Sep release, or TBD)
  - Readiness status: URS available, Estimation complete (P3AP done), Children broken down
- **Align epic team ownership** with the 3 sub-team capacity bands:
  - Kelvin's team (RMD, AM, TJ, USSO): Live Positions, HK Advanced Orders, Pre-Trade Fees, USSO Single Ledger, US 24, DLC Visibility, CBOE GY/UK
  - Andrew's team (SR, WM, GAMI, FUN): CFD Market Discovery, SMART Portfolio Revamp, OOE, Recurring Order Plan
  - VuVuong's team (AU, COM): Transaction Notifications
- **Flag cross-team blockers**: USSO Single Ledger (SR-3588) has Phase 1 blockers (M2 access control + CIS flag API); OOE (GAMI-1596) blocks the larger P3AP-1152 project
- **Track release grouping**: Public Release 3.3.57 (Aug) vs. subsequent releases

## Capabilities

### New Capabilities

- `epic-planning-tab`: A structured Google Sheets tab (attached to the Sprint 16 capacity workbook) that maps all 12 v3.3.57 epics to team ownership, URS links, child story counts, effort estimates, and sprint targets. One row per Epic, updated weekly.
- `epic-release-roadmap`: A release grouping that separates the Public Release 3.3.57 epics (Aug) from downstream epics (Sep), accounting for the USSO FE-only vs. full UMO integration scope.
- `capacity-sprint-alignment`: Cross-reference between the Epic Planning tab and the existing `Capacity of Resource` / `Person Capacity` tabs to surface over/under-allocation.

### Modified Capabilities

_(none — this change is planning-only; no existing spec requirements change)_

## Impact

### Affected Systems

- **Jira**: Reads 12 Epics (TJ, SR, AM, RMD, AU, GAMI, PWM projects) and their child stories via `tdt_core.clients.jira.JiraClientFactory`
- **Google Sheets**: Writes a new "Epic Planning" tab to Sprint 16 workbook `1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg` via `tdt_sheets.SheetsClient`
- **OpenSpec**: Creates change `p3-release-3357-epic-planning` as the living artifact for this release's epic planning

### Dependencies

- Sprint 16 capacity spreadsheet: `https://docs.google.com/spreadsheets/d/1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`
- Existing `enhance-sr3588-single-ledger-jira-tasks` change (SR-3588 child tasks enhancement)
- URS links per Epic (all 12 extracted — see design.md)

### New Dependencies

- None anticipated for the planning phase

## Non-Goals

- This change does NOT create or modify any Jira sub-tasks under the 12 epics
- This change does NOT implement any feature in poems-mobile3-ios or poems-mobile3-android
- This change does NOT produce URS documents or Figma designs
- This change does NOT assign story points or sprint capacity beyond what is already in the capacity sheet

## Epic Summary

| # | Jira Key | Project | Summary | Team | Priority | Status | URS |
|---|----------|---------|---------|------|----------|--------|-----|
| 1 | TJ-1635 | TJ | US 24 | Kelvin | High | To Do | SharePoint |
| 2 | SR-3588 | SR | USSO Single Ledger | Kelvin | High | To Do | SharePoint |
| 3 | AM-1244 | AM | Live Positions | Kelvin | High | In Progress | SharePoint |
| 4 | RMD-4160 | RMD | DLC Visibility | Kelvin | High | To Do | SharePoint |
| 5 | AU-348 | AU | Transaction Notifications | VuVuong | Medium | TO DO | SharePoint |
| 6 | TJ-1773 | TJ | HK Advanced Orders | Kelvin | High | To Do | SharePoint |
| 7 | TJ-1960 | TJ | Pre-Trade Fees Charges | Kelvin | Medium | To Do | SharePoint |
| 8 | GAMI-1596 | GAMI | Offline Online Experience (OOE) | Andrew | Medium | To Do | SharePoint |
| 9 | SR-3391 | SR | CFD Market Discovery Page | Andrew | Medium | To Do | SharePoint |
| 10 | TJ-1893 | TJ | Recurring Order Plan Enhancements | Andrew | Medium | To Do | SharePoint |
| 11 | RMD-4148 | RMD | GY, UK - Switch Feed to CBOE EU Sources | Kelvin | Medium | In Progress | SharePoint |
| 12 | PWM-1778 | PWM | SMART Portfolio Revamp New | Andrew | Medium | To Do | SharePoint |

## Release Grouping (4-Phase Model)

### Sprint Calendar (2-week sprints, 10 workdays/sprint)

| Sprint | Dates | Workdays | Phase | Focus |
|--------|-------|----------|-------|-------|
| 16 | 2026-06-08 → 2026-06-19 | 10 | FINISH | USSO solution design + CIS flag + M2 access; v3.3.54 UAT regression |
| 17-18 | 2026-06-22 → 2026-07-17 | 20 | DEVELOP | All v3.3.57 epics coding + unit tests + internal verification |
| 19 | 2026-07-20 → 2026-07-31 | 10 | VERIFY | SIT, regression, UAT readiness |
| 20 | 2026-08-03 → 2026-08-14 | 10 | BUFFER + RELEASE | Bug fix, soft release, UAT, **Public Release 3.3.57 cut (2026-08-14)** |
| 22+ | 2026-08-31+ | 10/sprint | SEPTEMBER+ | Defer RMD-4148, RMD-4160, TJ-1635, TJ-1773, TJ-1960 |

### Why 4 phases, not 3

The original 3-phase plan (Finish + Develop + Verify in 3 sprints) was too tight because:
- Each sprint is **10 workdays**, not 14. Each dev has 80h/sprint of available time.
- Sprint 16 is already loaded with v3.3.54 UAT regression (PUB-39 = 576h) + v3.3.55 biometric work (VuVuong 176h).
- Total v3.3.57 feature work = 1358h. Need 2 dedicated 10-day sprints (1818h available, 25% buffer) — not 1.
- Verification needs its own sprint (Sprint 19). Combined dev+verify in 2 sprints creates the "throw-it-over-the-wall" anti-pattern.

### Public Release 3.3.57 (Aug 2026)

**FINISH (Sprint 16) → DEVELOP (Sprint 17-18) → VERIFY (Sprint 19) → BUFFER + RELEASE (Sprint 20)**

| Epic | Team | Stories | Effort (h) | Sprint 16 | Sprint 17-18 | Sprint 19 | Sprint 20 |
|------|------|---------|------------|-----------|--------------|-----------|-----------|
| **SR-3588** USSO Single Ledger | Kelvin | 20 | 320 | **FINISH** | DEVELOP | VERIFY | Bug fix |
| **AM-1244** Live Positions | Kelvin | 8 | 128 | (in prog) | DEVELOP | VERIFY | Bug fix |
| **AU-348** Transaction Notifications | VuVuong | 29 | 350 | setup | DEVELOP | VERIFY | Bug fix |
| **GAMI-1596** OOE | Andrew | 2 | 48 | — | DEVELOP | VERIFY | Bug fix |
| **SR-3391** CFD Market Discovery | Andrew | 50 | 200 | — | DEVELOP | VERIFY | Bug fix |
| **TJ-1893** Recurring Order Plan | Andrew | 9 | 144 | — | DEVELOP | VERIFY | Bug fix |
| **PWM-1778** SMART Portfolio Revamp | Andrew | 7 | 168 | — | DEVELOP | VERIFY | Bug fix |

### Per-Team Load Check (Sprint 17-18 combined)

| Team | v3.3.57 Effort (h) | Available (S17-18) | Buffer |
|------|--------------------|---------------------|--------|
| **Kelvin** | 448h | 1152h (576h × 2) | 704h / 61% |
| **Andrew** | 560h | 1036h (518h × 2) | 476h / 46% |
| **VuVuong** | 350h | 844h (422h × 2) | 494h / 59% |
| **TOTAL** | 1358h | 3032h | 1674h / 55% |

### September Release (post-Aug)

| Epic | Team | Sprint 22 | Sprint 23 | Sprint 24+ |
|------|------|-----------|-----------|------------|
| **RMD-4148** CBOE GY/UK | Kelvin | DEVELOP (continues) | VERIFY | Bug fix |
| **RMD-4160** DLC Visibility | Kelvin | DEVELOP | VERIFY | Bug fix |
| **TJ-1635** US 24 | Kelvin | — | DEVELOP | VERIFY |
| **TJ-1773** HK Advanced Orders | Kelvin | — | DEVELOP | VERIFY |
| **TJ-1960** Pre-Trade Fees | Kelvin | — | — | DEVELOP (ITSR-blocked) |

### Capacity Allocation Per Sprint

Each sub-team's capacity is split into 3 lanes:

| Lane | % Capacity | Purpose |
|------|-----------|---------|
| **Feature Development** | 60% | Story implementation per Epic |
| **Tech Tasks + Dependencies** | 25% | API contracts, feature flags, performance, build, dev tools, dependency upgrades |
| **Buffer (incidents, ad-hoc, learning)** | 15% | Production bugs, code review, tech training, meetings |

**Per-sprint DEV net (10 workdays):** Kelvin 576h, Andrew 518h, VuVuong 422h. **Total 1516h/sprint** = 909h available for feature dev after 40% overhead.
