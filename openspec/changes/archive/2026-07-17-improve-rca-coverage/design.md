# Design — improve-rca-coverage

## 1. Stem-suffix wrapper

The single most impactful fix is a small helper that expands bare keywords to match common inflections. This is **not full morphological analysis** — just the inflections that appear in our failure survey:

```python
def _stem_pattern(keyword: str) -> str:
    """Expand a bare keyword to a regex matching common English inflections.

    Handles:
    - verbs:     run/runs/ran/running, hang/hangs/hanging/hung, freeze/freezes/freezing/frozen
    - verbs -ed: crash/crashed/crashes/crashing, deadlock/deadlocked
    - nouns:     cache/caches, format/formats, error/errors
    - adjectives: stuck, blocked, frozen
    """
    # The "?" suffix on `s` matches both singular and plural for nouns
    # The `(s|es|ed|ing|ize|ized)` chain covers common verb inflections
    ...
```

The implementation will:
- For each `pattern` string in `RCA_PATTERNS`, post-process to expand `\bword\b` → `\bword(?:s|es|ed|ing|ized|ization)?\b` for bare keywords.
- Preserve existing patterns that already include suffixes (e.g., `\b(jank|jitter)\b` is left alone).
- Preserve regex character classes (`[a-z]`) and quantifiers (`*`, `+`, `?`).

This is **safe by construction** because:
- "hang" → "hangs" is desired; "hang" → "hangs the laundry" is *also* desired (Performance).
- "stuck" → "stucks" is grammatically wrong, so the stem wrapper doesn't add an `s` suffix to words that don't take it.
- The wrapper is opt-in: patterns can opt out by using a sentinel like `\brawkeyword\b` (no change) or marking `no_stem=True` in the pattern entry.

**Design choice:** Implement as a regex post-processor that operates on the pattern source string *before* `re.compile()`. This is the simplest approach that requires no schema changes.

## 2. Pattern catalog additions

| Category | New patterns (post-stem) | Example matches |
|----------|--------------------------|-----------------|
| **Crash** | `\b(stops? responding|not responding|application.*hangs?)\b`, `\b(frozen|crash.*on.*start)\b` | "Application stops responding", "App frozen on launch" |
| **Wrong Data** | `\b(incorrect|wrong.*format|format.*wrong)\b`, `\b(cache not invalidated|cache.*not.*invalidat)\b` | "Account balance is incorrect", "Wrong date format", "Cache not invalidated" |
| **Silent Exit** | `\b(has no effect|no effect|does nothing|does not respond)\b`, `\b(fails? to (validate|save|load|submit|process))\b` | "Submit button has no effect", "Form fails to validate" |
| **Performance** | `\b(stuck|blocked|deadlock|deadlocked|freezes?|freezing|frozen)\b` | "App stuck on splash", "Thread blocked", "Spinner frozen" |
| **Auth** | `\b(sso.*fails?|sso.*redirect|sso.*broken)\b` | "SSO fails to redirect" |
| **UI Layout** | `\b(cuts? off|cut off|gets cut)\b` | "Image cuts off at bottom" |
| **Network** | `\b(fails? to load|cannot load|won't load|image not loading|photo not loading|asset not loading)\b` | "Profile photo fails to load" |
| **Feature** | `\b(need to add|add feature|missing implementation|not implemented|missing feature)\b` | "Need to add feature X" |
| **UI/UX** | `\b(confused|wrong language|wrong translation|i18n|localization|localize|locale)\b` | "User confused by error", "Button text is wrong language" |

## 3. Trade-offs and false-positive risk

| Pattern | Risk | Mitigation |
|---------|------|------------|
| `\bstuck\b` (Performance) | "stuck in traffic", "stuck in meeting" | Risk is low for bug ticket content; "stuck" in a ticket almost always refers to UI hang. If FP appears, refine later. |
| `\b(blocked|deadlock)\b` (Performance) | "blocked user" (auth context) | The "deadlock" stem is crash-like; we keep it in Performance. The "blocked" pattern is fine because in bug tickets it usually means request/thread block. |
| `\b(frozen)\b` (Crash + Performance) | "frozen account" (auth) | Only one category gets to claim the keyword. We put `frozen` in Performance (lower priority number wins). |
| `\b(confused|confusing)\b` (UI/UX) | "confused state machine" | Low risk; rare in bug tickets. |
| `\b(wrong language)\b` (UI/UX) | Very specific — almost always i18n issue. | Low risk. |

We accept these false-positive risks in v1 and document them. If precision regresses in production telemetry, we refine in v2.

## 4. Test strategy

- **`TestRcaCoverage`** — all 19 survey failures as regression tests. Each test must pass after the fix.
- **`TestRcaStemMatching`** — parametrized cases verifying stem suffix behavior:
  - `hang`, `hangs`, `hanging`, `hung` → all Performance
  - `crash`, `crashes`, `crashed`, `crashing` → all Crash
  - `deadlock`, `deadlocks`, `deadlocked`, `deadlocking` → all Crash (or Performance, depending on category assignment)
  - `freeze`, `freezes`, `frozen`, `freezing` → all Performance
- **`TestRcaFalsePositiveGuard`** — explicit FP guards:
  - `"stuck in traffic"` → `None` or "General UI/UX Polish" (low priority)
  - `"blocked user account"` → Authentication (not Performance)
  - `"frozen yogurt shop"` → `None`
  - `"format hard drive"` → `None`
- **Survey replay** — rerun the 65-ticket survey and assert precision ≥ 85%.

## 5. Spec delta

Add a new requirement to `rca-taxonomy-v2/spec.md`:

```markdown
### Requirement: Stem-suffix pattern expansion
RCA patterns SHALL match common English inflections of bare keywords.

#### Scenario: Verb stem "hang" matches all inflections
- **WHEN** `detect_rca()` is called with `"App hangs on splash"`, `"App hang on splash"`, or `"App hanging on splash"`
- **THEN** it SHALL return category "Performance / Slow Loading" for all three inputs

#### Scenario: Past tense "deadlocked" matches stem "deadlock"
- **WHEN** `detect_rca()` is called with `"App is deadlocked"`
- **THEN** it SHALL return category "Crash / ANR / Force Close"
```

## 6. Backwards compatibility

The pattern engine change is **internal** — `detect_rca()`'s public signature and the `RootCauseSignal` schema are unchanged. Existing tests continue to pass; new tests are additive.

The only consumer-visible change is: tickets that previously returned `None` may now return a category. This is the *intended* improvement (false-negative reduction).
