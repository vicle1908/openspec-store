## Context

`agent-harness` is a new planning consumer, not a framework extension. It starts only after:

1. `stabilize-agent-framework-integration` has repaired dependency, capability, approval, hook, guardrail, DynamicWorkflow, and checkpointer behavior.
2. `converge-agent-framework-upstream` has exposed typed capability/toolset composition, official Hooks, native deferred continuation, Harness memory stores, typed LangGraph state, and native commands.

The reviewed execution baseline is Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.19 through the `dynamic-workflow` extra, and LangGraph 1.2.9.

The ownership boundary is:

- Pydantic AI owns agent runs, capabilities, toolsets, lifecycle hooks, streaming, and deferred tool calls.
- Harness owns reusable guardrails, memory, subagents, step persistence, and optional bounded DynamicWorkflow.
- LangGraph owns workflow topology, typed state, routing, interrupts, async execution, and checkpoints.
- `agent-core` owns TDT gateway, policy, budgets, skills, tool authorization/metadata, audit defaults, and stable composition.
- `agent-harness` owns planning artifacts, domain state, stage topology, approver policy, workspace selection, and traceability.

## Goals / Non-Goals

**Goals:**

- Produce grounded engineering-planning artifacts across multiple repositories.
- Use upstream-owned mechanisms through public APIs.
- Make state, evidence, decisions, and traceability schema-valid.
- Keep human authorization explicit and durable.
- Keep the first release read-only outside its artifact directory.

**Non-Goals:**

- Modifying `agent-core` during this change.
- Implementing source code, tests, OpenSpec changes, or merge requests.
- Exposing general shell, code execution, or arbitrary filesystem tools.
- Treating model judgment as authentication or authorization.
- Using DynamicWorkflow for deterministic scanning, persistence, validation, or approval routing.

## Decisions

### 1. Dependency gates precede repository creation

The implementation first verifies both prerequisite OpenSpec changes and their contract suites. It then obtains explicit approval before adding the new repository's external dependencies. The new project declares every package it imports directly and uses `uv`; no transitive-import reliance or `pip` command is permitted.

### 2. Agent composition uses the converged public SDK

Stage agents are created through `agent_core.sdk` with:

- official upstream `AgentCapability` values;
- official upstream `AgentToolset` values;
- TDT gateway, budget, skills, tool authorization, audit, and correlation policy;
- per-run instructions, dependencies, and toolsets.

Consumers import concrete capabilities from public Pydantic AI/Harness modules. They do not import `agent_core._ai`, inspect private toolsets, reconstruct agents, or encode upstream constructors in `harness_config`.

### 3. The workflow is native, typed LangGraph

`agent-harness` owns a `HarnessState` `TypedDict` (or equivalent supported typed schema) with explicit fields for each artifact, trace entries, revision counters, current stage, pending gate, status, and errors. Accumulated trace/revision fields declare reducers.

The workflow imports native `StateGraph`, `Command`, and `interrupt` from LangGraph. `agent-core` lifecycle/policy helpers may be used, but `WorkflowBuilder`, dict-only state, and `CommandResult` are not part of the new consumer.

The exact planning stages are:

1. `intake`
2. `context`
3. `clarify`
4. `spec`
5. `impact`
6. `design`
7. `api_contract`
8. `implementation_plan`
9. `coding_plan`
10. `plan_review`
11. `test_plan`
12. `verification`

No stage edits target source repositories. Stage 10 reviews plans and cross-artifact consistency, not code.

### 4. Human stage gates and tool approvals stay separate

Stage gates call native LangGraph `interrupt()` with a typed `GateRequest`. The authenticated local CLI resumes with `Command(resume=GateDecision(...))` using the same `thread_id`. The consumer validates the actor, stage, decision ID, expiry, and allowed transition before resume.

Pydantic AI `DeferredToolRequests`/`DeferredToolResults` remain reserved for approval of a particular agent tool call. They do not implement workflow-stage gates.

Initial approval transport is the local CLI authenticated by the operating-system/session identity. Webhook or Jira transport requires a later OpenSpec change. Auto-approval is permitted only for deterministic host-evaluated conditions; an LLM expression cannot authorize itself.

### 5. Persistence layers have one owner each

| State | Owner |
|---|---|
| Workflow node state, pending interrupts, stage resume | LangGraph checkpointer |
| Agent model/tool step continuation | Harness `StepPersistence` and public `StepStore` |
| Semantic/cross-ticket memory | Harness `Memory` over a TDT-authorized `MemoryStore` |
| Generated artifact files and trace JSONL | Bounded `$TDT_HOME/agent-harness/artifacts/` |
| Scheduled durable execution | Out of scope; no DBOS workflow is introduced |

Durable mode uses `AsyncPostgresSaver.from_conn_string()` as an async context manager. The graph is compiled and all `ainvoke`/`astream`/resume calls finish before the saver context exits. `thread_id` is a stable workflow run ID, not merely the ticket ID, so repeated runs do not collide.

### 6. Code intelligence is evidence, not an agent assertion

GitNexus MCP `query`, `context`, and `impact` are the primary symbol and execution-flow tools. Each result records the indexed repository, index commit, symbol UID when present, and query parameters. GitNexus CLI is a bounded operational fallback, not an LLM-visible shell.

Graphify supplies intra-repository structural traversal and shortest paths from the repository's graph file. The adapter exposes only `query`, `path`, and freshness checks with validated repository roots and arguments.

If an index is missing or stale:

- the result is marked unavailable/stale;
- confidence is reduced;
- the system may use bounded read-only file evidence;
- it cannot promote an unverified claim to “verified”;
- HIGH/CRITICAL change recommendations require current GitNexus impact evidence.

### 7. Artifacts are bounded and immutable by revision

Artifacts are written beneath:

`$TDT_HOME/agent-harness/artifacts/<ticket-id>/<run-id>/`

Each stage writes a new revision with a content digest and trace entry. Paths are normalized and checked against the configured root before directory creation or write. Target repositories are mounted/read as read-only inputs from the harness perspective.

The spec stage produces a draft planning artifact inside the harness root. Promotion into the canonical OpenSpec store is a separate authorized workflow and is not part of this change.

### 8. DynamicWorkflow is optional and narrow

The deterministic 12-stage graph is always authoritative. Harness `DynamicWorkflow` may later be enabled for bounded alternative exploration within `context` or `design`, but the initial implementation does not require it. If enabled by a follow-up:

- it receives read-only tools;
- it has finite calls, retries, usage, memory, and CPU-time limits;
- structured output is required;
- it cannot route gates, write artifacts, or mutate external systems.

### 9. Observability uses one lifecycle authority

Pydantic AI `Instrumentation` and official `Hooks` are the agent lifecycle sources. Agent-core's structured audit/budget callbacks compose on that lifecycle. LangGraph stage spans include workflow run ID, ticket ID, stage, artifact digest, gate decision ID, repository/index commit, and correlation ID.

No parallel consumer hook registry or duplicate manual model/tool span source is added.

### 10. Configuration follows TDT_HOME and least authority

Configuration uses typed settings with:

- `$TDT_HOME/harness/config.yaml`;
- `$TDT_HOME/harness/workspace.yaml`;
- `$TDT_HOME/.env` for secrets;
- local environment overrides.

Repository paths are expanded, resolved, and required to be explicit bounded roots. Index status is detected from actual tools; it is not trusted from manually maintained boolean flags.

## Risks / Trade-offs

- **Prerequisite changes are broad** → block implementation until their strict validation and contract suites pass.
- **Typed state increases initial modeling work** → gain deterministic reducers, safer checkpoint state, and consumer-owned schemas.
- **Current indexes can become stale** → carry index commits in evidence and fail confidence gates.
- **Human gates can stall** → use explicit expiry/escalation state without silently approving.
- **Cross-ticket memory may leak tenant context** → namespace by tenant/workspace/ticket and test isolation.
- **Planning scope may frustrate users expecting code changes** → report the authority boundary clearly and require a separate apply workflow.

## Migration Plan

1. Verify both prerequisite changes and their version/contract gates.
2. Obtain dependency approval and create the `agent-harness` repository.
3. Implement configuration, typed artifacts, state, and evidence models.
4. Implement read-only GitNexus MCP, Graphify, file, and Jira adapters.
5. Implement official agent composition, memory, and validation capabilities.
6. Implement the 12 native LangGraph stages and routing.
7. Implement native interrupts, authorization, durable async persistence, and CLI resume.
8. Add traceability, observability, authority, restart, and no-mutation tests.
9. Publish the C4, operator, configuration, and consumer-integration documentation.

Rollback removes the new repository or disables its CLI entry point. The change does not alter existing services or source repositories, and artifact data remains under the isolated TDT_HOME root.

## Resolved Execution Decisions

- The initial workflow has exactly 12 planning stages and does not generate or apply code.
- The initial approval transport is the authenticated local CLI.
- A missing/stale code-intelligence index produces an explicit incomplete-evidence outcome, not a fabricated result.
- Native LangGraph state, commands, interrupts, and async checkpointers replace custom workflow semantics.
- Official Harness memory and step stores replace private consumer memory capabilities.
