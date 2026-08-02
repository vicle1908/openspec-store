## Why

agent-docs-sync has a fully implemented but completely unwired memory module (`memory/sync_state.py`, `memory/metrics.py`, `memory/migrate.py`). The pipeline recomputes everything from scratch on every run — scanning 65+ files, re-classifying each one, running link checking and Diataxis enforcement twice per pipeline. The `SyncState` class is designed exactly to cache discovery results, and `MetricsStore` is designed to track cross-repo metrics, but neither is ever called from production code.

Wiring the existing dead code eliminates redundant computation (biggest perf win), enables cross-repo metrics tracking, and provides a migration path from the primitive YAML state file to the Memory facade.

## What Changes

### Wire SyncState into Pipeline
- `run_full_pipeline()` and `run_full_audit()` will construct `SyncState` and inject it into the state dict
- `discover_handler` will check `sync_state.is_stale()` before scanning — if fresh, load cached `auto_mapping` and skip full scan
- After discovery, `sync_state.save_state()` will persist the new `auto_mapping` (already implemented, just never called)

### Wire MetricsStore into Pipeline
- `MetricsStore` will be constructed at pipeline start and injected into state
- After each pipeline run, `metrics_store.record_run()` will be called with cost, docs generated, and quality score
- This enables historical trend analysis across repos

### YAML-to-Memory Migration
- `migrate_yaml_to_memory()` will be called on first run for each repo
- Existing `.docs-sync-state.yaml` files will be migrated to Memory scratch layer
- YAML files renamed to `.bak` after migration

### Deduplicate Link/Diataxis Validation
- Link checking and Diataxis enforcement currently run twice (audit + validate handlers)
- Results will be cached in Memory context layer per file + content hash
- Unchanged files skip re-validation

## Capabilities

### New Capabilities
- `docs-sync-memory-wiring`: Wire existing SyncState and MetricsStore into pipeline handlers
- `docs-sync-validation-dedup`: Cache link/Diataxis results to eliminate duplicate validation

### Modified Capabilities
- `docs-sync-full-pipeline`: Add memory/sync_state/metrics to state dict, check staleness before scan

## Impact

### Cross-Repo Compatibility
- **agent-core**: No changes — agent-docs-sync uses `agent_core.sdk.Memory` (stable SDK facade)
- **Other repos**: No impact

### Code Changes
- **Modified**: `workflows/full_pipeline.py` (~50 lines changed)
- **Modified**: `memory/sync_state.py` (~10 lines — add `is_stale` enhancement)
- **Modified**: `memory/metrics.py` (~5 lines — add `record_run` enhancement)
- **New**: `workflows/validation_cache.py` (~40 lines — link/Diataxis result caching)

### Non-Goals
- Modifying agent-core's Memory module
- Changing the pipeline's sequential architecture
- Replacing the YAML StateTool used by agent tool-calling
- Adding new memory backends or types
