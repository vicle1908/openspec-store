# jira-epic-report-generation - Index

**Status:** ✅ Implemented v2.0
**Tests:** 217/217 passing, 71% coverage
**Date:** 2026-05-19
**Version:** 2.0.0

---

## Quick Navigation

### 📋 Planning Documents

- [Proposal](./proposal.md) — Business justification and ROI analysis
- [Specification](./spec.md) — Complete functional & non-functional specs (v2.0.0)
- [Design](./design.md) — Architecture and component design
- [Tasks](./tasks.md) — Implementation task breakdown

### 📁 Implementation

- `epic_report/` — Python package (21 files)
- `tests/` — pytest test suite (14 files, 217 tests)
- Dependencies: `atlassian-python-api>=3.41.16`, `pydantic`, `typer`, `rich`, `jinja2`, `weasyprint`, `markdown`

### 🎯 Quick Links

- [Feature Matrix](#feature-matrix)

---

## Overview

Automated Jira epic report generation system that analyzes epics across multiple projects,
identifies risks, tracks resource utilization, and generates comprehensive reports with
actionable recommendations in 4 formats. Tier 2 adds recursive work item collection, sprint
analysis, progress tracking, escalation detection, and a full dashboard report.

**Built with:** Python 3.12+, uv, typer, rich, pydantic, jinja2, weasyprint
**SDK:** `atlassian-python-api>=3.41.16` (official Jira Cloud SDK)
**Purpose:** Cross-epic, multi-project risk analysis and executive reporting
**Output path:** `tdt/reports/epics/` (auto-created)

---

## Key Design Decisions

1. **atlassian-python-api SDK** — Official Atlassian Python SDK for Jira Cloud.
   No wrapper layer needed. Uses `Jira.get_issue()`, `Jira.epic_issues()`, `Jira.jql()`.

2. **Constructor injection** — Analyzers accept `cutoff_date` and `overload_threshold`
   as constructor params, allowing `--no-risks` / `--no-resources` flags.

3. **TTL caching** — `cachetools.TTLCache` with 300s epic TTL, 900s sprint TTL, 1800s subtask TTL.
   Module-level shared across collector instances.

4. **Status-weighted completion** — Not raw count. Weights: Done=100, In Progress=70,
   QA=60, Ready=50, To Do=20, Draft=0. More accurate than simple done/total.

5. **TaskStatus aliases** — Handles Jira variants (`To do`, `READY TO DEVELOP`,
   `Rejected/Duplicated`) via `_missing_` classmethod.

6. **JQL fallback** — `epic_issues()` fails on next-gen projects → falls back to
   `parent = "{key}" OR "Epic Link" = "{key}"` JQL with manual pagination.

7. **Default reports path** — Auto-detects workspace root via `.agents/` marker,
   saves to `tdt/reports/epics/{project}_{date}_epic_report.{ext}`.

8. **Two-tier architecture** — Tier 1 (`generate`): fast, lightweight epic health.
   Tier 2 (`dashboard`): comprehensive with recursive work items, bugs, sprints,
   progress tracking, and escalation detection.

---

## Feature Matrix

| Feature | Status | Format |
|---------|--------|--------|
| Epic data collection (Tier 1) | ✅ | Jira Cloud API |
| Recursive work item collection (Tier 2) | ✅ | Subtasks + bugs, max depth 5 |
| 9 risk detection rules | ✅ | Python analyzers |
| Resource utilization | ✅ | Per-assignee, cross-project |
| Timeline analysis | ✅ | Days remaining, on-track, est. completion |
| Sprint alignment | ✅ | SprintAnalyzer — mapping, allocation, capacity |
| Progress tracking | ✅ | ProgressTracker — changelog velocity, staleness |
| Escalation detection | ✅ | EscalationDetector — blockers, staleness >60d |
| Dashboard report | ✅ | DashboardReporter — 6 sections MD + HTML |
| Markdown report | ✅ | epic_report.md (375 lines) |
| JSON report | ✅ | Pydantic serialization |
| HTML report | ✅ | Standalone, embedded CSS |
| PDF report | ✅ | weasyprint |
| CLI (4 commands) | ✅ | generate, dashboard, list-epics, show-config |
| Configuration | ✅ | env vars + `~/.tdt/.env` |
| Auto-save path | ✅ | `tdt/reports/epics/` |
| Test coverage | ✅ | 71% (217/217 passing) |

---

## Spec Alignment

All 11 functional requirements met. 4/5 NFRs met (coverage at 71%, targeting ≥80%).

Delivered beyond spec: PDF output, HTML report, auto-save reports path, recursive subtask
discovery, sprint analysis, progress tracking, escalation detection.
