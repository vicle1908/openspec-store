## 1. Update SPEC_INDEX Files

- [ ] 1.1 agent-core: update test count to 630, remove "excludes secret_scan" note
- [ ] 1.2 agent-docs-sync: update test count to 215, remove "excludes secret_scan" note
- [ ] 1.3 agent-harness: update test count to 327, remove "excludes secret_scan" note

## 2. Update README Status Sections

- [ ] 2.1 agent-core: update "608 tests" to "630 tests", ecosystem total to 1,172
- [ ] 2.2 agent-docs-sync: update "210 tests" to "215 tests"
- [ ] 2.3 agent-harness: update "323 tests" to "327 tests"

## 3. Refresh uv.lock

- [ ] 3.1 Run `uv lock` in agent-docs-sync to refresh lock file

## 4. Add AST Import Boundary Test

- [ ] 4.1 Add `tests/test_sdk_import_boundary.py` to agent-docs-sync with AST-based check
- [ ] 4.2 Verify test passes: `uv run pytest tests/test_sdk_import_boundary.py`

## 5. Final Validation

- [ ] 5.1 Run full test suite in all 3 repos — all pass
- [ ] 5.2 Run ruff in all 3 repos — clean
- [ ] 5.3 Run `openspec validate --strict --all` — pass
- [ ] 5.4 Commit all changes
