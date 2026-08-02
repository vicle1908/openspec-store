# Proposal: Fix `_extract_message` Truncation Causing Aggregate/Dedicated Parity Gap

## Why

MR !23873 revealed that the aggregate `<!-- mr-auto-review -->` note shows "Findings: 3" while the dedicated `<!-- code-scan-review -->` note shows "Code scan found 17 issue(s)". Both notes are published by the same pipeline, but the orchestrator's `_extract_message()` silently truncates code-scan output before parsing findings.

Root cause: `_extract_message()` was designed for verbose LLM reviewer output and applies two aggressive truncation limits:
1. `lines[:6]` — Only keeps the first 6 lines. Code-scan output has ~19 lines (header + 17 findings).
2. `len(joined) > 800` — Truncates at 800 characters. 17 findings ≈ 2,500 characters.

This violates the archived `mr-code-scan-integrity-gap-closure` spec requirement: "the aggregate summary SHALL publish the same contributing count."

## What Changes

1. Detect code-scan output by its `Code scan found` prefix.
2. For code-scan output, skip the `lines[:6]` limit and the 800-character truncation.
3. Preserve the existing truncation behavior for LLM reviewer output (which can be very verbose).
4. Add a spec delta requiring `_extract_message` to preserve all lines from structured (non-LLM) reviewer output.

## Capabilities

### Modified Capabilities

- `mr-review-orchestration`: `_extract_message` preserves all code-scan output lines without truncation.

## Impact

- `ai-review/src/ai_review/review_flow/orchestrator.py`: modify `_extract_message` to detect code-scan output and skip truncation.
- No external dependencies, no API changes.
- Test: verify aggregate and dedicated notes show identical finding counts on a multi-finding MR.

## Non-Goals

- Changing the truncation behavior for LLM reviewer output (which may contain reasoning/thinking text).
- Changing the `MARKDOWN_PATTERN` parser or the `CodeScanReviewer` output format.
