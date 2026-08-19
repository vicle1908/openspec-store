## Why

Two agent-docs-sync bugs were discovered during full pipeline verification:

1. **doc_generator timeout too low**: The `doc_generator` flavor had `timeout_seconds=180`, but the generate step reads large source files that take >180 seconds (one run consumed 1M prompt tokens). This caused `agent_timeout` failures, preventing documentation generation.

2. **CLI JSON output tests reference wrong path**: `test_cli_json_output.py` hardcoded `DSV` to a non-existent path (`~/Developer/agent-docs-sync-fix-json-contract/.venv/bin/docs-sync`), causing 3 pre-existing test failures.

Additionally, the pydantic-ai version baseline in `test_dependency_baseline.py` was stale (2.18.0 vs actual 2.31.0).

## What Changes

- `flavors.py`: `doc_generator` flavor `timeout_seconds` from 180.0 to 300.0 (matching `doc_full_sync`)
- `test_cli_json_output.py`: DSV path updated to use `Path(__file__).parents[1] / ".venv" / "bin" / "docs-sync"` (relative to current repo)
- `test_dependency_baseline.py`: pydantic-ai version 2.18.0 → 2.31.0

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-docs-sync-tdt-runtime`: Document that `doc_generator` flavor uses `timeout_seconds=300` (was 180)

## Impact

- **Code**: `agent_docs_sync/flavors.py` (1 line), tests (2 files, 2 lines)
- **Specs**: 1 modified capability
- **Tests**: All 280 agent-docs-sync tests pass (including 3 previously failing CLI tests)
- **Behavior**: Generate step can now read large source files without timing out; first successful doc generation confirmed
