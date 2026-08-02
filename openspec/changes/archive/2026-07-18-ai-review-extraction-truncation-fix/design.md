# Design: Fix `_extract_message` Truncation

## Context

`_extract_message()` in `orchestrator.py` is called by `_run_reviewer_once()` to extract the reviewer's output before the orchestrator parses findings from it. The method was designed for LLM reviewers (Claude, GPT) whose output can be verbose with thinking blocks, JSON events, and conversational text.

Code-scan reviewers (`CodeScanReviewer`) produce structured, concise output: a header line ("Code scan found N issue(s):") followed by finding lines ("- [severity] file:line - [RULE] message"). This output is already filtered by the hunk gate and should be preserved in full.

## Decision

### D-1. Detect code-scan output by prefix

`_extract_message()` SHALL check if the output starts with `"Code scan found"` (case-insensitive, after stripping). Code-scan output is identified by this prefix because `CodeScanReviewer._format_findings()` always emits it as the first line.

### D-2. Skip truncation for code-scan output

When code-scan output is detected, `_extract_message()` SHALL:
- NOT apply the `lines[:6]` limit
- NOT apply the 800-character truncation
- Return the full joined output

This ensures the finding parser receives all finding lines and the aggregate note shows the same count as the dedicated note.

### D-3. Preserve LLM truncation behavior

For non-code-scan output (LLM reviewers), the existing `lines[:6]` and 800-character limits remain unchanged. LLM output can be very verbose and the truncation is intentional to keep the aggregate note concise.

## Risks

- **Risk**: Code-scan output with hundreds of findings could produce a very large aggregate note. **Mitigation**: The scanner already limits findings via rule post-filters and hunk gate; typical MRs produce <50 findings. The aggregate note is a GitLab comment, which supports long content.
- **Risk**: The `"Code scan found"` prefix check could match LLM output that happens to contain this phrase. **Mitigation**: The prefix check is on the first non-empty line, and LLM output rarely starts with this exact phrase.
