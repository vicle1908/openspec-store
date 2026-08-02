## Purpose

This specification defines requirements for Epic Data Collection.

# Epic Data Collection — Specification (Delta)

**Capability:** epic-data-collection
**Status:** Modified
**Date:** 2026-06-02
**Version:** 1.1 (adds blocking relationship post-processing)

---

## Requirements

### Requirement: Comprehensive work item collection

The system SHALL find ALL work items linked to an epic using a 4-phase JQL strategy and SHALL compute reverse blocking relationships after collection completes.

**Phases:**
- Phase 1: Direct children — JQL `(parent = EPIC OR "Epic Link" = EPIC) AND issuetype != Epic`
- Phase 2: Subtasks — JQL `parent in (child_keys...) AND issuetype != Epic` (batched 50 keys/call)
- Phase 3: Linked bugs — JQL `issuetype = Bug AND ("Epic Link" = EPIC OR parent = EPIC OR issue in linkedIssues(EPIC))`
- Phase 4: ~~Project-level bugs~~ **REMOVED** — per-epic analysis focuses on the specific epic only. Project-wide bugs are available via the separate "Blocking Bugs" spreadsheet tab which lists ALL project bugs with blocking relationships.

The system SHALL deduplicate items across phases via key tracking, paginate Phase 1 with `maxResults=100`, extract `blocked_by` from issuelinks, and collect items regardless of status. After all phases complete, SHALL call `_build_reverse_blocking_map()` passing both `child_tasks` and `project_bugs`.

**Implementation:** `epic_report/collector.py:_fetch_via_jql()` + `_jql_paginated()` + `_build_reverse_blocking_map()`

#### Scenario: Reverse map populated after collection
- **WHEN** PDS-124 has `blocked_by = ["PDS-100"]` and PDS-128 has `blocked_by = ["PDS-100"]`
- **THEN** after collection completes, PDS-100.blocks = ["PDS-124", "PDS-128"]

#### Scenario: Deduplication across phases
- **WHEN** same item key appears in Phase 1 and Phase 3
- **THEN** item is included only once in collected results

#### Scenario: All statuses collected
- **WHEN** epic has tasks with status "Done", "Closed", "Cancelled"
- **THEN** all are included in collection regardless of status

#### Scenario: Coverage improvement
- **WHEN** collecting PDS-81 epic
- **THEN** 3-phase collection returns ~199 items vs 77 items from Phase 1 only

#### Scenario: Item appears in multiple collection phases
- **WHEN** the same issue key is returned as a direct child and linked bug
- **THEN** the collected epic contains one normalized item for that key

#### Scenario: Optional collections are empty
- **WHEN** an epic has no subtasks, no linked bugs, or no sprint assignments
- **THEN** collection succeeds with empty or unspecified values
- **AND** downstream analysis can report those states without an exception

**PBT Invariants:**
- No returned task has `issuetype == "Epic"`
- Same key never returned twice across phases
- Pagination handles up to 1000 items per epic
- For all items: if A in B.blocked_by, then B in A.blocks

---


### Requirement: Reverse blocking relationship computation

The system SHALL implement `_build_reverse_blocking_map(items: list[Task]) -> None` in `epic_report/collector.py`. It SHALL iterate all collected items, build a map of `{blocker_key: [blocked_item_keys]}`, populate the `blocks` field on each item, log a warning for any `blocked_by` key not present in the collection, and preserve the existing `blocked_by` field unchanged. SHALL execute after all collection phases complete but before returning the Epic.


#### Scenario: Simple reverse map
- **WHEN** PDS-124 has `blocked_by = ["PDS-100"]` and PDS-128 has `blocked_by = ["PDS-100"]`
- **THEN** after `_build_reverse_blocking_map()`, PDS-100.blocks = ["PDS-124", "PDS-128"]

#### Scenario: No blocking relationships
- **WHEN** PDS-101 has `blocked_by = []` and no items reference it
- **THEN** after computation, PDS-101.blocks = []

#### Scenario: Transitive chain
- **WHEN** PDS-124 has `blocked_by = ["PDS-100"]` and PDS-127 has `blocked_by = ["PDS-124"]`
- **THEN** PDS-100.blocks = ["PDS-124"], PDS-124.blocks = ["PDS-127"]

#### Scenario: Orphaned blocker reference
- **WHEN** PDS-130 has `blocked_by = ["PDS-999"]` but PDS-999 not in collected items
- **THEN** warning logged, PDS-130.blocked_by preserved, no error raised

**Performance:**
- Complexity: O(N×M) where N = item count, M = avg blocked_by length
- Expected: <100ms for 200 items with avg 2 blockers each
- SHALL complete within 1s for epics with up to 1000 items

**Implementation:**
```python
def _build_reverse_blocking_map(items: list[Task]) -> None:
    """Compute reverse blocking relationships."""
    # Build map: blocker_key -> list of blocked item keys
    blocks_map: dict[str, list[str]] = defaultdict(list)
    item_keys = {t.key for t in items}

    for item in items:
        for blocker_key in item.blocked_by:
            if blocker_key not in item_keys:
                logger.warning(f"{item.key} blocked by {blocker_key} not in collection")
            blocks_map[blocker_key].append(item.key)

    # Populate blocks field
    for item in items:
        item.blocks = blocks_map.get(item.key, [])
```

---

## Data Model Changes

### Task Model (epic_report/models.py)

**Existing fields:**
- `blocked_by: list[str] = Field(default_factory=list)` — keys of items blocking this one (from Jira issuelinks)

**NEW fields:**
- `blocks: list[str] = Field(default_factory=list)` — keys of items this one blocks (computed)
- `blocker_chain_depth: int = 0` — depth in blocker chain (0 = root, computed by analyzer)
- `impact_radius: int = 0` — total items blocked (direct + transitive, computed by analyzer)

**Backward compatibility:**
- New fields have defaults, existing code unaffected
- Serialization includes new fields with default values if not computed
- JSON schema backward compatible (new fields optional)

---

## Integration Points

**Upstream (data source):**
- Jira Cloud API `/rest/api/3/issue/{key}` for issuelinks
- `blocked_by` extracted from inward "blocks" or "is blocked by" link types

**Downstream (consumers):**
- `epic_report/analyzers/blocking.py` (NEW) — uses `blocks` field for impact radius calculation
- `epic_report/reporters/sprint_reporter.py` — uses `blocks`, `impact_radius` for Root Blockers table
- `epic_report/dashboard/reporter.py` — uses blocking fields for Dependency Graph section
- `epic_report/reporters/spreadsheet.py` (NEW) — exports blocking fields to Excel sheets

---

## Testing Requirements

**Unit tests (new):**
- `test_build_reverse_blocking_map_simple()` — single blocker with multiple blocked
- `test_build_reverse_blocking_map_chain()` — transitive chain
- `test_build_reverse_blocking_map_empty()` — no blocking relationships
- `test_build_reverse_blocking_map_orphaned()` — blocker not in collection
- `test_build_reverse_blocking_map_circular()` — circular dependency (invalid but handle gracefully)

**Integration tests (modified):**
- `test_get_epic_with_blocking_relationships()` — verify `blocks` field populated after collection
- `test_collect_multiple_epics_with_blocking()` — verify reverse map applied to all epics

**Property-based tests:**
- Invariant: for all items, if A in B.blocked_by, then B in A.blocks
- Invariant: len(A.blocks) = count of items where A in item.blocked_by
- Idempotency: calling `_build_reverse_blocking_map()` twice produces same result

**Observability (P1 per evaluation + new observability/spec.md):**
- Emit or prepare early `BlockingAnalysisMetrics` fields (items, orphaned) during/after map (full emission in analyzer phase per report-generation delta).
- Test log records for metrics (see observability spec tests).

---

## Performance Impact

**Before (v1.0):**
- Epic collection time: ~4.7s for PDS-81 (87 items)
- No post-processing after collection

**After (v1.1):**
- Epic collection time: ~4.8s for PDS-81 (87 items)
- Reverse map computation: <100ms (O(N×M), N=87, M=2)
- Total overhead: <2% increase

**Memory:**
- Additional memory: O(N) for blocks_map dictionary
- Per-item overhead: ~100 bytes for `blocks` list (avg 2 keys × 10 chars each)

---

## Migration Notes

**No migration required:**
- New fields have defaults, backward compatible
- Existing reports continue to work without changes
- New sections only appear if analyzers compute blocking metrics

**Enabling new features:**
1. Upgrade to v1.1 (includes reverse map computation)
2. Reports automatically include blocking data
3. No configuration changes needed
