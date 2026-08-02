# Jira Epic Report Generation - Design

**Status:** ✅ Implemented v2.0
**Date:** 2026-05-19
**Version:** 2.0.0

---

## Overview

Standalone Python/uv package (`epic_report`) that uses `atlassian-python-api` SDK directly.
Modular architecture: CLI → Collector → Analyzers → Reporters. No wrapper layers.

**Design Principle:** Use the official SDK directly. The `epic_report` package consumes
`atlassian-python-api` Jira class for all API communication — no intermediate wrappers.

---

## Architecture

### High-Level Data Flow

```
CLI (typer + rich)                        # epic_report/cli.py — 4 commands
  │
  ├─ Config: AppConfig.from_env()         # epic_report/config.py
  │    └─ auto-loads ~/.tdt/.env
  │
  ├─ Collection                           #
  │    ├─ EpicCollector                   # epic_report/collector.py (Tier 1)
  │    │   ├─ get_issue() → Epic          # TTL cache 300s
  │    │   ├─ epic_issues() → children    # Falls back to JQL for next-gen
  │    │   └─ _fetch_child_tasks()        # Manual JQL pagination @100/page
  │    │
  │    └─ WorkItemCollector               # epic_report/dashboard/collector.py (Tier 2)
  │        ├─ collect_work_items()        # Recursive subtask discovery (max depth 5)
  │        ├─ collect_bugs()              # All bugs in target projects
  │        └─ TTL cache (epics 300s, tasks 900s, subtasks 1800s)
  │
  ├─ Analysis (parallel)                  #
  │    ├─ Tier 1 (4 analyzers)
  │    │   ├─ RiskAnalyzer               # epic_report/analyzers/risk.py — 9 rules
  │    │   ├─ ResourceAnalyzer           # epic_report/analyzers/resource.py — overload + cross-project
  │    │   ├─ TimelineAnalyzer           # epic_report/analyzers/timeline.py — on-track estimation
  │    │   └─ StatusAggregator           # epic_report/analyzers/status.py — weighted completion
  │    │
  │    └─ Tier 2 (3 analyzers — NEW v2.0)
  │        ├─ SprintAnalyzer             # epic_report/analyzers/sprint.py — 18 tests
  │        │   └─ Sprint mapping, allocation report, unallocated detection, capacity
  │        ├─ ProgressTracker            # epic_report/analyzers/progress.py — 18 tests
  │        │   └─ Changelog-based velocity, status transitions, staleness detection
  │        └─ EscalationDetector         # epic_report/analyzers/escalation.py
  │            └─ Blocker chains, staleness >60d, unassigned near deadline, mitigation
  │
  ├─ Models: Pydantic v2                  # epic_report/models.py — 9 models
  │    ├─ TaskStatus (StrEnum): 8 statuses + _missing_ alias handler
  │    ├─ RiskSeverity (StrEnum): CRITICAL, HIGH, MEDIUM, LOW, NONE
  │    ├─ Task: key, status, assignee, blocked_by, story_points, etc.
  │    ├─ Epic: child_tasks, computed fields (completion_pct, task_count, etc.)
  │    ├─ Risk: type, severity, epic, task, description, impact, recommendation
  │    ├─ Report: epics, risks, recommendations, resource_utilization, timeline_analysis
  │    ├─ WorkItem: key, type, summary, status, assignee, sprint, age, parent_key
  │    ├─ SprintInfo: name, goal, start_date, end_date, item_count, completion_pct
  │    └─ DashboardReport: work_items, sprint_data, progress_entries, escalations
  │
  └─ Output                                #
       ├─ Tier 1 reporters
       │   ├─ markdown.py                 # generate_full_report() — epic_report.md (375 lines)
       │   ├─ json_reporter.py            # generate_json_report() — Pydantic serialization
       │   ├─ html_reporter.py           # generate_html() — standalone HTML + CSS
       │   └─ pdf_reporter.py            # generate_pdf() — weasyprint
       │
       └─ Tier 2 reporter
           └─ dashboard/reporter.py       # DashboardReporter — 6 sections, dashboard.md (82 lines)
```

### Package Layout

```
epic_report/                           # 21 production .py files
├── __init__.py
├── __main__.py                        # python -m epic_report
├── cli.py                             # 4 commands: generate, dashboard, list-epics, show-config
├── models.py                          # 9 models: TaskStatus, RiskSeverity, Task, Epic, Risk, Report, WorkItem, SprintInfo, DashboardReport
├── collector.py                       # EpicCollector (Tier 1)
├── config.py                          # AppConfig, CacheConfig, RiskConfig, OutputConfig
├── analyzers/
│   ├── __init__.py
│   ├── risk.py                        # RiskAnalyzer — 9 detection rules
│   ├── resource.py                    # ResourceAnalyzer — overload + cross-project
│   ├── timeline.py                    # TimelineAnalyzer — days-remaining, on-track
│   ├── status.py                      # StatusAggregator — weighted completion
│   ├── sprint.py                      # SprintAnalyzer — sprint mapping, allocation (18 tests)
│   ├── progress.py                    # ProgressTracker — changelog velocity, staleness (18 tests)
│   └── escalation.py                  # EscalationDetector — blockers, staleness, mitigation
├── reporters/
│   ├── __init__.py
│   ├── markdown.py                    # generate_full_report() — Tier 1 MD
│   ├── json_reporter.py              # generate_json_report()
│   ├── html_reporter.py              # generate_html()
│   └── pdf_reporter.py               # generate_pdf()
└── dashboard/
    ├── __init__.py
    ├── collector.py                   # WorkItemCollector — recursive subtasks + bugs
    └── reporter.py                    # DashboardReporter — 6 sections (MD + HTML)

tests/                                 # 14 test files
├── conftest.py                        # Shared test fixtures
├── test_models.py
├── test_collector.py
├── test_cli.py
├── test_config.py
├── analyzers/
│   ├── test_risk.py
│   ├── test_resource.py
│   ├── test_timeline.py
│   └── test_status.py
└── reporters/
    ├── test_markdown.py
    └── test_json.py
```

---

## Key Design Decisions

### 1. atlassian-python-api SDK (not wrapper)
Uses `atlassian.Jira` class directly. Methods: `get_issue()` for metadata,
`epic_issues()` for children, `jql()` for advanced queries.
Benefits: official support, type safety, active maintenance, no wrapper overhead.

### 2. TTL Caching
Module-level `cachetools.TTLCache` instances (`_epic_cache`, `_task_cache`).
Epic TTL=300s, sprint TTL=900s, subtask TTL=1800s. Shared across collector instances.
Invalidated via `invalidate_cache()`.

### 3. Constructor Injection
Analyzers accept config at construction:
- `RiskAnalyzer(cutoff_date=...)` — supports `--no-risks` flag
- `ResourceAnalyzer(overload_threshold=5)` — supports `--no-resources` flag
- `SprintAnalyzer(board_id=...)` — supports Agile API board targeting

### 4. Status-Weighted Completion
Not raw done/total. Weights: Done=100, In Progress=70, QA=60, Ready=50, To Do=20, Draft=0.
More accurate representation of actual progress than simple counting.

### 5. TaskStatus Aliases
Jira returns status names that don't match enum: `"To do"` (lowercase), `"READY TO DEVELOP"`,
`"Rejected/Duplicated"`. `TaskStatus._missing_()` classmethod handles case-insensitive
matching + known aliases.

### 6. Reports Path Auto-Detection
`_find_workspace_root()` walks up from CWD looking for `.agents/` or `openspec/` markers.
Reports auto-save to `tdt/reports/epics/{project}_{date}_epic_report.{ext}`.
No `--output` flag needed for standard use.

### 7. Two-Tier Architecture (v2.0)
Tier 1 (`generate`): fast, lightweight — epics + direct children, 4 analyzers, 4 reporters.
Tier 2 (`dashboard`): comprehensive — recursive work items, bugs, sprints, progress, escalations.
Separate collectors and reporters per tier to keep concerns isolated.

---

## Interface Contracts

### Collector → Analyzers
- `EpicCollector.get_epic(key) → Epic` (with populated `child_tasks` list)
- `WorkItemCollector.collect_all(epic_keys) → list[WorkItem]` (recursive, max depth 5)

### Analyzers → Report
- `RiskAnalyzer.analyze_epics(list[Epic]) → list[Risk]`
- `ResourceAnalyzer.analyze(list[Epic]) → dict[str, dict]`
- `TimelineAnalyzer.analyze_all(list[Epic]) → dict[str, dict]`
- `StatusAggregator.aggregate(list[Epic]) → dict`
- `SprintAnalyzer.analyze(list[WorkItem]) → list[SprintInfo]`
- `ProgressTracker.track(list[WorkItem]) → list[ProgressEntry]`
- `EscalationDetector.detect(list[WorkItem], list[SprintInfo]) → list[Escalation]`

### Reporters
All accept report models and return `str` (or `bytes` for PDF):
- `generate_full_report(report) → str`
- `generate_json_report(report) → str`
- `generate_html(report) → str`
- `generate_pdf(report) → bytes`
- `DashboardReporter.generate(dashboard_report) → str`

---

## Error Handling

- `epic_issues()` fails → falls back to JQL with `parent = "{key}" OR "Epic Link" = "{key}"`
- JQL pagination: 100 results per page, loops until `< max_results`
- Cache miss → `_mock_epic_data()` returns minimal stub (key + default fields)
- PDF: weasyprint OSError → descriptive message with brew install hint
- Config: `validate()` returns error list, `is_configured` property for quick check
- Sprint API failures → graceful degradation, returns empty sprint list

## Performance

| Metric | Value |
|--------|-------|
| 5 epics, 35 tasks (Tier 1) | ~4.7s (live Jira) |
| 5 epics, 150+ work items (Tier 2) | <60s (live Jira) |
| Test suite (217 tests) | ~3.5s (mocked) |
| Coverage | 71% |
| Report generation | <5s (Tier 1), <10s (Tier 2) |

---

**Version:** 2.0.0
**Status:** ✅ Aligned with codebase (217 tests, 71% coverage, 21 prod files, 14 test files)
