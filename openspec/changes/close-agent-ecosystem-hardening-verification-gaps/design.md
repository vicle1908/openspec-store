## Context

Post-archive audit executed the exact commands recorded in the original tasks and found:

- `llm_gateway` focused coverage: 77.62% (<80%).
- `foundation` focused coverage: 72.30% (<80%).
- `cli` focused coverage: 77.62% (<80%).
- `tests/test_sdk_import_boundary.py` passes pytest but fails Ruff (`F541`) and ignores `ast.Import`.
- docs-sync/harness scanner tests can fail with a secondary missing-report error when no scanner backend is available.
- harness PostgreSQL integration tests error when required infrastructure is absent.
- README/SPEC_INDEX metrics contain stale counts and ratios.

## Design Decisions

### 1. Preserve the existing 80% gates

The corrective implementation SHALL make the exact archived commands pass. It SHALL NOT weaken `--cov-fail-under=80` or replace focused coverage with a broader suite that hides module gaps.

### 2. Exercise reachable behavior

Coverage additions must target meaningful uncovered behavior: Bifrost/Resilient gateway paths, migration optional modules and tracing paths, CLI eval/utils/error/JSON paths, and workspace resolution edge cases. Avoid filler assertions or line-count padding.

### 3. Enforce the SDK boundary generically

The boundary checker will inspect both `ast.Import` and `ast.ImportFrom`. Any import rooted at `agent_core` is invalid unless it is exactly `agent_core.sdk` or a permitted SDK submodule. Regression fixtures will prove bare and aliased internal imports are rejected.

### 4. Report unavailable prerequisites truthfully

Scanner and PostgreSQL tests will distinguish an unavailable external prerequisite from a failed behavior assertion. Local suites may skip explicitly with a clear reason when the prerequisite is absent; hosted CI/integration jobs must still install/start the prerequisite and execute the tests. Tests must not continue to read reports/resources after prerequisite execution failed.

### 5. Generate documentation metrics from commands

Test counts, module LOC ratios, and coverage values will be measured after code changes. README and SPEC_INDEX values must match the captured output exactly. No manual estimate may be recorded as a completed metric.

## Verification

- Focused coverage commands exit 0 at >=80%.
- SDK boundary positive and negative regression tests pass and Ruff is clean.
- Full source/tests Ruff and strict mypy pass in all affected repos.
- Full unit suites pass; infrastructure suites either pass with prerequisites or report explicit skips documented in evidence.
- `openspec validate --strict --all` passes.
