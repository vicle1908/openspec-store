# p3-release-3357-epic-planning

## Purpose

Surface an **Epic Planning** view in the existing Sprint 16 capacity
spreadsheet for the upcoming POEMS Mobile 3 **Public Release 3.3.57** so
that the 12 candidate Epics (across 3 P3 sub-teams + Chennai QA) are
mapped to dev/test effort, URS availability, and sprint windows before
the team enters the release.

## ADDED Requirements

### Requirement: Epic Planning tab is appended to the Sprint 16 capacity workbook

`tdt-sheets` (via `SheetsClient.append_tab`) SHALL add an **Epic
Planning** tab to the workbook with ID
`1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`. The new tab SHALL have
exactly one header row followed by one row per Epic.

#### Scenario: Tab is created with the canonical column header

- **WHEN** the operator runs the bootstrap command for the first time
- **THEN** a tab titled `Epic Planning` is appended
- **AND** the header row contains: `Epic Key, Summary, Team, Sub-team, URS Link, Estimated Children, iOS API h, iOS FE h, Android API h, Android FE h, Sprint Window, Readiness, Notes`

#### Scenario: One row per Epic, sourced from Jira

- **WHEN** the workbook is rebuilt against the live Jira instance
- **THEN** there is exactly one row per Epic across `TJ`, `SR`, `AM`, `RMD`, `AU`, `GAMI`, `PWM`
- **AND** each row is keyed by the Epic's Jira key (e.g. `TJ-1656`)

### Requirement: Readiness status aggregates three boolean checks

Each Epic row SHALL expose a `Readiness` cell whose value is a `+`
where each of the following holds and `-` where it does not:

1. URS document is available and linked
2. P3AP estimation ticket is closed (estimation complete)
3. At least one child story is filed against the Epic

#### Scenario: Ready state is visible at a glance

- **WHEN** an Epic has URS linked, P3AP done, and ≥1 child story
- **THEN** `Readiness` shows `+++`
- **WHEN** only URS is missing
- **THEN** `Readiness` shows `++-`

### Requirement: Effort cells are sourced from Epic descriptions and child stories

For each Epic, the workbook SHALL populate platform-effort cells
(`iOS API h`, `iOS FE h`, `Android API h`, `Android FE h`) using, in
order of preference:

1. The Epic's `P3AP` child estimation tickets (closed or in-progress)
2. The Epic description's hour breakdown
3. A `TBD` placeholder if no source is available

#### Scenario: Estimated Epic populates four numeric columns

- **WHEN** Epic `TJ-1656` (Trade Ticket Revamp) has a closed P3AP with
  iOS=24h API, 32h FE; Android=20h API, 28h FE
- **THEN** `iOS API h=24, iOS FE h=32, Android API h=20, Android FE h=28`

#### Scenario: Unestimated Epic shows TBD placeholders

- **WHEN** Epic has no P3AP and no description hours
- **THEN** all four effort cells display `TBD` (literal string)
- **AND** `Readiness` includes a `-` for the estimation-complete check

### Requirement: Team ownership aligns with the three P3 sub-team capacity bands

Sub-team assignment SHALL follow the canonical mapping established in
the proposal (Kelvin's RMD/AM/TJ/USSO; Andrew's SR/WM/GAMI/FUN;
VuVuong's AU/COM). Cross-team blockers SHALL be flagged in the
`Notes` column with the prefix `BLOCKER:`.

#### Scenario: Cross-team blockers are flagged in the Notes column

- **WHEN** Epic `SR-3588` (USSO Single Ledger) has Phase-1 blockers
  `M2 access control` and `CIS flag API`
- **THEN** its `Notes` cell contains `BLOCKER: M2 access control; CIS flag API`

#### Scenario: Team column matches the canonical owner

- **WHEN** Epic `RMD-1234` is owned by Kelvin's team
- **THEN** `Team=Kelvin, Sub-team=RMD`

### Requirement: Capacity sheet cross-reference flags over-allocation

The Epic Planning tab SHALL include a derived column that cross-references
each Epic's estimated iOS + Android effort against the available Sprint
16 hours on its owning sub-team (read from the existing `Capacity of
Resource` / `Person Capacity` tabs).

#### Scenario: Over-allocated team is highlighted

- **WHEN** a sub-team's total Epic effort exceeds its Sprint 16 capacity
- **THEN** the row's `Notes` cell gains an `OVER-ALLOC:` prefix and the cell colour is set to red

### Requirement: Release grouping separates Aug PR 3.3.57 from downstream

The `Sprint Window` column SHALL resolve to one of:

- `Aug — PR 3.3.57`
- `Sep — follow-on`
- `TBD`

based on the Epic's documented release target.

#### Scenario: Aug-release Epic tagged correctly

- **WHEN** Epic `AM-2031` (Live Positions) is documented to ship in the Aug Public Release 3.3.57
- **THEN** `Sprint Window = Aug — PR 3.3.57`

#### Scenario: Follow-on Epic tagged correctly

- **WHEN** Epic `SR-3588` (USSO Single Ledger) is documented as
  FE-only in PR 3.3.57 with full UMO integration to follow
- **THEN** `Sprint Window = Sep — follow-on`

## MODIFIED Requirements

### Requirement: Sprint 16 capacity workbook gains an `Epic Planning` tab

The Sprint 16 capacity workbook SHALL contain the existing tabs
(`Capacity of Resource`, `Person Capacity`, ...) **plus** a new
`Epic Planning` tab. No existing tab is renamed, removed, or re-ordered.

#### Scenario: Existing tabs remain in place

- **WHEN** the workbook is re-evaluated after this change
- **THEN** all pre-existing tabs are still present
- **AND** the new `Epic Planning` tab is the last in the workbook

## REMOVED Requirements

_(none)_

## Cross-references

- Implementation tracking: `tdt-meta/openspec/changes/p3-release-3357-epic-planning/tasks.md`
- Design notes: `tdt-meta/openspec/changes/p3-release-3357-epic-planning/design.md`
- Sprint 16 workbook: `1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`
- Upstream child ticket work: `tdt-meta/openspec/changes/enhance-sr3588-single-ledger-jira-tasks`
