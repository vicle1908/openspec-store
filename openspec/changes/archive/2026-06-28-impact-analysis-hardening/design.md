# Impact Analysis Hardening — Technical Design

## Context

The impact-analysis pipeline (`jira-skill/src/jira_skill/impact/` + `webhook-receiver/src/webhook_receiver/impact.py`)
runs every time a GitLab MR webhook fires (`open`/`reopen`/`merge`) and produces
a structured `ImpactReport` that is posted to both Jira (merge-only) and GitLab
(open/reopen/merge). The pipeline was implemented and shipped but has not been
exercised against a high-fidelity MR with full symbol-level blast-radius data.

A live evaluation against MR 23433 (`pspl/poems-mobile3-android`, commit 75c6cf0,
17 changed files, 3 features) surfaced four bugs. Three are correctness gaps that
mislead operators; one is an observability gap.

## Goals / Non-Goals

**Goals:**
- Fix the `coverage_gaps` case-sensitive substring bug (false positive)
- Surface real `duration_ms` in the GitLab note (already implemented in this session)
- Eliminate the path-as-symbol fallback noise
- Extend `_SYMBOL_REGEX` to cover Kotlin/Swift declaration keywords

**Non-Goals:**
- Changing the pipeline architecture or data model
- Refactoring GitNexus invocation or caching
- Changing the staleness threshold (20%)
- Adding new pipeline stages

## Decisions

### D1: Case-insensitive substring check for `coverage_gaps`

**Decision:** Replace the case-sensitive `module in tf.file_path` check in
`coverage_analyzer.py:309` with `module.lower() in tf.file_path.lower()`.

**Alternatives considered:**
- Normalize module names to lowercase at insertion time: requires touching
  `at_risk_modules` building sites (`coverage_analyzer.py:286-287` and 246-247)
- Use a fuzzy matching library: overkill for two strings

**Rationale:** Case-insensitive comparison at the comparison site is the
smallest change with the least blast radius. It does not change the data
model — `at_risk_modules` still contains mixed-case strings like
`feature.common` and `Corporateaction` — only the comparison is normalized.

### D2: Drop path-as-symbol fallback

**Decision:** `extract_symbols_from_diff` returns `[]` instead of `[filename]`
when neither regex nor hunk-context yields symbols. The function signature,
caller behavior, and `AnalysisResult` are unchanged.

**Alternatives considered:**
- Keep the fallback but add a flag `used_path_fallback: bool` to `FileAnalysis`:
  surfaces the behavior but doesn't fix it; operators still see noise
- Skip GitNexus entirely for files with no symbols: changes the pipeline
  architecture; out of scope

**Rationale:** The fallback was added when GitNexus used `--include-tests` and
needed a symbol-shaped input for every file. The current `--summary-only` mode
returns `affected_modules` from the indexed graph, not from the input symbol.
Empty input now produces a cleaner `not_found` result that the staleness
threshold already handles. The cache layer (10-min TTL) ensures the no-op is
cheap on re-runs.

### D3: Extend `_SYMBOL_REGEX` to cover Kotlin/Swift

**Decision:** Add `fun `, `internal fun`, `protected fun`, `object ` (Kotlin)
and `extension `, `protocol ` (Swift) to the regex alternation.

**Alternatives considered:**
- Add a separate per-language AST parser for Kotlin/Swift: high effort, requires
  tree-sitter or jvm tooling in the Python path
- Rely solely on `_HUNK_CONTEXT_PATTERN` and skip `_SYMBOL_REGEX` for
  `.kt`/`.swift` files: loses precision for files without hunk context

**Rationale:** A regex extension costs ~10 lines and zero new dependencies.
The hunk-context pattern already covers these keywords — the fix is to keep
the two patterns aligned so the line-level regex can independently catch
declarations when `diff -p` is unavailable (e.g., plain `git diff` without
function-context).

### D4: `duration_ms` capture (already implemented)

**Decision:** Wrap `analyze_diff(...)` in `t0 = time.monotonic()` and pass
`int((time.monotonic() - t0) * 1000)` to `build_impact_report`. Both copies
of `_run_pipeline` are updated.

**Why both copies:** `deployments/webhook-receiver/` is a separate deployment
artifact, not a symlink. Drift between the two is a known risk; both copies
must be updated in lockstep.

## Data Flow

```
GitLab webhook → app.py → run_gitlab_note_workflow
  ↓
_run_pipeline (now times analyze_diff)
  ↓
analyze_diff (coverage_analyzer)
  ├─ extract_line_delta                 (already correct)
  ├─ feature_map.resolve (path → tags)  (already correct)
  ├─ Base-module escalation             (already correct)
  ├─ extract_symbols_from_diff (FIX:    ← Bug 3 + Bug 4
  │    drop path fallback, extend regex)
  ├─ run_impact (GitNexus subprocess)   (unchanged)
  └─ coverage_gaps (FIX:                ← Bug 1
       case-insensitive substring)
  ↓
build_impact_report(duration_ms=t1-t0)  ← Bug 2 (already fixed this session)
  ↓
post_gitlab_note (idempotent upsert)
```

## Test Strategy

| Test | Validates |
|------|-----------|
| `tests/test_coverage_gaps_case_insensitive.py` | Bug 1 — `Corporateaction` in module name, `corporateaction/` in test path |
| `tests/test_extract_symbols_kotlin_swift.py` | Bug 4 — Kotlin `fun`, Swift `extension`, etc. extracted via `_SYMBOL_REGEX` |
| `tests/test_extract_symbols_no_fallback.py` | Bug 3 — empty symbols when neither regex nor hunk-context fires (config files, docs) |
| `tests/test_pipeline_duration_capture.py` | Bug 2 — `duration_ms > 0` after `_run_pipeline` |
| Existing `tests/test_impact_workflow.py` | Regression baseline (6/6 currently passing) |

## Migration

No data migration. The cache layer (`webhook-impacts-cache.sqlite`) is keyed
on `(repo, commit_sha, sorted(symbols))` — a smaller symbol list (no path
fallback) produces a different cache key, which is correct.

## Validation

End-to-end:
1. Trigger `run_gitlab_note_workflow` against MR 23433 with the new code
2. Confirm `duration_ms` is ~12s (matches measurement from earlier this session)
3. Confirm `coverage_gaps` no longer contains `Corporateaction`
4. Confirm `at_risk_modules` no longer contains `Corporateaction` for the
   `Config.kt` line (which had no symbols extracted)

## Implementation Guardrails

These are concrete rules a worker must follow during implementation. They are
derived from pitfalls observed during research.

### G1: Update existing tests before adding new ones (Section 3 critical)

**Pitfall:** Existing `jira-skill/tests/impact/test_gitnexus_impact.py` lines
75 and 92 explicitly accept both `[]` and `[filename]` as valid results. Removing
the path-as-symbol fallback WILL break these tests.

**Required actions before merge:**
- Update `test_empty_diff_returns_empty_or_path` (line 72-75) → rename to `test_empty_diff_returns_empty`, assert `result == []`
- Update `test_handles_binary_no_diff` (line 87-92) → rename to `test_binary_diff_returns_empty`, assert `result == []`

**Why this guardrail exists:** Both tests contain comments like
"# Either [] or [filename] is acceptable; the spec allows both" — the previous
spec was ambiguous. This change makes it unambiguous. A worker who only adds
new tests without updating these will fail CI.

### G2: Deployment copy parity (Section 2 critical)

**Pitfall:** `webhook-receiver/src/webhook_receiver/impact.py` and
`deployments/webhook-receiver/app/src/webhook_receiver/impact.py` are
separate files (not symlinks). Drift between the two is a known risk.

**Required action:** After editing the source file, mirror the change to the
deployment copy in the SAME commit. The diff verification at task 7.5
ensures parity.

**Why this guardrail exists:** The live measurement of `duration_ms=11938`
was performed against the source copy, but production uses the deployment copy.
A worker who fixes only the source file will deploy unchanged behavior.

### G3: Test both deployment and source paths in CI

**Pitfall:** `tests/test_impact_workflow.py` lives in the source repo, not the
deployment repo. Tests that import `from webhook_receiver.impact import ...`
will only exercise the source copy.

**Mitigation:** Run `diff` (task 7.5) as part of final verification. If the
deployment copy diverges, the diff command fails the task.

### G4: Cache invalidation is automatic but documented

The cache key (`webhook-impacts-cache.sqlite`) is `(repo, commit_sha,
sorted(symbols))`. Removing the path-as-symbol fallback changes the symbol
list, producing a new cache key. **No manual cache flush is required** for the
symbol fallback change.

For the case-insensitive matching change, the cache layer is unrelated —
coverage_gaps is derived at runtime, not stored in the cache. **No cache flush
is required**.

For the regex extension change, additional keywords may produce additional
symbols, which changes the cache key. **No manual flush is required**.

For the duration capture change, only metadata is affected. **No cache flush
is required**.

### G5: Worker must read the spec scenarios before writing tests

Each spec scenario maps to one or more test functions in `tasks.md`. A worker
who writes tests without first reading the spec scenarios will likely
undertest. The scenarios are the contract; the tests are the verification.