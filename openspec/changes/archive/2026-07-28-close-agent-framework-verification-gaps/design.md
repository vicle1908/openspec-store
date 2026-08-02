## Context

`converge-agent-framework-upstream` was archived with every task checked, while `implementation-evidence.md`, the current source, and the strict repository gates disagree with that state. The remaining work crosses `agent-core`, `agent-docs-sync`, `agent-harness`, and the active `agent-harness-stage-modules` change. The affected paths include CRITICAL workflow roots, so the correction must make task ownership and verification evidence explicit before implementation.

The architectural constraint remains unchanged: public Pydantic AI, Pydantic AI Harness, and LangGraph contracts own generic mechanics; `agent-core` owns narrow reusable TDT integration and policy; consumers own domain tools, prompts, state, artifacts, and topology. Configuration and extension use composition rather than framework subclassing.

## Goals / Non-Goals

**Goals:**

- Restore agreement among active specs, active tasks, implementation, tests, and archive evidence.
- Remove compatibility adapters and parallel lifecycle, memory, pipeline, tool-registry, and workflow implementations after caller census.
- Make docs-sync routing deterministic and singular.
- Make harness gates fail closed on identity, authorization, expiry, and checkpoint incompatibility.
- Require reproducible cross-repository evidence before completion or archive.
- Keep future upstream upgrades localized to public composition boundaries.

**Non-Goals:**

- Mutating the archived convergence artifacts to hide the discrepancy.
- Introducing a common stage framework into `agent-core`.
- Removing a compatibility surface without zero-production-caller evidence.
- Changing mobile application behavior, external APIs, deployment orchestration, or framework dependency versions.
- Adding a new persistence, observability, or authorization dependency.

## Decisions

### 1. Correct through a follow-up change and an ownership ledger

The archived change remains immutable. This change records each disputed archived task, its current evidence, its owning corrective task, and its final verification result. Where `agent-harness-stage-modules` has a falsely completed checkbox, that task is reopened and linked to the corrective task; work is not duplicated between changes.

Alternative considered: edit the archive and restore it as active. Rejected because it destroys the historical fact that completion was recorded prematurely and makes audit history unreliable.

### 2. Remove compatibility projections

New code composes official upstream protocols directly:

- Lifecycle behavior composes Pydantic AI `Hooks` directly with exact return propagation and exactly-once dispatch.
- Memory uses one official Harness `Memory` capability and public `MemoryStore` implementations.
- Docs commands call the canonical pipeline; deprecated workflow functions are absent.
- Removed compatibility modules are not exported, imported, or vendored.

The user explicitly authorized compatibility deletion after the caller census showed no production callers for the removed memory and workflow symbols. HIGH-impact builder/guard removal remains gated on explicit confirmation and full consumer migration.

### 3. Keep consumer composition explicit

`agent-core.sdk` exposes typed composition inputs matching the public Pydantic AI `AgentToolset` and `AgentCapability` contracts, including only provider callables accepted by those contracts, plus narrow TDT adapters. `agent-docs-sync` owns one builder that receives its resolved gateway, official toolsets/capabilities, hooks, and mode policy. `agent-harness` owns stage definitions, native graph edges, gate policy, and checkpointed state. Neither consumer builder accepts untyped `Any` composition values or silently creates a replacement registry, gateway, hook registry, or capability set.

Alternative considered: promote docs pipeline and harness stage concepts into `agent-core`. Rejected because they are consumer-specific and would increase inheritance and upgrade coupling.

### 4. Route all docs commands through a mode-aware canonical boundary

One canonical per-repository function owns command-mode dispatch for `check`, `discover`, `update`, `sync`, and `audit`. `sync-all` remains an aggregate coordinator only: each selected repository is executed through that same canonical function, and the coordinator owns only bounded concurrency and result aggregation. Deterministic stages remain ordinary functions; agent generation is invoked only where the selected mode permits it. Existing full/discovery entry points are removed, with caller-census tests proving no independent orchestration remains.

Errors are normalized at the canonical boundary with the original cause preserved. Existing report and CLI exit semantics remain characterization-tested.

### 5. Derive immutable gates and authorize decisions at the trusted boundary

Gate identity is derived deterministically from checkpointed inputs: `run_id`, `thread_id`, stage, artifact ID/digest, and the artifact's timezone-aware UTC `created_at`. `issued_at` is that trusted artifact timestamp and `expires_at` is `issued_at + configured TTL`; neither value is read from the decision or recomputed from wall time when the interrupt node re-executes. The request also contains allowed continuations/backtracks and the configured approver allowlist. A protected graph with an empty allowlist fails during construction.

The CLI or service boundary resolves the acting principal through a narrow consumer-owned `ActorResolver` protocol and passes it separately from user decision data. The runner reads `StateSnapshot.interrupts` or task interrupts through public graph state, binds the pending native `Interrupt.id`, stamps a timezone-aware UTC audit timestamp, and constructs the trusted decision. A decision must match the request, run, thread, stage, artifact digest, and pending interrupt ID, and the resolved actor must be in the checkpointed approver set. Expiry is evaluated against the runner's trusted UTC clock; a caller-provided timestamp is never used for authorization. Expired, unauthorized, stale, replayed, or cross-thread decisions fail before `Command(resume=...)` advances the checkpoint. Accepted decisions are recorded exactly once.

Alternative considered: trust the actor and timestamp serialized by the CLI caller. Rejected because self-asserted identity and time do not establish authorization and cannot prevent expiry bypass, cross-thread use, or replay.

### 6. Version checkpoint state and use only public history APIs

The static harness state carries a schema version. Run, stream, status, history, and resume compile the same graph with the same operation-scoped checkpointer boundary and thread configuration. Durable operations use the shared Postgres saver boundary. A gated non-durable run uses an in-process `InMemorySaver` retained by its `WorkflowRunner`; it supports same-process resume only and makes no restart guarantee. An interrupting graph is never compiled without a checkpointer.

Before stage execution or checkpoint writes, the runner rejects unsupported versions without modifying the checkpoint. Current state uses public `aget_state`; history uses bounded `aget_state_history(limit=...)`; pending identity comes from public snapshot interrupts. Saver internals are not queried.

### 7. Validate topology at the composition root

Stage definitions continue to exclude topology. The composition root declares one immutable consumer-local topology plan containing native node identifiers, entry, edges, terminals, gates, and any bounded retry cycles. The same plan is the single source used first for validation and then for `StateGraph.add_edge`/branch wiring; it is not a second execution engine. The validator verifies:

- all edge endpoints and gate targets exist;
- entry-reachable stages match the intended registered graph;
- terminal paths are valid;
- parallel writers have compatible deterministic reducers;
- fan-in reads are available on every incoming path;
- cycles are explicit and bounded by a declared retry policy.

The validator reports stage and field names and runs before graph compilation. It does not inspect private LangGraph builder state, add execution semantics, or create a second workflow DSL.

### 8. Close work only with a reproducible evidence manifest

Completion evidence records exact commands, exit status, relevant fixture/backend, GitNexus change scope, compatibility versions, rollback result, and reproducible source identity. In a dirty worktree, source identity is the repository `HEAD`, a hash of the tracked binary diff, and a sorted untracked-path inventory; the commit hash alone is insufficient. Required gates are:

- strict OpenSpec validation for both active changes;
- Ruff check and format, strict mypy, and pytest in all three Python repos;
- cross-repository compatibility and characterization suites against (1) the frozen lockfiles and (2) a disposable fresh resolution within the existing dependency bounds; if both resolve identically, the evidence records the collapsed matrix;
- Postgres restart/resume evidence when durable behavior is claimed;
- deployment-bundle inspection and rollback exercise;
- zero-production-caller evidence before compatibility deletion.

Unit tests passing alone are not sufficient. A failed, skipped, unavailable, or stale required gate leaves its task open with the blocker recorded.

Evidence is invalidated by later changes to any covered source, state-channel semantics, planning requirement, deployment artifact, or required backend assumption. The owning implementation remains in `agent-harness-stage-modules`; this corrective change reopens only its Postgres/checkpoint evidence, rollback, change-detection, manifest, and archive gates. This preserves exactly one implementation owner while preventing an earlier green matrix from authorizing a later dirty state.

### 9. Observability and deployment

Existing TDT audit/metrics hooks remain the observability path and must prove exactly-once lifecycle and gate-decision events. No agentmemory integration is added because workflow checkpoints and semantic agent memory retain distinct owners.

Implementation is library and CLI code deployed through each repository's existing process. If Docker scheduler artifacts include `agent-core`, deployment verification rebuilds with `docker compose up --build -d`; no running container is modified directly. Docs-sync and harness changes use their current manual/library rollout. Rollback restores the prior compatible entry point while preserving checkpoint data and evidence.

## Risks / Trade-offs

- **[CRITICAL workflow roots regress multiple CLI paths]** → Add characterization tests first, change one routing root at a time, and run GitNexus change detection after each repository.
- **[Removed compatibility imports break stale callers]** → Require zero-production-caller evidence and full repository suites before removal is accepted.
- **[Existing checkpoints lack schema or gate identity fields]** → Treat the legacy version explicitly, allow only a documented safe read/migration path, and fail closed when identity cannot be proven.
- **[Explicit approvers break current default protected-gate configuration]** → Mark the safety correction as breaking, add migration examples, and fail during construction rather than at resume.
- **[Local actor resolution is weaker than remote authentication]** → Scope the initial resolver to trusted local CLI/service invocation, never accept actor text from decision payloads, and require a separate change before remote transports.
- **[Topology validation becomes a shadow DSL]** → Validate native graph declarations only; do not add execution semantics or stage inheritance.
- **[Dirty worktrees obscure evidence]** → Record pre-existing paths, restrict diffs by repo, and never claim unrelated changes as corrective evidence.

## Migration Plan

1. Add the correction ledger and reopen mismatched active harness tasks.
2. Add characterization and negative tests for every verified gap.
3. Correct `agent-core` hooks and memory composition; remove legacy surfaces and verify SDK compatibility.
4. Collapse docs routing and builders onto the canonical boundary; prove CLI parity and dead-path removal.
5. Complete harness toolset composition and single-source topology-plan validation.
6. Add deterministic gate identity, trusted actor resolution, explicit approvers, checkpoint version checks, bounded history, an in-process saver for non-durable gates, and restart-safe durable resume.
7. Run strict per-repository and cross-repository gates, Postgres restart evidence, deployment-bundle inspection, and rollback.
8. Mark tasks complete only from the evidence manifest; archive only when all required evidence is current.

The final harness slice is executed by `agent-harness-stage-modules` tasks 3.6, 5.4–5.6, 7.5, 7.8, and 11.1–11.6. This change consumes that evidence; it does not add a second implementation of configuration, reducers, checkpointing, or database provisioning.

Rollback is per repository: retain the last known compatible public entry point, revert the smallest corrective commit, and preserve checkpoints and generated evidence. A rollback must not re-enable an independent legacy implementation.

## Open Questions

- Compatibility surfaces may be removed only after production-caller analysis; this proposal does not predict that date.
