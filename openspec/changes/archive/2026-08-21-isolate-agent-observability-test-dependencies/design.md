# Design: Isolate Agent Core Observability Test Dependencies

## Context

See proposal.md - Why.
During test execution in `agent-core`, tests executing `init_observability()` and CLI commands interact with global singletons (the OpenTelemetry `TracerProvider`, `structlog` processors, and Pydantic `Settings`). Two specific failure modes were observed:
1. `Settings.agent` validation error in lifecycle tests: tests executing after other test modules inherit modified or uninitialized environment variables, causing `Settings` instantiation to fail.
2. Short-lived CLI export timeout: the CLI test asserts that spans flush before process exit, but with tight timeout limits and background process scheduling on busy CI/local runners, the flush check times out.

## Goals / Non-Goals

**Goals:**
- Provide isolated pytest fixtures (e.g. `monkeypatch`, `autouse` reset fixtures) for observability tests to guarantee clean settings and reset provider states.
- Increase export timeout threshold slightly and ensure deterministic flush completion in CLI test assertions.
- Achieve reliable 100% test pass rate across the full `agent-core` suite.

**Non-Goals:**
- Modifying production runtime logic in `agent_core.observability` or `agent_core.foundation`.
- Introducing new external test dependencies.

## Decisions

### Decision 1: Use scoped pytest fixtures for global state reset
- **Rationale**: Pytest fixtures with `autouse=True` or explicit fixture injection can reset `TracerProvider`, environment variables, and cached `Settings` before and after each test case, preventing cross-test pollution.
- **Alternatives Considered**: Modifying global production classes to permit arbitrary runtime re-initialization was rejected as it would compromise the production idempotency contract.

### Decision 2: Bound test timeouts with safe concurrency headroom
- **Rationale**: Setting a reasonable timeout margin (e.g. 5-10s instead of 1s) for the sub-process / CLI runner test prevents false-positive flakiness under high CPU load.
- **Alternatives Considered**: Removing the timeout assertion entirely was rejected because verifying short-lived flush completion is an important test invariant.

## Risks / Trade-offs

- [Risk] Leaked state in non-pytest test runners → Mitigation: Enforce fixture cleanups in standard conftest / fixture definitions.

## Migration Plan

1. Author change planning artifacts in `openspec-store`.
2. Apply changes in `agent-core` test files during implementation phase.
3. Validate with `pytest tests/test_observability.py` and full suite run.

## Transaction Boundaries

Changes are restricted to test files and test configuration in `agent-core`. No database transactions, API contracts, or production artifacts are affected.
