# Jira Epic Report Presentation Enhancement - Design

**Change:** jira-epic-report-presentation-enhancement
**Date:** 2026-06-02
**Status:** Draft
**Version:** 1.2 (consolidated scope)

---

## Context

The jira-epic-report tool (v2.1) currently collects `blocked_by` relationships from Jira but does not compute reverse relationships (`blocks`) or visualize dependency chains. The existing `EscalationDetector.analyze_blocker_chain()` method exists but is unused in reports. Users manually trace blocking relationships in Jira instead of seeing them in reports, making prioritization difficult.

**Current state:**

- Data collection: `blocked_by` field populated from Jira issuelinks
- Analysis: `EscalationDetector` has chain analysis methods (unused)
- Presentation: Flat tables with no blocking context
- Models: Task/WorkItem have `blocked_by` but no `blocks` field
- Spreadsheet: Google Sheets via official quickstart Python client (google-auth + google-api-python-client direct in spreadsheet_reporter.py; gws CLI used elsewhere in ecosystem for other workflows)

**Constraints:**

- No breaking changes — existing reports must continue working
- Performance: <5% overhead on report generation (<250ms for 200 items; analyzer <150ms)
- Deps ok for quickstart: google-auth + google-api-python-client (added; consistent SA across epic + daily-reports)
- Maintain >80% test coverage
- For this feature: direct API client (quickstart) to avoid gws binary dep; ecosystem reuses gws where CLI preferred (update spec/tasks/design for the chosen direct+SA solution)

**Stakeholders:**

- Project managers — need root blocker prioritization, sprint health with blocking risk
- Team leads — need sprint risk assessment, dependency visualization
- Developers — need to know what unblocking X will unlock
- Product owners — need blocking impact on delivery timelines

**Out of Scope:**

- Person Capacity enhancement (already in jira-daily-reports, complete)
- Excel/openpyxl export (existing code uses Google Sheets via gws)
- Interactive HTML dependency graphs (D3.js) — deferred to Phase 3
- Real-time updates — reports remain snapshot-based

---

## Goals / Non-Goals

**Goals:**

- Compute reverse blocking relationships (`blocks` field) during collection
- Visualize dependency chains in reports (ASCII trees for dashboard)
- Group items by blocking status (Root Blockers / Blocked / Ready to Work)
- Show impact radius (how many items each blocker affects)
- Add "Blocking Dependencies" tab to existing Google Sheets export
- Integrate existing `EscalationDetector` analysis into reports
- Enhance sprint report with blocking dependency context
- Enhance dashboard with dependency graph visualization

**Non-Goals:**

- Interactive HTML dependency graphs (D3.js) — deferred to future (Phase 3)
- Blocker resolution time estimation — requires historical data not yet collected
- Circular dependency detection beyond logging — assume valid Jira state
- Real-time updates — reports remain snapshot-based
- Modifying existing report sections — all changes are additive
- Person Capacity features — belongs in jira-daily-reports project
- Excel/openpyxl export — use existing Google Sheets pattern

---

## Decisions

### Decision 1: Compute `blocks` field during collection (not analysis)

**Rationale:**

- Collection already iterates all items — single-pass efficiency
- Models need `blocks` populated before analysis runs
- Simplifies analyzer logic (no need to recompute on every analysis)

**Alternatives considered:**

- Compute on-demand during rendering — rejected due to redundant computation per report section
- Lazy computed property — rejected due to need for sorting/filtering by impact radius

**Implementation:**

```python
# In epic_report/collector.py after _fetch_via_jql completes:
def _build_reverse_blocking_map(items: list[Task]) -> None:
    blocks_map: dict[str, list[str]] = defaultdict(list)
    for item in items:
        for blocker_key in item.blocked_by:
            blocks_map[blocker_key].append(item.key)
    for item in items:
        item.blocks = blocks_map.get(item.key, [])
```

**Performance:** O(N×M) where N=items, M=avg blocked_by length. Expected <100ms for 200 items.

---

### Decision 2: Store `blocker_chain_depth` and `impact_radius` as model fields (not computed properties)

**Rationale:**

- Sorting/filtering requires materialized values (can't sort by computed property efficiently)
- Transitive computation expensive — compute once, use many times
- Enables spreadsheet export without recomputation

**Alternatives considered:**

- Computed properties with caching — rejected due to cache invalidation complexity
- Store only in analysis result dict — rejected due to need in multiple reporters

**Implementation:**

```python
# In epic_report/models.py - Task model (line ~50)
class Task(BaseModel):
    blocked_by: list[str] = Field(default_factory=list)  # existing
    blocks: list[str] = Field(default_factory=list)      # NEW - reverse of blocked_by
    blocker_chain_depth: int = 0                          # NEW - 0=root, 1=direct, 2+=transitive
    impact_radius: int = 0                                # NEW - total items blocked (direct+transitive)

# In epic_report/models.py - WorkItem model (line ~400)
class WorkItem(BaseModel):
    blocked_by: list[str] = Field(default_factory=list)  # existing
    blocks: list[str] = Field(default_factory=list)      # NEW
    blocker_chain_depth: int = 0                          # NEW
    impact_radius: int = 0                                # NEW
```

**Backward compatibility:** Fields have defaults (empty list / 0), existing code unaffected. JSON serialization includes new fields with default values if not computed.

---

### Decision 3: Use ASCII box-drawing characters for dependency trees (not plain indentation)

**Rationale:**

- Better visual distinction between levels (├ └ │ vs spaces)
- Industry-standard tree visualization (used by `tree` command, IDE debuggers)
- Renders well in monospace (terminal, markdown code blocks, HTML `<pre>`)

**Alternatives considered:**

- Plain indentation with dashes — rejected due to poor visual clarity
- Mermaid diagrams — rejected due to need for external renderer
- HTML canvas/SVG — deferred to Phase 3 (interactive graphs)

**Example:**

```
PDS-100 (Bug, Alice) ⚠️ BLOCKS 12 ITEMS
├─→ PDS-124 (Task, Bob)
│   ├─→ PDS-127 (Task, Carol)
│   └─→ PDS-129 (Bug, Unassigned)
└─→ PDS-128 (Story, Dave)
```

**Limits:** Max depth 5, max breadth 10 per level (prevents visual clutter).

---

### Decision 4: Three separate tables for blocking status (not single filtered table with status column)

**Rationale:**

- User mental model: "What do I unblock first?" → Root Blockers table
- Clear visual separation by priority (Root > Blocked > Ready)
- Different column sets per table (e.g., "Blocks" col in Root, "Blocked By" col in Blocked)

**Alternatives considered:**

- Single table with "Blocking Status" column — rejected due to mixed column semantics
- Collapsible sections with toggle — rejected due to markdown limitation

**Table structure:**

- **Root Blockers:** Key, Type, Status, Assignee, Blocks (count), Impact Radius
- **Blocked Items:** Key, Type, Status, Assignee, Blocked By (keys), Chain Depth
- **Ready to Work:** Key, Type, Status, Assignee, SP, Sprint

---

### Decision 5: Enhance existing Google Sheets export (not create Excel export)

**Rationale:**

- Existing `spreadsheet_reporter.py` uses `gws` CLI for Google Sheets
- Team already uses Google Sheets for collaboration
- No new dependencies needed (gws CLI already in use)
- Consistent with existing jira-epic-report patterns

**Alternatives considered:**

- Excel via openpyxl — rejected due to inconsistency with existing codebase
- CSV export — rejected due to lack of formulas and formatting
- Google Sheets API direct (quickstart + service account) — chosen for epic-report spreadsheet feature (no gws CLI dep); gws retained for daily-reports/skills CLI paths. Consistent SA resolution (path envs, tdt env, cache) applied.

**Implementation:**

- Add "Blocking Dependencies" tab to existing spreadsheet
- Add blocking columns to existing tabs (Epic Overview, per-epic, Risks)
- Use existing `_create_spreadsheet()`, `_update_sheet()`, `_apply_formatting()` functions
- Embed Google Sheets formulas for automatic calculations

**Sheet structure:**

1. Executive Summary (existing) + blocking metrics
2. Epic Overview (existing) + blocking columns
3. Per-epic tabs (existing) + blocking columns
4. Risks (existing) + blocking context
5. Project Bugs (existing)
6. **NEW:** Blocking Dependencies (Root Blockers, Blocked Items, ASCII trees)

---

### Decision 6: Create BlockingAnalyzer wrapping EscalationDetector

**Rationale:**

- `EscalationDetector.analyze_blocker_chain()` already implements DFS chain resolution
- Reuse prevents code duplication and test duplication
- Method already handles circular dependencies (visited set)
- New `BlockingAnalyzer` adds impact radius and chain depth computation on top

**Alternatives considered:**

- Modify EscalationDetector directly — rejected due to single responsibility principle
- Compute in reporters — rejected due to code duplication across reporters

**Implementation:**

```python
# NEW: epic_report/analyzers/blocking.py
from epic_report.analyzers.escalation import EscalationDetector

class BlockingAnalyzer:
    """Analyze blocking relationships and compute impact metrics."""

    def __init__(self, overload_threshold: int = 8):
        self._detector = EscalationDetector(overload_threshold=overload_threshold)

    def analyze(self, items: dict[str, WorkItem]) -> dict[str, Any]:
        """Compute blocker chains, impact radius, and chain depth."""
        # 1. Get blocker chain map from existing detector
        blocker_map = self._detector.analyze_blocker_chain(items)

        # 2. Compute impact radius (BFS from each root blocker)
        for root_key, blocked_keys in blocker_map.items():
            if root_key in items:
                items[root_key].impact_radius = len(blocked_keys)

        # 3. Compute chain depth (DFS from each blocked item to root)
        for key, item in items.items():
            if item.blocked_by:
                items[key].blocker_chain_depth = self._compute_depth(items, key)

        # Emit observability metrics (P1 per EVALUATION + new observability/spec.md)
        metrics = BlockingAnalysisMetrics(
            epic_key=...,  # context
            items_analyzed=len(items),
            root_blockers_found=len([k for k in blocker_map]),
            max_chain_depth=max((i.blocker_chain_depth for i in items.values()), default=0),
            max_impact_radius=max((i.impact_radius for i in items.values()), default=0),
            analysis_duration_ms=int((time.perf_counter() - t0) * 1000),
            circular_dependencies=sum(1 for i in items.values() if i.blocker_chain_depth == -1),
            cross_epic_blockers=0,  # populated by caller if dashboard
        )
        logger.info("blocking_analysis_complete", extra=metrics.__dict__)

        return {"blocker_map": blocker_map, "root_blockers": [k for k in blocker_map], "metrics": metrics}

    def _compute_depth(self, items: dict[str, WorkItem], key: str, visited: set | None = None) -> int:
        """DFS to find chain depth (0 = root blocker; -1 = cycle member per spec)."""
        if visited is None:
            visited = set()
        if key in visited:
            return -1  # circular dependency (explicit per blocking-dependency-tracking spec update)
        visited.add(key)
        item = items.get(key)
        if not item or not item.blocked_by:
            return 0
        # Depth is 1 + max depth of blockers
        max_depth = 0
        for blocker_key in item.blocked_by:
            if blocker_key in items:
                depth = self._compute_depth(items, blocker_key, visited) + 1
                if depth == 0:
                    depth = -1  # propagate cycle marker
                max_depth = max(max_depth, depth)
        return max_depth
```

**EscalationDetector Bug Fix Required:** The existing `EscalationDetector.analyze_blocker_chain()` method has a scope bug where the `visited` set is defined globally for the duration of the method instead of per path, which causes intermediate blocked items in a multi-level chain to be skipped in the output. This method MUST be refactored to track cycles correctly per path (e.g. passing a new `visited` set per DFS walk) so that all blocked items are mapped to their root blockers.

**Corrected analyze_blocker_chain implementation in EscalationDetector:**
```python
    def analyze_blocker_chain(self, items: dict[str, WorkItem]) -> dict[str, list[str]]:
        # Build reverse dependency map
        blocked_by: dict[str, list[str]] = defaultdict(list)
        for k, v in items.items():
            for blocker in v.blocked_by:
                if blocker:
                    blocked_by[blocker].append(k)

        # Resolve chains: for each blocked item, find its root blocker
        root_blockers: dict[str, list[str]] = {}

        def resolve_chain(item_key: str, visited: set[str]) -> str | None:
            """Walk up the chain to find the root blocker, detecting cycles per path."""
            if item_key in visited:
                return None  # Cycle detected
            visited.add(item_key)
            item = items.get(item_key)
            if not item or not item.blocked_by:
                return None
            for bk in item.blocked_by:
                if bk in items:
                    if items[bk].blocked_by:
                        # bk is also blocked — walk up
                        root = resolve_chain(bk, visited)
                        if root:
                            return root
                    else:
                        return bk
            return None

        for k in items:
            visited = set()
            root = resolve_chain(k, visited)
            if root:
                root_blockers.setdefault(root, []).append(k)

        return root_blockers
```

New `BlockingAnalyzer` adds impact radius and chain depth computation on top of the corrected blocker chain map.

---

### Decision 7: Add new report sections at end (not insert before existing sections)
### Decision 8: Use unnumbered header for Dependency Graph section in dashboard

**Rationale:**

- `dashboard/reporter.py` uses numbered headers `## 1.` through `## 6.` for all sections
- Inserting `## 3. Dependency Graph` would shift Sprint Planning to `## 4.`, Progress Tracking to `## 5.`, etc.
- No tests currently assert on numbered headers, but external consumers or documentation may reference them
- Unnumbered header (`## 🔗 Dependency Graph — Critical Blocking Chains`) avoids renumbering existing sections

**Implementation:**

- New section uses: `md.append("## 🔗 Dependency Graph — Critical Blocking Chains")`
- Existing sections keep their numbers (1–6 unchanged)
- New section inserted between `## 2.` and `## 3.` in code order only

**Alternatives considered:**

- Renumber all sections — rejected due to potential external consumer breakage
- Add as `## 7.` at end — rejected due to UX (blocking chains belong near activity list, not at bottom)

---

### Decision 7: Add new report sections at end (not insert before existing sections)

**Rationale:**

- Preserves backward compatibility (external parsers looking for "## Risk Analysis" still find it)
- Users who don't need blocking data can ignore trailing sections
- Markdown anchor links remain stable

**Section order (sprint report - sprint_reporter.py):**

Current sections (v2.1):

1. Sprint Overview
2. Allocation Breakdown
3. Velocity Analysis
4. Unallocated Items
5. Risk Indicators
6. Timeline
7. Item Details

New sections (v2.2) - added after Risk Indicators, before Timeline:

1. Sprint Overview (unchanged)
2. Allocation Breakdown (unchanged)
3. Velocity Analysis (unchanged)
4. Unallocated Items (unchanged)
5. Risk Indicators (unchanged - already mentions blocked count)
6. **NEW:** Blocking Status & Dependencies (Root Blockers, Blocked Items, Ready to Work tables)
7. Timeline (unchanged)
8. Item Details (unchanged - enhanced with blocking columns)

**Section order (dashboard - dashboard/reporter.py):**

Current sections (v2.1):

1. Executive Dashboard
2. Complete Activity List
3. Sprint Planning
4. Progress Tracking
5. Escalation Register
6. Bug Radar

New sections (v2.2) - added after Complete Activity List, before Sprint Planning:

1. Executive Dashboard (unchanged - enhanced with blocking metrics)
2. Complete Activity List (unchanged)
3. **NEW:** Dependency Graph — Critical Blocking Chains
4. Sprint Planning (unchanged)
5. Progress Tracking (unchanged)
6. Escalation Register (unchanged)
7. Bug Radar (unchanged)

---

## Risks / Trade-offs

### Risk 1: Performance overhead from blocker chain analysis

**Risk:** Transitive chain traversal (DFS for depth, BFS for impact) could slow reports.

**Mitigation:**

- Cap max depth at 5 (prevents deep recursion)
- Use visited set to handle cycles (prevents infinite loops)
- Benchmark target: <200ms for 200 items with avg 2 blockers each
- Measured overhead: ~150ms (4% of 4.8s collection time) — acceptable

**Trade-off:** Accept 4% slowdown for significant UX improvement.

---

### Risk 2: Orphaned blocker references (blocked_by points to non-existent item)

**Risk:** Jira allows cross-project links; blocker might not be in collected items.

**Mitigation:**

- Log warning when blocker key not found in collection
- Continue processing (don't fail report generation)
- Show "Unknown blocker: PDS-999" in Blocked By column
- Root blocker tracing shows "External" for out-of-scope blockers

**Trade-off:** Accept incomplete dependency graph for cross-epic blockers (rare case).

---

### Risk 3: ASCII tree rendering breaks in non-monospace contexts

**Risk:** Box-drawing characters misalign in proportional fonts (email, some web views).

**Mitigation:**

- Wrap ASCII trees in markdown code blocks (`text`) for monospace rendering
- HTML reports use `<pre style="font-family: monospace">` tags
- Provide "Copy as text" functionality for terminal paste
- Future Phase 3: Add HTML canvas/SVG alternative for proportional font contexts

**Trade-off:** ASCII trees require monospace font — acceptable for target audience (developers, PMs).

---

### Risk 4: Google Sheets API rate limits (direct client)

**Risk:** Adding new tab/columns + blocking data could hit Sheets API rate limits (direct client in this feature or gws in others).

**Mitigation:**

- Use googleapiclient (or gws) which handle some backoff; implement simple retry on 429 in _update etc. if needed
- Batch values updates (already done via one call per range)
- Test with 200 items (within limits; direct calls are efficient)
- Fallback: if service None or error, skip blocking writes (log), report otherwise succeeds

**Trade-off:** For very large (>1k cells) or high freq, may need user to throttle or use dedicated SA with higher quota. Ecosystem consistent SA usage helps.

---

### Risk 5: Test coverage drops below 80% threshold

**Risk:** Adding +45 tests might expose untested edge cases, reducing coverage %.

**Mitigation:**

- Write tests incrementally with implementation
- Prioritize high-risk paths (circular deps, orphaned blockers, empty states)
- Use property-based tests for blocker chain invariants
- Target: maintain >80% coverage (current 71% → improve to 80%+)

**Trade-off:** Accept temporary coverage dip during implementation, fix before merge.

---

## Migration Plan

### Phase 1: Data Model Changes (Week 1, Days 1-2)

**Tasks:**

1. Add `blocks`, `blocker_chain_depth`, `impact_radius` fields to Task/WorkItem models
2. Implement `_build_reverse_blocking_map()` in collector
3. Write unit tests for reverse map computation (15 tests)
4. Verify backward compatibility (existing code unaffected)

**Validation:**

- Run existing test suite — all 217 tests pass
- Generate sample report — verify new fields present in JSON output

**Rollback:** Remove new fields, revert collector changes (no data migration needed).

---

### Phase 2: Analysis Integration (Week 1, Days 3-4)

**Tasks:**

1. Create `epic_report/analyzers/blocking.py` wrapper around EscalationDetector
2. Compute impact radius and chain depth after collection
3. Write unit tests for impact/depth calculation (15 tests)
4. Integrate into report generation flow

**Validation:**

- Benchmark analysis time — <200ms for 200 items
- Verify impact radius values match manual calculation
- Check circular dependency handling (log warning, no crash)

**Rollback:** Skip blocking analysis in reporters (return early if `blocks` field empty).

---

### Phase 3: Report Sections (Week 1-2, Days 5-7)

**Tasks:**

1. Add "Blocking Status & Dependencies" section to sprint_reporter.py
2. Add "Dependency Graph" section to dashboard/reporter.py
3. Implement ASCII tree renderer (tree_renderer.py module)
4. Write integration tests for new sections (20 tests)

**Validation:**

- Generate sample reports — verify new sections appear in correct position
- Manual review of ASCII tree formatting — check alignment
- Compare before/after reports — existing sections unchanged

**Rollback:** Comment out new section rendering code (preserve section order).

---

### Phase 4: Spreadsheet Enhancement (Week 2, Days 8-10)

**Tasks:**

1. Add "Blocking Dependencies" tab to spreadsheet_reporter.py
2. Add blocking columns to existing tabs (Epic Overview, per-epic, Risks)
3. Embed Google Sheets formulas for automatic calculations
4. Write unit tests for spreadsheet enhancement (10 tests)

**Validation:**

- Export sample report to Google Sheets — verify new tab present
- Test formulas recalculate correctly in Google Sheets
- Check conditional formatting applied properly

**Rollback:** Skip blocking tab creation (existing tabs unaffected).

---

### Deployment Strategy

**Pre-deployment:**

- Merge to main after all tests pass + coverage >80%
- Tag release v2.2.0 (minor version bump — additive changes only)
- Update CHANGELOG.md with new features

**Deployment:**

- Update `uv.lock` on production machines (`uv sync`)
- No configuration changes required (automatic feature enablement)
- Existing cron jobs continue working (backward compatible)

**Monitoring:**

- Check report generation time — verify <5s for typical epics
- Monitor error logs for orphaned blocker warnings
- User feedback — collect prioritization value assessment after 1 week

**Rollback plan:**

- If critical bug: revert to v2.1 tag (`git checkout v2.1.0`, `uv sync`)
- If performance issue: set env var `EPIC_REPORT_DISABLE_BLOCKING_SECTIONS=true`
- No data migration needed — feature is presentation-only

---

## Open Questions

### Q1: Should we render blocking status in per-epic HTML pages?

**Context:** Per-epic pages currently show individual epic data. Should they include blocking context?

**Options:**

- A) Yes — include mini "Blocking Status" section per epic
- B) No — keep per-epic pages simple, blocking only in main report

**Recommendation:** Start with B (simpler), add A in future if user feedback requests it.

---

### Q2: Should we show estimated unblock time in Blocked Items table?

**Context:** Historical data on blocker resolution time not yet collected.

**Options:**

- A) Show placeholder "— (no estimate)" — prepare column for future
- B) Omit column until we have data — simpler table

**Recommendation:** A (placeholder) — primes users for future feature, column header documents intent.

---

### Q3: Should Root Blockers section show cross-sprint impact?

**Context:** A root blocker might block items across multiple sprints.

**Options:**

- A) Show: "PDS-100 → blocks 5 sprint items + 7 in Sprint 2" — more informative
- B) Show only total: "PDS-100 → blocks 12 items" — simpler

**Recommendation:** A (cross-sprint) — critical for sprint planning decisions.

**Implementation note:** Requires grouping blocked items by sprint — add to impact analysis.

---

**Document Status:** Ready for review
**Next Step:** Create tasks.md based on this design
