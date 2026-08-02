# Agent Docs Sync Memory Wiring Specification

## Purpose

Define the memory wiring contract for docs-sync: how sync state is initialized, read, and updated across agent-core Memory layers, including scratch-to-long-term promotion and eviction.

## Requirements

### Requirement: SyncState wired into pipeline entry points
`run_full_pipeline()` and `run_full_audit()` SHALL construct `SyncState` and inject it into the state dict.

#### Scenario: SyncState available in handlers
- **WHEN** `run_full_pipeline(repo_root, repo_name)` is called
- **THEN** `state["sync_state"]` SHALL be a `SyncState` instance
- **AND** `discover_handler` SHALL be able to call `sync_state.is_stale(repo_name, commit_hash)`

#### Scenario: SyncState saves after discovery
- **WHEN** `discover_handler` completes discovery
- **THEN** `sync_state.save_state(repo_name, {"auto_mapping": ..., "last_commit": ..., "last_sync_at": ...})` SHALL be called
- **AND** subsequent runs SHALL load cached auto_mapping from scratch layer

### Requirement: Incremental discovery via staleness check
`discover_handler` SHALL check staleness before scanning.

#### Scenario: Fresh state skips scan
- **WHEN** `sync_state.is_stale(repo_name, current_commit)` returns `False`
- **THEN** the handler SHALL load `auto_mapping` from scratch layer
- **AND** `ScannerTool` and `ClassifierTool` SHALL NOT be called
- **AND** the cached `auto_mapping` SHALL be used directly

#### Scenario: Stale state triggers full scan
- **WHEN** `sync_state.is_stale(repo_name, current_commit)` returns `True`
- **THEN** the handler SHALL run the full scan and classification as before
- **AND** results SHALL be saved via `sync_state.save_state()`

### Requirement: MetricsStore wired into pipeline
`MetricsStore` SHALL track cross-repo metrics when Postgres is available.

#### Scenario: Metrics recorded after run
- **WHEN** a pipeline run completes
- **THEN** `metrics_store.record_run(repo_name, cost_usd, docs_generated, quality_score)` SHALL be called
- **AND** the data SHALL be available via `metrics_store.get_cost_per_repo()` and `metrics_store.get_quality_scores()`

#### Scenario: Graceful degradation without Postgres
- **WHEN** Postgres long_term is not configured
- **THEN** `MetricsStore` methods SHALL be no-ops
- **AND** the pipeline SHALL complete normally without metrics

### Requirement: YAML-to-Memory migration
Existing `.docs-sync-state.yaml` files SHALL be migrated on first run.

#### Scenario: Migration on first run
- **WHEN** a repo has `.docs-sync-state.yaml` and no ScratchMemory entries for that repo
- **THEN** `migrate_yaml_to_memory()` SHALL be called
- **AND** the YAML file SHALL be renamed to `.docs-sync-state.yaml.bak`
- **AND** the `auto_mapping` and `last_commit` SHALL be stored in ScratchMemory

#### Scenario: Migration skipped if already done
- **WHEN** ScratchMemory already has entries for the repo
- **THEN** migration SHALL be skipped
- **AND** the pipeline SHALL proceed normally
