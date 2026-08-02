## Why

The RCA (Root Cause Analysis) detection logic in `jira-ticket-intelligence`, after the `fix-rca-fix-status-detection` change, achieves ~70% precision on a 60-ticket real-world sample survey. The 19 false negatives cluster into 4 systematic gaps that are best addressed at the *pattern engine* level rather than via ad-hoc pattern additions.

Survey methodology: 65 ticket descriptions representative of common iOS/Android mobile app bug reports were classified by `detect_rca()`. Of 63 clear-intent cases:
- **44 correct** (69.8% precision)
- **19 false negatives** (30.2% miss rate)
- **2 ambiguous** (excluded from precision)

The false negatives break down as:

| Group | Count | Examples |
|-------|-------|----------|
| **A. Stem/inflection gaps** (word boundary failures) | 6 | "App is deadlocked" (deadlock vs deadlocked), "App hangs on splash" (hang vs hangs), "Frame drops" (drop vs drops), "App stuck", "Thread blocked" |
| **B. Missing bare keywords** | 3 | "Application stops responding" (responding/stops responding), "SSO fails" (sso.*fail needs plural), "Wrong date format" (format) |
| **C. Compositional phrases** | 5 | "Account balance is incorrect" (incorrect not incorrect.*value), "Cache not invalidated" (not invalidated), "Profile photo fails to load" (fails to load not fail), "Login form does not validate" (form issue), "Submit button has no effect" |
| **D. Taxonomy/word gaps** | 4 | "Need to add feature X", "User confused by error message" (confused not confusing), "Button text is wrong language", "Image cuts off at bottom" (cuts off with space) |

The pattern **Group A** issues (6 of 19 failures, ~32%) are a single bug class: `\bkeyword\b` regexes fail to match inflected forms. A pattern like `\bhang\b` won't match "hangs" or "hanging" because the trailing letter breaks the word boundary. Patching individual patterns is brittle and won't scale as new patterns are added.

The pattern **Group B** and **C** issues are real gaps — bare keywords that just aren't in the taxonomy yet.

## What Changes

**Pattern engine — stem-aware matching (Addresses Group A):**
- Introduce a small **stem-suffix wrapper** that automatically expands bare keywords to match their common inflections (`s`, `es`, `ed`, `ing`, `ize`, `ized`, `ize` for verbs; `ation`, `ed`, `s` for nouns).
- Apply this wrapper uniformly to the existing `RCA_PATTERNS` entries so all current patterns benefit.
- Document the wrapper's contract in `rca_patterns.py`.

**Pattern catalog — new keywords and phrases (Addresses Groups B, C, D):**
- **Crash / ANR / Force Close**: add `stops responding`, `stops.*responding`, `not responding`, `frozen` (where `frozen` ≠ `freeze`).
- **Wrong Data / Incorrect Value**: add bare `incorrect`, `wrong.*format`, `format.*wrong`, `cache not invalidated`, `cache.*not.*invalidat`.
- **Silent Exit / No Feedback**: add `has no effect`, `no effect`, `fails to (validate|save|load|submit|process)`, `does not (validate|save|load|submit|process)`, `form.*not.*work`.
- **Performance / Slow Loading**: add `stuck`, `blocked`, `frozen`, `deadlock` (as a non-crash performance issue).
- **Authentication / Authorization**: add plural-inflected `sso.*fails?`, `sso.*redirect`.
- **UI Layout / Visual Defect**: add `cuts off` (with space), `cut off`, multi-word `image cuts off`, `text cuts off`.
- **Network / API Connectivity**: add `fails? to load`, `load.*fail`, `cannot load`, `image.*not.*loading`, `photo.*not.*loading`.
- **Feature Not Working / Missing**: add `need to add`, `add feature`, `not implemented`, `missing implementation`.
- **General UI/UX Polish — no specific pattern matched**: add `confused` (variant of confusing), `language` (i18n issue), `wrong language`, `wrong translation`, `i18n`, `localization`.

**Testing:**
- Add a `TestRcaCoverage` class to `tests/analysis/test_rca.py` with all 19 false-negative cases as regression tests, expected to PASS after the fix.
- Add a `TestRcaStemMatching` class with parametrized stem cases (e.g., `hang`, `hangs`, `hanging`, `hung` should all match Performance).
- Add a `TestRcaFalsePositiveGuard` class to ensure the new patterns don't introduce false positives (e.g., "stuck in traffic" should NOT match Performance; "blocked user" should NOT match Performance; "image of an ice cream cuts off nicely" should match UI Layout but not "cut off" if it's a positive context — note: this is a known limitation we'll accept for v1).

**Documentation:**
- Update the spec to document the stem-suffix wrapper.
- Update `docs/bundle-contract.md` if RCA output schema changes (it shouldn't — output is unchanged).

## Capabilities

### New Capabilities

- `rca-coverage-v2`: Expands the RCA pattern catalog and introduces stem-aware pattern matching to improve precision from ~70% to ≥85% on the survey set.

### Modified Capabilities

- None — this is purely additive to the existing `rca-taxonomy-v2` capability. The taxonomy catalog gains new patterns and a new wrapper, but the public contract (9 categories, `RootCauseSignal` output schema) is unchanged.

## Impact

**Owning repo:** `jira-skill`

**Affected files:**
- `src/jira_skill/analysis/extractors/rca_patterns.py` — pattern catalog (add new patterns, add stem-suffix wrapper)
- `src/jira_skill/analysis/rca.py` — `detect_rca()` engine to use the stem wrapper when compiling patterns
- `tests/analysis/test_rca.py` — add `TestRcaCoverage`, `TestRcaStemMatching`, `TestRcaFalsePositiveGuard`

**Spec deltas:** Add `## ADDED Requirements` to `rca-taxonomy-v2/spec.md` (or create a sibling spec if the existing one is full).

**Out of scope:**
- Multilingual support (English-only patterns for v1).
- Context-aware disambiguation (e.g., "stuck in traffic" vs "app stuck on splash"). The v1 fix is pattern-level; context-level disambiguation is a future ML/NLP improvement.
- Adding new RCA categories. All 9 existing categories remain.
