## Purpose

This specification defines requirements for Risk Analysis.

# Risk Analysis - Specification

**Capability:** risk-analysis  
**Status:** Draft  
**Date:** 2026-05-18  
**Version:** 1.0

---


## Requirements

### Requirement: risk-analysis specification applies unchanged

The risk-analysis contract documented below SHALL apply unchanged for
this delta. The OpenSpec delta section above is the canonical delta
declaration; the FR-N items and SDK Contract Requirements below are
preserved verbatim from the pre-delta-era authoring of this
specification.

#### Scenario: risk-analysis is implemented per the FR-N contract below

The risk-analysis is implemented per the FR-N contract below.

---


## Overview

The system SHALL analyze collected epic and task data to identify risks, compute severity-weighted scores, and provide actionable recommendations.

---

## Functional Requirements

### FR-1: Weighted Risk Scoring

**Description:** Calculate composite risk scores using a 9-factor weighted algorithm.

**Requirements:**
- SHALL define `RISK_WEIGHTS` mapping risk types to integer weights:
  - `UNASSIGNED_TASK`: 3
  - `UNASSIGNED_NEAR_DEADLINE`: 5 (task unassigned AND < 7 days to cut-off)
  - `PLANNING_INCOMPLETE`: 4 (child tasks in Draft status while epic is In Progress)
  - `NO_SPRINT_ALLOCATION`: 3 (tasks without sprint assignment when cut-off date exists)
  - `RESOURCE_OVERLOAD`: 4 (assignee with > 5 active tasks across epics)
  - `TIMELINE_AT_RISK`: 5 (completion < 30% AND days to cut-off < 7)
  - `MISSING_INFO`: 2 (no description, no Figma link, no URS link)
  - `BLOCKED_TASK`: 5 (task has "blocked by" issue links)
  - `CROSS_PROJECT_CONFLICT`: 3 (same assignee across 2+ projects in report)
- SHALL compute total risk score as sum of all detected risk weights
- SHALL map total score to severity level:
  - `score >= 15` -> CRITICAL
  - `score >= 10` -> HIGH
  - `score >= 5` -> MEDIUM
  - `score < 5` -> LOW

**PBT Properties:**
- Invariant: risk score is always non-negative integer
- Monotonicity: adding more detected risks never decreases total score
- Bounds: max possible score = sum(all RISK_WEIGHTS values) = 34

---

### FR-2: Unassigned Task Detection

**Description:** Identify tasks without assignees, especially those near deadlines.

**Requirements:**
- SHALL detect tasks where `assignee is None` or `assignee == ""` in To Do, Ready, and Draft statuses (pre-execution states only)
- SHALL flag unassigned tasks near cut-off date (< 7 days remaining) as HIGH risk
- SHALL include task key, epic key, and days remaining in risk output
- SHALL NOT flag tasks with status "Done", "Closed", "In Progress", "QA", or "In Review" (execution-phase states)

---

### FR-3: Planning Completeness Check

**Description:** Detect epics with incomplete planning indicators.

**Requirements:**
- SHALL flag epics with status "In Progress" that have child tasks in "Draft" status
- SHALL calculate planning completeness ratio: `non_draft_tasks / total_tasks`
- SHALL include ratio in risk description

---

### FR-4: Sprint Allocation Gap Detection

**Description:** Identify tasks not assigned to any sprint when a cut-off date exists.

**Requirements:**
- SHALL only activate when `cutoff_date` is provided
- SHALL detect tasks with `sprint_id is None`
- SHALL count unallocated tasks per epic

---

### FR-5: Resource Overload Detection

**Description:** Identify team members with excessive workload.

**Requirements:**
- SHALL count active tasks per assignee across ALL epics in report
- SHALL flag assignees with > 5 active tasks (configurable threshold)
- SHALL calculate overload severity: `(task_count - threshold) / threshold`
- SHALL NOT count tasks with status "Done" or "Closed" as active

---

### FR-6: Timeline Risk Assessment

**Description:** Evaluate whether epic completion timeline is at risk.

**Requirements:**
- SHALL calculate weighted completion percentage (see status-aggregation spec)
- SHALL compare days remaining to cut-off date
- SHALL flag as HIGH risk when: `completion_pct < 30% AND days_remaining < 7`
- SHALL flag as MEDIUM risk when: `completion_pct < 50% AND days_remaining < 14`

---

### FR-7: Blocked Task Detection

**Description:** Identify tasks with blocking dependencies.

**Requirements:**
- SHALL check `issuelinks` field for "blocks" and "blocked by" relationships
- SHALL count blocking dependencies per task
- SHALL flag tasks with any unresolved blocker

---

### FR-8: Cross-Project Conflict Detection

**Description:** Identify resource conflicts across projects.

**Requirements:**
- SHALL group tasks by assignee across all epics
- SHALL detect assignees working on 2+ different projects
- SHALL flag potential context-switching overhead

---

### FR-9: Missing Information Detection

**Description:** Identify epics with incomplete documentation.

**Requirements:**
- SHALL check for empty description
- SHALL check for missing Figma URL
- SHALL check for missing URS URL
- SHALL flag each missing element separately

---

## Risk Output Model

```python
@dataclass
class Risk:
    id: str                        # e.g., "RISK-001"
    type: str                      # From RISK_WEIGHTS keys
    severity: RiskSeverity         # CRITICAL, HIGH, MEDIUM, LOW
    epic: str                      # Parent epic key
    task: str | None               # Related task key (optional)
    description: str               # Human-readable description
    impact: str                    # Business impact if not addressed
    recommendation: str            # Actionable recommendation
    detected_at: datetime          # Detection timestamp
```

## Dependencies

- `epic_report.models` - Risk, RiskSeverity, Epic, Task models
- `epic_report.collector` - Epic data source

---

### FR-10: Blocker Chain Risk (Future Enhancement)

> **Status:** Transitive blocker chain detection deferred. Current baseline detects single-level blockers via `BLOCKED_TASK` weight (FR-7).


**Description:** Detect transitive blocker chains and circular dependencies.

**Requirements:**
- SHALL traverse `issuelinks` for "blocks" and "blocked by" link types recursively
- SHALL compute blocker chain depth per issue
- SHALL detect circular dependencies (A blocks B blocks A)
- SHALL assign `BLOCKER_CHAIN` risk weight = 6 for items with chain depth >= 2
- SHALL assign `CIRCULAR_DEPENDENCY` risk weight = 8 for detected cycles
- SHALL identify root blockers (blocking others but not blocked)
- SHALL display blocker relationships in risk output with indented chain notation

---

### FR-11: Configurable Risk Weights

**Description:** Allow per-project risk weight tuning via configuration.

**Requirements:**
- SHALL load risk weights from `~/.tdt/epic-report-config.toml` under `[projects.X.risk_weights]`
- SHALL merge project-specific weights with base `RISK_WEIGHTS` (project overrides take priority)
- SHALL validate weight values (must be positive numbers)
- SHALL accept risk weights as optional parameter to `RiskAnalyzer.__init__`
- SHALL recalculate severity thresholds using custom weights:
  - `total_score >= 15` -> CRITICAL
  - `total_score >= 10` -> HIGH
  - `total_score >= 5` -> MEDIUM
  - `total_score < 5` -> LOW

