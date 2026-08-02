## Why

The TDT ecosystem relies on external infrastructure (Redis, PostgreSQL) for critical state management, but integration tests use in-memory fakes that don't exercise real protocol behavior. The `jira-skill` package uses `_FakeRedis` — a dict-based stand-in that misses TTL semantics, atomic operations, connection pooling, and serialization edge cases. This creates a false sense of confidence: tests pass locally but production Redis behavior remains unverified.

Testcontainers already proved viable in `agent-harness` (PostgreSQL). Extending this pattern to Redis closes the highest-value integration gap while establishing a reusable infrastructure testing pattern across the ecosystem.

## What Changes

- Add `testcontainers[redis]` dependency to `jira-skill` dev dependencies
- Create shared `conftest.py` fixtures with `RedisContainer` support
- Add integration test suite for `RedisStateStore` with real Redis
- Establish marker convention (`@pytest.mark.integration`) for container-dependent tests
- Preserve existing `_FakeRedis` unit tests for fast local iteration
- Document the testcontainers pattern for future adoption in other packages

## Capabilities

### New Capabilities

- `redis-integration-testing`: Real Redis integration tests for jira-skill state management, verifying TTL behavior, atomic operations, serialization, and connection handling against an actual Redis instance via testcontainers

### Modified Capabilities

_(none — this is additive infrastructure, not behavior change)_

## Impact

**Affected packages:**
- `jira-skill`: New dev dependency, new integration tests, conftest updates
- `agent-harness`: Reference implementation (no changes, already has testcontainers)

**Dependencies added:**
- `testcontainers[redis]>=4.15.0` (jira-skill dev dependency)

**Testing workflow change:**
- `uv run pytest` — runs unit tests only (fast, no Docker required)
- `uv run pytest -m integration` — runs integration tests with real Redis (requires Docker)

**Non-goals:**
- Migrating existing `_FakeRedis` unit tests (they remain for fast iteration)
- Adding testcontainers to packages without external infrastructure dependencies
- CI/CD integration (local verification only for now)
- PostgreSQL testcontainers expansion (separate change)

**Risk:** LOW
- Additive only — no existing tests modified
- Docker already available locally (v29.6.2)
- Pattern already proven in agent-harness
