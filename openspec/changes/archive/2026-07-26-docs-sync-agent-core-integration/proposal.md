## Why

`agent-docs-sync` depends on `agent-core` but only uses ~30% of its capabilities. The docs-sync pipeline has no observability (no OTel tracing, no Langfuse, no cost tracking), no resilience (no circuit breakers around LLM calls), uses a legacy SchedulerEngine instead of the newer WorkflowBuilder, tracks sync state in a flat YAML file instead of agent-core's Memory layer, and runs multi-repo syncs sequentially. Meanwhile, `agent-core` v0.2.0 ships WorkflowBuilder (LangGraph + PostgresSaver checkpointing), OTel/Langfuse/MLflow observability, Memory (context/scratch/long_term), resilience (circuit breaker, retry, degradation), and a scoring framework — none of which docs-sync uses.

This integration closes the gap: migrates orchestration to WorkflowBuilder for durability and resume, adds observability for cost and quality tracking, wires Memory for structured sync state, wraps LLM calls with resilience, and enables parallel multi-repo execution.

## What Changes

- **Orchestration migration**: Replace `SchedulerEngine` (used in `full_pipeline.py`, `durable.py`) with `WorkflowBuilder`/`WorkflowEngine` from `agent_core.orchestration`. The codebase already has partial migrations (`full_dag.py`, `discovery_pipeline.py`, `sync_pipeline.py` import WorkflowBuilder but delegate back to SchedulerEngine steps). This change completes the migration.

- **Observability integration**: Wire `agent_core.foundation.tracing` (OTel), `agent_core.observability.LangfuseClient`, and `agent_core.observability.scorers` into pipeline steps. Add a `DocGenerationCostScorer` and `DocQualityScorer` to the scoring framework. Pipeline nodes emit OTel spans; LLM calls get traced with cost attribution.

- **Memory integration**: Replace `.docs-sync-state.yaml` with `agent_core.memory.Memory` facade. Use `scratch` layer for per-repo sync state (last commit, file hashes, gap history), `long_term` layer for cross-repo metrics (cost per repo, generation stats), and `context` layer for per-run working state.

- **Resilience**: Wrap LLM calls in `agent_core.resilience` circuit breaker + `retry_with_jitter`. Add `FallbackChain` for provider failover (OmniRoute → direct). Wire `DegradationManager` for system health monitoring during heavy sync runs.

- **Multi-repo parallel**: Replace sequential `sync_all_repos()` loop with parallel execution via `asyncio.gather` with semaphore (max 3 concurrent repos). Each repo runs as an independent WorkflowBuilder subgraph with its own Memory session.

- **Hook enrichment**: Add `langfuse_hooks` and `mlflow_hooks` hook packs (already available in `agent_core.agent_base.hooks.builtins`) to the doc-sync agent. Add `cost_tracker` hook for per-run cost attribution.

## Capabilities

### New Capabilities

- `docs-sync-observability`: OTel tracing, Langfuse integration, cost/quality scoring for doc generation pipeline steps
- `docs-sync-resilience`: Circuit breaker, retry, fallback chain, degradation management around LLM calls
- `docs-sync-memory`: Structured sync state via agent-core Memory facade (scratch/long_term/context layers)
- `docs-sync-parallel-multi-repo`: Parallel multi-repo orchestration with subgraph isolation

### Modified Capabilities

(none — no existing specs in `openspec/specs/` are affected)

## Impact

- **Code**: `agent-docs-sync/src/agent_docs_sync/` — 6 files modified, 4 files created, 2 files deleted
  - Modified: `cli.py`, `agent.py`, `hooks.py`, `llm/gateway.py`, `multi_repo.py`, `workflows/full_pipeline.py`
  - Created: `observability/__init__.py`, `observability/scorers.py`, `memory/__init__.py`, `memory/sync_state.py`
  - Deleted: `durable.py` (replaced by WorkflowBuilder), `.docs-sync-state.yaml` format (replaced by Memory)
- **Dependencies**: None new — all observability, memory, and resilience deps already in `agent-core`'s `pyproject.toml` (opentelemetry-sdk, langfuse, mlflow, psycopg, psutil)
- **agent-core**: No changes needed — all integration points already exist
- **Docker**: Scheduler container already has `CRASH_RECOVERY_ENABLED=true` and Postgres — Memory's `long_term` layer uses the same Postgres
- **Breaking**: `.docs-sync-state.yaml` format changes — one-time migration script needed for existing state files
