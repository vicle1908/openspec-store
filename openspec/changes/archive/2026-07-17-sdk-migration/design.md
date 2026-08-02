# Design: SDK Migration & Legacy Cleanup

**Change ID:** sdk-migration  
**Date:** 2026-05-20  
**Last Updated:** 2026-06-13

## Architecture

```
Scripts Layer (scripts/, skills/)
    │
    ├── acli (existing, unchanged) ──► GitLab CLI output
    │
    └── jira_sdk.py (new) ──► atlassian-python-api ──► Jira REST API
            │
            └── .agents/skills/shared/jira_sdk.py (already implemented)

Python Package Layer (jira-skill, code-daily-scan)
    │
    ├── tdt_core.clients ──► JiraClientFactory ──► PatchedJira
    │
    ├── tdt_sheets ──► SheetsClient ──► Google Sheets API
    │
    └── Domain Exceptions ──► Proper error propagation
```

## Design Decisions

### 1. Wrapper Pattern (Original)
- `JiraClient` is a singleton so all scripts share one authenticated session
- Wrapper hides SDK complexity; scripts call `client.search("filter = 15113")` not raw SDK calls

### 2. Dual Mode (acli + SDK) (Original)
- Scripts gain `--sdk` flag for SDK mode
- Without `--sdk`, existing acli behavior is preserved
- This enables gradual migration with zero downtime

### 3. Retry Strategy (Original)
- Exponential backoff: 1s, 2s, 4s, 8s (4 retries max)
- Only retries on 429 (rate limit) and 5xx errors
- 401/403 are not retried (authentication failures)

### 4. Rate Limiting (Original)
- Hard cap at 5 requests/second
- Token bucket algorithm with smoothing
- Configurable via `JIRA_RATE_LIMIT` env var

### 5. Share Permissions (Original)
- `get_filter_share_permissions(filter_id)` returns structured list
- `add_filter_share_permission(filter_id, type, project_id)` handles the full workflow
- This fixes the acli bug where share permissions couldn't be read/written

### 6. Exception Handling Strategy
- Use domain-specific exceptions from `jira_skill.workflow.exceptions`
- Never use bare `except Exception: pass`
- Always propagate context with `raise ... from e`
- Log with sufficient context for debugging

### 7. Environment Initialization Strategy
- Single `load_tdt_env()` at CLI entry point via Typer callback
- Factory methods handle their own initialization
- Helper functions remain env-agnostic

## Migration Phases

### Phase 1: Core SDK Wrapper ✅ (COMPLETED)
- `.agents/skills/shared/jira_sdk.py` implemented (394 lines)
- All methods implemented with retry, rate limiting, error handling

### Phase 2: jira-skill Legacy Cleanup (IN PROGRESS)
#### 2.1 Remove Factory Bypass
- Remove `create_with_options()` from `jira_skill/config.py`
- Verify no external callers exist
- All code uses `JiraClientFactory.create()` or `from_env()`

#### 2.2 Replace Bare Exception Catches
Files affected (14 instances):
- `workflow/client.py` - 5 instances (lines 315, 355, 462, 555, 668)
- `dashboard/service.py` - 3 instances (lines 367, 373, 474)
- `analysis/analyzer.py` - 1 instance (line 555)
- `analysis/collector.py` - 1 instance (line 262)
- `analysis/gitlab_evidence.py` - 1 instance (line 325)
- `backup/changelog.py` - 1 instance (line 155)
- `resilience/executor.py` - 1 instance (line 109)
- `resilience/circuit_breaker.py` - 1 instance (line 98)
- `security/validator.py` - 1 instance (line 79)

#### 2.3 Consolidate Environment Loading
- Add Typer `@app.callback()` in `cli.py`
- Remove 8 scattered `load_tdt_env()` calls
- Keep only one at application entry point

#### 2.4 Fix Type Annotations
- `PatchedJira` instead of `Any` or raw `Jira`
- Verify `TYPE_CHECKING` blocks for type-only imports

### Phase 3: code-daily-scan Cleanup (PLANNED)
#### 3.1 Migrate to tdt_sheets
- `_validate_sheet_access` → `SheetsClient.get_spreadsheet()`
- `_append_to_sheet` → `SheetsClient.append_row()`

#### 3.2 Centralize Budget Config
- Single env var: `{PLATFORM}_SCAN_MONTHLY_BUDGET_USD`
- Remove duplicate defaults in `health.py`

### Phase 4: agent-core Type Cleanup (FUTURE)
#### 4.1 Fix Actionable Type Ignores
- `engine.py:259` - `assert last_error is not None`
- `agent.py:321-322` - `cast()` instead of inline ignores
- `graph.py:254,295,299` - named functions instead of lambdas

#### 4.2 Document Unavoidable Ignores
- LangGraph generics - document as library limitation
- DBOS decorator attrs - document as intentional

### Phase 5: Verification
#### 5.1 Linter & Type Check
- `ruff check` on all affected packages
- `mypy` on all affected packages
- Zero new warnings introduced

#### 5.2 Functional Tests
- Run CLI commands with new exception handling
- Verify SheetsClient operations work
- Verify JiraClientFactory creates valid clients

#### 5.3 Deploy
- Sync to `deployments/ai-review/deps/jira-skill/`
- Sync to `deployments/webhook-receiver/deps/jira-skill/`

## Files Summary

| File | Changes | Priority |
|------|---------|----------|
| `jira_skill/config.py` | Remove `create_with_options()` | HIGH |
| `jira_skill/workflow/client.py` | Fix 5 bare excepts | HIGH |
| `jira_skill/cli.py` | Consolidate env loading | MEDIUM |
| `jira_skill/dashboard/service.py` | Fix 3 bare excepts | MEDIUM |
| `jira_skill/analysis/*.py` | Fix 3 bare excepts | MEDIUM |
| `jira_skill/resilience/*.py` | Fix 2 bare excepts | MEDIUM |
| `jira_skill/security/validator.py` | Fix 1 bare except | MEDIUM |
| `code_daily_scan/cli.py` | Migrate to tdt_sheets | MEDIUM |
| `code_daily_scan/health.py` | Centralize budget | LOW |
| `agent_core/*.py` | Type ignore cleanup | LOW |
