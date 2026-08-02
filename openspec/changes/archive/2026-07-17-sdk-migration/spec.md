# SDK Migration - Specification

**Status:** Proposed
**Date:** 2026-05-18
**Scope:** Migrate from acli CLI to atlassian-python-api SDK for all Jira operations

---

## Motivation

The current implementation relies entirely on `acli` CLI commands parsed via shell scripts.
This has several limitations:

1. **Parsing fragility**: Output parsing with grep/awk/sed is error-prone
2. **Rate limiting**: No proper retry/backoff built in
3. **Permission issues**: acli filter update doesn't properly return share permissions
4. **Type safety**: Shell scripts cannot validate Jira API responses
5. **Testability**: Shell scripts are hard to unit test
6. **Performance**: Each acli command spawns a new process

The `atlassian-python-api` SDK addresses all these issues.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    jira_sdk.py (wrapper)                      │
│                                                              │
│  - Authenticated Jira client (singleton)                     │
│  - Retry/backoff logic                                       │
│  - Rate limiting                                              │
│  - Unified error handling                                    │
│  - Type-annotated wrappers                                   │
│                                                              │
│  Methods:                                                    │
│  - update_filter(id, jql, name, share_permissions)           │
│  - get_filter(id) → Filter dict                              │
│  - search(jql) → issue list                                  │
│  - search_count(jql) → int                                   │
│  - get_board(id) → Board dict                                │
│  - add_filter_share_permission(filter_id, type, ...)          │
│  - get_filter_share_permissions(filter_id) → list             │
└──────────────────────────────────────────────────────────────┘
```

## Migration Path

### Phase 1: Core SDK Wrapper
- Create `.agents/skills/shared/jira_sdk.py`
- Implement singleton Jira client
- Implement core methods: filter ops, search, board ops
- Implement retry/backoff/rate-limiting

### Phase 2: kanban-board-from-spreadsheet
- `generate_jql.py` → add SDK verification after generation
- `run_workflow.sh` → optional SDK mode for filter update
- All scripts gain ability to use SDK

### Phase 3: jira-daily-reports
- `common_functions.sh` → add SDK fallback option
- All report scripts can use SDK instead of acli

### Phase 4: jira-integration
- `tasks.md` → document SDK usage pattern
- `SKILL.md` → update documentation

## Non-Goals
- Remove acli entirely (backward compatibility maintained)
- Migrate sprints/board operations that acli handles well
- Full test suite (manual verification sufficient for MVP)

## Key Decisions

1. **SDK + acli coexistence**: acli remains primary for interactive use; SDK for automation
2. **Environment variables**: Both share `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
3. **Permission type**: SDK uses `authenticated` type (same as acli input) but API returns `loggedin`
4. **Retry strategy**: Exponential backoff (1s, 2s, 4s, 8s) for rate limiting (413, 429, 503)
