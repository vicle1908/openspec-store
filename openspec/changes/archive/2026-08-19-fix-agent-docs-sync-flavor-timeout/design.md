# Design: fix-agent-docs-sync-flavor-timeout

## Context

Two bugs discovered during full pipeline verification. Both fixes are already committed to agent-docs-sync.

## Decisions

### D1: Increase doc_generator timeout to match doc_full_sync
The generate step reads large source files (up to ~1M tokens). The 180s timeout was insufficient for files like agent_profile.py. The doc_full_sync flavor already uses 300s. Bumping doc_generator to 300s aligns the generate step's timeout with the orchestrating flavor.

### D2: Fix DSV path to be portable
Hardcoded absolute path (`~/Developer/agent-docs-sync-fix-json-contract/.venv/bin/docs-sync`) was stale. Changed to `Path(__file__).parents[1] / ".venv" / "bin" / "docs-sync"` which resolves relative to the test file's location.

## Verification

- Full sync completed in 1075s with 0 agent_timeout errors (was 1 with 180s timeout)
- Docs generated: 1 (was 0 before fix)
- All 280 agent-docs-sync tests pass (including 3 previously failing CLI tests)
