## Verification Evidence

Date: 2026-08-04

### Agent-core (`834d91e`)

- `uv run ruff check src/ tests/` — passed.
- `uv run mypy src/agent_core/ --strict` — passed, 98 source files.
- Exact focused coverage commands were run serially after `uv run coverage erase`:
  - `tests/llm_gateway/` — passed, 89% displayed coverage.
  - `tests/foundation/` — passed, 85.92% coverage.
  - `tests/cli/` — passed, 87.22% coverage.
- `uv run pytest tests/ -q` — exit 0; 687 collected, 667 passed, 20 explicit prerequisite skips.
- Added clean-worktree Docker development assets/policy required by existing tests.
- Local missing scanner skips explicitly; `CI=1` missing scanner fails closed.

### Agent-docs-sync (`f30c146`)

- `uv run ruff check src/ tests/` — passed.
- `uv run mypy src/agent_docs_sync/ --strict` — passed, 48 source files.
- `uv run pytest tests/ -q` — 219 passed, 1 explicit scanner-prerequisite skip, 4 deprecation warnings.
- SDK boundary test now checks `ast.Import` and `ast.ImportFrom`, rejects every non-`agent_core.sdk` import, and includes bare/aliased regression fixtures.
- `uv run pytest tests/test_sdk_import_boundary.py -v` — passed (5 cases).
- Local missing scanner skips explicitly; CI missing/report failure remains fail-closed.

### Agent-harness (`5f274ea`)

- `uv run ruff check src/ tests/` — passed.
- `uv run mypy src/agent_harness/ --strict` — passed, 52 source files.
- `uv run pytest tests/ -q` — 321 passed, 6 explicit prerequisite skips (1 scanner, 5 PostgreSQL integration).
- PostgreSQL integration still executes when `TDT_POSTGRES_TEST_URL` or operational Docker is available.
- Local missing scanner skips explicitly; `CI=1` missing scanner fails closed.

### Cross-repository

- `actionlint .github/workflows/ci.yml` — passed in all three repositories.
- `git diff main...HEAD --check` — passed in all three implementation worktrees.
- All implementation worktrees and main checkouts were clean after commits/fast-forward integration.
- Full-history gitleaks scan was **blocked, not passed**: host `gitleaks` is absent and `docker info` exits 1 because no daemon is available. CI workflows remain pinned to gitleaks v8.30.1, full-history checkout, redaction, and fail-closed execution.
- `openspec validate close-agent-ecosystem-hardening-verification-gaps --strict` — passed before implementation.
- Final change/all-store validation is required immediately before archive.
