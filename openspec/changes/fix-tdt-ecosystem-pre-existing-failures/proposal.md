# Proposal: Fix TDT Ecosystem Pre-existing Failures

## Why

Verification of the config/env loading simplification surfaced three pre-existing
issues that block clean test collection and verification across the ecosystem:

1. **webhook-receiver**: `app = create_app()` at module level triggers import-time
   DBOS init + missing `jira_guard` module → collection error for 3 test files
2. **jira-daily-reports**: 5 formatting tests assert old output format without
   daily total prefix that the implementation now emits
3. **jira-skill**: 3 test files reference hardcoded paths from another user's
   workspace (`/Users/lekhanhvinh/...`) or depend on an external file that may
   not exist

## What Changes

| Repo | Fix | Risk |
|------|-----|------|
| webhook-receiver | Remove module-level `app = create_app()` | Low — app was never used at module level |
| jira-daily-reports | Update 5 test assertions to match current format | Low — test-only |
| jira-skill | Fix hardcoded paths, add skipWhenMissing for taxonomy tests | Low — test-only |
