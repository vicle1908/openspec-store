## Purpose

This specification defines requirements for Docs Sync Parallel Multi Repo.

## Requirements

### Requirement: Parallel multi-repo execution
The `sync-all` command SHALL support a `--parallel` flag that runs doc sync across multiple repos concurrently. Concurrency SHALL be limited by a semaphore (default: 3 concurrent repos). Each repo SHALL run as an independent WorkflowBuilder subgraph with its own `thread_id` (repo name) for checkpoint isolation.

#### Scenario: Parallel sync with 3 repos
- **WHEN** `docs-sync sync-all --parallel` is run with 3 repos configured
- **THEN** all 3 repos are processed concurrently (not sequentially)

#### Scenario: Concurrency limit enforced
- **WHEN** `docs-sync sync-all --parallel` is run with 6 repos
- **THEN** at most 3 repos are processed concurrently; the remaining 3 wait

### Requirement: Per-repo checkpoint isolation
Each repo SHALL use `thread_id={repo_name}` when running the pipeline. This ensures that each repo has a unique identifier for checkpoint isolation when PostgresSaver is enabled.

#### Scenario: Thread ID passed to pipeline
- **WHEN** `docs-sync sync-all --parallel` runs multiple repos
- **THEN** each repo's `run_full_audit()` call receives `thread_id=repo_name`

#### Scenario: Checkpoint isolation with durable mode
- **WHEN** `docs-sync sync --full --durable` is used with PostgresSaver
- **THEN** each repo's state is checkpointed under its own thread_id

### Requirement: Aggregated multi-repo report
After all repos complete (or fail), the aggregate node SHALL merge per-repo reports into a unified summary. The summary SHALL include: repos_scanned, repos_failed, total source_files_scanned, total docs_found, total gaps_identified, total docs_generated, per-repo breakdown.

#### Scenario: Mixed success and failure
- **WHEN** 4 repos sync: 3 succeed, 1 fails with error
- **THEN** the aggregate report shows repos_scanned=3, repos_failed=1, with the failed repo's error in per-repo breakdown

### Requirement: Sequential fallback
The `sync-all` command without `--parallel` SHALL run repos sequentially (existing behavior). The `--parallel` flag is opt-in.

#### Scenario: Default sequential behavior preserved
- **WHEN** `docs-sync sync-all` is run without `--parallel`
- **THEN** repos are processed sequentially, one at a time

### Requirement: Per-repo Memory isolation
Each repo subgraph SHALL use its own Memory session key (`docs-sync:{repo_name}`) for scratch state. The aggregate node SHALL use the metrics session (`docs-sync:metrics`) for long-term cross-repo data.

#### Scenario: Parallel repos do not share scratch state
- **WHEN** repos "agent-core" and "ai-review" run in parallel
- **THEN** each reads/writes only its own Memory session; no cross-contamination
