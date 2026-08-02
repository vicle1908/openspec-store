# Jira Epic Report Presentation Enhancement - Proposal

**Status:** Draft
**Date:** 2026-06-02
**Author:** Kiro (AI Analysis)
**Change:** jira-epic-report-presentation-enhancement
**Version:** 1.2 (consolidated scope)

---

## Why

Current jira-epic-report presentation (v2.1) collects `blocked_by` relationships from Jira but does not compute reverse relationships (`blocks`) or visualize dependency chains. The existing `EscalationDetector.analyze_blocker_chain()` analysis is unused in reports. Users cannot see blocking chains, root cause blockers, or impact radius when items are unblocked. This makes it difficult to prioritize work, understand sprint risks, and identify which blockers to address first. Teams waste time manually tracing dependencies in Jira instead of seeing them directly in reports.

## What Changes

- **Add reverse blocking relationship** — Compute `blocks` field for all Task/WorkItem models (reverse of `blocked_by`)
- **Blocker chain visualization** — New report sections showing root blockers, blocked items with chain depth, and dependency trees
- **Grouped presentation** — Split items by blocking status: Root Blockers, Blocked Items (waiting), Ready to Work (no blockers)
- **Impact radius calculation** — Show how many items (direct + transitive) each blocker affects
- **Enhanced sprint report** — Add "Blocking Status & Dependencies" section to existing sprint_reporter.py
- **Enhanced dashboard** — Add "Dependency Graph" section to existing dashboard/reporter.py
- **Enhanced spreadsheet export** — Add "Blocking Dependencies" tab to existing Google Sheets export via gws CLI
- **Blocker analysis integration** — Use existing `EscalationDetector.analyze_blocker_chain()` in reports instead of ignoring it

All changes are **additive** — no breaking changes to existing reports. New sections added, existing sections preserved.

## Capabilities

### New Capabilities

- `blocking-dependency-tracking`: Track reverse blocking relationships (`blocks` field), compute impact radius (transitive blocked count), calculate chain depth, identify root blockers (items that block others but aren't blocked themselves)

- `dependency-visualization`: ASCII tree rendering of blocking chains, grouped tables by blocking status (root/blocked/ready), impact radius display ("blocks 12 items"), chain depth indicators (direct/indirect/multi-blocked)

- `enhanced-report-sections`: New sprint report section "Blocking Status & Dependencies" with Root Blockers table, Blocked Items table, Ready to Work table. New dashboard section "Dependency Graph" with ASCII tree per root blocker. Enhanced assignee workload tables with blocker/blocked counts.

- `spreadsheet-export-enhancement`: Add "Blocking Dependencies" tab to existing Google Sheets export via gws CLI. Add blocking columns to existing tabs (Epic Overview, per-epic, Risks). Embed Google Sheets formulas for automatic calculations. Add conditional formatting and filter views.

### Modified Capabilities

- `epic-data-collection`: Add `_build_reverse_blocking_map()` post-processing step to compute `blocks` field after task collection. Add `blocker_chain_depth` and `impact_radius` computed fields to Task/WorkItem models (requires analysis integration).

- `report-generation`: Integrate `EscalationDetector.analyze_blocker_chain()` results into markdown/HTML/spreadsheet reporters. Add new report sections for blocking status. Enhance sprint report and dashboard with blocking context. No changes to existing sections (additive only).

## Impact

**Code Changes:**

- `epic_report/models.py` — Add `blocks`, `blocker_chain_depth`, `impact_radius` fields to Task/WorkItem
- `epic_report/collector.py` — Add `_build_reverse_blocking_map()` post-processing
- `epic_report/analyzers/blocking.py` — New analyzer using existing `EscalationDetector.analyze_blocker_chain()`
- `epic_report/reporters/sprint_reporter.py` — Add "Blocking Status" section (3 tables)
- `epic_report/dashboard/reporter.py` — Add "Dependency Graph" section (ASCII tree)
- `epic_report/reporters/spreadsheet_reporter.py` — Add "Blocking Dependencies" tab and blocking columns to existing tabs

**API Compatibility:**

- No breaking changes — all new fields have defaults
- Existing CLI commands unchanged
- Existing report sections preserved
- New sections added at end

**Dependencies:**

- No new external dependencies
- Uses existing `EscalationDetector` from `analyzers/escalation.py`
- Uses existing `gws` CLI for Google Sheets (already in use)

**Testing Impact:**

- Add tests for reverse blocking map computation (~15 tests)
- Add tests for new report sections (~20 tests)
- Add tests for spreadsheet export enhancement (~10 tests)
- Estimated: +45 tests, maintain >80% coverage

**User Impact:**

- Immediate value: Users can now see "PDS-100 blocks 12 items" and prioritize accordingly
- Sprint reports show which blockers cause the most risk
- Dashboard shows full dependency chains for root cause analysis
- Spreadsheet export provides blocking data in Google Sheets for team collaboration
- No migration needed — new features available immediately on next report generation

## Out of Scope

- **Person Capacity enhancement** — Already implemented in jira-daily-reports project (complete)
- **Excel/openpyxl export** — Existing codebase uses Google Sheets via gws CLI, not Excel
- **Interactive HTML dependency graphs (D3.js)** — Deferred to future (Phase 3)
- **Blocker resolution time estimation** — Requires historical data not yet collected
- **Real-time updates** — Reports remain snapshot-based
- **Modifying existing report sections** — All changes are additive
