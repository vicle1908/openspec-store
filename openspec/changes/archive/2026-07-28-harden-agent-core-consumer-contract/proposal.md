## Why

`agent-core` is a mature shared kernel, but its consumer-facing tool-allowlist semantics conflate an omitted policy with an explicit empty policy, and its implicit step-persistence behavior is easy to mistake for restart durability. Clarifying these contracts first removes sentinel workarounds and gives docs-sync and harness a stable composition boundary.

## What Changes

- Define an omitted tool allowlist as unrestricted and an explicitly empty allowlist as deny-all across runtime profiles, static preparation, and run-scoped preparation.
- Preserve legacy missing-field compatibility while removing the need for impossible sentinel tool names in consumers.
- State that implicit in-memory step persistence is process-local and suitable only for ephemeral/test execution.
- Require durable consumers to compose an upstream `StepPersistence` with an explicit persistent store and reconstruct the agent with the same store after restart.
- Correct stale configuration and documentation claims without adding a second persistence abstraction or consumer topology to `agent-core`.
- Add characterization and consumer-contract tests for unrestricted, deny-all, bounded allowlist, process-local, and restart-safe persistent modes.
- **BREAKING**: An explicitly empty `tools_allowed` value will deny every tool instead of falling back to all registry tools; omitted legacy values remain unrestricted.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-runtime`: Define explicit omitted-versus-empty tool visibility semantics through public composition APIs.
- `agent-step-persistence`: Replace stale config-driven construction claims with explicit consumer composition, process-local defaults, and restart reconstruction requirements.

## Non-Goals

- Moving docs-sync or harness stages into `agent-core`.
- Creating a TDT-specific persistence layer over Pydantic AI Harness stores.
- Changing LangGraph checkpointer ownership or merging graph checkpoints with agent-step persistence.
- Broad refactoring of the legacy registry, gateway, observability, or memory systems.

## Impact

- Repository: `agent-core`; direct consumers: `agent-docs-sync` and `agent-harness`.
- Primary boundaries: `ConsumerRuntimeProfile`, `build_agent`, `AgentRuntime._prepare_tools`, `AgentRuntime.restrict_tools`, documentation, and contract tests.
- GitNexus rates `build_agent`, `_prepare_tools`, and `restrict_tools` LOW with no indexed upstream production callers; cross-repository compatibility tests remain required because consumers are separate repositories.
- No new external dependency is required; the existing upstream persistence APIs are reused.
- Mobile applications are unaffected.
