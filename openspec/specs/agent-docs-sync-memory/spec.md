# Agent Docs Sync Memory Specification

## Purpose

Define the memory layer for docs-sync: structured sync state persistence, change tracking, and cross-run context via agent-core Memory (scratch + long-term layers).

## Requirements

### Requirement: Scratch layer for per-repo sync state
The doc-sync system SHALL use `agent_core.memory.Memory` with the `scratch` layer to store per-repo sync state. Each repo SHALL have a session key `docs-sync:{repo_name}`. Stored keys: `last_commit` (git hash), `file_hashes` (dict of file→hash), `gap_history` (list of past gaps), `last_sync_at` (ISO timestamp).

#### Scenario: Save sync state after successful run
- **WHEN** a doc sync run completes for repo "agent-core"
- **THEN** Memory scratch stores `last_commit`, `file_hashes`, `gap_history`, and `last_sync_at` under session `docs-sync:agent-core`

#### Scenario: Load sync state for staleness check
- **WHEN** a new sync run starts for repo "agent-core"
- **THEN** the system reads `last_commit` from Memory scratch to compare against current HEAD

### Requirement: Long-term layer for cross-repo metrics
The doc-sync system SHALL use `agent_core.memory.Memory` with the `long_term` layer to store cross-repo metrics. Session key: `docs-sync:metrics`. Stored keys: `total_runs` (int), `cost_per_repo` (dict), `generation_stats` (dict with docs_generated, docs_updated, avg_cost_per_doc), `quality_scores` (list of recent scores).

#### Scenario: Record run metrics after completion
- **WHEN** a doc sync run completes for any repo
- **THEN** `total_runs` is incremented and `cost_per_repo[repo_name]` is updated in long-term memory

#### Scenario: Query historical cost per repo
- **WHEN** the aggregate node runs in multi-repo mode
- **THEN** `cost_per_repo` from long-term memory is included in the report

### Requirement: Context layer for per-run working state
The doc-sync system SHALL use `agent_core.memory.Memory` with the `context` layer for ephemeral per-run state. Pipeline handlers store intermediate results in Memory context alongside dict-based state passing. Session key: `docs-sync:run:{thread_id}`.

#### Scenario: Pipeline steps store results in context layer
- **WHEN** the discover node completes
- **THEN** `discover_result` is stored in Memory context under session `docs-sync:run:{thread_id}`

#### Scenario: Pipeline steps can read from context layer
- **WHEN** the audit node needs discover results
- **THEN** results are available both in dict state and Memory context

### Requirement: Migration from YAML state files
On first use after upgrade, the system SHALL read existing `.docs-sync-state.yaml` files and write their `auto_mapping` and `invalidation` data to Memory scratch layer. The original YAML file SHALL be renamed to `.docs-sync-state.yaml.bak` after successful migration.

#### Scenario: First run migrates YAML to Memory
- **WHEN** the system starts and finds `.docs-sync-state.yaml` but no Memory scratch data for that repo
- **THEN** the YAML data is written to Memory scratch and the YAML is renamed to `.bak`

#### Scenario: Subsequent runs skip migration
- **WHEN** the system starts and Memory scratch already has data for that repo
- **THEN** no migration occurs and `.docs-sync-state.yaml.bak` is ignored
