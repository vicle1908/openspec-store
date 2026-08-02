# Tasks: Fix `_extract_message` Truncation

## 1. Implement fix

- [x] 1.1 Modify `_extract_message()` in `orchestrator.py` to detect code-scan output by `"Code scan found"` prefix
- [x] 1.2 Skip `lines[:6]` and 800-char truncation for code-scan output
- [x] 1.3 Preserve existing truncation for LLM output

## 2. Tests

- [x] 2.1 Add unit test: code-scan output with 17 findings preserves all lines
- [x] 2.2 Add unit test: LLM output still truncated to 6 lines / 800 chars
- [x] 2.3 Add unit test: empty output returns None
- [x] 2.4 Run full test suite

## 3. Validation

- [x] 3.1 Run `ruff check`, `ruff format --check`, `mypy --strict`
- [x] 3.2 Run `openspec validate --strict ai-review-extraction-truncation-fix`
- [x] 3.3 Deploy and re-trigger MR !23873 to verify parity
- [x] 3.4 Verify aggregate note shows same count as dedicated note

## 4. Archive

- [x] 4.1 Commit changes
- [x] 4.2 Archive change
