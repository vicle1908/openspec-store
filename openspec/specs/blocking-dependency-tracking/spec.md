## Purpose

This specification defines requirements for Blocking Dependency Tracking.

# Blocking Dependency Tracking — Specification

**Capability:** blocking-dependency-tracking
**Status:** New
**Date:** 2026-06-02

---

## Requirements

### Requirement: Compute reverse blocking relationships (epic-scope only)

The system SHALL compute reverse blocking relationships (`blocks` field) for all Task and WorkItem models within the epic scope only. Cross-epic blockers (items in other projects/epics not in the collected set) SHALL be excluded from the blocker map and treated as external dependencies. The analysis result SHALL include an `external_blockers` dict mapping blocker keys to their blocked items for reference.

#### Scenario: Single blocker with multiple blocked items
- **WHEN** PDS-100 appears in the `blocked_by` field of PDS-124, PDS-128, PDS-131
- **THEN** PDS-100.blocks = ["PDS-124", "PDS-128", "PDS-131"]

#### Scenario: Item with no blockers and no blocked items
- **WHEN** PDS-101 has empty `blocked_by` and no items reference it as a blocker
- **THEN** PDS-101.blocks = []

#### Scenario: Blocked item that also blocks others
- **WHEN** PDS-124 has `blocked_by = ["PDS-100"]` and appears in PDS-127's `blocked_by`
- **THEN** PDS-124.blocks = ["PDS-127"]

### Requirement: Calculate impact radius

The system SHALL calculate the total number of items (direct + transitive) blocked by each item and store it in the `impact_radius` field.

#### Scenario: Direct blocking only
- **WHEN** PDS-100 blocks [PDS-124, PDS-128, PDS-131] and none of those block others
- **THEN** PDS-100.impact_radius = 3

#### Scenario: Transitive blocking chain
- **WHEN** PDS-100 blocks PDS-124, and PDS-124 blocks [PDS-127, PDS-129]
- **THEN** PDS-100.impact_radius = 3 (PDS-124 + PDS-127 + PDS-129)

#### Scenario: Multi-level chain
- **WHEN** PDS-100 → PDS-124 → PDS-127 → PDS-140 (4-level chain)
- **THEN** PDS-100.impact_radius = 3, PDS-124.impact_radius = 2, PDS-127.impact_radius = 1

#### Scenario: Diamond dependency
- **WHEN** PDS-100 blocks [PDS-124, PDS-128], and both block PDS-130
- **THEN** PDS-100.impact_radius = 3 (count PDS-130 once, not twice)

### Requirement: Calculate blocker chain depth

The system SHALL calculate how many levels deep each item is in its blocker chain and store it in the `blocker_chain_depth` field.

#### Scenario: Root blocker
- **WHEN** PDS-100 has empty `blocked_by` but non-empty `blocks`
- **THEN** PDS-100.blocker_chain_depth = 0

#### Scenario: Direct blocked item
- **WHEN** PDS-124 has `blocked_by = ["PDS-100"]`
- **THEN** PDS-124.blocker_chain_depth = 1

#### Scenario: Transitive blocked item
- **WHEN** PDS-127 has `blocked_by = ["PDS-124"]` and PDS-124 has `blocked_by = ["PDS-100"]`
- **THEN** PDS-127.blocker_chain_depth = 2

#### Scenario: Multi-blocked item
- **WHEN** PDS-130 has `blocked_by = ["PDS-102", "PDS-105"]` where both are root blockers
- **THEN** PDS-130.blocker_chain_depth = 1 (minimum depth from any blocker)

### Requirement: Identify root blockers

The system SHALL identify root blockers as items that have non-empty `blocks` but empty `blocked_by` fields.

#### Scenario: Root blocker identification
- **WHEN** PDS-100 has `blocked_by = []` and `blocks = ["PDS-124", "PDS-128"]`
- **THEN** PDS-100 is classified as a root blocker

#### Scenario: Blocked item is not root
- **WHEN** PDS-124 has `blocked_by = ["PDS-100"]` and `blocks = ["PDS-127"]`
- **THEN** PDS-124 is NOT classified as a root blocker

#### Scenario: Item with no blocking relationships
- **WHEN** PDS-101 has `blocked_by = []` and `blocks = []`
- **THEN** PDS-101 is NOT classified as a root blocker

### Requirement: Handle circular dependencies gracefully

The system SHALL detect circular blocking dependencies and prevent infinite loops during impact radius and chain depth calculations. Cycle members SHALL be marked with the special value `blocker_chain_depth = -1` (distinct from root=0) and include a "⚠️ CIRCULAR DEPENDENCY" indicator in reports/visualizations.

#### Scenario: Simple circular dependency
- **WHEN** PDS-100 blocks PDS-124, and PDS-124 blocks PDS-100 (invalid Jira state but possible in data)
- **THEN** both items have `blocker_chain_depth = -1` and `impact_radius = 1`, a warning is logged with the cycle path (e.g. "Cycle: PDS-100 → PDS-124 → PDS-100"), and reports show a "⚠️ CIRCULAR DEPENDENCY" badge for affected items.

#### Scenario: Multi-item cycle
- **WHEN** PDS-100 → PDS-124 → PDS-127 → PDS-100 (3-item cycle)
- **THEN** calculation completes without hanging, all items in cycle have depth = -1, cycle is logged as a warning/error with full path, and they are grouped or flagged in "Circular Dependencies" sections of reports.

### Requirement: Optimize impact radius calculation (BFS per root)

The system SHALL compute `impact_radius` using an efficient per-root BFS traversal (O(V+E) for sparse graphs) rather than naive full transitive closure or repeated walks. This achieves ~100× speedup for typical epic sizes (200 items) while correctly counting unique direct + transitive blocked items (diamond deduping preserved).

#### Implementation Guidance
Use a queue-based BFS starting from each root blocker, traversing the pre-computed `.blocks` lists (populated by reverse map), tracking visited to avoid re-counting.

```python
from collections import deque

def _compute_impact_radius(self, items: dict[str, WorkItem], root_key: str) -> int:
    """BFS per root blocker: O(V+E) instead of O(V³)."""
    visited = set()
    queue = deque([root_key])
    count = 0
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        if current in items:
            for blocked_key in items[current].blocks:
                if blocked_key not in visited:
                    queue.append(blocked_key)
                    count += 1
    return count
```

#### Scenario: Transitive + diamond (performance critical)
- **WHEN** large chain or diamond structure (e.g. root blocks 5 direct, each blocks 10 more with overlap)
- **THEN** impact_radius computed correctly and quickly (<150ms target for 200 items); benchmarked vs naive.

#### Scenario: Benchmark validation
- **WHEN** running analysis on 200-item epic
- **THEN** analysis_duration_ms recorded (see observability spec); target <150ms including reverse map + depth + impact.

### Requirement: Emit observability metrics for blocking analysis

After reverse map computation and/or full chain/impact analysis, the system SHALL emit structured `BlockingAnalysisMetrics` (see dedicated `specs/observability/spec.md` for full dataclass and logging contract). This includes items_analyzed, root_blockers_found, max_chain_depth (respecting -1 for cycles), max_impact_radius, analysis_duration_ms, circular_dependencies, cross_epic_blockers, orphaned_blocker_refs.

#### Scenario: Full metrics on successful run
- **WHEN** analysis completes
- **THEN** logger.info("blocking_analysis_complete", extra=metrics.__dict__) (or project-equivalent structured logging) is emitted with accurate values. Metrics are also available for reporters/CLI if needed.

Integration: Called from `BlockingAnalyzer.analyze(...)` (and optionally from collection post-processing for early orphaned counts). Follows existing collector logging style (e.g. "collector.get_epic ...") but uses extra= or structured fields for machine parsing.

### Requirement: Preserve backward compatibility

The system SHALL compute new fields (`blocks`, `blocker_chain_depth`, `impact_radius`) with default values to maintain compatibility with existing code.

#### Scenario: Fields default to safe values
- **WHEN** a Task or WorkItem is created without explicit values for new fields
- **THEN** `blocks = []`, `blocker_chain_depth = 0`, `impact_radius = 0`

#### Scenario: Existing serialization works
- **WHEN** a Task model is serialized to JSON
- **THEN** new fields appear in output with default values if not computed

#### Scenario: Existing code can read models
- **WHEN** existing analyzer code reads a Task with new fields
- **THEN** no errors occur and new fields are accessible via standard attribute access
