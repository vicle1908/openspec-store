## Context

`agent-harness` turns an engineering ticket into 12 grounded planning artifacts. Its current implementation already uses native LangGraph state, `Command`, interrupts, `ainvoke`, and `astream`, and it imports the public `agent_core.sdk`. That is the right base, but the implementation and previous modularization proposal contain problems:

- `create_stage_agent()` calls `build_agent()` without the gateway later required by `BaseAgent.run`;
- `HarnessConfig` subclasses `ConsumerConfig`, coupling domain settings to the core configuration layout;
- the single `gate` node is connected to every gated stage, so a visit can fan out to unrelated stages;
- `workspace_repos`, `errors`, and `gate_history` use LangGraph's message reducer despite containing strings;
- only `run()` uses Postgres checkpointing, while `astream()` and `resume()` compile fresh in-memory graphs;
- the Postgres saver is not initialized through its public setup contract;
- the prior design duplicates an agent tool registry, graph composer, runtime state-type merger, string capability lookup, and config inheritance already owned elsewhere.

The prerequisite `converge-agent-framework-upstream` defines the cross-repository boundary: upstream libraries own generic mechanics, `agent-core` owns reusable TDT integration/policy, and `agent-harness` owns planning stages, artifacts, validation, gates, state, and topology.

The implementation baseline is Pydantic AI 2.18.0, Harness 0.11.0, and LangGraph 1.2.9. No new dependency is proposed.

Final API verification established four implementation constraints:

- LangGraph re-executes the node containing `interrupt()` on resume.
- native `Interrupt.id` is the supported identity, and `Command.resume` accepts an interrupt-ID-to-decision mapping.
- compiled graphs expose public async `aget_state` and `aget_state_history` for status/history.
- `AsyncPostgresSaver.setup()` is an explicit first-use schema-provisioning operation, while the saver context must remain open through compile and execution.

Current baseline verification is intentionally recorded rather than treated as green: dependency-lock resolution, Ruff, and all 42 tests pass; strict mypy reports 27 production errors across nine files and 74 total errors across 15 files. The production findings include the exact integration seams in this change (`factory.py`, configuration, state/graph typing, gate request construction, and runner result types) plus existing workspace/Jira/artifact typing. Execution starts by mapping every finding to a task and ends only at zero strict-mypy diagnostics.

The later corrective implementation reached zero strict-mypy diagnostics and 186 passing tests. A subsequent LangGraph 1.2.9 verification found one remaining semantic error: a node returning `Command(update=..., goto=...)` executes in one Pregel step and its target executes in the following step after observing the update. The target is not a concurrent writer in the source step. Adding `_last_value` to `current_stage` or `status` is therefore unnecessary for that routing case and weakens the intended fail-fast behavior for genuinely parallel writes.

## Goals / Non-Goals

**Goals:**

- Make every stage independently testable and replaceable.
- Preserve static typing and native LangGraph execution semantics.
- Fix agent construction, reducers, gate routing, and durable resume before adding parallel branches.
- Compose runtime configuration, toolsets, and capabilities without inheritance or duplicate registries.
- Extract stages incrementally with observable CLI and checkpoint parity.

**Non-Goals:**

- A reusable stage framework in `agent-core`.
- A workflow DSL over LangGraph.
- Runtime generation or merging of `TypedDict` classes.
- A plugin marketplace, dynamic entry-point discovery, or new planning stages.
- Source, Jira, GitLab, or OpenSpec mutation outside harness artifacts.

## Decisions

### 1. Stage modules are consumer-local structural objects

A harness stage is a frozen dataclass or protocol-compatible object containing only consumer concepts:

```python
@dataclass(frozen=True)
class StageDefinition(Generic[StateT]):
    name: Stage
    node: Callable[[StateT, RuntimeContext], Awaitable[StateUpdate | Command]]
    reads: frozenset[str]
    writes: frozenset[str]
    reducers: Mapping[str, Reducer[Any]]
    validators: tuple[Validator, ...]
    toolsets: tuple[AgentToolset, ...]
    capabilities: tuple[AgentCapability, ...]
    gate: GatePolicy | None = None
```

The object does not include a state class, initial-state fragment, string tool/capability names, dependency list, `parallel` flag, or a method that inherits configuration. Graph topology and initial state remain explicit at the composition root.

Alternative: promote a rich `StageModule` framework. Rejected because only one consumer requires it and most proposed fields reproduce native graph or agent composition behavior.

### 2. Harness configuration contains a runtime profile

`HarnessConfig(BaseModel)` contains `runtime: ConsumerRuntimeProfile` plus gate, validation, persistence, budget, retention, and authority models. A stage creates an immutable profile copy for model/limit changes and passes run-scoped instructions/toolsets/capabilities separately.

Legacy flat configuration is accepted by one loader adapter during the convergence compatibility window. Internal code never subclasses the core profile.

Alternative: `HarnessConfig(ConsumerConfig)`. Rejected because core field changes propagate through inheritance and domain configuration becomes coupled to core internals.

### 3. Agent construction requires explicit dependencies

The harness composition root resolves the gateway through the TDT factory and passes it to the typed SDK. Stage factories receive a ready composition context; they do not create gateways, hook registries, or registries implicitly.

Tools are adapted once to official Pydantic AI toolsets. Per-stage visibility uses supported filtered/prepared toolsets and TDT authorization policy. Capabilities are typed objects imported from their public upstream modules.

Failure to resolve the gateway or required toolset is a construction error before graph execution.

### 4. State is static and reducers match field semantics

One statically declared `HarnessState` remains the checkpoint schema. Domain artifacts may move into typed nested containers to reduce repetitive fields, but the type is declared in source and validated by mypy; no runtime `TypedDict` creation occurs.

Reducers are explicit:

- trace entries append with the trace reducer;
- string sets/lists use stable deduplicating or append reducers as specified;
- artifact mappings merge by stage key;
- scalar status/current-stage fields have a single writer per superstep and use LangGraph's default single-value channel.

`Command(goto=...)` does not make its source and target concurrent: the target runs in the next step and observes the source update. A latest-write-wins reducer is not used to silence multiple scalar writes. If a future native fan-out creates more than one scalar writer in a step, graph construction fails unless the field has an explicitly justified, domain-correct, order-independent reducer. `current_stage` and `status` have no such reducer in this change.

Each stage declares read/write fields for validation and parallel-safety tests, not for runtime projection into a different state type.

Alternative: merge module-local TypedDict types dynamically. Rejected because runtime synthesis gives little static type safety, complicates checkpoint compatibility, and creates field-conflict machinery.

### 5. Native graph construction is the only topology authority

`build_graph()` remains a consumer composition function that adds native nodes and explicit edges to `StateGraph(HarnessState)`. A small helper may wrap a stage node with validation and tracing, but there is no registry-backed `WorkflowComposer`.

Parallelism is introduced only after dependency analysis proves:

- no branch writes the same scalar;
- shared accumulators have deterministic reducers;
- both branches have the same authority and checkpoint guarantees;
- fan-in behavior is covered by an execution-trace test.

Alternative: `parallel=True` and automatic dependency resolution. Rejected because a boolean cannot establish data or reducer safety.

### 6. Dedicated post-stage gates have one target and native identity

A gate is a unique node such as `gate_design` placed after the artifact-producing stage. Its outgoing path has exactly one normal continuation. The request payload records run ID, thread ID, stage, artifact digest, expiry, and authorization context; the native `Interrupt.id` returned by LangGraph is recorded as the resume identity.

Because only the gate node contains `interrupt()`, resume may re-execute the gate but SHALL not re-run artifact generation or validation side effects. Approval continues only the intended next stage. Rejection uses native `Command(goto=...)` after validating the allowed backtrack target. Resume uses `Command(resume={pending_interrupt.id: decision})`, and the decision is appended exactly once.

The existing shared gate is characterized with a failing trace fixture before replacement so the bug cannot recur.

The `Command(goto=...)` used for an authorized backtrack routes the next step only. Its state update is visible to the backtrack target without annotating the target's scalar fields with a custom reducer.

### 7. The shared core checkpointer boundary serves every operation

`agent-core` already exports `create_async_checkpointer`, and `agent-docs-sync` already consumes it. Convergence extends that boundary to own TDT DSN resolution, explicit first-use schema provisioning, and saver context lifetime. `agent-harness` SHALL consume it rather than add another saver factory.

For each durable operation the runner:

1. acquires an opened saver from the shared boundary;
2. compiles the graph with that saver;
3. uses the same `thread_id` contract for run, stream, status, and resume;
4. reads status/history through public `aget_state`/`aget_state_history`;
5. maps the recovered native interrupt ID to the authorized resume decision;
6. keeps the saver resource alive for the whole operation.

`HarnessConfig.load()` invokes the public `tdt_core.env.load_tdt_env()` boundary before reading environment overrides. The stable public keys are `HARNESS_DURABLE` and `TDT_POSTGRES_URL`; the change does not introduce `HARNESS_PERSISTENCE_DURABLE` or a nested environment-name convention. Effective precedence follows the shared loader and then the harness merge: repository-local `.env`, existing process environment, `$TDT_HOME/.env`, harness YAML, and model defaults, from highest to lowest. Tests isolate the loader state and prove both environment keys populate `PersistenceConfig`.

Durable resume after restart uses the same backend. DBOS may own scheduled execution but does not substitute for LangGraph checkpoints.

### 8. Migration is incremental

The 12-stage graph remains behaviorally stable while stages are extracted. Each extraction adds characterization tests for inputs, artifact digest, validation/revision behavior, trace, and next node. Old module paths delegate during the transition and are removed only after all CLI fixtures pass.

No all-at-once rewrite or immediate deletion is allowed because `build_graph` is HIGH impact and the CLI is the operational entry point.

## Error Handling and Observability

- Construction errors identify the missing gateway, toolset, capability, or configuration path.
- Node failures record stage, run/thread IDs, bounded diagnostic context, and one audit event without leaking secrets.
- Invalid gate decisions fail closed and do not advance the checkpoint.
- Checkpointer setup/recovery failures are surfaced before any new stage executes.

## Known Issues

### LangGraph Deserialization Warnings

Checkpoint deserialization emits warnings about unregistered types (`Stage`, `ValidationStatus`, artifact types). These are cosmetic in LangGraph checkpoint 4.1.1 but will become errors in future versions. Fix: register harness types in `allowed_msgpack_modules` or set `LANGGRAPH_STRICT_MSGPACK=false` until types are registered.

### GitNexus Risk Level

`detect_changes` reports "high" risk due to `validate_stage_topology` affecting 11 processes (Report, Approve, Reject, Status flows). This is expected — topology validation is central to all gate workflows. The changes are additive (added `workspace_repos` to accumulator set) and do not introduce new risk.
- Official Hooks/Instrumentation plus TDT audit callbacks remain the lifecycle authority; stage wrappers add domain events only.

## Risks / Trade-offs

- **[Risk] Existing shared gate has incorrect fan-out and interrupted nodes replay** → capture exact failing visited-node trace, replace with dedicated post-stage gates, and prove artifact-producing stages do not rerun.
- **[Risk] Checkpoint schema changes break resume** → version state, test old-checkpoint loading, and reject incompatible versions before writing.
- **[Risk] Stage extraction creates many files without reducing coupling** → permit one file per simple stage; split only when tools or validators justify it.
- **[Risk] Parallel execution changes ordering and budgets** → ship no parallel branch until read/write/reducer and usage-budget tests pass.
- **[Risk] Latest-write-wins hides an invalid parallel scalar topology** → leave lifecycle scalars unreduced, assert source/target step ordering for `Command(goto=...)`, and retain graph-construction rejection for genuine parallel writers.
- **[Risk] State-channel semantics drift without a checkpoint version change** → remove the unsupported reducer before release; if any persisted channel semantics remain changed, increment the schema version and verify pending/completed fixtures before writes.
- **[Risk] Core convergence is delayed** → this change remains blocked at its dependency gate; correctness characterization can proceed, but SDK migration cannot.
- **[Risk] Passing tests hide 27 production type errors, including a missing gate expiry argument** → preserve the 42-test baseline, map every type error before edits, add failing behavior tests at affected seams, and require zero strict-mypy diagnostics at completion.
- **[Trade-off] Explicit graph wiring is more verbose** → topology remains inspectable, native, and easy to upgrade with LangGraph.

## Infrastructure

The `agent-core-local` Docker Compose stack (defined in `agent-core/compose.yaml`) provides a single PostgreSQL server for all three repositories. Each repo uses its own database to avoid schema conflicts.

### Database Allocation

| Database | Repo | Purpose | Tables |
|----------|------|---------|--------|
| `agent_core` | agent-core | Memory stores (PostgresMemory, VectorMemory) | memory, vector embeddings |
| `tdt_scheduler` | agent-core | DBOS scheduler state | scheduler workflows |
| `agent_harness` | agent-harness | LangGraph checkpoint tables | checkpoint, checkpoint_blobs, checkpoint_writes |

**All repos share one Postgres server** at `127.0.0.1:54329`. No dedicated Postgres instance per repo is needed.

### Setup

**First-time setup** (runs automatically on a fresh local-development data volume):

Add `20-create-harness-db.sql` to `agent-core/docker-entrypoint-initdb.d/`:

```sql
-- Create the agent_harness database for LangGraph checkpoint tables.
-- Runs only on first init of the postgres data volume.
SELECT 'CREATE DATABASE agent_harness'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'agent_harness')\gexec
```

**Existing installation** (data volume already initialized):

```bash
cd agent-core && docker compose run --rm postgres \
  psql -U agent_core -d postgres \
  -c "SELECT 'CREATE DATABASE agent_harness' WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'agent_harness')\gexec"
```

### Enabling Durable Mode

Add to `~/.tdt/.env`:

```bash
# Postgres checkpoint backend (use agent_harness database, not agent_core)
TDT_POSTGRES_URL="postgresql://agent_core:agent_core_dev@localhost:54329/agent_harness"
HARNESS_DURABLE=true
```

Or create `~/.tdt/harness/config.yaml`:

```yaml
harness:
  persistence:
    durable: true
    postgres_url: "postgresql://agent_core:agent_core_dev@localhost:54329/agent_harness"
```

### Schema Provisioning

`AsyncPostgresSaver.setup()` creates checkpoint tables on first use — no manual migration needed. The checkpoint tables are:
- `checkpoint` — workflow state snapshots
- `checkpoint_blobs` — serialized state values
- `checkpoint_writes` — pending state updates

### Configuration Loading Order

`HarnessConfig.load()` first delegates dotenv loading to `tdt_core.env.load_tdt_env()`, then merges harness settings. Effective precedence is highest to lowest:

1. Repository-local `.env` loaded by the shared boundary.
2. Existing process environment.
3. `$TDT_HOME/.env` loaded by the shared boundary.
4. `$TDT_HOME/harness/config.yaml` (`harness:` section).
5. Model defaults (`durable=false`, `postgres_url=None`).

`$TDT_HOME/harness/workspace.yaml` remains owned by workspace resolution and SHALL NOT be projected as undeclared top-level `HarnessConfig` fields.

## Migration Plan

1. Complete and verify `converge-agent-framework-upstream` typed composition APIs.
2. Freeze current CLI, graph trace, artifact, validation, and checkpoint behavior with characterization tests, including known failing gate/durable cases.
3. Compose `HarnessConfig` with the core runtime profile and inject the gateway explicitly.
4. Replace duplicate tool/capability lookup with official typed composition.
5. Remove unsupported scalar reducers, preserve fail-fast parallel conflict validation, and prove native `Command` step ordering and checkpoint compatibility.
6. Extract stages in dependency order while retaining one static state and explicit graph.
7. Compose configuration through `load_tdt_env()`, finalize local database bootstrap, and run real Postgres restart/resume tests after explicit approval for existing-volume database creation.
8. Keep the measured graph sequential; introduce no parallel edge in this change.
9. Run lint, strict mypy, unit/integration/CLI/durable-restart suites and GitNexus change detection.
10. Remove compatibility paths in a separate reviewable commit.

Rollback selects the prior graph composition root only if it can read the current checkpoint version. Otherwise rollback fails closed before workflow execution and provides a new-run path; it never silently discards pending gate state.

Deployment is a normal `agent-harness` package/source release. The only Docker change is a local-development init script for fresh Postgres volumes. Creating the database in an existing volume is an explicit operator-approved local migration; no production database, launchd, or mobile deployment change is introduced.

## Open Questions

None for this execution slice. The measured graph remains sequential and artifact fields remain explicit; either decision may be revisited only through a separate checkpoint-aware change.
