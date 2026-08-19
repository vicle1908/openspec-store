## Why

GitNexus and Graphify indexes were stale because:
1. The graphify hook rebuilds `graphify-out/` after each commit but never commits the changes
2. The refresh script (`refresh-knowledge-indexes.sh`) skipped repos when the working tree was dirty — including repos with only graphify-out modifications
3. `tdt-scheduler` was missing from the refresh inventory
4. GitNexus analyze failed with embedding dimension mismatch (768d vs expected 384d)
5. GitNexus analyze failed with WAL checkpoint threshold errors on large repos

## What Changes

- **Fix `refresh-knowledge-indexes.sh`**: Update `is_dirty()` to exclude `graphify-out/` and `uv.lock` from the dirty check
- **Fix `refresh-knowledge-indexes.sh`**: Add `GITNEXUS_WAL_CHECKPOINT_THRESHOLD=67108864` to the analyze command
- **Update `knowledge-refresh-inventory.tsv`**: Add `tdt-scheduler` entry
- **Re-index all scheduling repos**: Run `gitnexus analyze` with correct embedding dims

## Capabilities

### Modified Capabilities

- `scheduler-docker-deployment`: Dev tooling now keeps indexes up to date

## Impact

- **Files touched**: `refresh-knowledge-indexes.sh`, `knowledge-refresh-inventory.tsv`
- **Repos re-indexed**: tdt-core, agent-core, code-daily-scan, jira-epic-report, jira-daily-reports, webhook-receiver, tdt-observability, tdt-scheduler
- **Risk**: LOW — tooling fix, no code changes
