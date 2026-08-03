## Why

The agent-ecosystem-hardening change was implemented and archived but left
several bookkeeping gaps: stale test counts in SPEC_INDEX and README files,
a stale uv.lock, a missing AST import boundary test, and unverified mypy.
This change addresses those gaps to maintain a correct baseline.

## What Changes

- Update SPEC_INDEX.md test counts in all 3 repos (630/215/327)
- Update SPEC_INDEX.md to remove stale "excludes secret_scan" notes (tests now pass)
- Update README Status sections with current test counts
- Refresh uv.lock in agent-docs-sync after dependency floor bump
- Add AST-based SDK import boundary test to agent-docs-sync

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None.

## Impact

- **Docs:** SPEC_INDEX.md and README.md updated in 3 repos
- **Lock file:** uv.lock refreshed in agent-docs-sync
- **Tests:** 1 new test in agent-docs-sync (AST import boundary)
- **Validation:** 351/351 store validation remains green
