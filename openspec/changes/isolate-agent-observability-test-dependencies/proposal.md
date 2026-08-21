# Proposal: Isolate Agent Core Observability Test Dependencies

## Why

Concurrent observability tests in agent-core experience intermittent failures due to unisolated environment configuration and tight timeout margins in CLI export tests.

During the release cleanup review, the `agent-core` test suite reported two non-functional failures in the observability test suite: the short-lived OTEL CLI export test times out under constrained runner concurrency, and the observability lifecycle test encounters an unrelated `Settings.agent` validation error caused by leaky test environment settings. Isolating test fixtures, mocking global configuration cleanly, and tuning export timeouts will ensure reliable local and CI execution without altering any product specifications.

## What Changes

- Isolate test fixtures in `tests/test_observability.py` and lifecycle tests so global settings (e.g. `Settings.agent`) are properly mocked/sandboxed per test.
- Adjust timeout and flush synchronization in the short-lived OTEL CLI test to prevent race conditions during test execution.
- Maintain full test isolation across parallel test workers.

## Capabilities

### New Capabilities
<!-- None: tooling and test quality change with skip_specs: true -->

### Modified Capabilities
<!-- None: no spec-level behavioral requirements changed -->

## Non-Goals

- Changing product runtime observability contracts or OpenTelemetry export behavior.
- Modifying main specifications in `openspec/specs/`.
- Changing production environment defaults or configuration schemas.
- Performing immediate archive operations or code modifications within this planning proposal.

## Impact

- **Affected Ownership Boundaries**:
  - `agent-core`: `tests/test_observability.py`, test environment mocks, and test runner configurations.
