## Approach

Each item is scoped to a single repo (with explicit exceptions noted). The
work is ordered by priority (P1 correctness → P2 coverage → P3 architecture)
and each item has a verification step before moving to the next.

## P1 — Correctness

### 1. Secret Scanning CI Workflow

All 3 repos share the same `test_secret_scanning_policy.py`. Tests assert:
- `fetch-depth: 0` present in workflow
- `docker://ghcr.io/gitleaks/gitleaks:v8.30.1` present (exact image reference)
- `git --redact=100 --no-banner --verbose .` present (exact command)

The GitHub Action (`gitleaks/gitleaks-action@v2`) does NOT match these
assertions. The test IS the contract — the CI workflow must use a standalone
Docker-based gitleaks step that matches the expected strings exactly:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Run gitleaks
        uses: docker://ghcr.io/gitleaks/gitleaks:v8.30.1
        with:
          args: git --redact=100 --no-banner --verbose .
```

docs-sync has 2 failing tests (not 1): `test_ci_scans_full_history_with_redaction`
AND `test_rollback_allows_only_a_synthetic_exact_fingerprint` both read the
workflow file.

### 2. Harness lifecycle_auth Docstring

Investigation confirms lifecycle_auth IS already wired into the harness:
- `workflow/runner.py` imports `GateResolverPolicy`, `GateSubjectResolver`
- `workflow/graph.py` imports `GATE_POLICY_VERSION`
- `cli.py` imports `GateIdentityUnavailableError`

The docstring in `agent_harness/lifecycle_auth.py` line 4 saying "not wired
into the public runner yet" is stale. Fix: update the module docstring to
reflect actual state.

## P2 — Coverage

### 3. llm_gateway Tests

Current state: 559 LOC src, 153 LOC tests, ratio 0.27. Actual coverage: 76%.

**What actually exists (verified against code):**
- `BifrostGateway`: class in gateway.py. Public API is `get_model()`, `from_env()`,
  health check, close. Does NOT have message-routing methods — it delegates
  to `pydantic-ai` model factory via `create_bifrost_model()`.
- `ResilientGateway`: class in resilient.py. Wraps any `LLMGateway` with
  `CircuitBreaker` per provider (opens after 5 failures, recovers after 30s)
  and `FallbackChain` for failover. Public API is `get_model()`, `is_available()`.

**What to test:**
- BifrostGateway: `get_model()` returns a valid model instance, `from_env()`
  reads env vars correctly, error handling for missing config
- ResilientGateway: `get_model()` delegates to inner gateway, `is_available()`
  reflects breaker state, fallback chain delegation when primary is unavailable,
  circuit breaker state transitions (closed → open → half_open)
- Factory edge cases: unknown provider raises error, missing config fields

**Do NOT test retry/timeout as if they exist in ResilientGateway** — the
retry/timeout behavior lives in `agent_core.resilience` module, not in
`llm_gateway/resilient.py`.

### 4. foundation Tests

Current state: 1290 LOC src, 452 LOC tests, ratio 0.35. Actual coverage: 75%.

**What already exists:**
- `migrations_eval.py` and `migrations_vector.py` are covered by
  `test_supported_zero_coverage_modules.py::test_optional_migrations_use_open_execute_close_contract`
- `migrations.py` has 3 tests covering basic error paths
- `tracing.py` has 4 tests but only 33% coverage

**What to add (real gaps):**
- Migration error paths: connection failure handling, pool cleanup on exception
- `tracing.py`: OTel span creation, context propagation (33% → target 60%+)
- `settings.py`: missing env var handling, validation edge cases
- Foundation edge cases: workspace resolution errors, config validation

### 5. cli Tests

Current state: 974 LOC src, 408 LOC tests, ratio 0.42. Actual coverage: 78%.

**IMPORTANT: Basic CLI tests already exist** (verified):
- `test_review_reads_file_and_truncates_prompt` ✓
- `test_review_uses_agent_prompt` ✓
- `test_propose_uses_agent_prompt` ✓
- `test_explore_uses_agent_prompt` ✓

**What to add (edge cases only):**
- Error handling: invalid target path, network failure, agent timeout
- Output modes: JSON output, verbose mode
- URL-based review targets
- Exit code behavior on failure

## P3 — Architecture

### 6. docs-sync SDK Coupling

Non-SDK imports to eliminate (verified, 4 import statements):

```python
# config.py:15 — TYPE_CHECKING guard
from agent_core.foundation.settings import Settings

# cli.py:537 — function-local import
from agent_core.agent_base import ApprovalDecision  # ALREADY in SDK

# lifecycle_auth.py:8 — module-level import (6 symbols)
from agent_core.lifecycle_identity import (
    AuthenticatedSubject,
    ConfigFileResolver,
    IdentityStatus,
    SignedSubjectAssertion,
    SubjectResolutionRequest,
    SubjectResolutionResult,
)

# state.py:17 — module-level import (2 symbols)
from agent_core.lifecycle_identity import SubjectResolutionRequest, SubjectResolutionResult
```

**Required SDK exports (7 new symbols):**
- `Settings` (from `agent_core.foundation.settings`)
- `AuthenticatedSubject` (from `agent_core.lifecycle_identity`)
- `ConfigFileResolver` (from `agent_core.lifecycle_identity`)
- `IdentityStatus` (from `agent_core.lifecycle_identity`)
- `SignedSubjectAssertion` (from `agent_core.lifecycle_identity`)
- `SubjectResolutionRequest` (from `agent_core.lifecycle_identity`)
- `SubjectResolutionResult` (from `agent_core.lifecycle_identity`)

Note: `ApprovalDecision` is already exported from the SDK. The existing
`agent_core.sdk.__init__.py` already imports it from `agent_core.agent_base`.

**Version dependency:** docs-sync currently declares `agent-core>=0.1.0`.
After adding new exports, this MUST be raised to `agent-core>=0.2.0` to
prevent import failures when installed outside the editable workspace.
