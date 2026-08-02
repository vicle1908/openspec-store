## 1. Dependency Setup

- [x] 1.1 Add `testcontainers[redis]>=4.15.0` to `jira-skill/pyproject.toml` dev dependencies
- [x] 1.2 Run `uv sync` in jira-skill to install testcontainers
- [x] 1.3 Verify testcontainers imports work: `uv run python -c "from testcontainers.community.redis import RedisContainer"`

## 2. Pytest Configuration

- [x] 2.1 Add `integration` marker to `jira-skill/pyproject.toml` under `[tool.pytest.ini_options]`
- [x] 2.2 Verify no marker warnings: `uv run pytest --strict-markers --collect-only`

## 3. Test Infrastructure

- [x] 3.1 Create `RedisTestBackend` dataclass in `jira-skill/tests/conftest.py`
- [x] 3.2 Implement `_managed_redis_backend()` context manager with dual-mode support
- [x] 3.3 Create session-scoped `redis_backend` fixture
- [x] 3.4 Add `redis_key_prefix` fixture for test isolation (UUID-based)
- [x] 3.5 Verify fixture works: `uv run pytest -m integration --collect-only`

## 4. Integration Tests

- [x] 4.1 Create `jira-skill/tests/test_redis_integration.py`
- [x] 4.2 Implement `TestRedisSerialization` — verify OperationState roundtrip
- [x] 4.3 Implement `TestRedisAtomicOperations` — concurrent save/load
- [x] 4.4 Implement `TestRedisConnectionResilience` — reconnection after interruption
- [x] 4.5 Verify all integration tests pass: `uv run pytest -m integration -v`

## 5. Verification

- [x] 5.1 Run unit tests (no Docker): `uv run pytest -x -q --tb=short`
- [x] 5.2 Run integration tests (with Docker): `uv run pytest -m integration -v`
- [x] 5.3 Run linter: `uv run ruff check tests/`
- [x] 5.4 Run type checker: `uv run mypy tests/`
- [x] 5.5 Verify test count: unit tests unchanged, integration tests added

## 6. Documentation

- [x] 6.1 Add comment in conftest.py explaining the dual-mode pattern
- [x] 6.2 Update jira-skill README.md with testing section (unit vs integration)
