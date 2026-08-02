## Context

agent-core (v0.2.0) is a shared agent runtime used by multiple repos in the TDT workspace. Currently, consumers import directly from internal modules (`agent_core.tool_registry`, `agent_core.agent_base`, etc.), creating tight coupling. With agent-docs-sync as the primary consumer and code-daily-scan (plus future consumers) planned, the framework needs a stable public API boundary.

Recent changes (v0.2.1-dev):
- **Memory is now production-ready**: wired into BaseAgent via `MemoryCapability`, no longer EXPERIMENTAL
- **BaseAgent accepts `memory` param**: optional `Memory` instance for agent memory integration
- **`resilient_tool` decorator**: new resilience pattern wrapping tool execution with retry + circuit breaker

The existing `agent-core-integration-contract` and `public-api` specs define the contract; this design implements the concrete SDK.

## Goals / Non-Goals

**Goals:**
- Create `agent_core.sdk` as the single recommended import path for consumers
- Provide composable `ConsumerConfig` that wraps `Settings` (not inherits)
- Eliminate boilerplate: tool registration, agent construction, memory init, observability setup, workspace discovery
- Migrate agent-docs-sync fully to SDK (no legacy paths)

**Non-Goals:**
- Changing agent-core's internal module structure (existing imports stay functional)
- Adding new framework capabilities (this is a packaging/API boundary change)
- Migrating code-daily-scan (out of scope, follows same pattern later)
- Deprecating internal import paths (no warnings, just SDK as recommended)

## Decisions

### D1: Dedicated SDK module vs. expanded __init__.py

**Decision:** Dedicated `agent_core.sdk` package (7 files).

**Rationale:** A dedicated module provides clear "this is public, this is internal" semantics. Expanding `__init__.py` would pollute the namespace and blur the boundary. The SDK module can evolve independently of internal structure.

**Alternatives considered:**
- Expand `agent_core/__init__.py` — rejected: mixes public and internal symbols
- Use `agent_core.public` — rejected: `sdk` is more conventional for this pattern

### D2: Composable vs. inherited config

**Decision:** ConsumerConfig composes Settings as a field (`config.settings: Settings`), not inherits.

**Rationale:** Composition avoids diamond inheritance issues and keeps consumer config independent from framework config evolution. Consumers access framework settings via `config.settings.gateway`, while adding their own fields at the top level.

**Alternatives considered:**
- Inherit Settings — rejected: tight coupling to framework config schema changes
- Separate config objects — rejected: consumers need gateway/secrets access without extra wiring

### D3: SDK re-exports vs. wrapper classes

**Decision:** SDK re-exports existing symbols directly (no wrapper classes).

**Rationale:** The existing `BaseTool`, `BaseAgent`, `WorkflowBuilder` APIs are stable and well-designed. Wrapping them would add indirection without value. The SDK's value is in the boundary declaration and helper utilities, not in API redesign.

**Alternatives considered:**
- Wrapper classes (e.g., `SDKBaseTool`) — rejected: unnecessary indirection
- Protocol-based interfaces — rejected: existing ABCs already serve this role

### D4: Helper utilities scope

**Decision:** Include 5 helpers in Phase 1: `build_toolkit`, `build_agent`, `create_consumer_memory`, `init_observability`, `discover_repos`.

**Rationale:** These cover the most common consumer boilerplate patterns observed in agent-docs-sync. Each helper saves 10-30 lines of setup code per consumer.

**Alternatives considered:**
- Fewer helpers (just re-exports) — rejected: doesn't solve the boilerplate problem
- More helpers (e.g., `build_workflow`) — deferred: wait for second consumer to validate pattern

### D5: No legacy deprecation paths

**Decision:** Old internal imports remain functional without deprecation warnings.

**Rationale:** Changing existing imports across the workspace creates churn without benefit. The SDK is the recommended path, but old paths work. Deprecation can be added later if the workspace stabilizes.

## Risks / Trade-offs

- **[Risk] SDK surface too thin for future consumers** → Mitigated by Phase 3 validation with code-daily-scan. The SDK can expand based on real consumer needs.
- **[Risk] Config field name conflicts** → Mitigated by ConsumerConfig using `settings` for framework config, keeping consumer fields at top level. Field name collisions are unlikely since consumer fields are domain-specific.
- **[Risk] discover_repos() may miss non-Python repos** → Mitigated by pattern parameter and override support. Future consumers can pass custom patterns.
- **[Trade-off] Composition over inheritance for config** → Slightly more verbose access (`config.settings.gateway` vs `config.gateway`), but much more flexible and resilient to framework changes.

## Migration Plan

1. **Phase 1 (agent-core):** Create `agent_core.sdk/` with 7 files. Zero changes to existing code.
2. **Phase 2 (agent-docs-sync):** Migrate imports, replace config, update helpers. Run full test suite.
3. **Phase 3 (validation):** Apply same pattern to code-daily-scan or new consumer.

**Rollback:** Revert agent-docs-sync imports to `agent_core.*` paths. SDK module can remain in agent-core (additive, no harm).

## Open Questions

- Should `build_agent()` accept a `hooks` parameter for direct hook registration? (Current: hooks are registered separately via HookRegistry)
- Should `discover_repos()` support non-Python repos (e.g., package.json markers)?
