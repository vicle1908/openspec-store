## Context

`ConsumerRuntimeProfile.tools_allowed` currently defaults to an empty tuple, while agent construction replaces an empty profile allowlist with all registry tool names and static preparation interprets an empty set as unrestricted. Run-scoped preparation already distinguishes `None` from an empty list. `agent-harness` therefore uses a fabricated sentinel name to express no registry tools.

`AgentRuntime` also composes in-memory upstream step persistence when a capability is not supplied. This is useful for ephemeral runs, but the canonical spec describes a stale config-driven API and can be read as restart durability. The change modifies `agent-core` and its docs/tests; consumers migrate afterward.

## Goals / Non-Goals

**Goals:**

- Give omitted, empty, and bounded allowlists one consistent meaning.
- Preserve missing-field compatibility while enabling explicit deny-all.
- Make process-local versus restart-safe step persistence explicit.
- Reuse upstream persistence APIs without adding a TDT abstraction.
- Keep `agent-core` free of consumer workflow topology.

**Non-Goals:**

- Refactor the entire legacy registry or flavor system.
- Merge Pydantic agent-step persistence with LangGraph checkpoints.
- Add docs-sync or harness state models to core.
- Introduce Jira/GitLab clients or agentmemory as persistence authority.

## Decisions

### 1. Represent omission explicitly

The public profile field becomes optional: `None` means no allowlist restriction, an empty tuple means deny-all, and a non-empty tuple is a bounded allowlist. Missing values in legacy serialized profiles resolve to `None`. The distinction is preserved through `build_agent`, flavor policy, and `PrepareTools` rather than normalized with truthiness.

Alternative: add a sentinel or separate `deny_all_tools` flag. Rejected because two controls can conflict and consumers already need normal collection semantics.

### 2. Intersect visibility policies

Static and run-scoped allowlists are intersections after deny rules; authority and approval policy remain independent additional constraints. Unknown tool names never broaden access. Characterization tests cover all combinations before behavior changes.

Alternative: treat later scopes as overrides. Rejected because an override could broaden an earlier least-privilege boundary.

### 3. Keep implicit persistence explicitly ephemeral

The runtime may continue composing `InMemoryStepStore` for convenience, but it exposes process-local classification. A consumer claiming restart durability must supply `StepPersistence` using an upstream persistent store. Failure to open a declared persistent store is fatal; no memory fallback occurs.

Alternative: add a core persistence config/factory. Rejected until multiple consumers demonstrate a stable need beyond direct upstream composition.

### 4. Reconstruct resources instead of serializing them

After restart, a consumer rebuilds gateway, tools, capabilities, and the same store from configuration, then calls the public upstream continuation API with the persisted run identifier. Live clients and handles are never serialized.

### 5. Preserve thin-kernel observability

Construction and lifecycle diagnostics report only policy classification and store backend class/path class, never credentials or persisted messages. Existing tracing remains intact; agentmemory is not continuation authority.

## Risks / Trade-offs

- **Explicit empty profiles lose tool access** → Mark as breaking, migrate consumers, and preserve omitted/missing as unrestricted.
- **Truthiness bugs reintroduce ambiguity** → Add focused profile/build/runtime matrix tests and public documentation examples.
- **Consumer restart tests pass only in one process** → Require separate-process reconstruction fixtures in docs-sync.
- **Upstream API changes** → Pin compatible versions and verify frozen plus disposable candidate resolutions.

## Migration Plan

1. Add characterization tests for current static/run-scoped behavior and serialized profiles.
2. Introduce the optional profile representation and explicit policy normalization.
3. Update build/static/run preparation with deny-all tests.
4. Correct persistence specs/docs and add persistent-store reconstruction tests.
5. Remove the harness sentinel in the dependent harness change.
6. Run the three-repository compatibility matrix.

Rollback restores the prior core version and consumer sentinel only during the compatibility window. Persistent store formats are not migrated, so rollback must not delete consumer state. Distribution is the normal library release/install path; no Docker or launchd deployment is required.

## Open Questions

- None required before implementation; any future shared persistent-store factory remains a separate change after a second production consumer need is proven.
