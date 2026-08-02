# Epic Data Collection — Specification

**Capability:** epic-data-collection


## ADDED Requirements

### Requirement: epic-data-collection specification applies unchanged

The epic-data-collection contract documented below SHALL apply unchanged for
this delta. The OpenSpec delta section above is the canonical delta
declaration; the FR-N items and SDK Contract Requirements below are
preserved verbatim from the pre-delta-era authoring of this
specification.

#### Scenario: epic-data-collection is implemented per the FR-N contract below

The epic-data-collection is implemented per the FR-N contract below.

---

### Functional Requirements

### FR-1: Epic Metadata Retrieval

**Description:** Fetch individual epic metadata from Jira API.

**Requirements:**
- SHALL use `epic_report.jira_client.PatchedJira` (extends `atlassian-python-api`) to call `/rest/api/3/issue/{key}` for epic metadata
- SHALL extract: key, summary, status, priority, project, description, labels, assignee, reporter
- SHALL parse epic description for Figma, URS, and documentation links via regex
- SHALL handle both company-managed and team-managed project structures
- SHALL validate epic issuetype equals "Epic" before processing

**Example:**
```python
from epic_report.collector import EpicCollector

collector = EpicCollector(jira_client)
epic = collector.get_epic("PDS-81")

print(f"Epic: {epic.key} - {epic.summary}")
print(f"Status: {epic.status}, Priority: {epic.priority}")
print(f"Project: {epic.project}")
print(f"Figma: {epic.figma_url}")
print(f"URS: {epic.urs_url}")
```

**PBT Properties:**
- Invariant: `epic.key` always matches pattern `^[A-Z]+-\d+$`
- Round-trip: fetched epic data -> model -> JSON -> model returns same values
- Bounds: response time < 5s per epic under normal network conditions

---

### FR-2: Comprehensive Work Item Collection (3-Phase)

**Description:** Find ALL work items linked to an epic — tasks, stories, subtasks, and bugs — using a 3-phase JQL strategy.

**Requirements:**
- SHALL execute 3-phase collection per epic:
  - **Phase 1: Direct children** — JQL `(parent = EPIC OR "Epic Link" = EPIC) AND issuetype != Epic`
  - **Phase 2: Subtasks** — JQL `parent in (child_keys...) AND issuetype != Epic` (batched 50 keys/call)
  - **Phase 3: Linked bugs** — JQL `issuetype = Bug AND ("Epic Link" = EPIC OR parent = EPIC OR issue in linkedIssues(EPIC))`
  - **Phase 4: Project-level bugs** — JQL `project = X AND issuetype = Bug AND status not in ("Done", "Closed", "Rejected/Duplicated")` (stored separately on `Epic.project_bugs`)
- SHALL deduplicate items across phases via key tracking
- SHALL paginate Phase 1 via `/rest/api/3/search/jql` with `maxResults=100` per page (POST body, per CHANGE-2046)
- SHALL extract per item: key, issuetype, summary, status, assignee, priority, labels, sprint, story points
- SHALL handle Jira Cloud custom field naming (customfield_10014 for Epic Link)
- SHALL collect items regardless of status (including Done, Closed, Cancelled)
- SHALL preserve issuetype for downstream classification (Task, Story, Sub-task, Bug)
- NOTE: Dashboard `WorkItemCollector` provides parallel project-wide bug scan (not epic-linked)

**Implementation:** `epic_report/collector.py:_fetch_via_jql()` + `_jql_paginated()` helper

**Coverage Improvement (real data):**
- Before (Phase 1 only): 77 items across 5 epics
- After (3-phase): 199 items — captures 87 bugs in PDS-81, 11 subtasks + 5 stories in AM-2054, 34 items in AM-2025

**PBT Properties:**
- Invariant: no returned task has `issuetype == "Epic"`
- Deduplication: same key never returned twice across phases
- Bounds: pagination handles up to 1000 items per epic

---

### FR-3: Sprint Association

**Description:** Link tasks to their sprint allocations.

**Requirements:**
- SHALL extract sprint info from task `sprint` field (customfield_10020)
- SHALL parse sprint info directly from issue fields (customfield_10020); detailed sprint metadata fetched via `sheets/agile/1.0/sprint/{id}` when needed
- SHALL identify tasks NOT assigned to any sprint
- SHALL parse sprint field to extract: sprint_id, sprint_name, state (active/future/closed)

---

### FR-4: Multi-Epic Concurrent Collection

**Description:** Collect data from multiple epics efficiently.

**Requirements:**
- SHALL collect epics sequentially (not via asyncio); `ThreadPoolExecutor` used in Phase 2.5 ticket intelligence (4 workers per epic)
- SHALL respect Jira API rate limit (default 10 req/sec, configurable via `EPIC_REPORT_RATE_LIMIT`)
- SHALL implement TTL caching (5 min for epics, 15 min for sprints)
- SHALL aggregate results from all epics into a single `Report` model
- SHALL handle individual epic failures gracefully (skip failed, continue others)

**PBT Properties:**
- Idempotency: collecting same epics twice returns equivalent results (within cache TTL)
- Commutativity: order of epic keys does not affect final aggregated report
- Invariant: each epic in result has at least its key and summary populated

---

### FR-5: URL Extraction from Descriptions

**Description:** Parse epic and task descriptions for documentation links.

**Requirements:**
- SHALL detect Figma URLs matching pattern `https://www.figma.com/design/...`
- SHALL detect SharePoint URLs matching pattern `https://[a-z]+.sharepoint.com/...`
- SHALL detect generic HTTP URLs as fallback
- SHALL store extracted URLs in model fields (`figma_url`, `urs_url`, `doc_urls`)
- SHALL handle multiple URLs per description

---

### Data Models

Key models used (defined in parent `spec.md`):
- `Epic` - Epic metadata with child tasks
- `Task` - Individual task data
- `Report` - Aggregated collection result

### Dependencies

- `epic_report.jira_client.PatchedJira` - Jira Cloud API client (extends atlassian-python-api)
- f-string JQL composition - direct query construction
- Direct customfield_10020 parsing - sprint data extraction
- `pydantic>=2.10.3` - Data validation
- `cachetools>=5.5.0` - TTL caching

---

### FR-6: Subtask & Linked Issue Collection

**Description:** Recursively collect subtasks and linked issues for comprehensive work item tracking.

**Requirements:**
- SHALL perform BFS recursive subtask collection up to `max_depth=5` via `WorkItemCollector._collect_subtasks_recursive()`
- SHALL parse `issuelinks` for outward and inward direction with link type names
- SHALL collect linked issues with type, direction, and key metadata
- SHALL use bulk JQL queries (`key in (A, B, C)`) for batch subtask fetching
- SHALL cache fetched issues via TTL cache (900s TTL, 500 item maxsize)
- SHALL collect bug issues linked via `issuelinks` + project-wide JQL scan

---

### FR-7: Comment Author Collection

**Description:** Extract comment authors and metadata for collaboration profiling.

**Requirements:**
- SHALL extract unique comment author display names per issue
- SHALL collect comment metadata: author, timestamp, body preview (first 150 chars)
- SHALL store authors list deduplicated in insertion order
- SHALL support cross-team detection via name-prefix heuristics
- SHALL enable `CollaborationProfile` computation from collected author data

