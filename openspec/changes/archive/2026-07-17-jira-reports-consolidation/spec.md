# TDT Ecosystem Architecture - Specification

**Status:** 📋 Final Draft  
**Version:** 1.0.0  
**Date:** 2026-05-20  
**Scope:** All Python projects in tdt workspace

---

## 1. Current Ecosystem Inventory

| Project | Version | LOC | Tests | Domain | Maturity |
|---------|---------|-----|-------|--------|----------|
| `jira-skill` | 1.1.0 | ~3K | 76 | Jira/GitLab management library | Growing |
| `jira-epic-report` | 2.0.0 | 8,904 | 368 | Epic analysis CLI | Stable |
| `jira-daily-reports` | 1.0.0 | ~? | 84 | Daily Jira reporting CLI | Active |
| `webhook-receiver` | 8.0.0 | ~5K | 40+ | AI-powered MR code review | Mature |
| `ops-automation-suite` | 1.0.0 | ~200 | 0 | Workflow orchestration | Early |
| `jira-daily-reports-skill` | 1.1 | ~600 | 0 | 9 daily reports (bash/acli) | Legacy |

### Shared Patterns (Already Duplicated)

| Pattern | jira-skill | jira-epic-report | webhook-receiver | ops-automation |
|---------|-----------|-----------------|-----------------|----------------|
| `~/.tdt/.env` loading | ✅ `ensure_env_loaded()` | ✅ `_load_env_files()` | ✅ `_load_tdt_env()` | ✅ `load_dotenv()` |
| GitLab client | python-gitlab | — | glab CLI subprocess | — |
| Jira client | atlassian-python-api | atlassian-python-api | — | aiohttp (planned) |
| Config model | pydantic BaseModel | dataclass | plain class | pydantic BaseModel |
| Resilience | circuit_breaker, retry | cachetools | circuit_breaker, rate_limiter | — |
| Logging | stdlib | stdlib | structlog | structlog |

**Key duplication:** 4 different implementations of `~/.tdt/.env` loading. 2 different GitLab clients. 2 different Jira auth patterns.

---

## 2. Architecture Decision

### Decision: Layered Ecosystem with `tdt-core` Shared Package

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI / Service Layer                        │
├──────────────┬──────────────┬───────────────┬───────────────────┤
│ jira-epic-   │ jira-daily-  │ webhook-      │ ops-automation-   │
│ report       │ reports      │ receiver      │ suite             │
│ (CLI)        │ (CLI/cron)   │ (FastAPI)     │ (orchestrator)    │
├──────────────┴──────────────┴───────────────┴───────────────────┤
│                      Domain Libraries                            │
├──────────────────────────────────────────────────────────────────┤
│ jira-skill (Jira/GitLab management, JQL, boards, sprints)       │
├──────────────────────────────────────────────────────────────────┤
│                        tdt-core (shared)                         │
│  • env loading  • config models  • client factories             │
│  • common models  • resilience primitives  • logging setup      │
└──────────────────────────────────────────────────────────────────┘
```

### Why Not Monorepo Merge

1. **webhook-receiver is v8.0.0** — extremely mature, different runtime (FastAPI server vs CLI tools)
2. **jira-epic-report is v2.0.0** — 368 tests, 80% coverage, stable
3. **Different deployment targets** — CLI tools vs long-running services vs cron jobs
4. **Different dependency profiles** — FastAPI+uvicorn vs typer+rich vs pure library
5. **Team velocity** — independent repos allow parallel work without merge conflicts

### Why Shared Core (Not Just Conventions)

1. **4 implementations of env loading** — bug in one won't propagate, but fixes won't either
2. **GitLab client divergence** — webhook-receiver uses glab CLI, jira-skill uses python-gitlab. Both valid for their use case, but shared models would help
3. **Future repos will need the same patterns** — every new tool re-implements auth
4. **Type safety across boundaries** — shared models enable typed interfaces between projects

---

## 3. `tdt-core` Package Design

### Scope (Minimal, Stable, No Business Logic)

```
tdt-core/
├── src/tdt_core/
│   ├── __init__.py
│   ├── env.py              # ~/.tdt/.env loading (single source of truth)
│   ├── config.py           # Base config patterns (TdtConfig base class)
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── jira.py         # JiraConfig + JiraClientFactory
│   │   └── gitlab.py       # GitlabConfig + GitlabClientFactory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── jira.py         # JiraIssue, JiraProject, JiraSprint (shared DTOs)
│   │   └── gitlab.py       # GitLabProject, MergeRequest, Pipeline (shared DTOs)
│   └── resilience/
│       ├── __init__.py
│       ├── retry.py        # Exponential backoff with jitter
│       └── circuit_breaker.py
├── tests/
├── pyproject.toml
└── README.md
```

### Design Principles

1. **Zero business logic** — only infrastructure concerns (auth, transport, models)
2. **Minimal dependencies** — pydantic, python-dotenv, atlassian-python-api, python-gitlab
3. **Stable API surface** — semver, breaking changes only in major versions
4. **Optional extras** — `tdt-core[gitlab]`, `tdt-core[jira]`, `tdt-core[all]`
5. **No framework opinions** — works with sync (requests) and async (aiohttp/httpx)

### Shared Environment Coercion

All Python projects in the ecosystem SHALL use the shared `tdt_core.env` coercion helpers for common config parsing:
`load_tdt_env()`, `get_bool_env()`, `get_int_env()`, `get_float_env()`, and `get_path_env()`.

1. Shared config code SHALL prefer the helpers over ad-hoc `int(os.getenv(...))`, `float(os.getenv(...))`,
   `bool(os.getenv(...))`, and path-construction wrappers.
2. Project-specific fallbacks MAY still wrap the shared helpers for legacy env names or optional overrides.
3. New service/config code SHALL default to the shared helpers unless a value requires custom validation.

### Key Interfaces

```python
# tdt_core/env.py
def load_tdt_env() -> None:
    """Load ~/.tdt/.env. Idempotent. Call early in app startup."""

# tdt_core/clients/jira.py  
class JiraConfig(BaseModel):
    url: str          # ATLASSIAN_SITE
    email: str        # ATLASSIAN_EMAIL
    token: SecretStr  # ATLASSIAN_ACCESS_TOKEN
    project_key: str  # JIRA_PROJECT_KEY
    
    @classmethod
    def from_env(cls) -> JiraConfig: ...

class JiraClientFactory:
    @classmethod
    def from_env(cls) -> Jira: ...

# tdt_core/clients/gitlab.py
class GitlabConfig(BaseModel):
    url: str          # GITLAB_HOST
    token: SecretStr  # GITLAB_PAT
    pagination: str = "offset"
    
    @classmethod
    def from_env(cls) -> GitlabConfig: ...

class GitlabClientFactory:
    def create_client(self) -> Gitlab: ...
    
    @classmethod
    def from_env(cls) -> GitlabClientFactory: ...
```

---

## 4. Ecosystem Dependency Graph (Target State)

```
tdt-core[gitlab]              (python-gitlab 8.3.0 — single GitLab API client)
tdt-core[jira]                (atlassian-python-api — single Jira API client)
  ├── jira-skill              (domain library: JQL, boards, sprints, issues, gitlab sync)
  │     ├── jira-epic-report  (CLI: epic analysis, depends on jira-skill for JQL)
  │     ├── jira-daily-reports(CLI/cron: 9 daily reports, depends on tdt-core[jira])
  │     └── ops-automation    (orchestrator: workflows using jira-skill + gitlab)
  └── webhook-receiver        (service: python-gitlab for API + git CLI for worktrees)
```

### Dependency Rules

1. `tdt-core` depends on **nothing internal** (only external packages)
2. `jira-skill` depends on `tdt-core`
3. Application projects depend on `jira-skill` and/or `tdt-core`
4. **No circular dependencies** — strictly layered
5. **No peer dependencies** — each project declares exactly what it needs
6. **python-gitlab is the standard** GitLab API client (via tdt-core[gitlab])
7. **git CLI only for local operations** (worktrees, fetch, merge — not API calls)

### Installation (uv workspace or path deps)

**Strategy:** Independent projects with path deps (not uv workspace). See [toolchain-standardization.md](toolchain-standardization.md) for full rationale.

**Standardized toolchain across all projects:**
- **uv** >=0.11.15 with `python-preference = "only-managed"`
- **ruff** for linting + formatting (replaces black, isort, flake8)
- **mypy** with gradual typing (strict for new code, pragmatic for legacy)
- **pytest** with 80% coverage minimum
- **hatchling** build backend, `src/` layout
- **pre-commit** with ruff + ruff-format + mypy hooks

```toml
# jira-skill/pyproject.toml
[project]
dependencies = [
    "tdt-core @ file:///${PROJECT_ROOT}/../tdt-core",
]

# jira-epic-report/pyproject.toml  
[project]
dependencies = [
    "jira-skill @ file:///${PROJECT_ROOT}/../jira-skill",
]

# webhook-receiver/pyproject.toml (only needs core, not full jira-skill)
[project]
dependencies = [
    "tdt-core[gitlab] @ file:///${PROJECT_ROOT}/../tdt-core",
]
```

---

## 5. Migration Strategy

### Phase 1: Extract tdt-core from jira-skill (1 day)

Current `jira-skill` already has `JiraConfig`, `GitlabConfig`, `env.py`. Extract these into `tdt-core`:

| Source (jira-skill) | Target (tdt-core) |
|--------------------|--------------------|
| `src/jira_skill/env.py` | `src/tdt_core/env.py` |
| `src/jira_skill/config.py` (JiraConfig) | `src/tdt_core/clients/jira.py` |
| `src/jira_skill/gitlab/config.py` (GitlabConfig) | `src/tdt_core/clients/gitlab.py` |

jira-skill then re-exports from tdt-core (backwards compatible):
```python
# jira_skill/config.py
from tdt_core.clients.jira import JiraConfig, JiraClientFactory  # re-export
```

### Phase 2: Create jira-daily-reports (1-2 days)

New Python project replacing bash scripts:
```
tdt/jira-daily-reports/
├── src/jira_daily_reports/
│   ├── __init__.py
│   ├── cli.py              # typer CLI
│   ├── reports/
│   │   ├── standup.py      # Daily standup (8 AM)
│   │   ├── blocked.py      # Blocked items (9 AM)
│   │   ├── missing_info.py # Missing info (8:30 AM)
│   │   ├── wip.py          # WIP per person (5 PM)
│   │   ├── velocity.py     # Completion velocity (10 AM)
│   │   ├── platform.py     # Platform distribution (10 AM)
│   │   ├── priority.py     # Priority distribution (10 AM)
│   │   ├── code_review.py  # Code review bottleneck (2 PM)
│   │   └── sprint_health.py # Sprint health dashboard (10 AM)
│   └── delivery/
│       ├── email.py
│       ├── slack.py
│       └── file.py
├── tests/
├── pyproject.toml          # depends on tdt-core[jira]
└── README.md
```

### Phase 3: Wire jira-epic-report to tdt-core (0.5 day)

Replace `AppConfig._load_env_files()` with `tdt_core.load_tdt_env()`. Optionally use `JiraConfig.from_env()` instead of manual env reading.

### Phase 4: Wire webhook-receiver to tdt-core (0.5 day)

Replace `Settings._load_tdt_env()` with `tdt_core.load_tdt_env()`. Keep glab CLI client (it's the right choice for subprocess-based review).

### Phase 5: Wire ops-automation-suite to tdt-core (when it matures)

Early stage — adopt tdt-core from the start for new development.

---

## 6. Future Growth Patterns

### Sprint Report Enrichment Requirements

The `jira-daily-reports sprint-sheet` capability is now the canonical sprint-report
surface for stakeholder exports. Future enhancements SHALL follow these rules:

1. **Python repos SHALL use `atlassian-python-api` via `tdt-core`.**
   - No new bash/`acli` implementation for Python reporting flows
   - No direct ad-hoc REST wrappers when `JiraClientFactory` / `PatchedJira` can be extended
   - Live validation on board `#1067` shows this path is available, but sprint metadata
     and field-based estimation may be absent depending on board type/config.

2. **Sprint report SHALL include sprint-level timeline metadata when supported by the live board/scope.**
   - Sprint name
   - Sprint start date
   - Sprint end date
   - Generated-at timestamp

3. **Sprint report SHALL include per-work-item estimation data when available.**
   - Estimation value for the board context
   - Estimation source/field identity
   - Normalized display in report output
   - Distinguish `missing` (field available, no value) vs `unavailable` (field/capability not available)

4. **Sprint report SHALL include per-work-item date fields.**
   - Start date
   - End date
   - Source-field note when dates are inferred

5. **Sprint report SHALL include per-work-item logged-work data when available.**
   - Total logged work
   - Logged-work count or compact worklog summary
   - Distinguish `missing` (worklog capability available, no value) vs `unavailable` (worklog capability not available)

6. **Sprint report SHALL include summarization.**
   - Sprint-level totals for estimation and logged work
   - Coverage counts for estimation/date/logwork completeness
   - At-risk summary (behind target, missing metadata, overdue/end-date issues)
   - Short narrative summary suitable for stakeholders
   - Summary MUST degrade gracefully when estimation/sprint/worklog data are partial
     or unavailable on the live board/filter scope.

7. **Sprint report SHALL include per-work-item type classification.**
   - Work type (Story/Task/Bug/Epic/Sub-task/etc.) from `issuetype.name`
   - Displayed as `Work Type` column in Target vs Actual sheet rows
   - Displayed in markdown Enriched Target vs Actual table
   - Used in Issue Type Distribution summary section
   - Always populated from Jira `issuetype` field (intrinsic to every issue — never missing/unavailable)

8. **Sprint report SHALL include per-work-item target status with automatic fallback.**
   - Target status from bucket sheet (manual sprint planning)
   - Fallback to `SPRINT_TARGET_STATUS` env var when bucket sheet empty (default: "Done")
   - Target source tracked: "bucket" (manual) or "default" (auto-generated)
   - Verdict calculated: ✅ Met / ❌ Behind / 🚫 Rejected / ? Unknown
   - All issues MUST have target (100% coverage, no "— No Target" state except for unknown statuses)
   - Displayed as `Target Status` and `Target Source` columns in sheet output

9. **Sprint report SHALL derive JQL scope from bucket sheets before filter fallback.**
   - Extract deduplicated Jira issue keys from all configured bucket sheets
   - Use a single Google Sheets `batchGet` snapshot for keys + target statuses so
     the report cannot drift between separate reads
   - If keys exist, query Jira with `issuekey in (...)` as sprint scope source of truth
   - If no keys exist, fallback to `filter = $JIRA_FILTER_ID`
   - Scope logic SHALL be shared by sheet/terminal/markdown/json outputs to keep
     all formats aligned for the same sprint cut

10. **Sprint report SHALL normalize live Jira workflow variants before ranking.**
   - Case variants of the same workflow state MUST collapse to canonical labels
     before aggregation and verdict calculations (e.g. `TO DO` → `To Do`,
     `IN PROGRESS` → `In Progress`, `CODE REVIEW` → `Code Review`)
   - Canonical ranking SHOULD include early planning states:
     `Draft (-2)`, `Ready (-1)`, then standard delivery states
   - Unknown states MAY surface as `?`/no-target only when no known mapping exists

11. **Sprint report SHALL include an included-ticket counter column.**
    - Target vs Actual rows MUST be numbered with a `No.` counter column
    - The counter MUST be present in both Google Sheet output and markdown output
    - The counter SHOULD reflect the included ticket order after verdict sorting

12. **Sprint sheet output SHALL include a person-capacity companion tab.**
    - The same `sprint-sheet` run SHALL also write a `Person Capacity` tab
    - Person rows SHALL separate assignee-based ownership from worklog-author-based activity
    - Person aggregation SHALL use canonical person identity, daily time buckets, and visible `No.` numbering

### Sprint Report Field Semantics

Unless project-specific custom fields are configured, the default interpretation is:

| Report concept | Preferred source | Fallback |
|---|---|---|
| Work type (Story/Task/Bug) | `issuetype.name` | `Unknown` |
| Target status | Bucket sheet "Target Status" column | `SPRINT_TARGET_STATUS` env var (default: "Done") |
| Sprint start date | Sprint metadata (`startDate`) | blank |
| Sprint end date | Sprint metadata (`endDate`) | blank |
| Work item estimation | Board estimation config + Agile estimation endpoint | `timetracking.originalEstimate` / normalized seconds |
| Work item start date | Custom Start Date field (if configured) | `created` |
| Work item end date | Custom End/Due field (if configured) | `duedate`, then `resolutiondate` |
| Work item logwork | Worklog endpoint / `timespent` aggregate | zero |
| Person capacity ownership | Issue assignee | Unassigned bucket |
| Person capacity activity | Worklog author | Unassigned bucket |

### Missing vs Unavailable Semantics

- `missing` = field/capability is available for the report path, but the ticket has no populated value
- `unavailable` = field/capability is not available on the live board/filter/API path

### Historical Live Capability Validation (2026-05-23)

The board/filter scope validated these facts at the time. Current live
operations MUST use `~/.tdt/.env` for `$JIRA_FILTER_ID` and `$JIRA_BOARD_ID`,
not these historical IDs:

- The configured filter returns issue data successfully.
- The configured board is readable.
- The configured board may not expose sprint support in live validation.
- The configured board may not expose field-based estimation in live validation.
- Sample issues expose `created`, `duedate`, and `resolutiondate` where applicable.
- Sample issues frequently have `timeoriginalestimate`, `timespent`, and worklogs empty.

**Implication:** sprint-sheet enrichment MUST be optional/fallback-based, not hard-required.
The report SHALL still render target-vs-actual and summarization when time data are sparse.

### API / SDK Expectations

The design SHALL probe for, but MUST NOT assume, the following Jira capabilities:

- Board configuration exposes the estimation field/type
- Agile estimation endpoint returns issue estimation in board context
- Sprint metadata exposes `startDate` / `endDate`
- Issue/worklog APIs expose time tracking and worklog data

Implementation SHOULD keep normalization logic inside `jira-daily-reports` while
reusing `tdt-core` Jira client creation and shared Jira access primitives.
The canonical work-item retrieval/normalization layer for sprint-sheet is
`jira-daily-reports/src/jira_daily_reports/work_item_fields.py`.

### Adding a New Tool to the Ecosystem

```bash
# 1. Scaffold
mkdir tdt/new-tool && cd tdt/new-tool
uv init --lib

# 2. Depend on tdt-core (and optionally jira-skill)
# pyproject.toml:
#   dependencies = ["tdt-core @ file:///../tdt-core"]

# 3. Use shared auth
from tdt_core import load_tdt_env
from tdt_core.clients.jira import JiraClientFactory
load_tdt_env()
jira = JiraClientFactory.from_env()
```

### Anticipated Future Repos

| Planned Tool | Type | Depends On |
|-------------|------|-----------|
| `jira-daily-reports` | CLI/cron | jira-skill |
| `gitlab-analytics` | CLI | tdt-core[gitlab] |
| `sprint-planner` | CLI | jira-skill |
| `release-manager` | CLI | jira-skill + tdt-core[gitlab] |
| `team-dashboard` | Web (FastAPI) | jira-skill |
| `notification-hub` | Service | tdt-core |

### Scaling Considerations

- **uv workspaces** — when ecosystem reaches 5+ Python projects, consider `uv workspace` for unified lockfile
- **Shared CI** — GitHub Actions reusable workflows for test/lint/publish
- **Version pinning** — tdt-core uses semver; consumers pin to `~=1.0` (compatible releases)
- **Breaking changes** — tdt-core major bumps require coordinated migration (rare, planned)

---

## 7. Decision Matrix (Final)

| Criterion | Monorepo (merge all) | Ecosystem + tdt-core | Loose ecosystem (no core) |
|-----------|---------------------|---------------------|--------------------------|
| Code reuse | 🟢 Maximum | 🟢 Good (via deps) | 🔴 Duplication |
| Migration risk | 🔴 High | 🟢 Low (incremental) | 🟢 None |
| New tool onboarding | 🟡 Complex | 🟢 Simple (depend on core) | 🟡 Re-implement patterns |
| Independent releases | 🔴 Locked | 🟢 Independent | 🟢 Independent |
| Test isolation | 🔴 Coupled | 🟢 Independent | 🟢 Independent |
| Consistency | 🟢 Enforced | 🟢 Via shared types | 🔴 Drift over time |
| Effort (initial) | 🔴 3+ days | 🟡 1 day (Phase 1) | 🟢 Zero |
| Effort (per new tool) | 🟡 Integrate into monolith | 🟢 Scaffold + depend | 🔴 Re-implement auth |
| 10+ repos scalability | 🔴 Monolith bloat | 🟢 Composable | 🔴 Fragmented |

**Winner: Ecosystem + tdt-core** — best balance of reuse, independence, and scalability.

---

## 8. Approval & Next Steps

### Decision Required

- [ ] Approve ecosystem architecture with tdt-core
- [ ] Approve Phase 1 (extract tdt-core from jira-skill)
- [ ] Approve Phase 2 (create jira-daily-reports)
- [ ] Decide: uv workspace now or later?

### Success Criteria

1. `tdt-core` installable as path dependency by all projects
2. Zero duplication of env loading across ecosystem
3. New tool can be scaffolded and authenticated in < 5 minutes
4. All existing tests continue to pass (no regressions)
5. Each project remains independently testable and deployable
