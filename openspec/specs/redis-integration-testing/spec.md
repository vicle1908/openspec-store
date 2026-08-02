# Redis Integration Testing

## Purpose

Provides real Redis integration testing infrastructure for TDT Python packages. Uses testcontainers to spin up ephemeral Redis instances for verifying protocol-level behavior that in-memory fakes cannot replicate.

## Requirements

### Requirement: Testcontainers Redis fixture provides real Redis instance

The test infrastructure SHALL provide a session-scoped Redis instance via testcontainers for integration testing. The fixture SHALL support both container-based and explicit URL modes.

#### Scenario: Container-based Redis instance
- **WHEN** `TDT_REDIS_TEST_URL` environment variable is not set
- **THEN** the fixture SHALL start a `redis:7-alpine` container
- **AND** provide a valid Redis DSN to tests
- **AND** clean up the container after the test session completes

#### Scenario: Explicit Redis URL mode
- **WHEN** `TDT_REDIS_TEST_URL` environment variable is set to a valid Redis DSN
- **THEN** the fixture SHALL use that DSN instead of starting a container
- **AND** report `provider="external"` in the backend metadata

#### Scenario: Docker unavailable
- **WHEN** Docker is not running and `TDT_REDIS_TEST_URL` is not set
- **THEN** the fixture SHALL fail with a clear error message indicating Docker is required
- **AND** the error message SHALL suggest setting `TDT_REDIS_TEST_URL` as an alternative

### Requirement: Integration tests verify real Redis behavior

Integration tests SHALL exercise `RedisStateStore` against a real Redis instance to verify protocol-level behavior that fakes cannot replicate.

#### Scenario: TTL expiration behavior
- **WHEN** a state is saved with a TTL configuration
- **THEN** the integration test SHALL verify the key expires after the configured duration
- **AND** subsequent reads SHALL return `None` for expired keys

#### Scenario: Atomic operations
- **WHEN** concurrent save and load operations execute against the same key
- **THEN** the integration test SHALL verify no data corruption occurs
- **AND** the final state SHALL be deterministic (either old or new value)

#### Scenario: Serialization roundtrip
- **WHEN** an `OperationState` with complex nested fields is saved and loaded
- **THEN** the integration test SHALL verify all fields survive the JSON serialization roundtrip
- **AND** datetime fields SHALL maintain timezone awareness
- **AND** enum fields SHALL deserialize to their correct types

#### Scenario: Connection resilience
- **WHEN** the Redis connection experiences a temporary network interruption
- **THEN** the integration test SHALL verify the client reconnects automatically
- **AND** subsequent operations SHALL succeed without manual intervention

### Requirement: Test isolation via key namespacing

Each integration test SHALL use unique Redis key prefixes to prevent test pollution when sharing a container instance.

#### Scenario: Parallel test execution
- **WHEN** multiple integration tests run concurrently
- **THEN** each test SHALL use a unique key prefix (UUID-based)
- **AND** no test SHALL read or modify keys from another test
- **AND** cleanup SHALL only remove keys with the test's prefix

#### Scenario: Test failure cleanup
- **WHEN** an integration test fails with an exception
- **THEN** the fixture SHALL still clean up all keys with that test's prefix
- **AND** the Redis instance SHALL remain usable for subsequent tests

### Requirement: Marker-based test separation

Integration tests SHALL be marked with `@pytest.mark.integration` to enable selective execution.

#### Scenario: Default test run
- **WHEN** developer runs `uv run pytest`
- **THEN** only unit tests (without `@pytest.mark.integration`) SHALL execute
- **AND** no Docker dependency SHALL be required

#### Scenario: Integration test run
- **WHEN** developer runs `uv run pytest -m integration`
- **THEN** only tests marked with `@pytest.mark.integration` SHALL execute
- **AND** Docker SHALL be required (or `TDT_REDIS_TEST_URL` set)

### Requirement: Pytest configuration for integration marker

The `jira-skill` package SHALL declare the `integration` marker in `pyproject.toml` to avoid pytest warnings.

#### Scenario: Marker declaration
- **WHEN** `pytest` is invoked with `--strict-markers`
- **THEN** the `integration` marker SHALL be recognized
- **AND** no deprecation warnings SHALL be emitted for the marker
