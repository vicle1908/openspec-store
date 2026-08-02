## Why

agent-docs-sync has 4 bugs discovered during feature verification: 2 test failures from an API signature mismatch, 1 runtime crash in the sync pipeline's validate step (currently masked), and 1 debug-log-spam issue that floods stdout with ~420K characters when running with `-v`. These block reliable CI and make the CLI unusable in verbose mode.

## What Changes

- **Fix test API mismatch**: `tests/test_tools/test_check_links.py` passes kwargs to `execute()` but the method now requires a pydantic args model (`CheckLinksArgs`). Both test functions fail.
- **Fix pipeline kwargs bug**: `sync_pipeline.py:validate()` calls `enforcer.execute(doc_path=..., quadrant=...)` with kwargs instead of wrapping in `EnforcerArgs`. This crashes at runtime when there are pending updates — currently masked because `check` usually has no affected docs.
- **Fix debug log spam**: `configure_logging(level="DEBUG")` sets the root logger to DEBUG, capturing all library internals (markdown-it emits token-level debug for every parsed file). Scope logging to `agent_docs_sync` only, or suppress noisy third-party loggers.
- **Relax Diátaxis reference rules**: The `reference` quadrant enforcement requires `signature`, `description`, `examples` sections with a 300-word limit. Most existing docs are narrative/API-reference hybrids that naturally violate these rules. Adjust thresholds or reclassify.

## Capabilities

### New Capabilities

_(none — all fixes are to existing behavior)_

### Modified Capabilities

- `agent-docs-sync`: Tool API contract — all `BaseTool.execute()` methods accept a single pydantic args model, not kwargs. Tests and pipeline code must match this contract.

## Impact

- **Files changed**:
  - `agent-docs-sync/tests/test_tools/test_check_links.py` — fix test calls
  - `agent-docs-sync/src/agent_docs_sync/workflows/sync_pipeline.py` — fix validate step
  - `agent-docs-sync/src/agent_docs_sync/cli.py` — scope debug logging
  - `agent-docs-sync/src/agent_docs_sync/tools/enforcer.py` — relax reference rules (optional)
- **Dependencies**: None added or removed
- **Breaking changes**: None — all changes are internal bug fixes
- **Risk**: LOW — surgical fixes to test calls, one pipeline line, and logging config
