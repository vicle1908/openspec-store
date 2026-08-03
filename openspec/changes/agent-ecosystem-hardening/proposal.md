## Why

The agent ecosystem assessment (2026-08-03) identified six concrete gaps across
agent-core, agent-docs-sync, and agent-harness. These range from test coverage
disparities in foundational modules to cross-repo coupling that bypasses the
SDK facade, and test failures caused by missing CI infrastructure. Fixing these
gaps before v0.2.0 stabilizes the ecosystem baseline and prevents regressions
as the codebase grows.

## What Changes

Priority 1 — Correctness (P1):
1. Fix `test_secret_scanning_policy.py` failures across all 3 repos by adding
   `.github/workflows/ci.yml` with gitleaks configuration
2. Wire `agent-harness.lifecycle_auth` into the public runner (or remove the
   stale docstring claiming it's not wired — it IS imported in runner.py)

Priority 2 — Coverage (P2):
3. Expand `llm_gateway` tests: add `BifrostGateway` and `ResilientGateway`
   coverage (current ratio 0.27, target ≥0.50)
4. Expand `foundation` tests: add `migrations_eval` and `migrations_vector`
   coverage (current ratio 0.35, target ≥0.50)

Priority 3 — Architecture (P3):
5. Expand `cli` tests: add `review` and `propose` command coverage (current
   ratio 0.41, target ≥0.50)
6. Reduce `agent-docs-sync` coupling: re-export `Settings` and
   `lifecycle_identity` symbols through `agent_core.sdk` facade so docs-sync
   imports only from the public SDK surface (4 non-SDK imports → 0)

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. This change adds tests, fixes CI infrastructure, and cleans import
  paths without changing normative behavior.

## Impact

- **Tests:** ~50 new test functions across agent-core (llm_gateway, foundation, cli)
- **CI:** New `.github/workflows/ci.yml` in 3 repos (gitleaks secret scanning)
- **Coupling:** agent-docs-sync non-SDK imports reduced from 4 to 0
- **Harness:** lifecycle_auth docstring corrected to reflect actual wiring
- **Validation:** All repos remain ruff-clean, all tests pass
