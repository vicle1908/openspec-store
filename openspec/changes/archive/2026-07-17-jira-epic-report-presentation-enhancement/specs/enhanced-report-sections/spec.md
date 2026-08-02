# Enhanced Report Sections — Specification

**Capability:** enhanced-report-sections
**Status:** New
**Date:** 2026-06-02

---

## ADDED Requirements

### Requirement: Add "Blocking Status & Dependencies" section to sprint report

The system SHALL add a new section "Blocking Status & Dependencies" to sprint reports containing three tables: Root Blockers, Blocked Items, and Ready to Work.

#### Scenario: Section appears after Item Details
- **WHEN** generating a sprint report
- **THEN** "Blocking Status & Dependencies" section appears after existing "Item Details" section

#### Scenario: Root Blockers table structure
- **WHEN** rendering Root Blockers table
- **THEN** columns are: Key, Type, Status, Assignee, Blocks (count), Impact Radius (with emoji)

#### Scenario: Blocked Items table structure
- **WHEN** rendering Blocked Items table
- **THEN** columns are: Key, Type, Status, Assignee, Blocked By (comma-separated keys), Chain Depth (with label)

#### Scenario: Ready to Work table structure
- **WHEN** rendering Ready to Work table
- **THEN** columns are: Key, Type, Status, Assignee, SP, Sprint

### Requirement: Add "Dependency Graph" section to dashboard

The system SHALL add a new section "Dependency Graph — Critical Blocking Chains" to dashboard reports showing ASCII trees for each root blocker.

#### Scenario: Section appears after Complete Activity List
- **WHEN** generating a dashboard report
- **THEN** "Dependency Graph" section appears after "Complete Activity List" and before "Sprint Planning"

#### Scenario: One tree per root blocker
- **WHEN** 2 root blockers exist (PDS-100, PDS-102)
- **THEN** section contains 2 subsections, each with header showing blocker key, type, status, assignee, and impact count

#### Scenario: Impact summary with action
- **WHEN** rendering each blocker tree
- **THEN** footer shows: "**Impact:** X direct + Y indirect = Z items blocked" and "**Action:** [specific recommendation]"

### Requirement: Enhance assignee workload tables with blocking context

The system SHALL add blocker/blocked counts and highlight root blockers in assignee workload sections.

#### Scenario: Assignee summary shows blocking stats
- **WHEN** rendering assignee workload summary (e.g., "Alice (8 items)")
- **THEN** header includes: "Alice (8 items, 2 are root blockers ⚠️)" if assignee owns root blockers

#### Scenario: Assignee table includes Blocks column
- **WHEN** rendering per-assignee item table
- **THEN** add "Blocks" column showing count of items blocked by each item

#### Scenario: Root blocker rows highlighted
- **WHEN** an item in assignee table is a root blocker
- **THEN** row uses bold formatting and includes "🔴 ROOT BLOCKER — Priority 1" in Notes column

#### Scenario: Blocked status visible
- **WHEN** an item in assignee table is blocked
- **THEN** "Blocked By" column shows blocker keys, Notes shows "Waiting"

### Requirement: Add sprint breakdown with blocker highlighting

The system SHALL enhance sprint sections to show blocked item percentage and root blockers within each sprint.

#### Scenario: Sprint summary includes blocked percentage
- **WHEN** rendering sprint section header
- **THEN** include: "Sprint 1 — 18 items, 8 blocked (45% of capacity)"

#### Scenario: Blocked items subsection
- **WHEN** sprint has blocked items
- **THEN** create subsection "🔴 Blocked (8 items, 45% of sprint capacity)" with table showing: Key, Summary, Assignee, SP, Blocked By, Estimated Unblock

#### Scenario: Root blockers in sprint
- **WHEN** sprint contains root blockers
- **THEN** add subsection "🔗 Root Blockers in This Sprint" listing each blocker with its impact: "**PDS-100** (Bug, Alice, In Progress) → blocks 5 sprint items + 7 in Sprint 2"

#### Scenario: Sprint risk assessment
- **WHEN** >40% of sprint items are blocked
- **THEN** add warning: "⚠️ **Risk:** 45% of sprint blocked — escalate PDS-100 and PDS-102 resolution"

### Requirement: Preserve existing report sections

The system SHALL NOT remove or modify existing report sections when adding new sections.

#### Scenario: Existing sections unchanged
- **WHEN** generating sprint report with new sections
- **THEN** all existing sections (Overview, Allocation, Velocity, Risks, Timeline) remain unchanged

#### Scenario: New sections are additive
- **WHEN** comparing v2.1 and v2.2 sprint reports
- **THEN** v2.2 report contains all v2.1 sections plus new blocking sections

#### Scenario: Backward compatibility for consumers
- **WHEN** external tool parses report looking for "## Sprint Overview" section
- **THEN** section exists at same position with same structure

### Requirement: Include section in table of contents

The system SHALL add new sections to report table of contents if TOC generation is enabled.

#### Scenario: TOC includes new sections
- **WHEN** generating report with TOC
- **THEN** TOC includes: "Blocking Status & Dependencies" and "Dependency Graph" entries

#### Scenario: TOC links work
- **WHEN** report has anchor links in TOC
- **THEN** clicking "Blocking Status & Dependencies" jumps to that section

### Requirement: Format consistently with existing sections

The system SHALL use the same markdown formatting, emoji indicators, and table styles as existing report sections.

#### Scenario: Section headers match existing style
- **WHEN** existing sections use "## 📊 Title" format
- **THEN** new sections use "## 🔗 Title" with appropriate emoji

#### Scenario: Tables match existing structure
- **WHEN** existing tables use markdown pipe format with left-aligned text
- **THEN** new tables use same format

#### Scenario: Emoji indicators consistent
- **WHEN** existing sections use ⚠️ for warnings and ✅ for success
- **THEN** new sections use same emoji set plus 🔴 for root blockers

### Requirement: Support HTML output with same structure

The system SHALL render new sections in HTML reports with equivalent structure and styling.

#### Scenario: HTML section headers styled
- **WHEN** generating HTML dashboard
- **THEN** "Dependency Graph" section has same CSS classes as other sections

#### Scenario: ASCII trees rendered in monospace
- **WHEN** rendering dependency trees in HTML
- **THEN** use `<pre>` tag with monospace font to preserve box-drawing characters

#### Scenario: Tables use existing HTML table class
- **WHEN** rendering blocking status tables in HTML
- **THEN** use same table classes as existing Item Details table
