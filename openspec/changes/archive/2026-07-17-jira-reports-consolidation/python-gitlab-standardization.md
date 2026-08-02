# TDT Ecosystem - python-gitlab Standardization Addendum

**Date:** 2026-05-20  
**Status:** 📋 Final Draft  
**Relates to:** [spec.md](spec.md), [design.md](design.md)

---

## Summary

Standardize on `python-gitlab` as the single GitLab API client across all tdt ecosystem projects. Local git operations (worktrees, fetch, merge) remain with git CLI.

---

## Current State: GitLab Client Fragmentation

| Project | Client | Transport | Operations |
|---------|--------|-----------|-----------|
| jira-skill | python-gitlab 8.3.0 | HTTP (requests) | Projects, MRs, notes, pipelines, branches |
| webhook-receiver | glab CLI (subprocess) | CLI → HTTP | MR view, diffs, notes CRUD, repository compare |
| webhook-receiver | git CLI (subprocess) | Local filesystem | fetch, worktree add/remove, merge, prune |
| ops-automation-suite | None yet | — | — |

**Problem:** Two different GitLab API clients doing the same thing (HTTP calls to GitLab REST API) via different mechanisms.

---

## Proposed State: Unified python-gitlab

| Project | API Client | Local Git | Operations |
|---------|-----------|-----------|-----------|
| tdt-core | python-gitlab 8.3.0 | — | GitlabConfig, GitlabClientFactory |
| jira-skill | python-gitlab (via tdt-core) | — | MR sync, status sync, comments, webhooks |
| webhook-receiver | python-gitlab (via tdt-core) | git CLI | MR view, diffs, notes, compare + worktrees |
| ops-automation-suite | python-gitlab (via tdt-core) | — | Future workflows |
| jira-daily-reports | python-gitlab (via tdt-core) | — | Code review bottleneck report |

**Rule:** python-gitlab for ALL GitLab REST API calls. git CLI ONLY for local filesystem operations (worktree, fetch, merge, checkout).

---

## webhook-receiver Migration Map

### Operations That Move to python-gitlab

| Current (glab CLI) | python-gitlab Equivalent | Benefit |
|--------------------|--------------------------|---------|
| `glab mr view {iid} -R {project} --output json` | `project.mergerequests.get(iid)` | Typed object, no JSON parsing |
| `glab api projects/{id}/merge_requests/{iid}/diffs` | `mr.diffs.list()` | Pagination handled, typed |
| `glab api projects/{id}/merge_requests/{iid}/notes` | `mr.notes.list(per_page=50)` | Typed, filterable |
| `glab api projects/{id}/repository/compare -f from=X -f to=Y` | `project.repository_compare(from_=X, to=Y)` | Typed response |
| `glab mr note create {iid} -R {project} -m {body}` | `mr.notes.create({'body': body})` | Returns note object |
| `glab api PUT .../notes/{id} -f body={body}` | `note.body = body; note.save()` | Object-oriented, clean |

### Operations That Stay with git CLI (worktree.py)

| Operation | Why git CLI Required |
|-----------|-------------------|
| `git fetch origin {branch}` | Local repo operation |
| `git worktree add {path} {branch}` | Local filesystem |
| `git worktree remove {path}` | Local filesystem |
| `git merge origin/{branch}` | Local repo operation |
| `git worktree prune` | Local cleanup |

**These cannot use python-gitlab** — they operate on local git repositories, not the GitLab REST API.

---

## Benefits of Full python-gitlab Adoption

### 1. Type Safety
```python
# Before (glab CLI): untyped dict, manual error handling
raw = json.loads(subprocess.check_output(["glab", "mr", "view", ...]))
title = raw.get("title", "")  # Any type, no IDE help

# After (python-gitlab): typed RESTObject, IDE autocomplete
mr = project.mergerequests.get(iid)
title = mr.title  # str, IDE knows the type
```

### 2. Error Handling
```python
# Before: parse stderr strings
except subprocess.CalledProcessError as e:
    if "404" in e.stderr.decode(): ...

# After: typed exceptions
from gitlab.exceptions import GitlabGetError
except GitlabGetError as e:
    if e.response_code == 404: ...
```

### 3. Retry & Rate Limiting (Built-in)
```python
# python-gitlab handles retries natively
gl = Gitlab(url, token, retry_transient_errors=True)
# Automatically retries on 500/502/503/504
```

### 4. Pagination (Built-in)
```python
# Before: manual per_page parameter in URL
cmd = ["glab", "api", f"...?per_page=50"]

# After: automatic pagination
notes = mr.notes.list(iterator=True)  # lazy iterator, handles pagination
```

### 5. No External Binary Dependency
```python
# Before: requires glab CLI installed, configured, in PATH
# After: pure Python, pip install python-gitlab
```

### 6. Shared Client Instance
```python
# All projects use the same factory:
from tdt_core.clients.gitlab import GitlabClientFactory
factory = GitlabClientFactory.from_env()
gl = factory.create_client()
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| python-gitlab behavior differs from glab | Medium | Test each operation against real API before switching |
| Timeout handling differs | Low | python-gitlab supports `timeout` param per-request |
| glab `--unique` flag for notes | Low | Implement check-before-create logic (already exists in `post_or_update_review`) |
| Memory usage in long-running server | Low | python-gitlab uses requests sessions, same as any HTTP client |
| Breaking change in python-gitlab 9.x | Medium | Pin to `>=8.3.0,<9.0.0`, upgrade deliberately |

---

## Implementation Plan

### Phase 1: tdt-core with python-gitlab (already planned)

Extract `GitlabConfig` + `GitlabClientFactory` into tdt-core. This is the foundation.

### Phase 2: webhook-receiver migration (1 day)

```python
# New: webhook_receiver/gitlab/client.py using python-gitlab

from tdt_core.clients.gitlab import GitlabClientFactory

class GitLabClient:
    """Client for GitLab MR operations via python-gitlab."""

    def __init__(self, project_id: int):
        factory = GitlabClientFactory.from_env()
        self._gl = factory.create_client()
        self._project = self._gl.projects.get(project_id)

    def mr_view(self, mr_iid: int) -> dict | None:
        try:
            mr = self._project.mergerequests.get(mr_iid)
            return mr.attributes
        except GitlabGetError:
            return None

    def fetch_diffs(self, mr_iid: int) -> list[dict] | None:
        mr = self._project.mergerequests.get(mr_iid)
        return [d.attributes for d in mr.diffs.list(iterator=True)]

    def check_existing_review(self, mr_iid: int) -> dict | None:
        mr = self._project.mergerequests.get(mr_iid)
        for note in mr.notes.list(per_page=50, iterator=True):
            if "<!-- mr-auto-review -->" in note.body:
                return {"id": note.id, "body": note.body, ...}
        return None

    def get_commit_diff(self, mr_iid: int, from_sha: str, to_sha: str) -> list[dict] | None:
        result = self._project.repository_compare(from_=from_sha, to=to_sha)
        return result.get("diffs", [])

    def post_review(self, mr_iid: int, review_body: str) -> bool:
        mr = self._project.mergerequests.get(mr_iid)
        mr.notes.create({"body": review_body})
        return True

    def update_review(self, mr_iid: int, note_id: int, review_body: str) -> bool:
        mr = self._project.mergerequests.get(mr_iid)
        note = mr.notes.get(note_id)
        note.body = review_body
        note.save()
        return True
```

**Key:** Same public interface (`mr_view`, `fetch_diffs`, etc.) — `MROperations` and all consumers unchanged.

### Phase 3: Remove glab dependency

After migration verified:
- Remove `glab` from deployment requirements
- Update Dockerfile (no glab install needed)
- Update docs

---

## Updated tdt-core Design (with python-gitlab as standard)

```toml
# tdt-core/pyproject.toml
[project]
name = "tdt-core"
dependencies = [
    "pydantic>=2.5",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
jira = ["atlassian-python-api>=3.41.16"]
gitlab = ["python-gitlab>=8.3.0,<9.0.0"]
all = [
    "atlassian-python-api>=3.41.16",
    "python-gitlab>=8.3.0,<9.0.0",
]
```

### Shared GitLab Interface in tdt-core

```python
# tdt_core/clients/gitlab.py

from __future__ import annotations
from typing import TYPE_CHECKING

from pydantic import AliasChoices, BaseModel, Field, SecretStr

if TYPE_CHECKING:
    from gitlab import Gitlab

class GitlabConfig(BaseModel):
    """GitLab connection configuration.
    
    Loads from ~/.tdt/.env:
      GITLAB_PAT (or GITLAB_TOKEN) → token
      GITLAB_HOST (or GITLAB_URL) → url
    """
    url: str = Field(
        default="https://git.ecomedic.vn",
        validation_alias=AliasChoices("GITLAB_HOST", "GITLAB_URL"),
    )
    token: SecretStr = Field(
        validation_alias=AliasChoices("GITLAB_PAT", "GITLAB_TOKEN"),
    )
    ssl_verify: bool = True
    timeout: int = 30
    per_page: int = 100
    pagination: str = "offset"
    retry_transient_errors: bool = True

    @classmethod
    def from_env(cls) -> GitlabConfig:
        from tdt_core.env import load_tdt_env
        load_tdt_env()
        import os
        return cls(
            url=os.getenv("GITLAB_HOST", os.getenv("GITLAB_URL", "https://git.ecomedic.vn")),
            token=os.getenv("GITLAB_PAT", os.getenv("GITLAB_TOKEN", "")),
        )


class GitlabClientFactory:
    """Factory for creating configured python-gitlab instances."""

    def __init__(self, config: GitlabConfig):
        self._config = config
        self._gl: Gitlab | None = None

    def create_client(self) -> Gitlab:
        """Create and return a configured gitlab.Gitlab instance."""
        from gitlab import Gitlab
        if self._gl is None:
            self._gl = Gitlab(
                url=self._config.url,
                private_token=self._config.token.get_secret_value(),
                ssl_verify=self._config.ssl_verify,
                timeout=self._config.timeout,
                per_page=self._config.per_page,
                pagination=self._config.pagination,
                retry_transient_errors=self._config.retry_transient_errors,
            )
        return self._gl

    def validate_connection(self) -> bool:
        gl = self.create_client()
        gl.auth()
        return gl.user is not None

    @classmethod
    def from_env(cls) -> GitlabClientFactory:
        return cls(config=GitlabConfig.from_env())
```

---

## Decision: Ecosystem GitLab Strategy

| Concern | Decision |
|---------|----------|
| GitLab REST API client | python-gitlab (standardized via tdt-core) |
| Local git operations | git CLI (subprocess) — only in projects that need worktrees |
| Auth pattern | `GitlabClientFactory.from_env()` everywhere |
| Error handling | Wrap python-gitlab exceptions in project-specific errors |
| Pagination | python-gitlab built-in (offset mode for git.ecomedic.vn) |
| Rate limiting | python-gitlab built-in retry_transient_errors |
| GraphQL | `python-gitlab[gql]` extra when needed |

---

## Updated Dependency Graph

```
tdt-core[gitlab]  ←── python-gitlab 8.3.0
    │
    ├── jira-skill (MR sync, status sync, comments, branch linking)
    │     ├── jira-epic-report (no gitlab needed currently)
    │     └── jira-daily-reports (code review bottleneck report)
    │
    ├── webhook-receiver (MR review: diffs, notes, compare)
    │     └── also uses: git CLI for worktrees (local only)
    │
    └── ops-automation-suite (future gitlab workflows)
```

**Single source of truth:** `tdt-core` owns `GitlabConfig` + `GitlabClientFactory`. All projects get python-gitlab through this.
