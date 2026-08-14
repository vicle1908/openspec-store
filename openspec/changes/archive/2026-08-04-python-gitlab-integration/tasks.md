# python-gitlab Integration - Tasks

## Phase 1: Foundation (Day 1-2)

**Status:** 📋 Not Started  
**Duration:** 2 days  
**Effort:** Medium

### Task 1.1: Add python-gitlab Dependency

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 30 min

**Description:**
Add `python-gitlab>=8.3.0,<9.0.0` to pyproject.toml and verify installation. Optionally add `python-gitlab[gql]` for GraphQL support.

**Acceptance Criteria:**

- [x] [historical] `python-gitlab>=8.3.0,<9.0.0` added to `dependencies` in pyproject.toml
- [x] [historical] `python-gitlab[gql]>=8.3.0,<9.0.0` added to `[project.optional-dependencies]` under `gql`
- [x] [historical] `pip install -e ".[dev]"` succeeds
- [x] [historical] `python -c "import gitlab; print(gitlab.__version__)"` outputs 8.3.x
- [x] [historical] `gitlab --version` CLI works
- [x] [historical] Verify python-gitlab's own dependencies: `requests`, `requests-toolbelt` installed automatically

**Deliverables:**

- Updated `pyproject.toml`

### Task 1.2: Create GitlabConfig Model

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1 hour

**Description:**
Create pydantic `GitlabConfig` model for typed configuration management.

**Acceptance Criteria:**

- [x] [historical] `GitlabConfig` class in `src/gitlab/client.py`
- [x] [historical] Fields: `url` (HttpUrl), `token` (SecretStr), `ssl_verify` (bool), `timeout` (int), `api_version` (str), `per_page` (int), `pagination` (str: "keyset"|"offset"), `retry_transient_errors` (bool)
- [x] [historical] Environment variable loading via `Config.env_prefix = "GITLAB_"`
- [x] [historical] Validation: URL must be valid, timeout > 0, per_page between 1-100, pagination must be "keyset" or "offset"
- [x] [historical] Supports python-gitlab's native config file auto-discovery (`PYTHON_GITLAB_CFG` env var, `~/.python-gitlab.cfg`)
- [x] [historical] Unit tests for validation

**Deliverables:**

- `src/gitlab/client.py` (GitlabConfig class)
- `tests/gitlab/test_client.py` (config tests)

### Task 1.3: Create GitlabClientFactory

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1.5 hours

**Description:**
Create factory class for typed `gitlab.Gitlab` instances.

**Acceptance Criteria:**

- [x] [historical] `GitlabClientFactory` class in `src/gitlab/client.py`
- [x] [historical] `from_config(config: GitlabConfig) -> Gitlab` static method
- [x] [historical] `from_env() -> Gitlab` static method
- [x] [historical] Client configured with `retry_transient_errors=True`, `obey_rate_limit=True`
- [x] [historical] `private_token` auth from config (python-gitlab handles token auth internally)
- [x] [historical] SSL verification from config (`ssl_verify` parameter)
- [x] [historical] Timeout from config (`timeout` parameter)
- [x] [historical] Pagination defaults: `per_page=100`, `pagination="keyset"` (keyset pagination is more efficient for large datasets)
- [x] [historical] Unit tests with mocked Gitlab

**Deliverables:**

- `src/gitlab/client.py` (GitlabClientFactory class)
- `tests/gitlab/test_client.py` (factory tests)

### Task 1.4: Create Exception Hierarchy

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1 hour

**Description:**
Create unified exception hierarchy wrapping python-gitlab's `gitlab.exceptions.GitlabError` exceptions.

**Acceptance Criteria:**

- [x] [historical] `src/gitlab/exceptions.py` created
- [x] [historical] `GitlabIntegrationError` base exception (wraps `gitlab.exceptions.GitlabError`)
- [x] [historical] `GitlabAuthError` — wraps `gitlab.exceptions.GitlabAuthenticationError` (401)
- [x] [historical] `GitlabResourceNotFoundError` — wraps `gitlab.exceptions.GitlabGetError` (404)
- [x] [historical] `GitlabRateLimitError` — wraps `gitlab.exceptions.GitlabRateLimitError` (429)
- [x] [historical] `GitlabValidationError` — wraps `gitlab.exceptions.GitlabCreateError` / `GitlabUpdateError` (422)
- [x] [historical] `GitlabConnectionError` — wraps `gitlab.exceptions.GitlabHttpError` for 5xx/connection errors
- [x] [historical] `map_gitlab_error(exc: gitlab.exceptions.GitlabError) -> GitlabIntegrationError` function
- [x] [historical] Preserves original exception as `__cause__` for traceback
- [x] [historical] Unit tests for all exception types and mapping

**Deliverables:**

- `src/gitlab/exceptions.py`
- `tests/gitlab/test_exceptions.py`

### Task 1.5: Create Model Adapters

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 2 hours

**Description:**
Add `from_gitlab_*` classmethods and `to_gitlab_dict` methods to existing dataclass models. python-gitlab objects are `RESTObject` subclasses — access attributes directly (e.g., `mr.title`, `mr.web_url`).

**Acceptance Criteria:**

- [x] [historical] `MergeRequest.from_gitlab_mr(mr: ProjectMergeRequest) -> MergeRequest`
- [x] [historical] `GitLabComment.from_gitlab_note(note: ProjectNote) -> GitLabComment`
- [x] [historical] `Pipeline.from_gitlab_pipeline(pipeline: ProjectPipeline) -> Pipeline`
- [x] [historical] `GitLabUser.from_gitlab_user(user: dict) -> GitLabUser`
- [x] [historical] `GitLabProject.from_gitlab_project(project: Project) -> GitLabProject`
- [x] [historical] `to_gitlab_dict()` methods for reverse conversion on all models
- [x] [historical] Handle `RESTObject` attribute access patterns (no `.get()`, use `getattr()` with defaults)
- [x] [historical] Handle `GitlabList` return types (list-like, iterate directly)
- [x] [historical] Unit tests for all adapter methods with mocked RESTObjects

**Deliverables:**

- Updated `src/gitlab/models.py`
- `tests/gitlab/test_models.py` (adapter tests)

---

## Phase 2: Module Migration (Day 3-4)

**Status:** 📋 Not Started  
**Duration:** 2 days  
**Effort:** High

### Task 2.1: Migrate webhook_handler.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1.5 hours

**Description:**
Update `WebhookHandler` and `WebhookQueue` to use typed `gitlab.Gitlab`.

**Acceptance Criteria:**

- [x] [historical] `WebhookHandler.__init__` accepts `gl: Gitlab` instead of `gitlab_client: Any`
- [x] [historical] `WebhookQueue.__init__` accepts `gl: Gitlab` instead of `gitlab_client: Any`
- [x] [historical] Webhook signature verification unchanged (uses raw payload, not python-gitlab)
- [x] [historical] Use `gl.projects.get(id)` for project lookups when needed
- [x] [historical] All existing webhook tests pass
- [x] [historical] No `Any` types remain in webhook_handler.py

**Deliverables:**

- Updated `src/gitlab/webhook_handler.py`
- Updated `tests/gitlab/test_webhook_handler.py`

### Task 2.2: Migrate mr_sync.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 2 hours

**Description:**
Update `MRSynchronization` to use python-gitlab's Project.mergerequests API.

**Acceptance Criteria:**

- [x] [historical] `MRSynchronization.__init__` accepts `gl: Gitlab` instead of `gitlab_client: Any`
- [x] [historical] MR fetching: `gl.projects.get(id).mergerequests.get(iid)` (uses IID, not global ID)
- [x] [historical] MR listing: `gl.projects.get(id).mergerequests.list(state=..., per_page=100, iterator=True)` for auto-pagination
- [x] [historical] MR creation: `gl.projects.get(id).mergerequests.create({'source_branch': ..., 'target_branch': ..., 'title': ...})`
- [x] [historical] MR update: `mr.state_event = 'close'` / `mr.save()`
- [x] [historical] Uses `MergeRequest.from_gitlab_mr()` adapter
- [x] [historical] All existing MR sync tests pass
- [x] [historical] No `Any` types remain in mr_sync.py

**Deliverables:**

- Updated `src/gitlab/mr_sync.py`
- Updated `tests/gitlab/test_mr_sync.py`

### Task 2.3: Migrate status_sync.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1.5 hours

**Description:**
Update `StatusSynchronization` to use python-gitlab's merge request state management.

**Acceptance Criteria:**

- [x] [historical] `StatusSynchronization.__init__` accepts `gl: Gitlab` instead of `gitlab_client: Any`
- [x] [historical] Status mapping logic preserved (DEFAULT_STATUS_MAPPING, DEFAULT_REVERSE_MAPPING)
- [x] [historical] MR state changes use `mr.state_event` property
- [x] [historical] `StatusMappingBuilder` updated if needed
- [x] [historical] All existing status sync tests pass
- [x] [historical] No `Any` types remain in status_sync.py

**Deliverables:**

- Updated `src/gitlab/status_sync.py`
- Updated `tests/gitlab/test_status_sync.py`

### Task 2.4: Migrate comment_sync.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 2 hours

**Description:**
Update `CommentSynchronization` and `BidirectionalCommentSync` to use python-gitlab's notes API.

**Acceptance Criteria:**

- [x] [historical] `CommentSynchronization.__init__` accepts `gl: Gitlab` instead of `gitlab_client: Any`
- [x] [historical] `BidirectionalCommentSync.__init__` accepts `gl: Gitlab` instead of `gitlab_client: Any`
- [x] [historical] Note creation: `mr.notes.create({'body': text})`
- [x] [historical] Note listing: `mr.notes.list(per_page=100, iterator=True)` for auto-pagination
- [x] [historical] Note update: `note.body = text` / `note.save()`
- [x] [historical] Note deletion: `note.delete()`
- [x] [historical] Discussion support: `mr.discussions.create({'body': '...'})` for threaded comments
- [x] [historical] Uses `GitLabComment.from_gitlab_note()` adapter
- [x] [historical] All existing comment sync tests pass
- [x] [historical] No `Any` types remain in comment_sync.py

**Deliverables:**

- Updated `src/gitlab/comment_sync.py`
- Updated `tests/gitlab/test_comment_sync.py`

### Task 2.5: Migrate branch_linking.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1 hour

**Description:**
Update `BranchLinking` to use python-gitlab's branch API for optional validation.

**Acceptance Criteria:**

- [x] [historical] `BranchLinking.__init__` accepts `gl: Gitlab` instead of `gitlab_client: Any`
- [x] [historical] `validate_branch_exists(project_id, branch_name)` method added
- [x] [historical] Uses `gl.projects.get(id).branches.get(name)` for validation (raises `GitlabGetError` if not found)
- [x] [historical] Regex-based issue key extraction preserved
- [x] [historical] `BranchNameValidator` updated if needed
- [x] [historical] All existing branch linking tests pass
- [x] [historical] No `Any` types remain in branch_linking.py

**Deliverables:**

- Updated `src/gitlab/branch_linking.py`
- Updated `tests/gitlab/test_branch_linking.py`

---

## Phase 3: New Modules (Day 5-6)

**Status:** 📋 Not Started  
**Duration:** 2 days  
**Effort:** Medium

### Task 3.1: Create projects.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 2 hours

**Description:**
Create `ProjectOperations` class for project management via python-gitlab.

**Acceptance Criteria:**

- [x] [historical] `ProjectOperations` class with `gl: Gitlab` parameter
- [x] [historical] `get_project(id: int) -> Project` — uses `gl.projects.get(id)`
- [x] [historical] `list_projects(**filters) -> list[Project]` — uses `gl.projects.list(**filters, pagination="keyset")`
- [x] [historical] `get_jira_integration(project_id: int) -> dict` — uses `project.services.list()` to find JiraService
- [x] [historical] `search_projects(query: str) -> list[Project]` — uses `gl.projects.list(search=query)`
- [x] [historical] Uses `GitLabProject.from_gitlab_project()` adapter
- [x] [historical] Unit tests with mocked Gitlab

**Deliverables:**

- `src/gitlab/projects.py`
- `tests/gitlab/test_projects.py`

### Task 3.2: Create pipelines.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 2 hours

**Description:**
Create `PipelineOperations` class for CI/CD pipeline management.

**Acceptance Criteria:**

- [x] [historical] `PipelineOperations` class with `gl: Gitlab` parameter
- [x] [historical] `get_pipeline(project_id: int, pipeline_id: int) -> Pipeline` — uses `project.pipelines.get(id)`
- [x] [historical] `list_project_pipelines(project_id: int, **filters) -> list[Pipeline]` — uses `project.pipelines.list(**filters, pagination="keyset")`
- [x] [historical] `get_latest_pipeline(project_id: int, ref: str) -> Pipeline` — uses `project.pipelines.list(ref=ref, per_page=1, order_by='id', sort='desc')`
- [x] [historical] `get_pipeline_variables(project_id: int, pipeline_id: int) -> dict` — uses `pipeline.variables`
- [x] [historical] `get_pipeline_jobs(project_id: int, pipeline_id: int) -> list` — uses `pipeline.jobs.list()`
- [x] [historical] Uses `Pipeline.from_gitlab_pipeline()` adapter
- [x] [historical] Unit tests with mocked Gitlab

**Deliverables:**

- `src/gitlab/pipelines.py`
- `tests/gitlab/test_pipelines.py`

### Task 3.3: Create deployments.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1.5 hours

**Description:**
Create `DeploymentOperations` class for deployment tracking.

**Acceptance Criteria:**

- [x] [historical] `DeploymentOperations` class with `gl: Gitlab` parameter
- [x] [historical] `list_deployments(project_id: int, **filters) -> list[Deployment]` — uses `project.deployments.list(**filters, pagination="keyset")`
- [x] [historical] `get_deployment(project_id: int, deployment_id: int) -> Deployment` — uses `project.deployments.get(id)`
- [x] [historical] `get_latest_deployment(project_id: int, environment: str) -> Deployment` — uses `project.deployments.list(environment=env, per_page=1, order_by='id', sort='desc')`
- [x] [historical] Unit tests with mocked Gitlab

**Deliverables:**

- `src/gitlab/deployments.py`
- `tests/gitlab/test_deployments.py`

### Task 3.4: Create releases.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1.5 hours

**Description:**
Create `ReleaseOperations` class for release management.

**Acceptance Criteria:**

- [x] [historical] `ReleaseOperations` class with `gl: Gitlab` parameter
- [x] [historical] `list_releases(project_id: int) -> list[Release]` — uses `project.releases.list(pagination="keyset")`
- [x] [historical] `get_release(project_id: int, tag_name: str) -> Release` — uses `project.releases.get(tag_name)`
- [x] [historical] `get_latest_release(project_id: int) -> Release` — uses `project.releases.list(per_page=1, order_by='released_at', sort='desc')`
- [x] [historical] Unit tests with mocked Gitlab

**Deliverables:**

- `src/gitlab/releases.py`
- `tests/gitlab/test_releases.py`

### Task 3.5: Create graphql.py

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 2 hours

**Description:**
Create `GitlabGraphQL` class for efficient cross-project GraphQL queries using python-gitlab's built-in GraphQL support (`gl.graphql(query, variables={...})`). Requires `python-gitlab[gql]` extra.

**Acceptance Criteria:**

- [x] [historical] `GitlabGraphQL` class with `gl: Gitlab` parameter
- [x] [historical] `get_pipelines_across_projects(project_ids, status, limit) -> list[dict]` — single GraphQL query across all projects
- [x] [historical] `get_mrs_across_projects(project_ids, state, limit) -> list[dict]` — single GraphQL query across all projects
- [x] [historical] `get_deployments_across_projects(project_ids, environment, limit) -> list[dict]`
- [x] [historical] All queries are parameterized using GraphQL variables (no string interpolation)
- [x] [historical] Error handling for GraphQL errors (`gl.graphql()` returns dict with 'errors' key on failure)
- [x] [historical] Uses `gl.graphql()` method — no separate HTTP client needed
- [x] [historical] Unit tests with mocked GraphQL responses

**Deliverables:**

- `src/gitlab/graphql.py`
- `tests/gitlab/test_graphql.py`

---

## Phase 4: Testing, Docs, Cleanup (Day 7)

**Status:** 📋 Not Started  
**Duration:** 1 day  
**Effort:** Medium

### Task 4.1: Update __init__.py Exports

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 30 min

**Description:**
Update `src/gitlab/__init__.py` to export all new modules and symbols.

**Acceptance Criteria:**

- [x] [historical] All new modules exported (client, projects, pipelines, deployments, releases, graphql, exceptions)
- [x] [historical] `GitlabClientFactory` and `GitlabConfig` exported
- [x] [historical] All exception classes exported
- [x] [historical] `__all__` list updated
- [x] [historical] Re-export key python-gitlab types for convenience: `Gitlab`, `Project`, `ProjectMergeRequest`, `ProjectPipeline`

**Deliverables:**

- Updated `src/gitlab/__init__.py`

### Task 4.2: Run Full Test Suite

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1 hour

**Description:**
Run all existing and new tests to verify nothing is broken.

**Acceptance Criteria:**

- [x] [historical] All 28 existing gitlab tests pass
- [x] [historical] All new tests pass (estimated 40+ new tests)
- [x] [historical] Test coverage ≥ 95% for gitlab package
- [x] [historical] No regressions in other packages
- [x] [historical] Mock patterns use `unittest.mock` with python-gitlab RESTObjects (not dicts)
- [x] [historical] Integration tests use real GitLab instance (git.ecomedic.vn test project)

**Verification:**

```bash
cd jira-skill && python -m pytest tests/ -v --cov=src/gitlab --cov-report=term
# Expected: 68+ tests pass, coverage ≥ 95%
```

### Task 4.3: Type Check with mypy

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 30 min

**Description:**
Run mypy in strict mode on the gitlab package.

**Acceptance Criteria:**

- [x] [historical] `mypy --strict src/gitlab/` passes with zero errors
- [x] [historical] Zero `Any` types in the gitlab package
- [x] [historical] All public methods have complete type annotations
- [x] [historical] python-gitlab type stubs verified compatible (python-gitlab ships with types)
- [x] [historical] `# type: ignore` comments only where python-gitlab types are incomplete

**Verification:**

```bash
cd jira-skill && mypy --strict src/gitlab/
# Expected: Success, no errors

# Count Any types
grep -r ": Any" src/gitlab/ | grep -v "#" | wc -l
# Expected: 0
```

### Task 4.4: Update Skill Documentation

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1.5 hours

**Description:**
Update jira-integration skill documentation with python-gitlab usage patterns.

**Acceptance Criteria:**

- [x] [historical] python-gitlab section added to SKILL.md with:
  - Installation: `pip install python-gitlab[gql]`
  - Configuration: `~/.python-gitlab.cfg` or env vars
  - Basic usage: `gl = gitlab.Gitlab(url, private_token=token)`
  - Object tree: `gl.projects.get(id).mergerequests.list()`
  - Pagination: `iterator=True` for auto-pagination, `pagination="keyset"` for large datasets
  - Error handling: `gitlab.exceptions.GitlabError` hierarchy
  - GraphQL: `gl.graphql(query, variables={...})`
- [x] [historical] CLI command examples (list projects, check pipelines, etc.)
- [x] [historical] Code examples updated to use python-gitlab patterns
- [x] [historical] Migration guide for developers (old `gitlab_client: Any` → new `gl: Gitlab`)
- [x] [historical] At least 5 python-gitlab references in docs

**Deliverables:**

- Updated `.agents/skills/jira-integration/SKILL.md`

### Task 4.5: Code Cleanup

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 1 hour

**Description:**
Remove dead code and verify codebase size reduction.

**Acceptance Criteria:**

- [x] [historical] Remove any unused custom HTTP/pagination/retry code (if only used by gitlab)
- [x] [historical] Verify codebase size reduced by at least 15% in gitlab package
- [x] [historical] Run linter: `pylint src/gitlab/`
- [x] [historical] Run formatter: `black src/gitlab/`

**Verification:**

```bash
# Count lines before/after
wc -l jira-skill/src/gitlab/*.py
# Expected: ~1,200 lines (down from ~1,500)

# Lint
cd jira-skill && pylint src/gitlab/
# Expected: Score ≥ 8.5/10
```

### Task 4.6: Final Verification

**Status:** 📋 Not Started  
**Assignee:** TBD  
**Duration:** 30 min

**Description:**
Run complete verification suite.

**Acceptance Criteria:**

- [x] [historical] All tests pass
- [x] [historical] Type checking passes
- [x] [historical] Linting passes
- [x] [historical] Import check: `python -c "from src.gitlab import *"` succeeds
- [x] [historical] CLI check: `gitlab --version` works

**Verification:**

```bash
cd jira-skill && python -m pytest tests/ -v && mypy --strict src/gitlab/ && pylint src/gitlab/
# Expected: All green
```


---

> **Historical record:** This change was archived with 140 incomplete task(s) (0/140 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
