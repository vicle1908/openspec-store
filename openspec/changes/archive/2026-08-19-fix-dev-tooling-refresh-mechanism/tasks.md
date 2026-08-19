## 1. Fix refresh script

- [x] 1.1 Update `is_dirty()` to exclude `graphify-out/` and `uv.lock` from dirty check
- [x] 1.2 Add `GITNEXUS_WAL_CHECKPOINT_THRESHOLD=67108864` to analyze command

## 2. Update inventory

- [x] 2.1 Add `tdt-scheduler` to `knowledge-refresh-inventory.tsv`
- [x] 2.2 Fix branch name (main → master) for tdt-scheduler
- [x] 2.3 Re-approve inventory SHA-256

## 3. Re-index repos

- [x] 3.1 Re-index tdt-core with `GITNEXUS_EMBEDDING_DIMS=768`
- [x] 3.2 Re-index agent-core, code-daily-scan, jira-epic-report, jira-daily-reports, webhook-receiver, tdt-observability
- [x] 3.3 Index tdt-scheduler (new repo)

## 4. Verify

- [x] 4.1 All 8 scheduling repos have fresh GitNexus indexes
- [x] 4.2 All 8 repos have graphify-out
- [x] 4.3 All 8 repos have post-commit hooks
- [x] 4.4 MCP router can query all repos
