# Status Aggregation - Specification

**Capability:** status-aggregation  
**Status:** Draft  
**Date:** 2026-05-18  
**Version:** 1.0

---


## ADDED Requirements

### Requirement: status-aggregation specification applies unchanged

The status-aggregation contract documented below SHALL apply unchanged for
this delta. The OpenSpec delta section above is the canonical delta
declaration; the FR-N items and SDK Contract Requirements below are
preserved verbatim from the pre-delta-era authoring of this
specification.

#### Scenario: status-aggregation is implemented per the FR-N contract below

The status-aggregation is implemented per the FR-N contract below.

---


## Overview

The system SHALL aggregate task statuses across epics, calculate weighted completion percentages, and produce cross-epic health summaries.

---

## Functional Requirements

### FR-1: Task Status Breakdown

**Description:** Count tasks by status category per epic.

**Requirements:**
- SHALL categorize tasks into: Done, Closed, In Progress, In Review, QA, Ready, To Do, Draft
- SHALL count tasks per category per epic
- SHALL include category counts in Report model

**PBT Properties:**
- Invariant: sum(all category counts) == total child tasks for epic
- Idempotency: same epic data always produces same breakdown

---

### FR-2: Weighted Completion Percentage

**Description:** Calculate epic completion using status-weighted scoring.

**Requirements:**
- SHALL use weight mapping:
  - Done/Closed: 100
  - In Review: 75
  - In Progress: 70
  - QA: 60
  - Ready: 50
  - To Do: 20
  - Draft: 0
- SHALL compute: `round(sum(weights[task.status]) / len(tasks))`
- SHALL return 0 for epics with no child tasks
- SHALL cap result at 100 (never exceeds 100%)

**PBT Properties:**
- Invariant: completion_pct is always in range [0, 100]
- Monotonicity: changing a task to a higher-weight status never decreases completion_pct
- Round-trip: completion_pct calculation is deterministic for same input

**Example:**
```python
from epic_report.analyzers.status import StatusAggregator

aggregator = StatusAggregator()
pct = aggregator.calculate_completion_weighted(tasks)
print(f"Epic completion: {pct}%")
```

---

### FR-3: Cross-Epic Aggregation

**Description:** Group and summarize metrics across multiple epics.

**Requirements:**
- SHALL group epics by project key
- SHALL compute portfolio-level metrics:
  - Total epics, total tasks, total done
  - Average completion percentage
  - Overall risk level (highest severity across epics)
- SHALL support filtering by project, version, status

---

### FR-4: Epic Health Score (Future Enhancement)

> **Status:** Composite health classification deferred. Baseline reports completion %, risk score, and resource utilization separately.


**Description:** Derive composite health indicator per epic.

**Requirements:**
- SHALL combine: completion_pct, risk_score, resource_utilization
- SHALL produce health level: Healthy, Warning, Critical
- Health thresholds:
  - Healthy: risk_score < 5 AND completion_pct >= 60%
  - Warning: risk_score < 10 OR completion_pct >= 30%
  - Critical: risk_score >= 10 AND completion_pct < 30%

---

### FR-5: Resource Utilization Tracking

**Description:** Aggregate workload data per assignee across epics.

**Requirements:**
- SHALL count tasks per assignee across all analyzed epics
- SHALL list which projects each assignee is involved in
- SHALL flag assignees with > 5 active tasks as overloaded
- SHALL generate workload balancing recommendations

---

### FR-6: Subtask Completion Tracking (Future Enhancement)

> **Status:** Composite health classification deferred. Baseline reports completion %, risk score, and resource utilization separately.


**Description:** Track recursive subtask completion and flag blocking subtrees.

**Requirements:**
- SHALL recursively collect subtasks for each task via BFS traversal
- SHALL compute subtask completion ratio per issue
- SHALL flag issues with incomplete subtasks (`blocking=true`) for health score penalties
- SHALL apply penalty of -10 health points when >50% of subtasks are incomplete
- SHALL report subtask status breakdown (Done, In Progress, To Do counts) per issue

**Data Model:**
```python
@dataclass
class SubtaskAnalysis:
    total: int = 0
    completed: int = 0
    incomplete: int = 0
    blocking: bool = False
    status_breakdown: dict[str, int] = {}
```

**Dependencies:** `epic_report.models.SubtaskAnalysis`, `epic_report.dashboard.collector.WorkItemCollector`

---

## Dependencies

- `epic_report.models` - Epic, Task, Report, SubtaskAnalysis models
- `epic_report.collector` - Data source
- `epic_report.analyzers.risk` - Risk scores for health calculation
