## Why

`agent-core` and `agent-docs-sync` currently report successful construction while several requested framework features are disabled, miswired, or unable to resume. The defects affect guardrails, sub-agents, write containment, DynamicWorkflow dependency compatibility, approval continuation, hook filtering, skill instructions, and durable LangGraph execution, so the shared framework contract must be stabilized before adding consumers such as `agent-harness`.

## What Changes

- Align both repositories on the reviewed baseline `pydantic-ai>=2.18.0,<2.19`, `pydantic-ai-harness[dynamic-workflow]==0.11.0`, and LangGraph `>=1.2.9,<1.3`. Remove the hand-maintained direct Monty pin and require both lockfiles to resolve the extra's declared `pydantic-monty==0.0.19` dependency. This changes existing dependency declarations and requires team review before implementation.
- Make explicitly requested capabilities fail clearly when unavailable or invalid instead of being replaced by an allow-all/no-capability fallback.
- Correct Harness guardrail and `SubAgents` construction contracts and add execution-level tests that cannot pass by swallowing exceptions.
- Enforce hook `tool_filter` values and guarantee one logical lifecycle event is emitted once.
- Propagate resolved skill instructions and consumer request context into each run without mutating future runs.
- Implement a complete approval pause/resume contract using deferred tool results while retaining `AgentResult` compatibility.
- Keep documentation writes inside configured roots at both the framework-policy and tool-execution boundaries.
- Execute LangGraph workflows asynchronously and keep checkpointer resources alive for the full run/resume lifetime.
- Require DynamicWorkflow agents that describe tools to actually receive those tools and enforce bounded usage/resource limits.
- Clear repository-wide Ruff, strict-mypy, and language-server diagnostics
  discovered during archive verification without weakening production checks.
- **BREAKING**: explicitly enabled but unavailable capabilities SHALL raise an actionable configuration/dependency error instead of silently degrading.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `harness-integration`: Require compatible dependency resolution, valid capability construction, public imports, and explicit failure semantics.
- `agent-guardrails`: Require configured guards to remain active and fail closed when their contract is invalid.
- `agent-delegation`: Require valid Harness `SubAgent` descriptors and executable delegation tests.
- `hooks`: Enforce tool filtering and exactly-once lifecycle delivery.
- `agent-runtime`: Require per-run skill/context propagation and resumable deferred approvals.
- `dynamic-workflow`: Require compatible Monty support, real agent tools, bounded execution, and no silent fallback.
- `agent-docs-sync`: Require contained writes and a live asynchronous durable workflow/checkpointer contract.

## Impact

- **Repositories**: `agent-core`, `agent-docs-sync`; no direct mobile application changes.
- **Dependencies**: existing Pydantic AI/Harness/Monty constraints and `uv.lock` files will change after explicit dependency-review approval; no new framework family is introduced.
- **Public behavior**: invalid capability configuration becomes visible; approval resume and durable execution become reliable.
- **GitNexus blast radius**:
  - `BaseAgent.run`: **CRITICAL**, 5 direct callers, 10 affected symbols, 5 execution-flow families.
  - `build_full_engine`: **CRITICAL**, reaches `run_full_dag` and the public CLI flow.
  - `_build_harness_capabilities`: LOW, one direct runtime constructor dependency.
  - `WorkflowEngine.run`, `build_dynamic_orchestrator`, and write-tool execution: locally LOW, but require cross-repository contract tests because repository-local indexes do not model all consumers.
- **Dependent work**: `agent-harness-c4-design` SHALL not begin runtime implementation until this change is complete.

## Non-goals

- Replacing all `agent-core` abstractions with upstream APIs.
- Migrating `ai-review`, `code-daily-scan`, or `jira-epic-report`; the
  repository-wide static-analysis cleanup is limited to `agent-core` and
  `agent-docs-sync`.
- Enabling high-authority Harness capabilities such as Shell, CodeMode, or RuntimeAuthoring by default.
- Changing iOS or Android application behavior.
