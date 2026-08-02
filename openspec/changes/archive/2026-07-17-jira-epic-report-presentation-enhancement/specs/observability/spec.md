# Observability for Blocking Analysis — Specification

**Capability:** observability
**Status:** New (P1 from evaluation)
**Date:** 2026-06-03

## ADDED Requirements

### Requirement: Emit structured metrics after blocking analysis

The system SHALL emit structured logging metrics after reverse blocking map computation and/or blocker chain analysis using a `BlockingAnalysisMetrics` dataclass (or equivalent).

#### Data Model

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class BlockingAnalysisMetrics:
    """Structured metrics for blocking dependency analysis (for observability)."""
    epic_key: str
    items_analyzed: int
    root_blockers_found: int
    max_chain_depth: int
    max_impact_radius: int
    analysis_duration_ms: int
    circular_dependencies: int
    cross_epic_blockers: int
    orphaned_blocker_refs: int = 0
```

#### Scenario: Successful analysis with metrics
- **WHEN** blocking analysis completes for epic PDS-81 with 199 items, 2 roots, max depth 3, max impact 12, 1 cycle, duration 87ms
- **THEN** logger emits:
  ```python
  logger.info("blocking_analysis_complete", extra=metrics.__dict__)
  ```
  or equivalent structured log with all fields populated accurately.

#### Scenario: Analysis with circular dependencies
- **WHEN** cycle detected during chain resolution
- **THEN** `circular_dependencies` incremented, warning logged with cycle path, metrics still emitted with depth=-1 items counted appropriately.

#### Scenario: Large epic or dashboard collection
- **WHEN** analysis on 500+ items (possibly cross-epic via dashboard collector)
- **THEN** metrics include `cross_epic_blockers` count, duration tracked, no performance degradation beyond targets.

#### Scenario: Metrics in collection phase
- **WHEN** `_build_reverse_blocking_map` completes (in epic-data-collection)
- **THEN** basic metrics (items, orphaned count) may be logged or passed to analyzer for full emission.

### Requirement: Use consistent structured logging

The system SHALL use the project's existing logger (with info/warning + structured fields or extra=) for blocking metrics and warnings. No new dependencies.

#### Scenario: Logged analysis with structured fields
- **WHEN** blocking analysis completes for epic PDS-81 with 87ms duration and 2 root blockers
- **THEN** logger emits `logger.info("blocking_analysis_complete", extra={"epic_key": "PDS-81", "items_analyzed": 199, "duration_ms": 87, "root_blockers_found": 2})` following collector.py patterns
- **AND** `extra=metrics.__dict__` is used for Prometheus, CloudWatch, or log aggregation compatibility

### Requirement: Expose metrics for monitoring and dashboards

Metrics SHALL be usable for:
- Post-report logging visible in CLI output or logs.
- Integration with project monitoring (future: count circulars, avg impact per epic, etc.).
- Debugging: high duration or many circulars trigger warnings.

#### Scenario: High impact or slow analysis warning
- **WHEN** max_impact_radius > 50 or analysis_duration_ms > 300
- **THEN** additional logger.warning("blocking_analysis_high_impact", extra=...) emitted.

### Integration Points

**Upstream:**
- `epic_report/collector.py` (after phases in `get_epic`, and for project_bugs + child_tasks)
- `epic_report/dashboard/collector.py` (WorkItemCollector post-processing for dashboard reports, if blocking enabled)

**Downstream (consumers of metrics):**
- `epic_report/analyzers/blocking.py` (BlockingAnalyzer.analyze emits full metrics)
- Reporters (optionally surface summary metrics in reports or logs)
- CLI (generate/insights may log final metrics)
- Tests (assert on captured log records for metrics fields)

**Observability in reports (enhanced-report-sections):**
- Optionally include summary stats (e.g. "Analysis: 87ms, 2 roots, 1 circular") in Blocking Status section or dashboard.

### Performance & Non-Functional

- Metrics emission must be <5ms overhead (simple dataclass + log).
- Must not affect core analysis time targets (<150ms for 200 items).
- Support both epic-specific and cross-epic (dashboard) collections.

### Testing Requirements

**Unit tests:**
- `test_blocking_metrics_emitted_on_success`
- `test_blocking_metrics_circular_count`
- `test_blocking_metrics_orphaned_and_cross_epic`
- Verify log record contains expected extra fields / structured data.

**Integration tests:**
- Full get_epic + analyzer flow captures correct metrics.
- Dashboard collect_all with blocking items emits cross-epic metrics.

**Property-based / benchmarks:**
- Metrics always consistent with computed roots/depth/impact (cross-check).
- No regression on analysis time when metrics enabled.

### Backward Compatibility

- Metrics are additive (observability only); no changes to models, reports, or public APIs unless explicitly logged.
- Existing log consumers unaffected (new log lines).

## Migration / Rollout Notes

- Add in Phase 1 (core analysis) alongside BlockingAnalyzer and reverse map.
- Default on; no config flag needed initially (can add `EPIC_REPORT_DISABLE_BLOCKING_METRICS` if needed for perf troubleshooting).
- Document in EVALUATION.md / README.md success metrics section.

## References

- EVALUATION.md (P1: Observability & Telemetry)
- design.md (BlockingAnalyzer decision)
- tasks.md (new observability tasks)
- collector.py and escalation.py current logging patterns
- jira-daily-reports for similar structured logging + gws patterns (reuse mindset)
