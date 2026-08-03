## 1. Agent-Core Focused Coverage and Missing Tests

- [x] 1.1 Add meaningful `llm_gateway` tests until `uv run pytest tests/llm_gateway/ --cov=src/agent_core/llm_gateway --cov-fail-under=80 --cov-report=term-missing` exits 0.
- [x] 1.2 Add foundation tests for optional migrations, tracing, and real workspace-resolution edge cases until `uv run pytest tests/foundation/ --cov=src/agent_core/foundation --cov-fail-under=80 --cov-report=term-missing` exits 0.
- [x] 1.3 Add CLI malformed-argument, review/propose JSON-output, eval/utils, and failure-path tests until `uv run pytest tests/cli/ --cov=src/agent_core/cli --cov-fail-under=80 --cov-report=term-missing` exits 0.
- [x] 1.4 Run `uv run ruff check src/ tests/`, `uv run mypy src/agent_core/ --strict`, and the agent-core full unit suite; capture exact results.
- [x] 1.5 Regenerate agent-core README/SPEC_INDEX test counts, test LOC ratios, and coverage prose from measured output.

## 2. Agent-Docs-Sync Boundary and Scanner Verification

- [x] 2.1 Fix `tests/test_sdk_import_boundary.py` Ruff errors.
- [x] 2.2 Extend the AST checker to reject bare and aliased internal `agent_core` imports and add negative regression fixtures for both `ast.Import` and `ast.ImportFrom`.
- [x] 2.3 Correct the archived verification-path drift by documenting/running `uv run pytest tests/test_sdk_import_boundary.py -v`.
- [x] 2.4 Make the gitleaks artifact test prerequisite-aware and ensure it never reads a missing report after scanner startup failure; preserve CI enforcement.
- [x] 2.5 Run `uv run ruff check src/ tests/`, `uv run mypy src/agent_docs_sync/ --strict`, and the full docs-sync suite; capture exact results.
- [x] 2.6 Regenerate docs-sync README/SPEC_INDEX metrics from measured output.

## 3. Agent-Harness Prerequisite Verification

- [x] 3.1 Make the gitleaks artifact test prerequisite-aware and avoid secondary missing-report failures.
- [x] 3.2 Make PostgreSQL integration tests explicitly declare/skip unavailable infrastructure while preserving execution when configured.
- [x] 3.3 Run `uv run ruff check src/ tests/`, `uv run mypy src/agent_harness/ --strict`, and the full harness suite; capture passes/skips.
- [x] 3.4 Regenerate harness README/SPEC_INDEX metrics from measured output.

## 4. Cross-Repository Integration

- [x] 4.1 Review all diffs for scope, test quality, and no public runtime API changes.
- [x] 4.2 Run actionlint on all three gitleaks workflows.
- [x] 4.3 Run full-history gitleaks with the pinned version when Docker/gitleaks is available; otherwise record the blocked prerequisite and do not claim a pass.
- [x] 4.4 Run `openspec validate close-agent-ecosystem-hardening-verification-gaps --strict` and `openspec validate --strict --all`.
- [x] 4.5 Commit each repository and the store with descriptive messages.
- [x] 4.6 Archive the corrective change only after every available gate passes and blocked external prerequisites are explicitly documented.
