# Report Generation — Specification (Delta)

**Capability:** report-generation
**Status:** Modified
**Date:** 2026-06-02
**Version:** 1.2 (adds blocking dependency sections)

---

## ADDED Requirements

### Requirement: Markdown report with blocking dependency sections

The system SHALL generate a human-readable Markdown report using string formatting. SHALL include sections: Executive Summary, Epic Overview table, Risk Analysis by severity, Resource Utilization table, Blocking Status & Dependencies (Root Blockers, Blocked Items, Ready to Work tables — new), Action Items, and Appendix. SHALL use emoji indicators (CRITICAL, HIGH, MEDIUM, LOW, ROOT BLOCKER). SHALL format dates as YYYY-MM-DD, support `--output` flag, integrate `EscalationDetector.analyze_blocker_chain()` results, and compute impact radius and chain depth before rendering blocking sections.

#### Scenario: Blocking section appears after Risk Analysis
- **WHEN** generating markdown report with blocking data
- **THEN** "Blocking Status & Dependencies" section appears after "Risk Analysis" and before "Action Items"

#### Scenario: Empty blocking section handling
- **WHEN** no root blockers exist
- **THEN** section shows: "No root blockers detected — all items are ready to work."

---

### Requirement: Dashboard report with dependency graph section

The system SHALL generate a single-file dashboard report combining all epics and work items with sections: Executive Dashboard, Complete Activity List, Dependency Graph (Critical Blocking Chains — new), Sprint Planning, Progress Tracking, Escalation Register, and Bug Radar. SHALL support markdown and HTML output formats, use `WorkItemCollector` for item discovery, render ASCII dependency trees per root blocker with impact summary, and write output to `reports/epics/{project}_{date}_dashboard.{ext}`.

#### Scenario: Dependency Graph section placement
- **WHEN** generating dashboard report
- **THEN** "Dependency Graph" section appears after "Complete Activity List" and before "Sprint Planning"

#### Scenario: Multiple root blockers
- **WHEN** 3 root blockers exist
- **THEN** section contains 3 subsections, one per root blocker, sorted by impact radius descending

#### Scenario: No root blockers
- **WHEN** no items qualify as root blockers
- **THEN** section shows: "✅ No blocking chains detected — all items are unblocked."

---

### Requirement: Integrate EscalationDetector blocker chain analysis

The system SHALL call `EscalationDetector(overload_threshold=8).analyze_blocker_chain(items)` after data collection and before rendering to get the blocker chain map. **Note:** The existing `analyze_blocker_chain()` implementation contains a scope bug where the `visited` set is not reset per path, causing intermediate nodes in multi-level chains to be skipped; this method MUST be refactored to pass a new `visited` tracker per DFS walk. The system SHALL compute impact radius (transitive blocked count) and chain depth (walk blocked_by to root) for each item and store results in `blocker_chain_depth` and `impact_radius` fields. SHALL handle items with no blocking relationships with defaults (depth=0, radius=0).

#### Scenario: Chain analysis integration
- **WHEN** generating report with 199 items including 2 root blockers
- **THEN** `analyze_blocker_chain()` returns map {PDS-100: [PDS-124, PDS-128, ...], PDS-102: [...]}

#### Scenario: Impact radius computation
- **WHEN** PDS-100 blocks PDS-124, and PDS-124 blocks [PDS-127, PDS-129]
- **THEN** PDS-100.impact_radius = 3, PDS-124.impact_radius = 2, PDS-127.impact_radius = 0

#### Scenario: Chain depth computation
- **WHEN** PDS-127 has `blocked_by = ["PDS-124"]` and PDS-124 has `blocked_by = ["PDS-100"]`
- **THEN** PDS-127.blocker_chain_depth = 2, PDS-124.blocker_chain_depth = 1, PDS-100.blocker_chain_depth = 0

**Performance:**
- SHALL complete chain analysis in <200ms for 200 items with avg 2 blockers each
- DFS traversal with visited set prevents infinite loops on circular dependencies

---

### Requirement: Render ASCII dependency trees

The system SHALL render blocking dependency chains as ASCII trees using box-drawing characters (├ └ │ →), indent 4 spaces per level, limit depth to 5 levels ("... (N more levels)" if deeper), limit breadth to 10 items per level ("... (N more items)" if more), show key/type/assignee metadata, label [DIRECT]/[INDIRECT] blocked items, include impact summary footer, and render one tree per root blocker sorted by impact_radius descending. Implementation: `epic_report/reporters/tree_renderer.py` with `render_dependency_tree(root, all_items, max_depth=5) -> str`.
#### Scenario: Tree rendering for 3-level chain
- **WHEN** rendering tree for PDS-100 that blocks PDS-124, which blocks [PDS-127, PDS-129]
- **THEN** output shows PDS-100 at root, PDS-124 indented with ├─→, PDS-127/PDS-129 indented with │ then └─→

#### Scenario: Empty tree handling
- **WHEN** root blocker has no blocked items (blocks list is empty)
- **THEN** tree shows root blocker only with note: "(no items currently blocked)"

**Implementation:**
- `epic_report/reporters/tree_renderer.py` (NEW module)
- `render_dependency_tree(root: WorkItem, all_items: dict[str, WorkItem], max_depth: int = 5) -> str`

---

### Requirement: Enhanced assignee workload with blocking context

The system SHALL include root blocker count in assignee summary headers when the assignee owns root blockers, add "Blocks" and "Blocked By" columns to per-assignee item tables, highlight root blocker rows with bold formatting and "🔴 ROOT BLOCKER — Priority 1" note, and compute/display blocked percentage per assignee.
#### Scenario: Assignee with root blockers
- **WHEN** Alice owns 8 items including PDS-100 (root blocker with impact 12)
- **THEN** header shows: "Alice (8 items, 1 is root blocker ⚠️)"

#### Scenario: Assignee mostly blocked
- **WHEN** Bob has 5 items, 3 are blocked
- **THEN** summary shows: "Bob (5 items, 3 blocked 🟠)" and note "60% blocked — provide alt work"

---

### Requirement: Sprint breakdown with blocker highlighting

The system SHALL include blocked count and percentage in sprint section headers, create a "🔴 Blocked" subsection per sprint (Key, Summary, Assignee, SP, Blocked By, Estimated Unblock), create a "🔗 Root Blockers in This Sprint" subsection with cross-sprint impact, add a risk warning when >40% of sprint items are blocked, and compute sprint risk level: HIGH (>40%), MEDIUM (20–40%), LOW (<20%).
#### Scenario: High-risk sprint
- **WHEN** Sprint 1 has 18 items, 8 are blocked (44%)
- **THEN** header shows: "Sprint 1 — 18 items, 8 blocked (44% of capacity)" and warning: "⚠️ **Risk:** 44% of sprint blocked — escalate blocker resolution"

#### Scenario: Root blockers in sprint
- **WHEN** Sprint 1 contains PDS-100 (blocks 5 sprint items + 7 in Sprint 2)
- **THEN** subsection shows: "**PDS-100** (Bug, Alice, In Progress) → blocks 5 sprint items + 7 in Sprint 2"

---

## Data Flow Changes

**Before (v1.1):**
```
Collection → Analysis (risk/resource/timeline) → Rendering
```

**After (v1.2):**
```
Collection → _build_reverse_blocking_map() → Analysis (risk/resource/timeline) →
  EscalationDetector.analyze_blocker_chain() → Compute impact/depth → Rendering
```

**New integration point:**
- After collection and before rendering, call blocker chain analysis
- Populate `blocker_chain_depth` and `impact_radius` on all items
- Pass enriched items to reporters

---

## Testing Requirements

**Unit tests (new):**
- `test_render_dependency_tree_single_level()` — root with direct children only
- `test_render_dependency_tree_multi_level()` — 3-level chain
- `test_render_dependency_tree_empty()` — root with no blocked items
- `test_blocking_section_in_markdown()` — verify new section appears in correct position
- `test_blocking_section_empty_state()` — verify empty state messaging

**Integration tests (modified):**
- `test_generate_report_with_blocking_data()` — full report with blocking sections
- `test_dashboard_with_dependency_graph()` — dashboard includes ASCII trees

**Snapshot tests (new):**
- `test_sprint_report_blocking_section_snapshot()` — snapshot of "Blocking Status" section
- `test_dashboard_dependency_graph_snapshot()` — snapshot of ASCII tree output

---

## Backward Compatibility

**Preserved:**
- All existing report sections remain unchanged
- Existing CLI commands work without modification
- JSON output includes new fields but is backward compatible (new fields optional)

**Additive:**
- New sections appear at end of existing section list
- HTML reports include new sections with same CSS classes
- Spreadsheet export adds new sheets without removing existing ones

**No breaking changes:**
- Consumers parsing existing sections unaffected
- Field addition to models uses defaults (backward compatible)

---

## Performance Impact

**Blocker chain analysis overhead (P1 updated):**
- 200 items: <150ms (optimized BFS per-root impact per blocking spec; metrics emission included)
- Depth uses -1 for cycles.
- Full metrics via observability spec.

**ASCII tree rendering:**
- 5 root blockers × 10 blocked items each: ~50ms
- Complexity: O(N×D) where N = blocked items, D = depth (capped at 5)

**Total overhead per report:**
- Collection: ~4.8s (unchanged)
- Analysis: +200ms (blocker chains + rendering)
- Total: ~5.0s (4% increase)

---

## Migration Notes

**Automatic migration:**
- No user action required
- Upgrade to v1.2 enables new sections automatically
- Existing reports continue to work

**Operational behavior:**
- Blocking sections are additive and emitted from available blocking data
- Empty blocking data uses explicit empty-state rendering without requiring a feature flag
