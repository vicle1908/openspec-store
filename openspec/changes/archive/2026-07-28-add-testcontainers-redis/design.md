## Context

The `jira-skill` package manages workflow state via `RedisStateStore`, which persists operation states and checkpoints to Redis. Current tests use `_FakeRedis` — an in-memory dict that implements the minimal async interface. While fast, this fake misses real Redis behavior: TTL expiration, atomic operations, connection pooling, serialization format, and network error handling.

The `agent-harness` package already uses `testcontainers[postgres]` successfully with a pattern that supports both explicit DSN (for shared CI databases) and container fallback. This design extends that pattern to Redis.

**Current state:**
- `jira-skill/tests/test_state_store_redis.py`: 17 tests using `_FakeRedis`
- `agent-harness/tests/test_postgres_integration.py`: Reference pattern with `PostgresContainer`
- Docker available locally (v29.6.2)

## Goals / Non-Goals

**Goals:**
- Verify `RedisStateStore` against real Redis protocol behavior
- Establish a reusable testcontainers pattern for the TDT ecosystem
- Keep fast unit tests (with `_FakeRedis`) for rapid iteration
- Support both container-based and explicit-URL testing modes

**Non-Goals:**
- Replacing existing `_FakeRedis` unit tests
- Adding testcontainers to packages without external infrastructure
- CI/CD pipeline integration (local verification only)
- PostgreSQL testcontainers expansion (separate change)
- Redis Cluster or Sentinel testing (single instance sufficient)

## Decisions

### 1. Session-scoped Redis container

**Decision:** Use `scope="session"` for the Redis container fixture.

**Rationale:** Container startup takes 5-10s. Sharing one container across all integration tests in a session avoids repeated startup cost. Isolation between tests achieved via key namespacing (unique prefixes per test), not separate containers.

**Alternative considered:** Function-scoped containers (one per test). Rejected due to 10x slower test suite with no meaningful isolation benefit — Redis key cleanup is deterministic.

### 2. Dual-mode testing (container + explicit URL)

**Decision:** Support `TDT_REDIS_TEST_URL` env var to bypass container creation.

**Rationale:** Follows the `agent-harness` pattern exactly. Enables:
- Local development with containers (default)
- CI environments with shared Redis services
- Debugging against a specific Redis instance

**Alternative considered:** Container-only. Rejected — loses flexibility for environments where Docker is unavailable or a shared Redis is preferred.

### 3. Marker-based test separation

**Decision:** Use `@pytest.mark.integration` for container-dependent tests.

**Rationale:**
- `uv run pytest` — runs unit tests only (fast, no Docker)
- `uv run pytest -m integration` — runs integration tests (requires Docker)
- Clear separation of test concerns

**Alternative considered:** Separate test directories (`tests/unit/` vs `tests/integration/`). Rejected — adds organizational complexity without clear benefit for a single package.

### 4. Key namespacing for test isolation

**Decision:** Prefix all Redis keys with `{test_id}:` using `uuid4().hex` per test function.

**Rationale:** Multiple tests run against the same container instance. Namespacing prevents key collisions while allowing parallel test execution if pytest-xdist is added later.

**Alternative considered:** `FLUSHDB` between tests. Rejected — slower and doesn't support parallel execution.

### 5. Redis image version pinning

**Decision:** Use `redis:7-alpine` (stable, lightweight ~30MB).

**Rationale:**
- Alpine variant minimizes container pull time
- Redis 7 is current stable with full feature set
- Matches production Redis version expectations

**Alternative considered:** `redis:7` (Debian-based). Rejected — larger image, no benefit for testing.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Docker unavailable in some environments | `TDT_REDIS_TEST_URL` fallback; tests skip gracefully with clear error message |
| Container startup adds ~5-10s to test suite | Session-scoped fixture amortizes cost; 1765 existing tests unaffected |
| Redis version drift between test and production | Pin `redis:7-alpine`; document version in conftest.py |
| Test pollution via shared keys | UUID-based key namespacing per test function |
| Container cleanup failures | Testcontainers handles cleanup; explicit `try/finally` in fixture |

**Trade-off accepted:** Integration tests are slower (~10s) but provide real protocol verification. Unit tests with `_FakeRedis` remain fast (<1s) for rapid iteration.

## Implementation Pattern

Following the `agent-harness` reference implementation:

```python
# jira-skill/tests/conftest.py

@dataclass(frozen=True, slots=True)
class RedisTestBackend:
    dsn: str
    provider: str  # "testcontainers" | "external"
    image: str | None = None

@contextmanager
def _managed_redis_backend() -> Iterator[RedisTestBackend]:
    explicit_dsn = os.getenv("TDT_REDIS_TEST_URL")
    if explicit_dsn:
        yield RedisTestBackend(dsn=explicit_dsn, provider="external")
        return

    with ExitStack() as stack:
        container = RedisContainer("redis:7-alpine")
        try:
            stack.enter_context(container)
        except Exception as error:
            pytest.fail(
                "Redis is required: set TDT_REDIS_TEST_URL or provide Docker "
                f"({type(error).__name__})"
            )
        yield RedisTestBackend(
            dsn=container.get_connection_url(),
            provider="testcontainers",
            image="redis:7-alpine",
        )

@pytest.fixture(scope="session")
def redis_backend() -> Iterator[RedisTestBackend]:
    with _managed_redis_backend() as backend:
        yield backend
```
