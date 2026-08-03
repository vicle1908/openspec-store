## Why

The archived `agent-ecosystem-hardening` and follow-up cleanup changes merged the intended specifications and implemented most code, but post-archive verification found checked tasks whose exact acceptance commands still fail. The focused agent-core coverage gates are below 80%, the docs-sync AST boundary test misses bare/aliased imports and fails Ruff, environment-dependent gitleaks/PostgreSQL checks do not report missing prerequisites cleanly, and README/SPEC_INDEX metrics drift from measured state.

This implementation-only change closes those verification gaps without changing the already-merged normative requirements.

## What Changes

- Bring the exact focused `llm_gateway`, `foundation`, and `cli` coverage commands to at least 80%.
- Add the missing CLI malformed-argument and JSON-output regression cases and genuine workspace-resolution edge tests.
- Correct the docs-sync SDK boundary test so it checks both `ast.Import` and `ast.ImportFrom`, rejects every non-`agent_core.sdk` import, includes regression fixtures, and passes Ruff.
- Make scanner/PostgreSQL-dependent tests prerequisite-aware and produce explicit skip/error evidence instead of secondary missing-file failures.
- Re-run full suites with prerequisites when available and record any unavailable integration layer honestly.
- Regenerate README and SPEC_INDEX metrics from measured test/LOC/coverage output.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. The merged specs are already correct; this change only completes implementation and verification.

## Compatibility

All changes are tests, validation behavior, and documentation metrics. Public runtime APIs remain unchanged. Test prerequisite handling must not weaken hosted CI secret scanning or PostgreSQL integration coverage.

## Rollout

1. Fix and verify agent-core focused tests and coverage.
2. Fix and verify docs-sync boundary/scanner tests and metrics.
3. Fix and verify harness prerequisite handling and metrics.
4. Run repo-wide Ruff, strict mypy, tests, and OpenSpec validation.
5. Integrate commits and archive only after all available gates pass.

## Rollback

Revert consumer test/documentation commits first, then provider test commits. Do not revert merged SDK exports or specification requirements. If prerequisite handling suppresses a real CI failure, revert that handling immediately while preserving the underlying scanner/PostgreSQL test coverage.
