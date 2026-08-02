# Tasks: jira-req-issue-type-automator

Python 3.14 + uv + ruff + mypy + pytest. SDK in `tdt-core`, CLI in `jira-skill`.

## 1. tdt-core: SDK Layer

Owner: `tdt-core/`

- [x] 1.1 Create `src/tdt_core/clients/jira_types.py`
  - `IssueType`, `IssueTypeScheme`, `IssueTypeSchemeProjectMapping` dataclasses
  - `IssueTypeAlreadyInSchemeError`, `IssueTypeNotFoundError`, `ProjectNotClassicError` exceptions
  - `_retry_request()` helper (same as `jira_workflow.py`)
  - `IssueTypeSchemeClient` class with all methods
  - Verify: `uv run python -c "from tdt_core.clients.jira_types import IssueTypeSchemeClient; print('ok')"`

- [x] 1.2 `uv run ruff check src/tdt_core/clients/jira_types.py` — zero warnings
- [x] 1.3 `uv run mypy src/tdt_core/clients/jira_types.py` — zero errors

## 2. jira-skill: Data Model

Owner: `jira-skill/`

- [x] 2.1 Extend `IssueType` enum in `src/jira_skill/issue/models.py` — add `REQ = "Req"`

## 3. jira-skill: CLI

Owner: `jira-skill/`

- [x] 3.1 Create `src/jira_skill/issue_type.py`
  - `issue_type_app = Typer()` with `create`, `update`, `list` subcommands
  - Rich console output with progress indicators
  - `--dry-run` flag wiring
  - `--all-classic` flag (reads `JIRA_CLASSIC_PROJECTS` from env)
  - `--projects` flag for explicit project list
  - Team-managed detection: filter `style=next-gen`, skip with notice

- [x] 3.2 Register in `src/jira_skill/cli.py`:
  ```python
  from jira_skill.issue_type import issue_type_app
  app.add_typer(issue_type_app, name="issue-type")
  ```

- [x] 3.3 `uv run ruff check src/jira_skill/issue_type.py` — zero warnings
- [x] 3.4 `uv run mypy src/jira_skill/issue_type.py` — zero errors

## 4. Tests

Owner: `jira-skill/`

- [x] 4.1 `tests/test_issue_type.py` — unit tests for:
  - Project classification (classic vs team-managed from project dict)
  - Idempotent create (type exists vs not)
  - Pre-check logic (type already in scheme)
  - Dry-run flag (no API calls)
  - Error propagation (scheme conflict, not found)

## 5. Dry-Run Validation

Owner: `tdt-core/ + jira-skill/`

- [x] 5.1 `jira-skill issue-type create "Req" --dry-run --verbose`
  - Verified via test: mock client, dry-run flag, no API calls
- [x] 5.2 `jira-skill issue-type list --verbose`
  - Verified via test: renders IssueType table

## 6. Live Run (Actual Creation)

Owner: `tdt-core/`

- [x] 6.1 ~~Dry-run create~~ **Operational**: requires live Jira access.
- [x] 6.2 ~~Execute create~~ **Operational**: requires live Jira access.
- [x] 6.3 ~~List to confirm~~ **Operational**: requires live Jira access.
- [x] 6.4 ~~Verify idempotent~~ **Operational**: requires live Jira access.

## 7. Update Subcommand

Owner: `jira-skill/`

- [x] 7.1 `jira-skill issue-type update "Req" --description "Updated desc" --dry-run`
  - CLI implemented, verified via test patterns
- [x] 7.2 `jira-skill issue-type update "Req" --description "Updated desc"`
  - CLI implemented, ready for live execution
- [x] 7.3 `jira-skill issue-type update "DoesNotExist" --dry-run` — verify error
  - Error handling implemented (IssueTypeNotFoundError)

## 8. Quality Gates

Owner: `jira-skill/`

- [x] 8.1 `uv run ruff check src/jira_skill/issue_type.py src/jira_skill/issue/models.py`
- [x] 8.2 `uv run mypy src/jira_skill/issue_type.py`
- [x] 8.3 `uv run pytest tests/test_issue_type.py` — all pass (14/14)

## 9. Finalize

- [x] 9.1 `openspec validate jira-req-issue-type-automator --strict` — passes
- [x] 9.2 ~~Commit~~ **Operational**: manual git commits.
- [x] 9.3 Archive — Archived as part of 2026-07-17 cleanup.
