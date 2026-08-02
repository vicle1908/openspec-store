## Why

`agent-harness` needs independently testable planning stages, but the current proposal solves that by creating framework-level abstractions already owned by LangGraph, Pydantic AI, Harness, or `agent-core`. The initial implementation also reveals correctness gaps—missing gateway injection, shared-gate fan-out, mismatched reducers, and non-durable stream/resume—that must be fixed before modularity or parallelism expands the execution surface.

## What Changes

- Depend on `converge-agent-framework-upstream`; do not implement this change against the current legacy SDK surfaces.
- Keep stage packaging consumer-local and structural: a stage exposes its native node callable, typed read/write contract, validators, official toolsets/capabilities, and optional gate policy.
- Build the workflow directly with native LangGraph `StateGraph`, edges, `Command`, interrupts, reducers, and checkpointers.
- Replace `HarnessConfig(ConsumerConfig)` with a harness configuration that contains an immutable `agent-core` runtime profile.
- Replace tool-name lookup and a second `ToolRegistry` with official toolsets filtered by explicit per-stage policy.
- Replace string capability names with typed upstream capability values.
- Keep one statically declared workflow state; do not synthesize `TypedDict` classes at runtime.
- Keep scalar workflow fields fail-fast for concurrent writes; do not add latest-write-wins reducers to compensate for a topology conflict.
- Determine parallelism from explicit graph topology plus read/write/reducer safety, not a `parallel` boolean.
- Replace the shared gate node with dedicated post-stage interrupt nodes that have one continuation and cannot replay artifact generation on resume.
- Make run, stream, status, and resume consume the shared initialized `agent-core` checkpointer boundary, native interrupt IDs, and one thread identity.
- Load durable settings through the canonical `tdt_core.env.load_tdt_env()` boundary, using `HARNESS_DURABLE` and `TDT_POSTGRES_URL` without a second settings framework.
- Extract the 12 stages incrementally behind characterization tests; remove the old entry points only after CLI and checkpoint parity.
- **BREAKING**: legacy `HarnessConfig` inheritance and monolithic builder entry points may be removed only after migration fixtures pass and a rollback-compatible checkpoint boundary is documented.

## Capabilities

### New Capabilities

- `stage-module-protocol`: Consumer-local structural contract for independently testable stages.
- `state-composition`: Statically declared harness state, reducers, and stage read/write boundaries.
- `stage-toolset-composition`: Official toolset/capability composition with least-privilege stage policy.
- `native-workflow-composition`: Direct LangGraph topology, validation wrappers, gates, and safe parallel branches.
- `agent-harness-workflow`: Correct 12-stage planning behavior after incremental modularization.
- `agent-harness-runner`: Unified run, stream, status, and durable resume behavior.

### Modified Capabilities

None.

## Impact

- **Repositories**: `agent-harness` implementation and tests; `agent-core` local-development Postgres bootstrap; `tdt-meta` planning evidence.
- **Dependencies**: no new libraries. Direct dependencies remain declared where imported and are verified by the shared compatibility matrix.
- **Public APIs**: stage packages become importable consumer-local units; native LangGraph and upstream agent types remain owned by their libraries.
- **GitNexus blast radius**: `build_graph` is **HIGH** (five indexed impacted symbols across run/stream/resume). Repository-local results mark runner methods lower, but durable behavior crosses process and persistence boundaries and requires end-to-end tests.
- **Known defects covered**: missing SDK gateway, one shared gate with multiple outgoing gated-stage edges, message reducers on arbitrary string lists, an unsupported latest-write-wins scalar reducer, missing canonical durable configuration, missing real Postgres restart evidence, stream/resume compiling without the durable saver, and replay risk when `interrupt()` shares a node with artifact-producing work.
- **Execution baseline**: Ruff, format, strict mypy, and 186 tests pass, but those gates do not cover real Postgres or the newly disputed reducer semantics. The remaining tasks explicitly add those contracts before completion.
- **Infrastructure**: `agent-core-local` Docker Compose provides Postgres at `127.0.0.1:54329` for durable checkpoint testing. Durable mode uses `HARNESS_DURABLE=true` and `TDT_POSTGRES_URL` loaded from the canonical TDT environment boundary.
- **Mobile apps**: no direct iOS or Android impact.

## Non-goals

- Adding a generic stage framework to `agent-core`.
- Creating a tool registry, workflow DSL, runtime TypedDict merger, module marketplace, or plugin loader.
- Adding new planning stages or enabling high-authority tools.
- Inferring parallel safety from names or a boolean flag.
- Adding a production database migration or a second environment/settings loader.
- Changing Jira, GitLab, source repositories, or OpenSpec content outside the bounded harness artifact root.
