## Why

The agent ecosystem assessment (2026-08-03) identified concrete gaps across
agent-core, agent-docs-sync, and agent-harness. These include test coverage
disparities in foundational modules, cross-repo coupling that bypasses the
SDK facade, missing CI infrastructure causing test failures, and a stale
docstring that misrepresents wiring state. Fixing these gaps before v0.2.0
stabilizes the ecosystem baseline and prevents regressions as the codebase
grows.

## What Changes

Priority 1 — Correctness (P1):
1. Fix `test_secret_scanning_policy.py` failures across all 3 repos by adding
   `.github/workflows/ci.yml` with gitleaks configuration matching test
   assertions. Pre-scan with gitleaks to identify and resolve false-positive
   findings (e.g., GitNexus metadata) via `.gitleaksignore` before enabling
   the blocking workflow.
2. Fix the stale docstring in `agent_harness/lifecycle_auth.py` which claims
   "not wired into the public runner yet" — it IS wired into
   `workflow/runner.py`, `workflow/graph.py`, and `cli.py`

Priority 2 — Coverage (P2):
3. Expand `llm_gateway` tests: add `BifrostGateway` and `ResilientGateway`
   contract tests focusing on actual observable behavior (model resolution,
   availability checks, forced-state fallback). ResilientGateway's
   `record_failure()` must be used to force breaker open (not private state
   mutation) since the wrapper never naturally transitions the breaker.
4. Expand `foundation` tests: add edge-case coverage for migration error
   paths, connection handling, and pool lifecycle

Priority 3 — Architecture (P3):
5. Expand `cli` tests: add edge-case coverage for agent failure, JSON output,
   and gateway error propagation (basic review/propose/explore already have tests)
6. Reduce `agent-docs-sync` coupling: re-export all 7 required symbols through
   `agent_core.sdk` facade so docs-sync imports only from the public SDK
   surface (4 non-SDK import statements → 0)

## Capabilities

### Modified Capabilities

- `sdk-public-api` — extended consumer symbol set with lifecycle identity types
- `agent-docs-sync` — import boundaries enforced via SDK facade
- `agent-core-quality-gate` — CI secret scanning requirement added

## Impact

- **Tests:** ~37 new test functions across agent-core (llm_gateway, foundation, cli)
- **CI:** New `.github/workflows/ci.yml` in 3 repos (gitleaks secret scanning)
- **Coupling:** agent-docs-sync non-SDK imports reduced from 4 statements to 0
- **SDK:** 7 new exports in `agent_core.sdk` (Settings, lifecycle identity types)
- **Harness:** lifecycle_auth docstring corrected to reflect actual wiring
- **Versioning:** agent-docs-sync agent-core dependency floor raised to >=0.2.0
- **Validation:** All repos remain ruff-clean, all tests pass, mypy strict clean
