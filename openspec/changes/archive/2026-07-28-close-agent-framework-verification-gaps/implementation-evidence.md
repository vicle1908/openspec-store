# Implementation Evidence

Status: corrective implementation and all required verification gates are
complete for the source identities recorded below.

## Source identity baseline

The following repositories were dirty before corrective implementation. The
existing paths are preserved and excluded from the corrective file set.

| Repository | HEAD | Tracked binary-diff SHA-256 |
| --- | --- | --- |
| `tdt-meta` | `2fef7405340ece45f2cbcf1f90c80eacd4d170e4` | `a6bb83f09c64998c7abb8185a29306de63eabe754a84e2f8ef95e8b89f418868` |
| `agent-core` | `b79bb6cfa6ad391c33b7630a4835d4c6df68a561` | `930f238006977af07e8a2fa0766c62792081396582453647e8223beca28c2c26` |
| `agent-docs-sync` | `33f441760b2487ccaec4b20119f108c3896184e2` | `8848c0dddb19a70ea5489ecffc9208e8b154ef4a38b480ab6a8befcbef969261` |
| `agent-harness` | `085d9c2e45da97c62110cf81fc231b14a2d6f0f0` | `9bd630771366d80a775e6cc9c1fb2c5c419520323aac2c4d0cae0c08e85d1f94` |

The sorted untracked inventory at baseline is:

- `tdt-meta`: `openspec/changes/agent-harness-stage-modules/ALIGNMENT.md`, `INVENTORY.md`, `implementation-evidence.md`; `openspec/changes/archive/2026-07-28-converge-agent-framework-upstream/**`; `openspec/changes/close-agent-framework-verification-gaps/**`; `openspec/specs/agent-harness-integration/**`, `agent-harness-runner/**`, `agent-harness-workflow/**`, `consumer-composition-boundary/**`, `native-workflow-composition/**`, `stage-module-protocol/**`, `stage-toolset-composition/**`, `state-composition/**`.
- `agent-core`: `docs/composition-migration.md`; `src/agent_core/sdk/composition.py`; `tests/_ai/test_agent_spec_convergence.py`, `test_run_controls.py`, `test_tool_preparation.py`; `tests/sdk/test_composition.py`, `test_memory_convergence.py`; `tests/test_characterization.py`, `test_deprecation_warnings.py`, `test_release_checks.py`, `test_rollback_exercise.py`.
- `agent-docs-sync`: `src/agent_docs_sync/workflows/canonical.py`; `tests/test_canonical_pipeline.py`, `tests/test_parity.py`.
- `agent-harness`: `src/agent_harness/stages/contracts.py`; `tests/test_cli.py`, `test_construction_regression.py`, `test_convergence_contracts.py`.

The full tracked status also contains pre-existing modifications and deletions
in the same repositories, including generated `__pycache__` files in
`agent-docs-sync`; those paths are not corrective implementation targets.

### Final verified source identity

The final 2026-07-28 verification used these current dirty-source identities:

| Repository | HEAD | Tracked binary-diff SHA-256 | Sorted untracked corrective paths |
| --- | --- | --- | --- |
| `tdt-meta` | `bae94f8f214de02fa9b44b39c42b341b939495f8` | `c205eeefacd4ca0a07b7c5d2489af044a5963c90a6c29bfb82bcee27ab4da90e` | none; hash excludes the two self-describing implementation manifests and `rollback-evidence.md` |
| `agent-core` | `3aff416eca0801ea3a1804892bc5700aac71ebf5` | `ce202335994dca60c501fe7254b8f3ea174afca3626b6833bbfa31ca6cbd3807` | `docker-entrypoint-initdb.d/20-create-harness-db.sql` |
| `agent-docs-sync` | `47e37e9a7c055e4db82e391b956a14f6d651d1b1` | `fed3ced9ee43a958c9b3aed02d8a09327bdd616a4752be5e4825cbe6af9a9bfe` | none |
| `agent-harness` | `087c064d83045f6262481355fc30fcf6d1ee1641` | `f2d2b0b068fabac1127fe0ab41b0d0e41ca383de58350c44acf9da60a1b442e7` | `tests/test_dependency_baseline.py`, `tests/test_postgres_integration.py` |

The unrelated `tdt-meta/openspec/changes/align-jti-skill-runtime-contract/**`
tree remains outside this change and is not claimed as completion evidence.
The `tdt-meta` diff hash deliberately excludes the manifests that contain the
hash, avoiding a self-referential identity while retaining every planning and
task change in the hashed scope.

## Corrective file set

Only these paths may be changed by this change:

- `tdt-meta/openspec/changes/close-agent-framework-verification-gaps/**`
- `tdt-meta/openspec/changes/agent-harness-stage-modules/tasks.md`
- `agent-core/src/agent_core/_ai/hooks.py`, `agent_core/agent_base/agent.py`,
  `agent_core/sdk/agents.py`, `agent_core/sdk/memory.py`,
  `agent_core/_ai/capability.py`, and focused tests/docs.
- `agent-docs-sync/src/agent_docs_sync/agent.py`,
  `agents/{discovery,generation,validation}.py`, `cli.py`,
  `workflows/{canonical,discovery_pipeline,full_pipeline,sync_pipeline}.py`,
  and focused tests/docs.
- `agent-harness/src/agent_harness/agents/factory.py`,
  `models/{gates,artifacts}.py`, `config.py`, `state.py`,
  `stages/contracts.py`, `workflow/{graph,runner}.py`, `cli.py`,
  and focused tests/docs.

Any other path requires an artifact update and explicit review before editing.

## Corrective ownership ledger

Archived completion claims remain historical. The following corrective owners
are the only implementation owners for the disputed ranges:

| Archived task range | Verified gap | Corrective owner | Closure evidence |
| --- | --- | --- | --- |
| 4.1–4.5 | Hook lifecycle coverage, return propagation, and exactly-once dispatch | 2.1, 3.1–3.5 | Hook protocol, warning, instrumentation, deferred, and stream tests |
| 5.1–5.4 | Deferred and stream parity | 2.3, 3.1–3.5 | Native event/deferred characterization and event-count evidence |
| 6.1–6.5 | Agent specification round-trip and safe capability loading | 2.3, 4.5–4.6 | Round-trip, unknown-field, and authority-negative tests |
| 7.1–7.6 | Harness memory stores, step persistence, and legacy memory projection | 2.2–2.3, 4.1–4.6 | Store isolation, official limits, step continuation, and restart tests |
| 9.1–9.6 | Docs canonical pipeline, builders, and parity/dead-path evidence | 2.4–2.5, 5.1–5.6 | CLI fixture parity and caller-graph evidence |
| 10.5 | Deployment bundle may retain stale `agent-core` source | 10.5 | Rebuilt bundle inspection |
| 11.1–11.8 | Harness consumer composition, topology, gates, and runner parity | 2.6–2.8, 6.1–9.6 | Construction, topology, gate, checkpoint, and CLI tests |
| 12.1–12.4 | Compatibility warnings, caller census, and removal criteria | 3.3, 4.2–4.3, 5.3, 10.4 | Warning, migration, zero-caller, and rollback evidence |
| 13.1–13.7 | Cross-repository quality, compatibility, Graphify/GitNexus, and rollback claims | 10.1–10.7, 11.1–11.8 | Full verification manifest with no skipped required gate |

## Framework baseline

The frozen dependency tuple is Pydantic AI `2.18.0`, Pydantic AI Harness
`0.11.0`, LangGraph `1.2.9`, LangGraph checkpoint `4.1.1`, and LangGraph
Postgres checkpoint `3.1.0`. The candidate matrix row must be freshly resolved
within existing bounds in a disposable workspace; no lockfile change is
authorized by this change.

The installed environments in all three Python repositories resolve this exact
tuple; `importlib.metadata` verification was run from `agent-core` and the
declared bounds/lockfiles match in `agent-docs-sync` and `agent-harness`.

On 2026-07-28 the final source was copied to disposable workspace
`/tmp/tdt-framework-matrix.agSVSy` and freshly resolved with
`uv lock --dry-run --refresh` followed by `uv sync --frozen` in each consumer.
The results were 221, 217, and 215 packages respectively, with no lockfile
changes. Focused cross-repository contracts then passed: agent-core 24 tests,
docs-sync 6 tests, and harness 12 tests. The candidate therefore collapses to
the frozen baseline tuple without requiring a lockfile update.

## GitNexus impact baseline

| Repository / symbol | Risk | Impact | Affected processes |
| --- | --- | ---: | --- |
| `agent-core:HookAdapter` | LOW | 6 | none |
| `agent-core:BaseAgent` | LOW | 11 | none |
| `agent-core:build_agent` | LOW | 0 | none |
| `agent-core:MemoryCapability` | LOW | 0 | none |
| `agent-docs-sync:run_canonical_pipeline` | CRITICAL | 7 | `audit`, `check`, `sync`, `discover`, `update` |
| `agent-docs-sync:sync_all` | LOW | 0 | none |
| `agent-docs-sync:run_discovery_pipeline` | LOW | 0 | none |
| `agent-docs-sync:run_full_pipeline` | LOW | 0 | none |
| `agent-docs-sync:run_full_audit` | HIGH | 5 | `sync_all_repos_parallel`, `sync_all`, `sync_all_repos_full` |
| `agent-docs-sync:build_doc_sync_agent` | HIGH | 3 | `build_validation_agent`, `build_discovery_agent`, `build_generation_agent` |
| `agent-harness:_make_gate_node` | CRITICAL | 6 | `approve`, `reject`, `status`, `astream`, `report` |
| `agent-harness:GateRequest` | LOW | 16 | none |
| `agent-harness:GateDecision` | LOW | 16 | none |
| `agent-harness:WorkflowRunner` | LOW | 1 | none |
| `agent-harness:validate_stage_topology` | CRITICAL | 6 | `approve`, `reject`, `status`, `astream`, `report` |
| `agent-harness:create_stage_agent` | LOW | 0 | none |

Corrective edits are limited to the declared file set. Final GitNexus compare
scans report no indexed tracked-symbol change for `agent-core`, one docs test
symbol with no affected process and LOW risk, and the approved harness
configuration/topology boundary at HIGH risk: seven indexed files/symbols and
eleven report, approve, reject, and status flows. The untracked core bootstrap
SQL and harness integration tests are recorded explicitly in the source
identity because GitNexus compare does not include untracked files. No
unexpected production symbol or execution flow was detected.

Graphify canonical-path queries were run for:

- agent-core: `SDK composition lifecycle memory` — composition, BaseAgent,
  memory facade/store, and lifecycle nodes.
- agent-docs-sync: `canonical docs routing builder` — `run_canonical_pipeline`
  through deterministic sync/discovery/full-DAG stages.
- agent-harness: `harness gates runner topology` — `build_graph`, gate models,
  stage nodes, validation pipeline, and runner/state nodes.

The refreshed Graphify results show the expected consumer-owned paths. After
the docs orchestration deletion, the rebuilt graph contains
`run_canonical_pipeline`, its private `_run_sync_dag` implementation, and the
single bounded `sync_all_repos` coordinator; removed dynamic/public legacy
entry points are absent. The refreshed harness graph contains the native graph,
runner, gate models, static stage modules, and official toolset composition.

Focused results:

- `agent-core`: full test suite passes (535) after removing `MemoryCapability`, the
  legacy `memory_*` tools, the `memory=` constructor path, `HookRegistry`,
  `HookAdapter`, hook packs, tool-registry hook attachments, and
  compatibility-only tests. Generic memory composition now uses public Harness
  `InMemoryStore`, `FileStore`, and `SqliteMemoryStore`; the TDT adapter is
  reserved for tenant/repository/session resolution. Persistent store
  reconstruction, CAS replay, bounded reads, memory tool exposure, injection
  limits, scoped isolation, and public step continuation pass focused tests.
  Strict mypy, Ruff, formatting, and the focused memory/spec/deferred suite
  pass.
  Deferred approval, stream ordering/cancellation, AgentSpec fidelity and
  `from_spec` round-trip, unknown capability rejection, and public step
  continuation are covered by focused tests.
- `agent-docs-sync`: Ruff check, format check, strict mypy, and the full test
  suite pass (166). Legacy dynamic/public full-workflow entry points,
  duplicate multi-repository coordinators, `doc_path_guard`, and
  `create_guardrails_config` are absent. The canonical builder now requires a
  prepared `ToolRegistry`; discovery and validation builders require their
  prepared registries too, so no builder silently substitutes a registry,
  gateway, hook registry, or capability set. Command-level fixtures cover
  check, discover, update dry-run, sync, audit, and sync-all routing, output,
  exit codes, and bounded delegation.
- `agent-harness`: full Ruff, strict mypy, format, and 196 tests pass, including
  the real PostgreSQL marker against a fresh disposable database.
  Checkpoint schema rejection tests cover unknown runs and incompatible
  versions without mutation. Stage-agent construction now requires an
  immutable `StageCompositionContext` with a resolved gateway and no fallback
  gateway resolution or `list[Any]` tool composition.
  Negative authority tests cover source/Jira/GitLab mutation, shell/code
  execution, bounded filesystem escapes, undeclared network imports, and
  read-only GitNexus/Graphify operations.
  GitNexus, Graphify, bounded-file, and Jira reads are adapted once to public
  `FunctionToolset` objects. Stage construction composes the immutable
  `StageDefinition.toolsets`/`.capabilities` values and denies the core builtin
  registry unless explicit run-scoped tool names are supplied. The topology
  plan is the single validation/wiring authority. Gate rejection uses
  `Command(goto=...)` as its sole route, and trusted-clock, identity, replay,
  exactly-once, same-process, and shared durable-boundary fixtures pass.
  Canonical environment tests cover process env, `$TDT_HOME/.env`, YAML
  fallback, alias rejection, and workspace configuration without undeclared
  fields. Native execution proves `Command(update=..., goto=...)` runs its
  target in the following step. A separate CLI process recovered and approved
  a real persisted interrupt without regenerating the completed spec artifact.

The active framework legacy census is clean across the three repositories:
there are no source or test references to `MemoryCapability`, `HookRegistry`,
`HookAdapter`, `create_guardrails_config`, `doc_path_guard`, the removed
workflow entry points, `build_sync_pipeline`, `approval_projection`, or
legacy `hooks=` constructor paths.

The agent-core dependency gate also AST-scans adapter imports and rejects
private upstream module paths for lifecycle, memory, toolsets, construction,
interrupt, checkpoint, and graph integrations.

## Compatibility caller census

The requested compatibility window is intentionally zero-length: the user
authorized removal after the production-caller census, and no compatibility
warning or parallel implementation remains.

| Removed projection | Replacement | Before → after | Removal criterion |
| --- | --- | --- | --- |
| `MemoryCapability` / `memory=` | Harness `Memory` composed through `create_memory_capability` or TDT-scoped adapter | implicit constructor memory → explicit capability/store | zero production callers |
| `HookRegistry` / `HookAdapter` | official Pydantic AI `Hooks` callbacks | registry dispatch → direct callback composition | zero production callers |
| docs legacy workflow entry points | `run_canonical_pipeline` | independent pipelines → one mode boundary | zero production callers |
| `create_guardrails_config` / `doc_path_guard` | typed `create_doc_guardrails` and official input/output guards | untyped projection → typed guard capabilities | zero production callers |

The census command returned no source or test references for these projections
or legacy `hooks=` constructor paths across `agent-core`, `agent-docs-sync`,
and `agent-harness`.

The HIGH-impact `create_guardrails_config` removal was approved and completed;
GitNexus scans still report critical aggregate risk because baseline dirty
paths remain in all repositories.

## Verification manifest

Every row below was rerun against the final corrective source identity above:

| Gate | Repository / command | Result | Source identity |
| --- | --- | --- | --- |
| OpenSpec strict validation | both active changes | passed after the final artifact refresh | current `tdt-meta` working tree |
| Ruff check and format | all three repositories | passed | final dirty-source identities above |
| Strict mypy | all three repositories | passed | final dirty-source identities above |
| Unit, characterization, and negative-path tests | full suites passed: agent-core 535, agent-docs-sync 166, agent-harness 196 | final dirty-source identities above |
| Frozen compatibility matrix | all three repositories assert Pydantic AI 2.18.0, Harness 0.11.0, LangGraph 1.2.9, checkpoint 4.1.1, Postgres saver 3.1.0 | passed | final dirty-source identities above |
| Fresh bounded-resolution matrix | `/tmp/tdt-framework-matrix.agSVSy` | passed: all three consumers resolved unchanged and focused contracts passed 24/6/12 | copied final dirty-source identities above |
| Shared durable restart/resume contract | `agent-harness` | passed across stream, recreated runner, status, bounded history, and resume; completed spec artifact did not rerun | final `agent-harness` identity above |
| Real Postgres restart/resume | `agent-harness` | passed against a fresh disposable PostgreSQL 18.4 database; setup provisioned three tables and a separate CLI process resumed the persisted interrupt | final `agent-harness` identity above |
| Deployment bundle inspection | `deployments/ai-review/deps/agent-core` | passed: `src/`, `pyproject.toml`, and `README.md` were rebuilt byte-for-byte from `agent-core`; legacy hook/memory symbols are absent | `agent-core@3aff416`, rebuilt 2026-07-28 |
| Rollback fixtures | all three Python repositories | passed independently: core 16, docs 11, harness 97 including real PostgreSQL; incompatible checkpoint schemas fail before writes and deleted legacy implementations are not rollback targets | final dirty-source identities above; see `rollback-evidence.md` |
| GitNexus detect changes and Graphify paths | all modified repositories | passed; final scope matches the approved configuration/topology boundary with no unexpected production flow | final dirty-source identities above |
