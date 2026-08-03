## 1. Update SPEC_INDEX Files

- [x] 1.1 agent-core: update test count to 630, remove "excludes secret_scan" note
- [x] 1.2 agent-docs-sync: update test count to 216, remove "excludes secret_scan" note
- [x] 1.3 agent-harness: update test count to 327, remove "excludes secret_scan" note

## 2. Update README Status Sections

- [x] 2.1 agent-core: update "608 tests" to "630 tests", ecosystem total to 1,172
- [x] 2.2 agent-docs-sync: update "210 tests" to "216 tests"
- [x] 2.3 agent-harness: update "323 tests" to "327 tests"

## 3. Refresh uv.lock

- [x] 3.1 Run `uv lock` in agent-docs-sync — "Resolved 217 packages in 33ms"

## 4. Add AST Import Boundary Test

- [x] 4.1 Add `tests/test_sdk_import_boundary.py` to agent-docs-sync
- [x] 4.2 Verify test passes: 1 passed in 0.07s

## 5. Final Validation

- [x] 5.1 agent-core: 630 passed, agent-docs-sync: 216 passed, agent-harness: 327 passed
- [x] 5.2 ruff clean in all 3 repos
- [x] 5.3 openspec validate: 351/351 pass
- [x] 5.4 Committed: agent-core `9b0f56e`, docs-sync `24aa305`, harness `cc0a027`, store `d2b1209`
