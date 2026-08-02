# Jira Epic Report Generation — Specification v2.0

**Status:** ✅ Implemented v2.1
**Date:** 2026-05-19
**Coverage:** 72% (217/217 tests pass)

---

## Overview

Two-tier reporting system with per-epic dedicated reports and cross-linked navigation for Jira epic analysis:

| Tier | Tool | Use case | Depth |
|------|------|---------|-------|
| **Tier 1** | `epic-report generate` | Quick epic health check | Epics + direct children |
| **Tier 2** | `epic-report dashboard` | Full project command center | Recursive work items, bugs, sprints, progress, escalations |

Both tiers complete. v2.0 adds recursive WorkItemCollector, SprintAnalyzer, ProgressTracker, EscalationDetector, and DashboardReporter.

---

## Architecture v2.0

```
epic-report CLI (typer + rich)
├── generate — Tier 1: quick epic health
├── dashboard — Tier 2: full project command center (MD + HTML)
├── Per-epic pages — AUTO: one report per epic with nav (MD + HTML)
│   ├── WorkItemCollector (recursive subtask + bug scanning)
│   ├── SprintAnalyzer (Agile API, sprint mapping, velocity)
│   ├── ProgressTracker (changelog analysis, daily status)
│   ├── EscalationDetector (staleness, blockers, unassigned)
│   └── DashboardReporter (MD + HTML output)
├── list-epics — existing
└── show-config — existing
```

### Package Layout

```
epic_report/
├── cli.py                    # 4 commands: generate, dashboard, list-epics, show-config
├── models.py                 # 9 models: TaskStatus, RiskSeverity, Task, Epic, Risk, Report, WorkItem, SprintInfo, DashboardReport
├── collector.py              # EpicCollector (Tier 1) + WorkItemCollector (Tier 2)
├── config.py                 # AppConfig, CacheConfig, RiskConfig, OutputConfig
├── analyzers/
│   ├── risk.py               # RiskAnalyzer — 9 detection rules (284 lines)
│   ├── resource.py           # ResourceAnalyzer — overload detection (93 lines)
│   ├── timeline.py           # TimelineAnalyzer — on-track estimation (79 lines)
│   ├── status.py             # StatusAggregator — weighted completion (53 lines)
│   ├── sprint.py             # SprintAnalyzer — sprint mapping, allocation, capacity (18 tests)
│   ├── progress.py           # ProgressTracker — changelog-based velocity, staleness (18 tests)
│   └── escalation.py         # EscalationDetector — blockers, staleness, unassigned
├── reporters/
│   ├── markdown.py           # generate_full_report() — Tier 1 MD
│   ├── json_reporter.py      # generate_json_report()
│   ├── html_reporter.py      # generate_html()
│   └── pdf_reporter.py       # generate_pdf()
└── dashboard/
    ├── __init__.py
    ├── collector.py           # recursive WorkItemCollector
    └── reporter.py            # DashboardReporter — 6 sections
```

---

## Functional Requirements v2.0

### FR-1: Epic Data Collection ✅
Collect epic metadata and direct child tasks from Jira Cloud.

### FR-2: Risk Analysis ✅
9 risk detection rules: UNASSIGNED_TASK, UNASSIGNED_NEAR_DEADLINE, PLANNING_INCOMPLETE, TIMELINE_AT_RISK, BLOCKED_TASK, RESOURCE_OVERLOAD, NO_SPRINT_ALLOCATION, CROSS_PROJECT_CONFLICT, MISSING_INFO.

### FR-3: Status Aggregation ✅
Weighted completion: Done=100, In Progress=70, QA=60, Ready=50, To Do=20, Draft=0.

### FR-4: Report Generation ✅
4 formats: Markdown, JSON, HTML, PDF. Auto-save to `tdt/reports/epics/`.

### FR-5: CLI Interface ✅
4 commands: `generate`, `dashboard`, `list-epics`, `show-config`.

### FR-6: Configuration ✅
Env-based config auto-loaded from `~/.tdt/.env`.

### FR-7: Work Item Collection ✅
Collect ALL work items across 5 epics (3 projects) — not just direct children.

- **FR-7.1: Recursive subtask discovery** — Starting from epic → direct children → subtasks → sub-subtasks. Max depth 5.
- **FR-7.2: Bug collection** — All bugs in PDS, AM, TJ projects (not necessarily linked to epics).
- **FR-7.3: Work item model** — Unified model: key, type, summary, status, assignee, sprint, story points, age, parent key, subtask list, linked issues.
- **FR-7.4: Caching** — TTL cache per item type (epics 300s, tasks 900s, subtasks 1800s).

### FR-8: Sprint Alignment ✅
Map all work items to sprints and provide sprint-level planning data.

- **FR-8.1: Sprint discovery** — Fetch boards → active/future sprints with dates, goals, item counts.
- **FR-8.2: Sprint allocation report** — Per sprint: item count by type, assignee workload, completion %.
- **FR-8.3: Unallocated items** — Items with no sprint assignment, grouped by epic.
- **FR-8.4: Sprint capacity** — Items per sprint vs. historical velocity.

### FR-9: Progress Tracking ✅
Track daily progress using Jira changelogs and created/updated timestamps.

- **FR-9.1: Status transition history** — Per item: status changes with timestamps and authors.
- **FR-9.2: Velocity calculation** — Items moved to Done per week from changelog data.
- **FR-9.3: Daily status** — On track / off track per epic based on completion trend.
- **FR-9.4: Staleness flag** — Items >30d in non-terminal status are flagged stale.

### FR-10: Escalation & Risk ✅
Identify escalation points and mitigation strategies from factual Jira data.

- **FR-10.1: Escalation triggers** — Unassigned near deadline, blocked items, stale items >60d, overloaded assignees.
- **FR-10.2: Blocker chain analysis** — Items blocked by other items → identify root cause blocker.
- **FR-10.3: Impact assessment** — Per escalation: affected epics, assignees, sprint impact.
- **FR-10.4: Mitigation recommendations** — Actionable steps based on detected patterns.

### FR-11: Dashboard Report ✅
Single comprehensive MD/HTML report covering all dimensions.

- **FR-11.1: Executive dashboard** — 1-page summary: item counts, risk level, sprint status, completion %.
- **FR-11.2: Epic detail with full work tree** — Epic → tasks → subtasks (indented, with status/assignee).
- **FR-11.3: Sprint planning view** — Items grouped by sprint, with allocation gaps highlighted.
- **FR-11.4: Progress view** — Status distribution, changelog-derived velocity, on/off-track indicators.
- **FR-11.5: Escalation register** — Table of escalation points with severity, owner, mitigation.
- **FR-11.6: Bug radar** — Bug count by project, grouped by status.

---

## Non-Functional Requirements

| NFR | Requirement | Status |
|-----|-----------|--------|
| NFR-1 | Performance: dashboard <60s for 5 epics | ✅ |
| NFR-2 | Test coverage >80% | ⚠️ 71% (217/217 pass) |
| NFR-3 | Type hints on all public APIs | ✅ Pydantic v2 + type hints |
| NFR-4 | No credentials in code or logs | ✅ |
| NFR-5 | Python 3.12+, macOS/Linux | ✅ |

---

## Success Criteria

### Functional (11 requirements)
- [x] FR-1..FR-6: Tier 1 epic health check (v1.0 ✅)
- [x] FR-7: Recursive work item collection (subtasks + bugs)
- [x] FR-8: Sprint alignment with Agile API data
- [x] FR-9: Changelog-based progress tracking
- [x] FR-10: Escalation detection with mitigation
- [x] FR-11: Comprehensive dashboard report (MD + HTML)

### Non-Functional
- [x] <60s dashboard generation (Tier 1 ~4.7s)
- [ ] ≥80% test coverage (currently 71%, 217/217 pass)
- [x] All public APIs typed
- [x] No credentials leaked
- [x] Cross-platform

---

**Version:** 2.0.0
**Last Updated:** 2026-05-19
**Status:** ✅ Implemented v2.1
