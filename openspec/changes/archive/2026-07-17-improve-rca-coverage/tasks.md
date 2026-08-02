## Tasks

### 1. Implement stem-suffix pattern engine

- [x] 1.1 Add `_stem_pattern()` helper in `rca.py`
  - Implement as a regex post-processor operating on pattern strings
  - Handles: verbs ending in consonant+`y` → `ies/ied/ying`; regular verbs `s/es/ed/ing/ize/ized`; bare keywords → `s?` optional plural for nouns
  - Preserve existing patterns that already have suffixes; preserve character classes and quantifiers
  - Test in isolation: `assert _stem_pattern(r"\bhang\b")` contains "hang(?:s|es|ed|ing)?"

- [x] 1.2 Refactor `detect_rca()` to use compiled patterns
  - Move pattern compilation (one-time) out of the per-call loop
  - Apply `_stem_pattern()` to each pattern string before `re.compile()`
  - Ensure `combined_content` (content + code_hints) is still matched

### 2. Pattern catalog updates — rca_patterns.py

- [x] 2.1 Crash / ANR / Force Close
  - Add `\b(stops? responding|not responding|application.*hangs?)\b`
  - Add `\b(frozen)\b` (to Performance, not Crash — see design)

- [x] 2.2 Wrong Data / Incorrect Value
  - Add bare `\bincorrect\b` to existing patterns
  - Add `\b(wrong.*format|format.*wrong)\b`
  - Add `\b(cache not invalidated|cache.*not.*invalidat)\b`

- [x] 2.3 Silent Exit / No Feedback
  - Add `\b(has no effect|no effect|does nothing)\b`
  - Add `\b(does not respond|does nothing|button has no effect)\b`
  - Add `\b(fails? to (validate|save|load|submit|process))\b`
  - Add `\b(form.*not.*work|form.*not.*respond)\b`

- [x] 2.4 Performance / Slow Loading
  - Add `\b(stuck|blocked|frozen|deadlock|deadlocked)\b` (add frozen, deadlock to Performance — Crash already has deadlock as priority 1, but Performance context in a ticket usually means not-an-actual-crash)

- [x] 2.5 Authentication / Authorization
  - Add `\b(sso.*fails?|sso.*redirect|sso.*broken)\b`

- [x] 2.6 UI Layout / Visual Defect
  - Add `\b(cuts? off|cut off|cuts? it off)\b`
  - Add `\b(image.*cuts? off|text.*cuts? off)\b`

- [x] 2.7 Network / API Connectivity
  - Add `\b(fails? to load|cannot load|won't load|image.*not.*load|photo.*not.*load)\b`

- [x] 2.8 Feature Not Working / Missing
  - Add `\b(need to add|add feature|missing implementation|not implemented|missing feature)\b`

- [x] 2.9 General UI/UX Polish
  - Add `\b(confused|wrong language|wrong translation|i18n|localization|localize|locale)\b`

### 3. Test coverage

- [x] 3.1 `TestRcaStemMatching` — parametrized stem tests
  - hang/hangs/hanging/hung → Performance
  - crash/crashes/crashed/crashing → Crash
  - deadlock/deadlocked/deadlocks → Crash
  - freeze/freezes/frozen/freezing → Performance
  - stuck → Performance
  - blocked → Performance

- [x] 3.2 `TestRcaCoverage` — all 19 survey failures as regression tests
  - Each test names the expected category and the issue it fixes
  - All 19 must pass

- [x] 3.3 `TestRcaFalsePositiveGuard`
  - "stuck in traffic" → not Performance
  - "blocked user account" → not Performance
  - "frozen yogurt" → not Performance
  - "format hard drive" → not Wrong Data
  - "Application hangs in the balance" → not Performance (positive context)

- [x] 3.4 `test_survey_precision` — quantitative regression
  - Run the 65-ticket survey and assert precision ≥ 85%

### 4. Verification

- [x] 4.1 Run full test suite: `uv run pytest tests/ -q`
  - All tests pass, no regressions
- [x] 4.2 Run lint: `uv run ruff check src/ tests/`
  - Clean
- [x] 4.3 Run types: `uv run mypy src/ tests/`
  - Clean
- [x] 4.4 Smoke-test: re-run the 65-ticket survey and verify precision ≥ 85%

### 5. Documentation

- [x] 5.1 Update `rca_patterns.py` module docstring to document the stem-suffix wrapper
- [x] 5.2 Commit with message following conventional commits