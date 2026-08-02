# Impact Analysis Hardening — Specification

## Overview

This spec covers four correctness fixes to the impact-analysis pipeline:

1. Case-insensitive `coverage_gaps` substring matching (fixes false positives)
2. Real `duration_ms` capture in `_run_pipeline` (already implemented)
3. Drop the path-as-symbol fallback in `extract_symbols_from_diff`
4. Extend `_SYMBOL_REGEX` to cover Kotlin and Swift keywords

The scope is limited to `jira_skill/impact/` and `webhook_receiver/impact.py`.
The `tdt_core` layer, `feature-map.yaml`, and `ImpactReport` model are
unchanged.

---

## ADDED Requirements

### Requirement: Coverage Gaps Substring Matching

The system SHALL derive `coverage_gaps` from `at_risk_modules` such that a
module is **excluded** from `coverage_gaps` when at least one test file path
contains the module name (case-insensitive). The comparison SHALL be applied
against `tf.file_path` (the test file path) using lowercase normalization on
both the module name and the path.

#### Scenario: Module name matches lowercase directory in test path
- **WHEN** `at_risk_modules` contains `Corporateaction` (capitalized)
- **AND** a test file path contains `corporateaction/` (lowercase directory)
- **THEN** the substring check `module.lower() in tf.file_path.lower()` SHALL succeed
- **AND** `Corporateaction` SHALL NOT appear in `coverage_gaps`

#### Scenario: Module name with no matching test file
- **WHEN** `at_risk_modules` contains `NewFeature`
- **AND** no test file path contains `newfeature` (case-insensitive)
- **THEN** `NewFeature` SHALL appear in `coverage_gaps`

#### Scenario: Empty at_risk_modules
- **WHEN** `at_risk_modules` is empty
- **THEN** `coverage_gaps` SHALL be empty (no derivation runs)

### Requirement: Extract Symbols from Diff (no path fallback)

The function `extract_symbols_from_diff` SHALL return an empty list when neither the regex match nor the hunk-context match yields any symbol names, and SHALL NOT return `[filename]` as a fallback.

This applies to `jira_skill.impact.gitnexus_impact.extract_symbols_from_diff(diff, filename, *, max_symbols=50)`. Returning the file path as a "symbol" was a legacy workaround for the pre-`--summary-only` GitNexus mode and produces noisy `affected_modules` in modern use.

#### Scenario: Diff with no declarations or hunk-context
- **WHEN** the diff is purely body modifications (no `def`, `class`, `func`, etc.)
- **AND** the diff has no hunk-context (`@@ -X,Y +A,B @@ func Foo { ... }`)
- **THEN** `extract_symbols_from_diff` SHALL return `[]`
- **AND** the caller (`analyze_diff`) SHALL record `blast_radius.status = "not_found"`
- **AND** the staleness threshold SHALL account for this file

#### Scenario: Diff with at least one declaration
- **WHEN** the diff adds a Kotlin `fun bar()` declaration
- **THEN** `extract_symbols_from_diff` SHALL return `["bar"]`
- **AND** the path fallback SHALL NOT be reached

### Requirement: Symbol Regex Coverage for Kotlin/Swift

The `_SYMBOL_REGEX` constant SHALL match the following declaration keywords
(in addition to the existing Python, Go, C-like, Java keywords):

| Language | Keyword | Match |
|----------|---------|-------|
| Kotlin | `fun ` | Top-level or class function |
| Kotlin | `internal fun ` | Internal-visibility function |
| Kotlin | `protected fun ` | Protected-visibility function |
| Kotlin | `object ` | Singleton object declaration |
| Swift | `extension ` | Extension block |
| Swift | `protocol ` | Protocol declaration |

The keyword list SHALL be kept in sync with the `_HUNK_CONTEXT_PATTERN`
regex, which already includes these keywords.

#### Scenario: Kotlin `fun` declaration in diff
- **WHEN** the diff adds `+fun calculateTotal() {`
- **THEN** `_SYMBOL_REGEX.match()` SHALL return a match
- **AND** the captured `name` group SHALL be `calculateTotal`

#### Scenario: Swift `extension` in diff
- **WHEN** the diff adds `+extension String {`
- **THEN** `_SYMBOL_REGEX.match()` SHALL return a match
- **AND** the captured `name` group SHALL be `String`

#### Scenario: Existing patterns still match
- **WHEN** the diff adds `+def foo():` (Python) or `+public class Bar {` (Java)
- **THEN** `_SYMBOL_REGEX.match()` SHALL continue to return a match (no regression)

### Requirement: Pipeline Duration Capture

The `_run_pipeline` function in `webhook_receiver.impact` SHALL measure the
wall-clock duration of the `analyze_diff(...)` call using `time.monotonic()`
and SHALL pass the resulting `duration_ms` (integer milliseconds) to
`build_impact_report(...)`.

The same change SHALL be applied to the parallel copy of `_run_pipeline` in
`deployments/webhook-receiver/app/src/webhook_receiver/impact.py` to keep the
two deployment copies in lockstep.

#### Scenario: Duration is captured for non-trivial MR
- **WHEN** `_run_pipeline` runs against an MR with 17 changed files
- **AND** the `analyze_diff` call takes ~12 seconds
- **THEN** the resulting `ImpactReport.analysis_duration_ms` SHALL be ≥ 1
- **AND** the GitLab note SHALL display the captured duration (not `0`)

#### Scenario: Duration is captured even on cache-hit
- **WHEN** all symbols are cache hits (subprocess returns in <100ms)
- **THEN** `analysis_duration_ms` SHALL still be ≥ 1
- **AND** the cache hit count SHALL be reflected in the note (`Cache: N hits / 0 misses`)

### Requirement: No Path-as-Symbol Fallback

The `extract_symbols_from_diff` function SHALL NOT return `[filename]` as a
fallback when no symbols can be extracted. The function MUST return `[]`
in this case.

#### Scenario: Fallback no longer returns file path
- **WHEN** the diff has no declarations and no hunk-context
- **THEN** the function SHALL return `[]`
- **AND SHALL NOT** return `[filename]`

---

### Requirement: Live Pipeline Validation Command

The system SHALL provide a pytest helper function
`validate_impact_pipeline(project_path, mr_iid, commit_sha)` in
`tests/test_impact_workflow.py` that runs the full pipeline against a real
MR and asserts correctness invariants. The function SHALL be marked
`@pytest.mark.slow` and skipped in CI by default; it is intended for
manual live validation.

#### Scenario: Duration is non-zero
- **WHEN** `validate_impact_pipeline` runs against an MR with 17 changed files
- **THEN** the assertion `report.analysis_duration_ms > 0` SHALL hold

#### Scenario: coverage_gaps excludes modules with matching test paths
- **WHEN** `validate_impact_pipeline` runs against an MR with `Corporateaction` in `at_risk_modules`
- **AND** test files exist at paths containing `corporateaction/` (lowercase)
- **THEN** `Corporateaction` SHALL NOT appear in `coverage_gaps`

#### Scenario: at_risk_modules excludes path-fallback noise
- **WHEN** `validate_impact_pipeline` runs against an MR with files that produced no extracted symbols
- **THEN** the corresponding `affected_modules` SHALL NOT contain spurious module names