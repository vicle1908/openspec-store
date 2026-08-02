# Impact Analysis Hardening — Proposal

## Why

A live evaluation of the impact-analysis pipeline against MR 23433 (PMP Connection
Center, 17 changed files, 3 features, commit 75c6cf0) surfaced four correctness
gaps that all derive from the same root cause: the pipeline was correct enough
to pass initial smoke tests but not robust enough for operator trust.

| # | Bug | Impact | Severity |
|---|-----|--------|----------|
| 1 | `coverage_gaps` substring check is case-sensitive; misses `Corporateaction` test paths (`corporateaction/` lowercase dirs) | False positive — `Corporateaction` is reported as a coverage gap even though `CorporateActionFragmentTest.kt` exists | Medium |
| 2 | `_run_pipeline` hardcodes `duration_ms=0` in `webhook-receiver/impact.py` | Operators see "in 0ms" in the GitLab note; performance regressions invisible | Low |
| 3 | Path-as-symbol fallback returns `[filename]` when no symbols are extracted | Spurious `Corporateaction`/`Communities` entries in `at_risk_modules` for non-symbolic changes (config, doc files) | Medium |
| 4 | `_SYMBOL_REGEX` does not match Kotlin `fun` / Swift `extension` keywords (only hunk-context saves them) | When `diff -p` is unavailable, Kotlin/Swift declarations are silently dropped | Low |

These are not feature gaps — the pipeline runs end-to-end and the GitLab note
posts correctly. They are **correctness gaps** that undermine operator trust
when they read the report and try to verify it against ground truth.

## What Changes

### 1. Case-insensitive `coverage_gaps` substring check (Bug 1)

Replace `any(module in tf.file_path for tf in f.blast_radius.test_files)` with a
case-insensitive check using `module.lower() in tf.file_path.lower()`. This
matches Android's `corporateaction/` directory naming convention where the
module name is capitalized in the source files but lowercase in directory paths.

### 2. Capture actual `duration_ms` in `_run_pipeline` (Bug 2)

Already implemented in this session. The fix wraps the `analyze_diff(...)` call
in `time.monotonic()` and threads the result through `build_impact_report(...,
duration_ms=...)`. Both copies (`webhook-receiver/`, `deployments/webhook-receiver/`)
are updated. Live measurement: 11,938ms for MR 23433 (was 0ms).

### 3. Skip path-as-symbol fallback when no symbols extracted (Bug 3)

Change `extract_symbols_from_diff` to return `[]` instead of `[filename]` when
neither the regex nor hunk-context finds any symbols. GitNexus already returns
`status: not_found` for empty symbol lists, which the pipeline handles
correctly via the staleness threshold. The path fallback was an old workaround
that produces noise in the modern `--summary-only` mode.

### 4. Extend `_SYMBOL_REGEX` to cover Kotlin/Swift keywords (Bug 4)

Add to the regex alternation:
- Kotlin: `fun `, `internal fun`, `protected fun`, `object `
- Swift: `extension `, `protocol ` (already in `_HUNK_CONTEXT_PATTERN`, not in `_SYMBOL_REGEX`)

Both regexes should be kept in sync; the existing hunk-context pattern already
covers these, so the fix is to align the line-level regex for resilience when
`diff -p` is unavailable.

### Non-Goals

- Changing the GitNexus subprocess invocation, caching, or staleness threshold
- Refactoring `extract_symbols_from_diff` AST extraction logic
- Adding new pipeline stages (test discovery, regression planning integration)
- Changing the public `ImpactReport` model shape
- Touching the iOS or Python impact paths (only the shared `coverage_analyzer.py`
  and `gitnexus_impact.py` modules are affected)

## Alignment with Existing Systems

| Component | Touched? | Notes |
|-----------|----------|-------|
| `jira_skill.impact.coverage_analyzer` | Yes (case-insensitive check) | Bug 1 fix |
| `jira_skill.impact.gitnexus_impact` | Yes (regex + fallback) | Bug 3 + 4 fix |
| `webhook_receiver.impact._run_pipeline` | Yes (timing already applied this session) | Bug 2 fix |
| `deployments/webhook-receiver/.../impact.py` | Yes (mirrors Bug 2 fix) | Bug 2 fix |
| `tdt_core.clients.gitlab_mr` | No | — |
| `feature-map.yaml` | No | — |
| `ImpactReport` pydantic model | No | — |
| Existing specs (`jira-impact-analysis`, `gitlab-impact-note`) | No (additive) | New spec for hardening |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Path-fallback removal causes a regression in tests that rely on it | Run existing `tests/test_impact_workflow.py` + new tests for empty-symbol cases; the cache layer already handles `not_found` gracefully |
| Case-insensitive check increases false negatives (e.g., matches unrelated files) | Restrict to the `coverage_gaps` derivation loop only; the blast radius itself is still case-sensitive |
| Regex extension breaks existing tests | Use the existing `extract_symbols_from_diff` test suite as the regression baseline; add Kotlin/Swift corpus fixtures |
| Operator confusion when `duration_ms` appears after deployment | Update CHANGELOG / notes; the field was already in the report (always 0 before) |

## Validation

1. Run live `analyze_diff` against MR 23433 (PMP Connection Center) before
   and after; confirm:
   - `Corporateaction` no longer in `coverage_gaps` (test files exist)
   - `duration_ms` is non-zero (~12s expected)
   - `at_risk_modules` no longer contains `Corporateaction` for `Config.kt`
2. Add `tests/test_coverage_gaps_case_insensitive.py` regression test
3. Add `tests/test_extract_symbols_kotlin_swift.py` corpus tests
4. Verify existing 6 `tests/test_impact_workflow.py` still pass