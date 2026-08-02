## 1. Fix Test API Mismatch

- [x] 1.1 Update `tests/test_tools/test_check_links.py` — import `CheckLinksArgs` and wrap kwargs in both test functions
- [x] 1.2 Run `uv run pytest tests/test_tools/test_check_links.py -v` — both tests must pass

## 2. Fix Pipeline Validate Step

- [x] 2.1 Update `src/agent_docs_sync/workflows/sync_pipeline.py` `validate()` function — import `EnforcerArgs` and wrap kwargs at line 166
- [x] 2.2 Run `uv run docs-sync check` — verify no crash (pipeline exercises the validate path)

## 3. Fix Debug Log Spam

- [x] 3.1 Update `src/agent_docs_sync/cli.py` `main()` callback — after `configure_logging()`, reset root logger to WARNING, set `agent_docs_sync` to DEBUG, suppress `markdown_it` and `httpx` loggers
- [x] 3.2 Run `uv run docs-sync -v validate` — verify output is clean (no `entering fence:` / `StateBlock` spam)
- [x] 3.3 Run `uv run docs-sync validate` (no `-v`) — verify normal output unchanged

## 4. Relax Diátaxis Reference Rules

- [x] 4.1 Update `src/agent_docs_sync/tools/enforcer.py` — increase reference `max_words` from 300 to 500, increase tier-2 `max_words_multiplier` from 1.5 to 2.0, remove `signature` and `examples` from reference `required_sections` (keep as `must_have` info suggestions only)
- [x] 4.2 Run `uv run docs-sync audit --output json` — verify reduced violations (target: 0-2 violations instead of 7)

## 5. Full Verification

- [x] 5.1 Run `uv run pytest tests/ -x -v` — 125 passed, 3 skipped, 0 failures
- [x] 5.2 Run `uv run ruff check src/ tests/` — pre-existing lint issues only (none from changes)
- [x] 5.3 Run `uv run mypy src/agent_docs_sync/ --strict` — pre-existing type issues only (none from changes)
