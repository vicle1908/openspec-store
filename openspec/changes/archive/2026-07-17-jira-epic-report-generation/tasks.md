# Jira Epic Report Generation — Implementation Tasks v2.0

**Status:** 🔧 Phase 5-8 in progress
**Date:** 2026-05-19
**Coverage:** 88% (v1.0) — targeting ≥80% for v2.0

---

## Phase 1-4: Tier 1 Epic Health Check ✅ (complete)

All v1.0 work complete: models, collector, risk/resource/timeline/status analyzers, MD/JSON/HTML/PDF reporters, CLI with 3 commands. 181 tests, 88% coverage.

---

## Phase 5: Work Item Collection (NEW) — 8h

### Task 5.1: Enhanced WorkItem model
- [x] Add `WorkItem` Pydantic model (unified: Epic + Task + Subtask + Bug)
- [x] Fields: key, type, summary, status, assignee, sprint, story_points, age_days, parent, subtasks[], linked_issues[], created, resolution
- [x] Computed: is_stale, is_unassigned, is_blocked, depth_in_tree

### Task 5.2: WorkItemCollector
- [x] Recursive subtask discovery (max depth 5)
- [x] Bug collection per project via JQL
- [x] Linked issue parsing (inward + outward)
- [x] BFS tree traversal from epic → tasks → subtasks
- [x] TTL caching per item type

### Task 5.3: Tests
- [x] Mock Jira API for recursive subtasks
- [x] Test depth limiting
- [x] Test bug collection per project

---

## Phase 6: Sprint & Progress Analysis (NEW) — 6h

### Task 6.1: SprintAnalyzer
- [x] Agile API: get_all_boards → get_all_sprints
- [x] Map items to sprints via customfield_10020
- [x] Sprint-level: item counts by type, assignee workload, completion %
- [x] Unallocated items report
- [x] Tests with mocked sprint data

### Task 6.2: ProgressTracker
- [x] Changelog fetching via REST API /rest/api/3/issue/{key}/changelog
- [x] Status transition extraction (from→to, date, author)
- [x] Velocity: items Done per week
- [x] On/off track detection per epic
- [x] Tests with mocked changelogs

---

## Phase 7: Escalation & Dashboard (NEW) — 6h

### Task 7.1: EscalationDetector
- [x] Triggers: stale >60d, unassigned active, blocked, overloaded
- [x] Blocker chain resolution
- [x] Impact assessment per escalation
- [x] Mitigation recommendations

### Task 7.2: DashboardReporter
- [x] Executive dashboard (1-page summary)
- [x] Full work tree per epic (indented)
- [x] Sprint planning view
- [x] Progress view with velocity
- [x] Escalation register
- [x] HTML + MD output

### Task 7.3: CLI `dashboard` command
- [x] typer command with --format, --output, --cutoff
- [x] Auto-save to reports/epics/dashboard_{date}.{md,html}

---

## Phase 8: Integration & Polish — 5h

### Task 8.1: Integration testing
- [x] Manual end-to-end dashboard smoke generation from live Jira — verified 2026-07-17 with `RMD-4160` and the five-epic set `PDS-81 AM-2054 AM-2025 TJ-1656 TJ-1683`; Markdown and HTML dashboards generated successfully. This was a manual smoke run, not an automated live integration test.
- [ ] Explicit automated edge tests: empty subtasks, no bugs, no sprints, and zero collected items — transferred to `jira-epic-report-archive-gap-closure` after post-archive verification found the named paths were not individually covered
- [x] Test coverage ≥80% — 626 tests passed at 84.39% on 2026-07-17

### Task 8.2: Documentation
- [x] spec.md v2.0 (done ✅)
- [x] design.md v2.0
- [x] INDEX.md v2.0
- [x] CHANGELOG.md v2.0 entry

---

**Total Phase 5-8:** 25 hours
**Total project:** 53h (v1.0) + 25h (v2.0) = 78 hours
