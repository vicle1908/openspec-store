# Proposal: SDK Migration & Legacy Code Cleanup

**Change ID:** sdk-migration  
**Status:** Proposed  
**Date:** 2026-05-18  
**Last Updated:** 2026-06-13

## Problem

### Shell-based Jira Automation (Original)
All Jira automation scripts rely on `acli` CLI commands with shell-based output parsing (grep/awk/sed). This causes:
- Parsing fragility from unstructured output
- No retry/backoff for rate limits
- Broken filter share permission handling
- Inability to validate API responses programmatically
- Hard-to-test shell scripts
- Process overhead per `acli` invocation

### Legacy Python Patterns (New)
The jira-skill Python package contains legacy patterns that bypass tdt-core standards:
- `create_with_options()` method bypasses canonical factory pattern
- Bare `except Exception:` swallows errors silently (14 instances across 9 files)
- Inconsistent type annotations (`Any` vs `PatchedJira`)
- Repeated `load_tdt_env()` calls in CLI (8 instances)
- Raw Google API client instead of `tdt_sheets`

These patterns cause:
- Inconsistent error handling across the codebase
- Hard-to-debug silent failures
- Type checker blind spots
- Duplicate environment loading overhead

## Solution

### Phase 1: SDK Wrapper (Completed)
Use `atlassian-python-api` SDK behind a shared `jira_sdk.py` wrapper (`.agents/skills/shared/jira_sdk.py`, 394 lines):
- Singleton authenticated Jira client
- Exponential retry/backoff (4 retries)
- Rate limiting (5 req/s)
- Type-annotated methods: `search()`, `search_count()`, `get_filter()`, `update_filter()`, `get_board()`, `add_filter_share_permission()`, `get_filter_share_permissions()`

### Phase 2: jira-skill Legacy Cleanup
Clean up jira-skill to enforce tdt-core patterns:

1. **Remove factory bypass** - Remove `create_with_options()` deprecated method
2. **Specific exception handling** - Replace 14 bare `except Exception:` with specific types
3. **Type annotations** - Use `PatchedJira` instead of `Any`/`Jira`
4. **Consolidate env loading** - Single `load_tdt_env()` call via Typer callback
5. **Google Sheets migration** - Replace raw `googleapiclient` with `tdt_sheets`

## Scope

- **In:** 
  - `jira-skill/src/` - legacy pattern cleanup
  - `code-daily-scan/src/` - Google Sheets migration
  - `agent-core/src/` - type ignore cleanup (low priority)
- **Out:** 
  - Shell scripts (`scripts/`, `skills/`) - handled by original scope
  - `tdt-core/` - foundational, do not modify
- **Dependencies:** `atlassian-python-api`, `tdt_sheets`

## Risk

- **MEDIUM:** Exception handling changes may surface hidden errors
- **LOW:** Factory removal is additive (method was deprecated)
- **LOW:** Google Sheets migration uses same auth patterns

## Capabilities

1. **jira-client-pattern** - Canonical Jira client factory usage
2. **exception-handling-standards** - Specific exception types instead of bare catches
3. **environment-initialization** - Centralized env loading
4. **google-sheets-migration** - tdt_sheets usage for all Google API calls
