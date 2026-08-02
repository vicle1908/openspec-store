## 1. Wire SyncState into Pipeline

- [x] 1.1 Read `workflows/full_pipeline.py` — identify `run_full_pipeline()` and `run_full_audit()` entry points
- [x] 1.2 In `run_full_pipeline()`, construct `SyncState(memory)` and inject `state["sync_state"] = sync_state`
- [x] 1.3 In `run_full_audit()`, construct `SyncState(memory)` and inject into state dict
- [x] 1.4 In `discover_handler`, add staleness check: if `sync_state.is_stale()` returns False, load cached `auto_mapping` and skip scan
- [x] 1.5 Verify `sync_state.save_state()` is called after discovery (already implemented, just ensure it's reached)

## 2. Wire MetricsStore into Pipeline

- [x] 2.1 In `run_full_pipeline()`, construct `MetricsStore(memory)` and inject into state dict
- [x] 2.2 In `run_full_audit()`, construct `MetricsStore(memory)` and inject into state dict
- [x] 2.3 After pipeline completion, call `metrics_store.record_run()` with cost, docs generated, quality score
- [x] 2.4 Verify graceful degradation when Postgres is unavailable (MetricsStore._has_long_term guard)

## 3. YAML-to-Memory Migration

- [x] 3.1 In `run_full_pipeline()`, call `migrate_yaml_to_memory(memory, repo_root)` before discovery
- [x] 3.2 Verify migration is idempotent (skips if already migrated)
- [x] 3.3 Verify `.docs-sync-state.yaml` is renamed to `.bak` after migration

## 4. Validation Result Caching

- [x] 4.1 Create `workflows/validation_cache.py` with content-hash based cache using Memory context layer
- [x] 4.2 In `audit_handler`, wrap `CheckLinksTool` calls with cache lookup/store
- [x] 4.3 In `audit_handler`, wrap `EnforcerTool` calls with cache lookup/store
- [x] 4.4 In `validate_handler`, reuse cached results from audit (avoid duplicate validation)
- [x] 4.5 Verify cache invalidation works (content hash mismatch triggers re-validation)

## 5. Final Verification

- [x] 5.1 Run `uv run ruff check src/` — zero new errors
- [x] 5.2 Run `uv run pytest tests/ -x` — all tests pass
- [x] 5.3 Verify pipeline still works without Postgres (graceful degradation)
- [x] 5.4 Verify pipeline still works with existing `.docs-sync-state.yaml` files
