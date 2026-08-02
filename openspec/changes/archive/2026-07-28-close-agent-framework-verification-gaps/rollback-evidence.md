# Rollback evidence

## Policy

Rollback uses the current public composition boundaries and forward recovery.
It never restores `HookRegistry`, `HookAdapter`, `MemoryCapability`, dynamic
docs workflows, duplicate multi-repository coordinators, string capability
lookup, or a second graph/checkpointer implementation. A rollback target that
cannot prove compatibility with persisted identity or checkpoint schema fails
before execution and requires a new run.

## Independent exercises

| Surface | Exercise | Preserved invariant | Result |
|---|---|---|---|
| Hooks | Construct/run with official `Hooks`, and construct without the optional capability | exactly-once callbacks; no legacy registry import or dispatch | passed |
| Memory | Reconstruct public file/SQLite stores and read bounded namespaced data | tenant/repository/session namespace, ordering, and persisted paths | passed |
| Docs routing/builders | Run canonical mode and CLI fixtures; census removed dynamic/full entry points | stable thread/report data and one canonical builder/routing authority | passed |
| Harness gates/topology | Run new/unknown, completed four-approval, pending-gate restart, rejection, and replay fixtures | request/run/thread/artifact/interrupt IDs, exactly-once history, completed artifacts | passed |
| Checkpoint schema | Read current schema and attempt legacy/unknown schema validation | incompatible state remains unchanged and execution does not start | passed fail-closed |

Commands executed on 2026-07-28:

```text
agent-core:
  uv run pytest -q tests/test_rollback_exercise.py \
    tests/agent_base/test_agent.py::TestHooks \
    tests/sdk/test_memory_convergence.py \
    tests/test_docker_local_dev.py::test_initdb_creates_harness_database_non_destructively \
    tests/test_dependency_baseline.py -x
  16 passed

agent-docs-sync:
  uv run pytest -q tests/test_canonical_pipeline.py \
    tests/test_cli_canonical_commands.py \
    tests/test_dependency_baseline.py -x
  11 passed

agent-harness:
  TDT_POSTGRES_TEST_URL=<disposable-local-dsn> uv run pytest -q \
    tests/test_durable_runner_boundary.py tests/test_runner_contracts.py \
    tests/test_workflow.py tests/test_gate_trace.py tests/test_state_runtime.py \
    tests/test_graph_validation.py tests/test_config.py \
    tests/test_dependency_baseline.py tests/test_postgres_integration.py -x
  97 passed
```

## Fixture outcomes

- New/unknown workflow IDs return an error and do not create a run.
- A completed workflow retains artifact and decision IDs; replay is denied.
- A pending gate recovered through the same saver retains its native interrupt,
  request, run, thread, stage, artifact digest, issued time, and expiry.
- A separate CLI process recovered and approved the pending real-Postgres
  interrupt without regenerating the completed spec artifact.
- Reconstructed memory stores retain tenant-scoped paths and bounded reads.
- Docs check/discover/audit reports remain deterministic under the canonical
  mode boundary; removed entry points cannot be selected as rollback targets.
- Checkpoint schema values other than the supported current value are rejected
  before stage execution, resume, or writes.

## Environment result

A disposable PostgreSQL 18.4 container with no host volume started from an
empty database. The core boundary provisioned all checkpoint tables on first
use and the process-restart test passed. A separate read-only check confirmed
the existing local `agent_harness` database and its three checkpoint tables
already exist, so no local-volume migration or production database operation
was performed.
