# Impact Analysis Hardening

Four correctness fixes to the impact-analysis pipeline, surfaced by live evaluation against MR 23433.

## What's here

| Artifact | Purpose |
|----------|---------|
| `proposal.md` | Why this change exists; the four bugs and their mitigations |
| `design.md` | Technical decisions, data flow, test strategy |
| `specs/coverage-analyzer-hardening/spec.md` | RFC 2119 requirements: case-insensitive matching, no path fallback, regex extension, duration capture |
| `tasks.md` | Concrete task breakdown for implementation |

## Bugs Addressed

| Bug | Severity | Status |
|-----|----------|--------|
| 1. `coverage_gaps` case-sensitive substring | Medium | Specified |
| 2. `_run_pipeline` hardcoded `duration_ms=0` | Low | Implemented in this session |
| 3. Path-as-symbol fallback noise | Medium | Specified |
| 4. `_SYMBOL_REGEX` missing Kotlin/Swift | Low | Specified |

## Validation Target

MR 23433 (PMP Connection Center, 17 files, 3 features, commit 75c6cf0) is the canonical validation case. After all fixes:

- `coverage_gaps` no longer contains `Corporateaction`
- `at_risk_modules` no longer contains `Corporateaction` for `Config.kt`
- `analysis_duration_ms` reflects actual wall-clock time (~12s)

## Related Changes

- `jira-impact-analysis` (Complete) — original Jira-side impact analysis
- `gitlab-impact-note` (Complete) — GitLab MR note posting