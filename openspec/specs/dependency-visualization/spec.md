## Purpose

This specification defines requirements for Dependency Visualization.

# Dependency Visualization — Specification

**Capability:** dependency-visualization
**Status:** New
**Date:** 2026-06-02

---

## Requirements

### Requirement: Render ASCII tree for blocking chains

The system SHALL render blocking dependency chains as ASCII trees using box-drawing characters (├, └, │, →).

#### Scenario: Single-level blocking chain
- **WHEN** PDS-100 blocks [PDS-124, PDS-128, PDS-131] with no further chains
- **THEN** output is:
  ```
  PDS-100 (Bug, Alice, In Progress) ⚠️ BLOCKS 3 ITEMS
  ├─→ PDS-124 (Task, Bob)
  ├─→ PDS-128 (Story, Dave)
  └─→ PDS-131 (Task, Eve)
  ```

#### Scenario: Multi-level blocking chain
- **WHEN** PDS-100 blocks PDS-124, and PDS-124 blocks [PDS-127, PDS-129]
- **THEN** output is:
  ```
  PDS-100 (Bug, Alice, In Progress) ⚠️ BLOCKS 3 ITEMS
  └─→ PDS-124 (Task, Bob)
      ├─→ PDS-127 (Task, Carol)
      └─→ PDS-129 (Bug, Unassigned)
  ```

#### Scenario: Multiple root blockers
- **WHEN** both PDS-100 and PDS-102 are root blockers
- **THEN** each root blocker gets its own tree section with header showing impact

### Requirement: Group items by blocking status

The system SHALL split items into three groups: Root Blockers, Blocked Items, and Ready to Work.

#### Scenario: Root Blockers group
- **WHEN** PDS-100 has empty `blocked_by` and blocks 5 items
- **THEN** PDS-100 appears in "Root Blockers" table with columns: Key, Type, Status, Assignee, Blocks, Impact Radius

#### Scenario: Blocked Items group
- **WHEN** PDS-124 has `blocked_by = ["PDS-100"]`
- **THEN** PDS-124 appears in "Blocked Items" table with columns: Key, Type, Status, Assignee, Blocked By, Chain Depth

#### Scenario: Ready to Work group
- **WHEN** PDS-101 has empty `blocked_by`
- **THEN** PDS-101 appears in "Ready to Work" table with columns: Key, Type, Status, Assignee, SP, Sprint

#### Scenario: Item appears in only one group
- **WHEN** an item qualifies for multiple groups (e.g., root blocker that is also blocked)
- **THEN** item appears in the highest priority group (Root Blockers > Blocked Items > Ready to Work)

### Requirement: Display impact radius

The system SHALL display how many items each blocker affects with emoji indicators based on severity.

#### Scenario: High impact blocker
- **WHEN** PDS-100 has impact_radius >= 10
- **THEN** display shows "12 items ⚠️" with warning emoji

#### Scenario: Medium impact blocker
- **WHEN** PDS-102 has 5 <= impact_radius < 10
- **THEN** display shows "8 items 🟡" with yellow circle emoji

#### Scenario: Low impact blocker
- **WHEN** PDS-105 has impact_radius < 5
- **THEN** display shows "3 items" with no emoji

### Requirement: Display chain depth indicators

The system SHALL show chain depth for blocked items with descriptive labels.

#### Scenario: Direct blocked item
- **WHEN** PDS-124 has blocker_chain_depth = 1
- **THEN** display shows "1 (direct)"

#### Scenario: Indirect blocked item
- **WHEN** PDS-127 has blocker_chain_depth = 2
- **THEN** display shows "2 (via PDS-124)" with immediate blocker name

#### Scenario: Multi-blocked item
- **WHEN** PDS-130 has `blocked_by = ["PDS-102", "PDS-105"]`
- **THEN** display shows "1 (multi-blocked)"

### Requirement: Sort tables by priority

The system SHALL sort items within each group by priority to highlight most important items first.

#### Scenario: Root Blockers sorted by impact
- **WHEN** multiple root blockers exist
- **THEN** items are sorted by impact_radius descending (highest impact first)

#### Scenario: Blocked Items sorted by chain depth
- **WHEN** multiple blocked items exist
- **THEN** items are sorted by blocker_chain_depth ascending (shallowest first, easier to unblock)

#### Scenario: Ready to Work sorted by sprint and assignee
- **WHEN** multiple ready items exist
- **THEN** items are sorted by sprint_name, then assignee, then key

### Requirement: Limit tree depth for readability

The system SHALL limit ASCII tree rendering to 5 levels deep to prevent visual clutter.

#### Scenario: Deep chain truncation
- **WHEN** a blocking chain exceeds 5 levels
- **THEN** render up to level 5 and append "... (3 more levels)" indicator

#### Scenario: Breadth limiting per level
- **WHEN** a blocker has more than 10 direct blocked items
- **THEN** render first 10 and append "... (5 more items)" indicator

### Requirement: Include actionable context in headers

The system SHALL include status, assignee, and impact information in section headers to enable quick decision-making.

#### Scenario: Root Blocker section header
- **WHEN** rendering Root Blockers section
- **THEN** header shows: "Root Blockers (2) — Unblock These First" with count

#### Scenario: Blocked Items section header
- **WHEN** rendering Blocked Items section
- **THEN** header shows: "Blocked Items (8) — Waiting on Dependencies" with count

#### Scenario: Action recommendation
- **WHEN** Root Blockers section has items
- **THEN** include line: "**Action:** Prioritize PDS-100 (blocks 12 items) and PDS-102 (blocks 8 items)."

### Requirement: Handle empty groups gracefully

The system SHALL display appropriate messages when a blocking status group has no items.

#### Scenario: No root blockers
- **WHEN** no items have empty `blocked_by` and non-empty `blocks`
- **THEN** Root Blockers section shows: "✅ No root blockers detected."

#### Scenario: No blocked items
- **WHEN** no items have non-empty `blocked_by`
- **THEN** Blocked Items section shows: "✅ All items are unblocked and ready to work."

#### Scenario: All items blocked
- **WHEN** Ready to Work group is empty
- **THEN** section shows: "⚠️ All items are blocked — resolve root blockers urgently."
