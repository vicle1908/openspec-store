# TDT Ecosystem - Design Document

**Date:** 2026-05-20

---

## Architecture Diagram

```
                    ┌─────────────────────────────┐
                    │         tdt workspace        │
                    └─────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
    ┌─────▼─────┐          ┌─────▼─────┐          ┌─────▼─────┐
    │  Services │          │   CLIs    │          │  Libraries │
    └───────────┘          └───────────┘          └───────────┘
          │                       │                       │
  ┌───────┴───────┐    ┌─────────┼─────────┐      ┌─────┴─────┐
  │               │    │         │         │      │           │
webhook-     ops-auto  epic-   daily-   future   jira-     tdt-core
receiver     -suite    report  reports  tools    skill
(FastAPI)    (async)   (typer) (typer)           (library)  (infra)
  v8.0        v1.0     v2.0    NEW               v1.1       NEW
```

## Layer Responsibilities

### Layer 0: tdt-core (Infrastructure)

**Owns:** Auth, config loading, client factories, shared DTOs, resilience primitives.

**Does NOT own:** Business logic, domain rules, API endpoints, CLI commands.

**Stability contract:** Semver. Breaking changes require major version bump + migration guide.

```python
# The "3 lines to authenticate" promise:
from tdt_core import load_tdt_env
from tdt_core.clients.jira import JiraClientFactory

load_tdt_env()
jira = JiraClientFactory.from_env()
```

### Layer 1: jira-skill (Domain Library)

**Owns:** JQL builder, board/sprint/issue management, GitLab sync logic, webhook handling, adapters.

**Depends on:** tdt-core (re-exports config classes for backwards compat)

**Consumers:** jira-epic-report, jira-daily-reports, ops-automation-suite

### Layer 2: Application Projects (CLIs / Services)

Each application is independently deployable with its own:
- Entry point (typer CLI, FastAPI server, cron job)
- Test suite
- Version number
- Deployment target

---

## Key Design Decisions

### D1: Path Dependencies (Not PyPI Publishing)

All projects reference each other via filesystem paths:
```toml
dependencies = ["tdt-core @ file:///${PROJECT_ROOT}/../tdt-core"]
```

**Rationale:** Single workspace, single developer, no need for package registry overhead. When/if the team grows, switch to private PyPI or uv workspace.

### D2: Optional Extras for Client Libraries

```toml
# tdt-core/pyproject.toml
[project.optional-dependencies]
jira = ["atlassian-python-api>=3.41.16"]
gitlab = ["python-gitlab>=8.3.0,<9.0.0"]
all = ["atlassian-python-api>=3.41.16", "python-gitlab>=8.3.0,<9.0.0"]
```

**Rationale:** webhook-receiver only needs gitlab config (env loading), not the full atlassian-python-api. Optional extras keep installs lean.

### D3: python-gitlab as Standard GitLab API Client

All ecosystem projects use `python-gitlab` (via tdt-core) for GitLab REST API operations. git CLI is used ONLY for local filesystem operations (worktrees, fetch, merge).

| Use Case | Tool | Rationale |
|----------|------|-----------|
| GitLab REST API (MRs, notes, diffs, compare) | python-gitlab | Typed, retries, pagination built-in |
| Local git operations (worktree, fetch, merge) | git CLI | Filesystem ops, not API calls |

**webhook-receiver migration:** Replace `glab` CLI subprocess calls with python-gitlab. Same public interface (`mr_view`, `fetch_diffs`, etc.) — consumers unchanged. See [python-gitlab-standardization.md](python-gitlab-standardization.md) for full migration map.

**Benefits:** Type safety, built-in retry/pagination, no external binary dependency, shared client factory, consistent error handling across ecosystem.

### D4: Re-export Pattern for Backwards Compatibility

When extracting code from jira-skill to tdt-core:
```python
# jira_skill/config.py (after extraction)
from tdt_core.clients.jira import JiraConfig, JiraClientFactory  # re-export

__all__ = ["JiraConfig", "JiraClientFactory"]  # existing consumers unaffected
```

**Rationale:** Zero breaking changes for existing code. Consumers can gradually migrate imports.

### D5: Dataclass DTOs (Not ORM Models)

Shared models in tdt-core are plain dataclasses:
```python
@dataclass
class GitLabProject:
    id: int
    name: str
    path_with_namespace: str
    web_url: str
    default_branch: str = "main"
```

**Rationale:** No framework coupling. Works with python-gitlab, glab CLI output, raw API responses. Each consumer adapts to/from these DTOs using their own adapter layer.

### D6: No Shared Database

Each project manages its own persistence:
- jira-epic-report: file cache (~/.cache/epic-report/)
- webhook-receiver: SQLite checkpoint
- ops-automation-suite: PostgreSQL (planned)
- jira-daily-reports: file output only

**Rationale:** Different persistence needs, different lifecycles. Shared DB creates coupling and migration nightmares.

### D7: Standardized Toolchain (ruff + mypy + uv)

All projects use identical tool configurations. See [toolchain-standardization.md](toolchain-standardization.md).

| Tool | Role | Replaces |
|------|------|----------|
| uv >=0.11.15 | Package manager, venv, Python install | pip, pyenv, poetry |
| ruff | Linting + formatting | flake8, isort, black, pyupgrade |
| mypy | Type checking (gradual → strict) | — |
| pytest | Testing (80% coverage min) | — |
| hatchling | Build backend | setuptools |
| pre-commit | Git hooks (ruff + mypy) | manual checks |

**Key decisions:**
- `line-length = 100` (standardized across all projects)
- `ruff format` replaces black (faster, same output)
- mypy strict for new code (tdt-core), pragmatic for legacy
- No uv workspace (independent projects with path deps)
- `src/` layout everywhere (prevents import confusion)

### D8: Sprint Report Metadata Enrichment (SDK-first)

`jira-daily-reports sprint-sheet` is the authoritative **filter-scoped stakeholder
export** in this ecosystem. It is not a Jira-native sprint report on the live
board `#1067`; it will be enriched with:

- Per-work-item estimation
- Per-work-item start date / end date
- Per-work-item logwork
- Sprint-level summarization

**Mandatory access pattern**

- Use `atlassian-python-api` through `tdt-core` client factories
- Avoid reintroducing bash/`acli` report pipelines in Python repos

**Planned retrieval flow**

1. Read bucket tabs once via Google Sheets `batchGet` snapshot
2. Parse issue keys + target statuses from that same snapshot
3. If keys exist, fetch scoped issues with `issuekey in (...)`; otherwise fallback to filter JQL
4. Probe board estimation config (field/type) when board supports it
5. Probe sprint metadata (start/end dates) when board supports sprints
6. Fetch/derive estimation per issue in board context when available
7. Fetch/derive worklog totals per issue
8. Normalize start/end date fields with explicit fallback strategy
9. Produce both per-item enriched rows and sprint-level summary section
10. Number included tickets with a stable counter column after verdict sorting

**Observed live constraint (2026-05-23)**

- Canonical board `#1067` currently behaves like a Kanban/non-sprint board for API purposes
- Sprint metadata lookup failed with: `The board does not support sprints`
- Agile estimation lookup failed with: `Board does not have field based estimation.`
- Sample issues returned empty worklog / timespent / original estimate values

Therefore the design MUST:

- gate sprint metadata behind capability detection
- gate board-estimation enrichment behind board config support
- allow sparse/empty logwork datasets
- preserve useful output when only `created`, `duedate`, `resolutiondate`, and status data are present

**Output contract**

- Sheet output keeps Target vs Actual section
- Add Estimation / Start / End / Logwork columns per issue
- Add summary block: totals, completeness coverage, risk highlights, short narrative

---

## Growth Playbook

### Adding a New CLI Tool

1. `mkdir tdt/new-tool && cd tdt/new-tool`
2. `uv init` + add `tdt-core` (or `jira-skill`) dependency
3. Implement domain logic
4. Use `load_tdt_env()` + client factories for auth
5. Add typer CLI entry point
6. Add tests
7. Done — independently deployable

### Adding a New Service

1. Same as CLI but with FastAPI/uvicorn
2. Depend on `tdt-core` for config
3. Add Dockerfile + docker-compose.yml
4. Health check endpoint at `/health`

### Promoting a Pattern to tdt-core

When 3+ projects implement the same pattern:
1. Identify the common interface
2. Add to tdt-core with tests
3. Consumers migrate at their own pace (re-export pattern)
4. Remove duplicated code after all consumers migrated

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| tdt-core becomes a kitchen sink | Strict scope: only infra, no business logic. PR review gate. |
| Breaking change in tdt-core | Semver + re-export pattern allows gradual migration |
| Circular dependency | Layered architecture enforced: core → library → application |
| Path deps break on different machines | All paths relative via `${PROJECT_ROOT}/../` |
| Over-engineering for single developer | Start minimal (Phase 1 = just env + config). Grow only when duplication hurts. |
