## Purpose

This specification defines requirements for Report Generation.

# Report Generation - Specification

**Capability:** report-generation  
**Status:** Draft  
**Date:** 2026-05-18  
**Version:** 1.1

---


## Requirements

### Requirement: report-generation specification applies unchanged

The report-generation contract documented below SHALL apply unchanged for
this delta. The OpenSpec delta section above is the canonical delta
declaration; the FR-N items and SDK Contract Requirements below are
preserved verbatim from the pre-delta-era authoring of this
specification.

#### Scenario: report-generation is implemented per the FR-N contract below

The report-generation is implemented per the FR-N contract below.

---


## Overview

The system SHALL generate multi-format reports (Markdown, JSON, HTML, PDF, DOCX) from analyzed epic data with risk scores, resource utilization, and actionable recommendations.

---

## Functional Requirements

### FR-1: Markdown Report

**Description:** Generate human-readable Markdown report with rich formatting.

**Requirements:**
- SHALL use string formatting for report structure (jinja2 available for future template migration)
- SHALL include sections:
  - Executive Summary (total epics, overall risk, avg completion, days to cut-off)
  - Epic Overview table (key, project, status, risk, tasks, done%, cut-off)
  - Risk Analysis by severity (emoji + type + description + impact + recommendation)
  - Resource Utilization table (assignee, tasks, epics, projects, status)
  - Action Items prioritized (IMMEDIATE, THIS WEEK, MONITOR)
  - Appendix (Figma links, URS links, Jira URLs)
- SHALL use emoji indicators for risk severity:
  - CRITICAL: red X
  - HIGH: red circle
  - MEDIUM: yellow circle
  - LOW: green circle
- SHALL format dates as YYYY-MM-DD
- SHALL support output to file via `--output` flag

**Example output:**
```markdown
# Epic Status Report

Generated: 2026-05-18 10:30:00

## Executive Summary

- **Total Epics:** 3
- **Overall Risk:** HIGH
- **Average Completion:** 45%
- **Days to Nearest Cut-off:** 12

## Epic Overview

| Epic    | Project | Status       | Risk   | Tasks | Done% | Cut-off   |
|---------|---------|--------------|--------|-------|-------|-----------|
| PDS-81  | PDS     | In Progress  | HIGH   | 24    | 52%   | 2026-06-03|
```

---

### FR-2a: DOCX (Word) Report

**Description:** Generate Word-format report covering all epics with structured layout.

**Requirements:**
- SHALL use `python-docx>=1.2.0` to build native DOCX bytes
- SHALL include sections: Executive Summary, Epic Overview table, Per-Epic Detail pages
- SHALL include per-epic: Metadata, Progress, Child Tasks (cap 100), Project Bugs (cap 50), Risks
- SHALL use page breaks between epics for printable layout
- SHALL apply table styling (Light Grid Accent 1) for readability
- SHALL include risk severity emoji (❌🔴🟡🟢) inline with severity labels
- SHALL output to `reports/epics/{project}_{date}_epic_report.docx`

**Implementation:** `epic_report/reporters/docx_reporter.py:generate_docx()`

**Performance:**
- 5 epics, 199 items: ~55KB output, 2-3 seconds generation time
- Includes all 4 collection phases (tasks, subtasks, epic bugs, project bugs)

---

### FR-2b: Google Sheets Report

**Description:** Generate a multi-tab Google Sheets report through the authenticated `tdt-sheets` integration and Google API batch operations.

**Requirements:**
- SHALL use the canonical service-account configuration under `TDT_HOME`
- SHALL use public `tdt-sheets` operations for value reads, writes, and clears
- SHALL use authenticated Google API batch operations only where `tdt-sheets` does not yet expose the required Drive or formatting primitive
- SHALL create tabs: Executive Summary, Epic Overview, per-epic tab (one per epic), Risks, Project Bugs
- SHALL populate values through the authenticated client path
- SHALL include per-epic: metadata, progress, child tasks (cap 200), project bugs (cap 100)
- SHALL aggregate Risks across all epics in single tab
- SHALL aggregate Project Bugs (deduplicated by key) across epics
- SHALL output spreadsheet URL to stdout + optional --output path file
- SHALL support `--output <path>` to save URL reference to local file
- SHALL default to folder ID `1DCzcp5gxmEKXU5-_QharKQdwDVcVK8rQ` (configurable via env)

**Implementation:** `epic_report/reporters/spreadsheet_reporter.py:generate_spreadsheet()`

**Real verification:**
- 5 epics × 9 tabs (Exec Summary, Overview, 5 per-epic, Risks, Bugs)
- 199 items + project bugs populated
- ~24s end-to-end (incl. gws CLI roundtrips)

**Dependencies:** `tdt-sheets` SDK backend and Google Sheets/Drive APIs

---

### FR-2: JSON Report

**Description:** Generate structured JSON for programmatic consumption.

**Requirements:**
- SHALL serialize the full `Report` Pydantic model
- SHALL include all epic data, risks, recommendations, resource utilization
- SHALL use ISO 8601 format for all timestamps
- SHALL be valid JSON (parseable by any JSON consumer)
- SHALL support pretty-print with indentation=2

**PBT Properties:**
- Round-trip: JSON serialization -> deserialization -> same Report model
- Invariant: all required fields present in JSON output

---

### FR-3: Template Engine (Future Enhancement)

**Description:** Extensible jinja2 template processing system (jinja2 dependency available but not yet integrated).

**Requirements:**
- SHALL load templates from `templates/` directory
- SHALL support custom template registration
- SHALL provide default context with all report data
- SHALL support custom Jinja2 filters for date formatting, emoji mapping

---

### FR-4: Report Output Destinations

**Description:** Support multiple output channels.

**Requirements:**
- SHALL auto-generate output path under `reports/epics/` relative to workspace root when `--output` is omitted
- SHALL use naming convention: `{project}_{date}_{suffix}.{ext}` (e.g., `PDS_2026-05-20_epic_report.md`)
- SHALL write to explicit path with `--output <path>` flag
- SHALL create parent directories if needed for file output
- SHALL locate workspace root by walking up from CWD looking for `.agents/` or `openspec/` markers
- SHALL generate per-epic pages (`{KEY}.md`, `{KEY}.html`) alongside the main report
- SHALL generate `INDEX.md` / `INDEX.html` with navigation to all epic pages

---

### FR-5: Actionable Recommendations

**Description:** Generate prioritized action items from risk analysis.

**Requirements:**
- SHALL categorize recommendations by urgency:
  - **IMMEDIATE**: CRITICAL severity risks
  - **THIS WEEK**: HIGH severity risks
  - **MONITOR**: MEDIUM/LOW severity risks
- SHALL include specific epic and task references
- SHALL provide concrete next steps (not generic advice)

---

## Dependencies

- `epic_report.models` - Report, Epic, Risk models
- `epic_report.analyzers.risk` - Risk data
- `epic_report.analyzers.status` - Completion data
- `jinja2>=3.1.5` - Template engine (future use, currently string-formatting)

---

### FR-13: Agent CLI Deep Analysis Integration

**Description:** Integrate AI agent CLIs (codex, claude, kimi, pi) to perform deep analysis on flagged issues and produce structured reports.

**Requirements:**
- SHALL support spawning agent CLI subprocesses with prompt injection for issue analysis
- SHALL detect available agents from PATH (`codex`, `claude`, `kimi`, `pi`) and auto-select the first available if none specified
- SHALL accept a `--deep-analysis` flag on the report CLI to enable agent-driven analysis
- SHALL accept a `--agent <name>` option to specify which agent CLI to use
- SHALL pass structured prompts containing: issue key, summary, status, assignee, risk flags, comment categories, linked issues, and changelog patterns
- SHALL capture agent stdout as structured analysis output with sections:
  - **Root Cause**: identified root cause of the issue
  - **Impact Assessment**: blast radius and downstream effects
  - **Recommended Actions**: concrete steps ranked by priority
  - **Confidence**: LOW / MEDIUM / HIGH
- SHALL parse agent output with markdown section markers (`## Root Cause`, `## Impact Assessment`, etc.)
- SHALL fall back gracefully if no agent CLI is available: log a warning and skip deep analysis
- SHALL enforce a configurable timeout per issue (default: 120 seconds) to prevent hangs
- SHALL append deep analysis results to the report under a dedicated `### Deep Analysis` subsection per issue
- SHALL NOT block report generation on deep analysis failures — partial results are acceptable

**Agent Prompt Template:**
```
You are a Jira issue analyst. Analyze this issue and produce a structured report:

Issue: {key}
Summary: {summary}
Status: {status}
Assignee: {assignee}
Risk Flags: {risk_flags}
Comment Categories: {comment_categories}
Linked Issues: {linked_issues}
Changelog Patterns: {changelog_patterns}

Output sections:
## Root Cause
## Impact Assessment
## Recommended Actions
## Confidence
```

---



---

### FR-13a: Multi-Agent Parallel Analysis

**Description:** Run multiple AI agent CLIs in parallel for consensus-based deep analysis.

**Requirements:**
- SHALL support `--multi-agent` flag on the `insights` command
- SHALL spawn ALL detected agents (codex, claude, kimi, pi) concurrently via ThreadPoolExecutor
- SHALL collect structured results from each agent independently
- SHALL synthesize results: pick highest-scoring agent as primary, report consensus score
- SHALL persist all agent results in JSON under `deep_analysis.all_agent_results`
- SHALL use per-agent timeouts: codex=120s, claude=240s, kimi=180s, pi=180s
- SHALL gracefully handle agent failures (timeout, parse error, not found) without blocking others
- SHALL report consensus score: `succeeded_agents / total_agents`

**Agent CLI Invocations:**
| Agent | Command | Notes |
|-------|---------|-------|
| codex | `codex exec --skip-git-repo-check "<prompt>"` | Fast, reliable |
| claude | `claude -p "<prompt>"` | Slow startup, needs 240s timeout |
| kimi | `kimi -p "<prompt>"` | Variable output format |
| pi | `pi --print --mode text "<prompt>"` | Provider-dependent |

**Synthesis Strategy:**
- Score each result by completeness (root_cause=3, impact=2, actions=2, confidence=1, error=-5)
- Primary = highest-scoring agent
- Report per-agent: has_root_cause, has_impact, has_actions, confidence, error

**Example:**
```bash
epic-report insights PDS-81 --deep-analysis --multi-agent --verbose
```



---

### FR-13b: Batch Parallel Analysis Strategy

**Description:** Distribute ALL tickets across available agent CLIs in parallel batches for full coverage.

**Requirements:**
- SHALL support `--all-tickets` flag on the `insights` command to analyze every ticket (not just flagged)
- SHALL support `--batch-size N` to control max concurrent agent subprocesses (default: 4)
- SHALL distribute tickets round-robin across available agents (codex→claude→kimi→pi→codex...)
- SHALL use adaptive total_timeout: `num_tickets × 45s` budget for entire batch
- SHALL preserve partial results when batch timeout expires (completed analyses kept)
- SHALL report success count: `N/M tickets analyzed successfully`
- SHALL gracefully handle per-agent failures without blocking the batch

**Execution Strategy:**
```
Tier 1: ALL tickets → heuristic analysis (3s, always runs)
Tier 2: Flagged tickets → single agent deep analysis (--deep-analysis)
Tier 3: ALL tickets → batch distributed (--deep-analysis --all-tickets)
         └── Round-robin across agents, --batch-size concurrent
```

**Performance Targets:**
- 76 tickets with 2 working agents, batch_size=4: ~5 min
- 76 tickets with 4 working agents, batch_size=8: ~2.5 min
- Graceful degradation: if only 1 agent available, runs sequentially

**Example:**
```bash
# Analyze all tickets, distribute across agents
epic-report insights PDS-81 AM-2054 AM-2025 TJ-1656 TJ-1683 \
  --deep-analysis --all-tickets --batch-size 8

# Single epic, all tickets
epic-report insights PDS-81 --deep-analysis --all-tickets
```

### FR-14: Per-Epic Dedicated Report Pages

**Description:** Generate individual per-epic report pages with cross-epic navigation.

**Requirements:**
- SHALL generate one dedicated report page per epic (`<epic-key>.md` and `<epic-key>.html`)
- SHALL include navigation header on each page linking to the dashboard and all other epic pages
- SHALL highlight the current epic in the navigation bar (bold, non-linked)
- SHALL include full epic metadata table: key, summary, status, priority, project, assignee, target version, cut-off, reporter, Figma, URS links
- SHALL display progress metrics: completion %, total tasks, unassigned count, sprint allocation %, story points, stale tasks, blocked tasks
- SHALL render a task status breakdown with visual bars and emoji indicators
- SHALL include a full child task table with: key, type, summary, status, assignee, story points, sprint, age
- SHALL surface epic-specific risks sorted by priority with emoji + severity + description + recommendation
- SHALL integrate insight analysis data when available: comment summaries, risk flags, linked work, changelog patterns
- SHALL include reference links section for Figma and URS URLs
- SHALL generate an HTML index page (`index.html`) listing all epics with links to individual pages and the dashboard
- SHALL support both Markdown and HTML output formats per epic

---

### FR-15: Dashboard with Activity Tree, Sprint Planning, Progress Tracking, Escalation Register

**Description:** Generate a comprehensive project command-center dashboard.

**Requirements:**
- SHALL generate dashboard in both Markdown and HTML formats (`dashboard.md`, `dashboard.html`)
- SHALL include an **Activity Tree** section showing epics and their child task hierarchy with status indicators
- SHALL include a **Sprint Planning** section with tables grouping items by sprint, completion percentages, item type distribution, and warnings for unallocated items
- SHALL include a **Progress Tracking** section with per-epic on-track/off-track status (✅/❌), completion %, item counts, and status distribution
- SHALL include an **Escalation Register** with CRITICAL (stale >60d), HIGH (unassigned active), and resource overload tables
- SHALL include a **Bug Radar** section showing per-project bug counts by status with issue links
- SHALL collect all work items recursively: epics → tasks → subtasks → bugs across projects
- SHALL use configurable thresholds for overload (default: 8 items) and staleness (default: 60 days)

---



---

### FR-23: Timeline Analysis Section

**Description:** Generate timeline risk analysis section in reports.

**Requirements:**
- SHALL compute days remaining to cut-off date per epic
- SHALL calculate required daily velocity to meet deadline
- SHALL flag epics where current velocity is insufficient
- SHALL include timeline metrics in markdown report under "Timeline Analysis" section
- SHALL accept `--cutoff` date parameter to anchor timeline calculations
- SHALL support configurable `risk_cutoff_buffer` (default: 7 days) via ProjectThresholds

**Implementation:** `epic_report/analyzers/timeline.py` — `TimelineAnalyzer` class

---

### FR-24: Sprint Allocation Progress Section

**Description:** Report sprint allocation coverage per epic.

**Requirements:**
- SHALL display per-epic sprint allocation table with columns: Epic, Tasks, Allocated, %, Sprint Names
- SHALL flag epics with 0% sprint allocation as ⚠️ warning
- SHALL compute sprint allocation percentage from `sprint_allocated_count / task_count`
- SHALL list sprint names associated with each epic's tasks

**Implementation:** `epic_report/reporters/markdown.py` — Sprint Allocation Progress section

---

### FR-25: Comment Intelligence Categorization

**Description:** Classify issue comments into actionable categories.

**Requirements:**
- SHALL categorize comments into 6 buckets via keyword matching:
  - `requirements_clarification`: question, clarify, confirm, kindly help
  - `bug_report`: bug, issue, problem, fix, broken, error, fail, crash
  - `qa_testing`: test, qa, uat, testing, testcase, sit
  - `blocker_mentioned`: block, blocker, waiting, depend, stuck, cannot proceed
  - `resolution`: done, completed, resolved, approved, lgtm
  - `urgent`: urgent, asap, rush, critical, priority
- SHALL derive risk flags from categories: `blocker_mentioned`, `requirements_clarification`, `heavy_discussion` (>5 comments), `urgent_mentioned`
- SHALL flag issues needing deep analysis when: blocker_mentioned OR high_churn OR reopened OR requirements_clarification

**Implementation:** `epic_report/analyzers/insight.py` — `InsightAnalyzer._analyze_comments()`



---

### FR-26: Cross-Format Status & Risk Highlighting

**Description:** Apply consistent visual highlighting for Status column and risk severity across all formats.

**Requirements:**
- SHALL color-code Status cells consistently across formats:
  - `Done`/`Closed`/`TEST DONE`/`UAT` → green family
  - `In Progress`/`Develop` → blue family
  - `CODE REVIEW`/`In Review` → purple family
  - `SIT`/`QA` → light blue (testing family)
  - `Ready`/`Ready to Develop` → yellow
  - `To Do` → gray
  - `Draft` → light purple
  - `Rejected/Duplicated` → red
  - `Deploy in Dev` → green-blue
- SHALL color-code Risk Severity cells:
  - CRITICAL → red
  - HIGH → orange
  - MEDIUM → yellow
  - LOW → green
- SHALL use case-insensitive matching for status values (handles "Code Review" / "CODE REVIEW" / "code review" identically)
- SHALL implement per format:
  - **HTML**: 11 CSS badge classes via `_badge_for_status()` (.done, .in-progress, .review, .testing, .ready, .todo, .draft, .rejected, .deploy, .critical, .high)
  - **DOCX**: 21 cell shading mappings via `_STATUS_SHADING` + `_SEVERITY_SHADING` dicts using OOXML `w:shd` elements
  - **Spreadsheet**: 17 conditional formatting rules per Status column + risk gradient on Completion column
  - **Markdown**: emoji indicators (🟢🟡🟠🔴❌) inline with severity
  - **PDF**: inherited from HTML rendering
- SHALL apply formatting AFTER data population (batchUpdate for Sheets)

**Implementation:**
- `epic_report/reporters/html_reporter.py:_badge_for_status()`
- `epic_report/reporters/docx_reporter.py:_STATUS_SHADING`, `_shade_cell()`
- `epic_report/reporters/spreadsheet_reporter.py:_apply_formatting()`

---

### FR-27: Spreadsheet Upsert Pattern

**Description:** Maintain a single spreadsheet per project — update existing, create only when not yet existing.

**Requirements:**
- SHALL search target Drive folder for existing spreadsheet by stable title `"Epic Status Report — {project}"` (no date)
- SHALL find by exact name match within the configured Drive folder
- SHALL UPDATE existing spreadsheet when found:
  - Sync only reporter-managed sheet structure (`addSheet`/`deleteSheet`) while preserving protected and unknown tabs
  - Clear managed output values through `tdt-sheets`
  - Repopulate fresh data
  - Reapply formatting
- SHALL CREATE new spreadsheet only when none exists with the title
- SHALL move newly-created spreadsheet to target folder via `gws drive files update --addParents`
- SHALL return tuple `(url, was_created)` to indicate action taken
- SHALL show user "✓ Spreadsheet updated/created: <url>" based on actual action
- SHALL preserve sheet IDs across updates (existing sheets keep their IDs, new sheets get new IDs)
- SHALL handle epic list changes gracefully:
  - New epic added → new tab created
  - Epic removed → orphan tab auto-deleted
- SHALL use descriptive tab names: `{KEY} {brief summary}` (e.g., "PDS-81 Design Library...") truncated to 100 chars

**Implementation:** `epic_report/reporters/spreadsheet_reporter.py`:
- `_find_existing_spreadsheet()`
- `_get_existing_sheet_ids()`
- `_sync_sheet_structure()`
- `_clear_sheet()`

**Behavior verified:**
- First run: creates new spreadsheet
- Second+ run: updates same spreadsheet (no duplicates in folder)
- Single source of truth per project

## Dependencies (Updated)

- `epic_report.models` - Report, Epic, Risk, WorkItem, DashboardReport models
- `epic_report.analyzers.risk` - Risk data
- `epic_report.analyzers.status` - Completion data
- `epic_report.analyzers.insight` - Issue insight data
- `epic_report.analyzers.escalation` - Escalation detection
- `epic_report.dashboard.collector` - Work item collection
- `epic_report.dashboard.reporter` - Dashboard generation
- `epic_report.reporters.per_epic` - Per-epic report generation
- `epic_report.reporters.html_reporter` - HTML report generation
- `jinja2>=3.1.5` - Template engine

---

### FR-16: Subtask Analysis (Future Enhancement)

> **Status:** Data model exists in `models.py`; analyzer populator is a future enhancement. Current baseline ships shallow `analyze_issue()` only.


**Description:** Analyze subtask completion for each issue and flag blocking subtrees.

**Requirements:**
- SHALL recursively fetch subtasks for each issue via Jira API
- SHALL compute subtask completion ratio (completed / total)
- SHALL flag issues with incomplete subtasks as potentially blocked (`blocked_by_incomplete_subtask`)
- SHALL report subtask status breakdown per issue (Done, In Progress, To Do, etc.)
- SHALL surface subtask analysis in per-epic reports under a dedicated section

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

---

### FR-17: Blocker Chain Detection (Future Enhancement)

> **Status:** Data model exists in `models.py`; analyzer populator is a future enhancement. Current baseline ships shallow `analyze_issue()` only.


**Description:** Detect transitive blocker relationships across epic issues.

**Requirements:**
- SHALL parse `issuelinks` for "blocks" and "blocked by" link types
- SHALL compute blocker chain depth (A→B→C = depth 2)
- SHALL identify root blockers (blocking others but not blocked themselves)
- SHALL cross-reference blockers within the epic scope
- SHALL display blocker chain relationships in report tables with indented notation

**Data Model:**
```python
@dataclass
class BlockerAnalysis:
    blocked_by: list[str] = []
    blocks: list[str] = []
    chain_depth: int = 0
    is_root_blocker: bool = False
    blocker_status: dict[str, str] = {}
```

---

### FR-18: Collaboration Profiling (Future Enhancement)

> **Status:** Data model exists in `models.py`; analyzer populator is a future enhancement. Current baseline ships shallow `analyze_issue()` only.


**Description:** Profile comment authorship and collaboration intensity per issue.

**Requirements:**
- SHALL extract unique comment authors per issue
- SHALL detect cross-team involvement via name-prefix heuristics
- SHALL measure thread depth (max consecutive same-author comments)
- SHALL flag external stakeholder involvement (non-dev commenters)
- SHALL surface collaboration metrics in insight reports

**Data Model:**
```python
@dataclass
class CollaborationProfile:
    unique_authors: int = 0
    authors: list[str] = []
    cross_team_count: int = 0
    thread_depth: int = 0
    external_involvement: bool = False
```

---

### FR-19: Bug Association Analysis (Future Enhancement)

> **Status:** Data model exists in `models.py`; analyzer populator is a future enhancement. Current baseline ships shallow `analyze_issue()` only.


**Description:** Find and aggregate bugs linked to tasks, stories, and epics.

**Requirements:**
- SHALL discover bugs via `issuelinks` (Bug type outward/inward links)
- SHALL search for bugs via JQL: `project = X AND issuetype = Bug AND issue in linkedIssues(KEY)`
- SHALL aggregate bug severity and status per epic
- SHALL flag bugs blocking release (Priority = Highest/High, status != Done)
- SHALL include bug association data in per-epic reports and dashboard Bug Radar

**Data Model:**
```python
@dataclass
class BugAssociation:
    linked_bugs: list[str] = []
    bug_count: int = 0
    active_bugs: int = 0
    critical_bugs: int = 0
    blocking_release: bool = False
```

---

### FR-20: Activity Timeline (Future Enhancement)

> **Status:** Data model exists in `models.py`; analyzer populator is a future enhancement. Current baseline ships shallow `analyze_issue()` only.


**Description:** Build chronological activity timeline per issue from comments and changelogs.

**Requirements:**
- SHALL merge comment events and changelog status/assignment transitions
- SHALL sort events chronologically (newest first)
- SHALL measure inactivity periods (>7 days without activity)
- SHALL flag issues with long inactivity in risk flags
- SHALL include timeline events in insight JSON output

**Data Model:**
```python
@dataclass
class ActivityEvent:
    date: str
    type: str  # "comment" | "status_change" | "assignment"
    description: str
    author: str = ""
```

---

### FR-21: Insights Command

**Description:** Generate per-epic insight reports analyzing comments, changelogs, and activity.

**Requirements:**
- SHALL accept epic keys as positional arguments
- SHALL support `--deep-analysis` to spawn AI agent CLIs (codex, claude, kimi, pi)
- SHALL support `--agent <name>` to select specific agent for deep analysis
- SHALL output to `reports/epics/{KEY}_insights.md` (Markdown) and `reports/epics/{KEY}_insights.json` (JSON)
- SHALL analyze comment categories, author collaboration patterns, and changelog transitions
- SHALL detect inactivity periods (>7 days without activity) and flag in risk output
- SHALL include bug associations, blocker chains, and activity timeline per issue
- SHALL fall back gracefully if no agent CLI is available (skip deep analysis with warning)

**Dependencies:**
- `epic_report.analyzers.insight` - Issue insight analysis
- `epic_report.analyzers.escalation` - Escalation detection
- `epic_report.reporters.per_epic` - Per-epic report generation

---

### FR-22: Dashboard Command

**Description:** Generate comprehensive multi-project dashboard with activity tree, sprint planning, progress tracking, and escalation register.

**Requirements:**
- SHALL generate dashboard in both Markdown and HTML formats (`dashboard.md`, `dashboard.html`)
- SHALL include an **Activity Tree** section: hierarchical view of epics → child tasks with status indicators
- SHALL include a **Sprint Planning** section: tables grouped by sprint, completion percentages, item type distribution, and warnings for unallocated items
- SHALL include a **Progress Tracking** section: per-epic on-track/off-track status (✅/❌), completion %, item counts, and status distribution
- SHALL include an **Escalation Register** section: CRITICAL (stale >60d), HIGH (unassigned active), and resource overload tables
- SHALL include a **Bug Radar** section: per-project bug counts by status with issue links
- SHALL include a **Resource Utilization** section: assignee workload across all projects with overload flags
- SHALL collect all work items recursively: epics → tasks → subtasks → bugs across projects
- SHALL support command flags:
  - `--format, -f`: Output format (markdown, html; default: markdown)
  - `--project, -p`: Filter by project key
  - `--cutoff`: Cut-off date YYYY-MM-DD
  - `--overload-threshold`: Max tasks per assignee before flagging (default: 8)
  - `--staleness-days`: Days since last activity before stale flag (default: 60)
- SHALL use `WorkItemCollector` for recursive work item collection across all projects

**Dependencies:**
- `epic_report.dashboard.collector` - Work item collection
- `epic_report.dashboard.reporter` - Dashboard generation
- `epic_report.reporters.html_reporter` - HTML report generation
- `epic_report.analyzers.status` - Status aggregation
- `epic_report.analyzers.risk` - Risk analysis
- `epic_report.analyzers.escalation` - Escalation detection
