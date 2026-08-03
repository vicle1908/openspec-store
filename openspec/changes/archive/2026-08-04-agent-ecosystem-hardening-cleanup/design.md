## Approach

All fixes are documentation/lock-file updates plus one small test. No
behavioral changes. Execute in order: docs first, then lock file, then test.

## Findings Addressed

1. **SPEC_INDEX stale counts** — agent-core shows 639 (actual 630), exclusion
   notes reference secret_scan which now passes. Update to actual counts.
2. **README stale counts** — agent-core: 608→630, docs-sync: 210→215,
   harness: 323→327. Ecosystem total: 1,141→1,172.
3. **uv.lock stale** — pyproject.toml changed Aug 3, lock last changed Jul 27.
   Run `uv lock` to refresh.
4. **AST import boundary test** — Task 6.3 from hardening was not implemented.
   Add AST-based check that all `from agent_core.*` imports in docs-sync use
   only `agent_core.sdk`.
