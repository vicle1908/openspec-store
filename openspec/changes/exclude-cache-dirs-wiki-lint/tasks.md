# Tasks

## 1. Scanner and Gitignore Updates in Developer/wiki

- [x] 1.1 Add `.pytest_cache/` and Python test cache entries to `/Users/androidteam/Developer/wiki/.gitignore`. Verify with `git -C /Users/androidteam/Developer/wiki check-ignore .pytest_cache/README.md`.
- [ ] 1.2 Update `EXCLUDED_DIRS` and directory traversal in `_scan_pages()` within `/Users/androidteam/Developer/wiki/scripts/wiki-lint.py` to skip dot-directories (`d.startswith('.')`) and `.pytest_cache`. Verify with `python3 /Users/androidteam/Developer/wiki/scripts/wiki-lint.py` showing no findings for `.pytest_cache/README.md`.

## 2. Unit Testing and Regression Verification

- [ ] 2.1 Add unit test in `/Users/androidteam/Developer/wiki/tests/test_wiki_lint.py` verifying that Markdown files located inside `.pytest_cache/` or dot-directories are excluded from page scanning. Verify test passes via `python3 -m unittest /Users/androidteam/Developer/wiki/tests/test_wiki_lint.py`.
- [ ] 2.2 Run full wiki lint suite `python3 -m unittest discover -s /Users/androidteam/Developer/wiki/tests` and confirm all tests pass cleanly.
