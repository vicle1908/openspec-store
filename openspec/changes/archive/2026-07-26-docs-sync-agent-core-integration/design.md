## Context

`agent-docs-sync` (v0.1.0) is an automated documentation synchronization agent for the TDT ecosystem. It scans repositories, classifies source files into Diátaxis quadrants, generates/validates docs, and produces reports.

**Current state**: The codebase is partially migrated. `full_dag.py`, `discovery_pipeline.py`, and `sync_pipeline.py` import `WorkflowBuilder` from agent-core, but delegate back to SchedulerEngine steps in `full_pipeline.py`. `durable.py` uses SchedulerEngine directly. The CLI (`cli.py`) calls both paths. No observability, no resilience, no structured memory.

**agent-core v0.2.0** provides: WorkflowBuilder (LangGraph + PostgresSaver), OTel/Langfuse/MLflow observability, Memory facade (context/scratch/long_term), resilience engine (circuit breaker, retry, degradation), and a scoring framework with cost and regression scorers.

**Constraint**: agent-core has no changes — all integration points already exist. The work is entirely in agent-docs-sync.

## Goals / Non-Goals

**Goals:**
- Complete the WorkflowBuilder migration (replace all SchedulerEngine usage)
- Add OTel tracing to pipeline nodes with Langfuse integration
- Wire agent-core Memory for structured sync state
- Wrap LLM calls with circuit breaker + retry
- Enable parallel multi-repo execution (asyncio.gather with semaphore)
- Add cost and quality scoring to the evaluation framework

**Non-Goals:**
- Changes to agent-core itself
- Migrating from LiteLLM gateway to Bifrost (docs-sync already uses LiteLLMGateway correctly)
- Real-time streaming of pipeline progress to UI
- Distributed execution across multiple machines
- Changing the CLI interface (same commands, same flags)

## Decisions

### D1: WorkflowBuilder over SchedulerEngine

**Decision**: Replace `tdt_core.scheduler.SchedulerEngine` with `agent_core.orchestration.WorkflowBuilder`.

**Why**: SchedulerEngine is older, runs in passthrough mode (enabled=False), provides no checkpointing, no resume, no subgraph composition. WorkflowBuilder offers LangGraph-backed durable execution with PostgresSaver, conditional routing, subgraph support, and per-node retry/timeout policies.

**Alternatives considered**:
- *Keep SchedulerEngine*: Simpler migration but no durability, no resume, no subgraph — blocks multi-repo parallel.
- *Use DynamicWorkflow (pydantic-ai-harness)*: Already prototyped in `dynamic_pipeline.py` but requires pydantic-monty sandbox, adds LLM cost for orchestration decisions that are deterministic.

**Pattern**: Each pipeline step becomes a WorkflowBuilder node handler. Handlers are async functions that receive `state: dict[str, Any]` and return `dict[str, Any]`. The existing step logic in `full_pipeline.py` is extracted into handler functions.

```
Builder pattern:
  builder = WorkflowBuilder("doc-sync")
  builder.add_node(NodeDescriptor(name="discover"), handler=discover_handler)
  builder.add_node(NodeDescriptor(name="audit"),    handler=audit_handler)
  builder.add_edge(EdgeDescriptor(source="discover", target="audit"))
  builder.set_entry("discover")
  engine = builder.build(checkpointer=create_checkpointer(dsn))
  result = await engine.run(initial_state, thread_id=repo_name)
```

### D2: Memory layers for sync state

**Decision**: Use agent-core Memory facade with three layers.

**Why**: `.docs-sync-state.yaml` is a flat file — not queryable, no cross-repo aggregation, no history. Memory provides structured, layered storage with per-session isolation.

**Layer mapping**:
- `context` (in-process): Per-run working state — current repo, step progress, intermediate results. Ephemeral, cleared after run.
- `scratch` (filesystem): Per-repo sync state — last commit hash, file hashes, gap history, last_sync_at. Survives restart. Key: `docs-sync:{repo_name}`.
- `long_term` (Postgres): Cross-repo metrics — total_runs, cost_per_repo, generation_stats, quality_scores. Historical. Key: `docs-sync:metrics`.

**Migration**: One-time script reads existing `.docs-sync-state.yaml` files and writes to Memory scratch layer. Old YAML files become read-only fallback.

### D3: Observability via OTel + Langfuse

**Decision**: Wire `agent_core.foundation.tracing` and `agent_core.observability.LangfuseClient` into pipeline nodes.

**Why**: Currently zero observability — can't track cost per repo, generation quality, or pipeline performance. OTel provides standard tracing; Langfuse provides LLM-specific observability (traces, scores, cost).

**Integration points**:
- Each WorkflowBuilder node handler wraps its logic in `tracer.start_as_current_span("node_name")`
- LLM calls are already traced by `agent_core.llm_gateway` (OTel spans with gen_ai attributes)
- Langfuse hooks (`langfuse_hooks` from `agent_core.agent_base.hooks.builtins`) added to doc-sync agent's HookRegistry
- Cost tracker hook (`cost_tracker`) added for per-run cost attribution
- Custom scorers: `DocGenerationCostScorer` (cost per doc generated), `DocQualityScorer` (Diátaxis compliance score)

### D4: Resilience around LLM calls

**Decision**: Wrap the LLM gateway with `agent_core.resilience` circuit breaker + retry.

**Why**: LLM calls are the most fragile part of the pipeline — rate limits, timeouts, provider errors. Currently no retry, no circuit breaking, no fallback.

**Pattern**: Create a `ResilientGateway` wrapper that:
1. Checks circuit breaker state before each call
2. Retries with exponential backoff + jitter on transient errors
3. Falls back to alternative provider if primary circuit is open
4. Records error rate for degradation manager

```
ResilientGateway:
  circuit_breaker: CircuitBreaker (per-provider)
  fallback_chain: FallbackChain [OmniRoute → direct]
  retry: retry_with_jitter(max_attempts=3)
  degradation: DegradationManager (monitors CPU/error rate)
```

### D5: Parallel multi-repo with subgraph isolation

**Decision**: Use `asyncio.gather` with semaphore inside a WorkflowBuilder node, not native LangGraph parallel edges.

**Why**: WorkflowBuilder's edge model is sequential (one edge per source). True parallelism requires either subgraphs or handler-level concurrency. `asyncio.gather` with a semaphore (max 3 concurrent) is simpler and gives us rate-limit control.

**Pattern**:
```
multi-repo graph:
  fan_out node → aggregate node

fan_out handler:
  semaphore = asyncio.Semaphore(3)
  async def run_repo(repo_name):
      async with semaphore:
          subgraph_engine = build_doc_sync_engine()
          return await subgraph_engine.run({"repo_root": paths[repo_name]}, thread_id=repo_name)
  results = await asyncio.gather(*[run_repo(r) for r in repos])
  state["results"]["per_repo"] = results

aggregate handler:
  merge per-repo reports into unified summary
```

Each repo subgraph gets its own `thread_id` (repo name) for checkpoint isolation and its own Memory session key.

## Risks / Trade-offs

- **[Risk] WorkflowBuilder uses `StateGraph(dict)` — untyped state** → Mitigation: Wrap handlers with type annotations; validate state shape at handler entry. Not blocking — existing code already uses dict state.

- **[Risk] PostgresSaver requires running Postgres** → Mitigation: Fallback to no checkpointer when Postgres unavailable (matches current SchedulerEngine disabled mode). Checkpointer is opt-in via `--durable` flag.

- **[Risk] Parallel repos competing for LLM rate limits** → Mitigation: Semaphore limits concurrency to 3; circuit breaker per provider prevents cascading failures; degradation manager reduces capabilities under pressure.

- **[Risk] Memory scratch layer (filesystem) may race with concurrent repos** → Mitigation: Per-repo session keys (`docs-sync:{repo_name}`) — no shared scratch state between repos.

- **[Risk] Existing `.docs-sync-state.yaml` data migration** → Mitigation: One-time migration script; old YAML preserved as fallback; Memory layer is additive.

- **[Trade-off] More complex API (WorkflowBuilder vs simple async functions)** → Accepted: The durability, resume, and subgraph capabilities justify the complexity. Existing `full_dag.py` already demonstrates the pattern.

## Migration Plan

1. **Phase 1 (non-breaking)**: Add observability + resilience wrappers around existing code. No pipeline changes. Ships independently.
2. **Phase 2 (breaking)**: Replace SchedulerEngine with WorkflowBuilder in `full_pipeline.py` and `durable.py`. Update CLI. Delete `durable.py`.
3. **Phase 3 (breaking)**: Replace `.docs-sync-state.yaml` with Memory. Migration script runs on first use.
4. **Phase 4 (non-breaking)**: Add parallel multi-repo execution. New `--parallel` flag. Sequential remains default.

**Rollback**: Each phase is independently reversible. Phase 1 is purely additive. Phases 2-3 can revert to previous file versions. Phase 4 is opt-in.

## Open Questions

- Should the `--durable` flag be the default when Postgres is available? (Currently opt-in)
- Should we add a `docs-sync status` command that queries Memory for cross-repo sync status?
- Should the parallel concurrency limit (3) be configurable via CLI flag or config.yaml?
