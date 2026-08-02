## Context

agent-core has implemented features that lack documentation. The codebase has:
- 10 harness capabilities wired via `_build_harness_capabilities()`
- Subgraph composition (shared-state + wrapper patterns)
- Command API via `CommandResult` → `LangGraph Command`
- Per-node features (retry, cache, error_handler, metadata, timeout)
- `run_stream()` async generator API
- `load_agent_config()` for YAML/JSON agents

## Goals / Non-Goals

**Goals:**
- Every implemented feature has documentation
- Docs match actual code behavior (not aspirational)
- Code examples are runnable

**Non-Goals:**
- Rewriting existing well-documented features
- Adding API reference docs (use docstrings for that)
- Changing code

## Decisions

### Decision 1: Leverage existing patterns

Follow the pattern of existing docs (e.g., `memory.md`, `resilience.md`) — short overview, public API, quick start, troubleshooting.

### Decision 2: Harness guide as standalone file

`harness-integration.md` gets its own file because it covers 10 capabilities. Configuration.md gets a summary pointing to it.

### Decision 3: Fix streaming.md completely

Replace outdated `stream_mode` content with actual `run_stream()` API. Remove LangGraph streaming section (not implemented).

### Decision 4: Orchestration.md gets new sections

Add subgraphs, command API, and per-node features as new sections. Keep existing content intact.
