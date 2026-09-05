# Knowledge Index Retention Plan

## Context & Purpose
This document establishes the review-only retention analysis and policy recommendations for knowledge index artifacts (`.gitnexus/` and `graphify-out/`) across all 20 repositories in `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`.

Under OpenSpec change `consolidate-knowledge-index-retention`, this plan operates under an **explicit NO-DELETION scope**. No index files, database records, graph models, or temporary artifacts are deleted as part of this change.

## Scope of Audited Repositories
The audit covers all 20 approved repositories:
1. `agent-core`
2. `agent-docs-sync`
3. `agent-harness`
4. `ai-harness-skills`
5. `ai-review`
6. `browser-cli`
7. `code-daily-scan`
8. `jira-daily-reports`
9. `jira-epic-report`
10. `jira-kanban-from-spreadsheet`
11. `jira-skill`
12. `mcp-router`
13. `openspec-store` (GitNexus enabled; Graphify disabled)
14. `ops-automation-suite`
15. `tdt-core`
16. `tdt-observability`
17. `tdt-sheets`
18. `webhook-receiver`
19. `go-microservices`
20. `tdt-scheduler`

## Artifact Classification & Retention Rules

### 1. Primary Generated Indexes
- **GitNexus**: `.gitnexus/meta.json`, SQLite databases (`kuzu`, index stores, vector/embedding indices).
- **Graphify**: `graphify-out/graph.json`, `graph.html`.
- **Classification**: Active Knowledge Base.
- **Retention Rule**: Retain indefinitely until refreshed. Freshness is strictly governed by **commit equality** (`recorded_revision == HEAD`). Stale indexes **MUST NOT** be deleted; they provide continuous local navigation and code intelligence until superseded by scheduled or triggered refresh runs.
- **Recovery Path**: `gitnexus analyze` or `graphify update .`.

### 2. Derived & Operational Files
- **Files**: `.gitnexus/schema.json`, `graphify-out/communities.json`, `graphify-out/report.html`.
- **Classification**: Derived Analysis Artifacts.
- **Retention Rule**: Preserved alongside primary graph/index data.
- **Recovery Path**: Regenerated during full index rebuild.

### 3. Transient Operational & Lock Files
- **Files**: `.gitnexus/*-wal`, `.gitnexus/*-shm`, `.gitnexus/locks/`, `~/.knowledge-refresh/locks/`.
- **Classification**: Transient Operational State.
- **Retention Rule**: Managed natively by database engines (SQLite/WAL) and process locks. Do not delete externally while processes are running.

### 4. Historical & Duplicate Candidates (Review-Only)
- **Identified Candidates**:
  - `tdt-scheduler/graphify-out/.graphify_old.json` (~825 KB): Legacy backup artifact from prior manual execution.
  - OS-generated files like `.DS_Store` within `.gitnexus/` directories (e.g. `jira-epic-report/.gitnexus/.DS_Store`).
- **Review-Only Recommendation**:
  - Future automated cleanup jobs may target orphaned historical backups like `.graphify_old.json` only after verifying that active `graph.json` is healthy and validated.
  - No deletions are performed in this change.

## Verification of No-Deletion Constraint
- All 40 inventory directories (`.gitnexus/` and `graphify-out/` across 20 repositories) remain intact.
- Git status across all workspace repositories confirms zero file deletions in knowledge index paths.
