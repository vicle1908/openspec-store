# align-gitnexus-freshness-and-hooks

## Why

GitNexus CLI is at **1.6.9** (latest stable, confirmed current). The package is current but there are three operational issues:

1. **Index staleness across 14/18 repos** — GitNexus anchors freshness to the exact commit hash in `.gitnexus/gitnexus.json:lastCommit`. Verified Aug 10, 14:57 UTC+7:
   - FRESH (4) = agent-core, agent-docs-sync, agent-harness, go-microservices
   - STALE (14) = ai-harness-skills, ai-review, browser-cli, code-daily-scan, jira-daily-reports, jira-epic-report, jira-kanban-from-spreadsheet, jira-skill, mcp-router, ops-automation-suite, tdt-core, tdt-observability, tdt-sheets, webhook-receiver

2. **Two independent freshness metrics exist** — Graphify's cron check uses code-content diff (file-level). GitNexus uses exact commit hash comparison (`lastCommit == git rev-parse HEAD`). The cron prompt currently conflates these two metrics. They MUST be reported as independent fields.

3. **Pre-commit hook performance** — The go-microservices pre-commit hook calls `gitnexus detect-changes --scope staged --repo "$root"` and has been observed to throw `Illegal instruction: 4` on arm64 (ONNX native addon issue). The existing hook is advisory-only and MUST remain advisory-only. A bounded timeout mitigates hangs but does NOT fix the underlying ONNX arch context issue.

## Ownership

This change owns GitNexus indexes and pre-commit advisory hooks. It does NOT own `graphify-out/` (Graphify's responsibility) or agentmemory data. References `docs/cli-agent-tooling-contract.md` for shared conventions.

## Dependency

This change MUST wait until `refresh-graphify-upstream` pilot rebuild completes its canary phase (§4), because graphify batch rebuild advances HEAD and would immediately stale GitNexus indexes.

## What Changes

- Reindex all 14 stale repositories with `gitnexus analyze --index-only --skip-agents-md --skip-skills`
- Wrap pre-commit hook with bounded timeout; never block commits
- Update the weekly-graphify-freshness cron prompt to report two independent freshness fields
- Add workspace-wide lock for reindex operations; skip cron runs if lock is held
- Verify all 18 repos show "up to date" after reindex

## Impact

- 14 repositories: graph indexes rebuilt (non-destructive, only `.gitnexus/` changes, gitignored)
- Pre-commit hooks: bounded and non-blocking
- Cron: freshness detection reports both metrics independently
- Risk: Low — reindex is non-destructive; no source code changes

## Evidence

Before:
- `gitnexus status` → 14/18 repos show "⚠️ stale"
- Weekly cron code-only check → 18/18 "fresh" (different metric than GitNexus)

After:
- `gitnexus status` → 18/18 repos show "up to date"
- `gitnexus detect-changes --repo <path>` → works without unbounded hang
- Weekly cron → reports `graphify_artifact_fresh` and `gitnexus_index_fresh` as independent fields
