## Approach

Each item is scoped to a single repo to keep commits atomic. The work is
ordered by priority (P1 correctness → P2 coverage → P3 architecture) and
each item has a verification step before moving to the next.

## P1 — Correctness

### 1. Secret Scanning CI Workflow

All 3 repos share the same `test_secret_scanning_policy.py` which reads
`.github/workflows/ci.yml` and asserts gitleaks configuration. The fix is a
shared workflow file:

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
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

The test asserts `fetch-depth: 0` and `docker://ghcr.io/gitleaks/gitleaks:v8.30.1`.
The GitHub Action uses a different image reference. The test needs updating to
match the action-based approach, OR we add a standalone gitleaks step that
matches the expected string. Best approach: match the test's exact assertions
since the test IS the contract.

### 2. Harness lifecycle_auth Wiring

Investigation shows lifecycle_auth IS already wired into the runner:
- `runner.py` imports `GateResolverPolicy`, `GateSubjectResolver`
- `graph.py` imports `GATE_POLICY_VERSION`
- `cli.py` imports `GateIdentityUnavailableError`

The docstring saying "not wired into the public runner yet" is stale.
Fix: update the module docstring to reflect actual state.

## P2 — Coverage

### 3. llm_gateway Tests

Current: 16 tests (10 gateway + 6 factory). Missing:
- `BifrostGateway`: 0 tests (class exists, no direct tests)
- `ResilientGateway`: 0 tests (circuit breaker + retry around gateway)
- `create_gateway` edge cases: only 4 tests

Target: add ~15 tests covering BifrostGateway message routing,
ResilientGateway retry/circuit-breaker behavior, and factory edge cases.

### 4. foundation Tests

Current: 36 tests across 8 files. Missing:
- `migrations_eval.py`: 48 LOC, 0 dedicated tests (eval migration logic)
- `migrations_vector.py`: 38 LOC, 0 dedicated tests (vector migration logic)
- `migrations.py`: 147 LOC, 3 tests (thin for the complexity)

Target: add ~12 tests covering eval/vector migration paths and edge cases.

## P3 — Architecture

### 5. cli Tests

Current: 31 tests. Missing:
- `review` command: 0 tests (most-used entry point)
- `propose` command: 0 tests
- `explore` command: 0 tests

Target: add ~10 tests covering review/propose/explore with mocked agents.

### 6. docs-sync SDK Coupling

4 non-SDK imports to eliminate:
- `agent_core.agent_base.ApprovalDecision` → already in `agent_core.sdk` ✅
- `agent_core.foundation.settings.Settings` → NOT in SDK, needs re-export
- `agent_core.lifecycle_identity.SubjectResolutionRequest` → NOT in SDK
- `agent_core.lifecycle_identity.SubjectResolutionResult` → NOT in SDK

Fix: add `Settings`, `SubjectResolutionRequest`, `SubjectResolutionResult` to
`agent_core.sdk.__init__.py` re-exports. Then update docs-sync imports.
