# ci-guard Specification

## Purpose
TBD - created by archiving change code-daily-scan-mirror-retirement-v2. Update Purpose after archive.
## Requirements
### Requirement: CI-1 — `check-docs-drift` runs as a GitLab CI job in Android

`poems-mobile3-android` SHALL include a GitLab CI job that runs `code-daily-scan check-docs-drift --platform=android` on every pipeline. The job MUST fail (exit non-zero) when drift is detected.

#### Scenario: Drift detected blocks merge
- GIVEN `poems-mobile3-android/docs/rules/categories/memory-lifecycle.md` differs from the canonical `poems-mobile3-docs/50.RCA/20.AOS/rules/categories/memory-lifecycle.md`
- WHEN the CI pipeline runs `check-docs-drift --platform=android`
- THEN the job MUST exit 1
- AND the merge request MUST be blocked.

#### Scenario: No drift allows merge
- GIVEN all 9 category files in `poems-mobile3-android/docs/rules/categories/` are byte-identical to the canonical source
- WHEN the CI pipeline runs `check-docs-drift --platform=android`
- THEN the job MUST exit 0
- AND the merge request MAY proceed.

### Requirement: CI-2 — `check-docs-drift` runs as a GitLab CI job in iOS

`poems-mobile3-ios` SHALL include a GitLab CI job that runs `code-daily-scan check-docs-drift --platform=ios` on every pipeline. The job MUST fail (exit non-zero) when drift is detected.

#### Scenario: iOS CI job blocks on drift
- GIVEN `poems-mobile3-ios/docs/rules/categories/crash-runtime.md` differs from the canonical `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/crash-runtime.md`
- WHEN the CI pipeline runs `check-docs-drift --platform=ios`
- THEN the job MUST exit 1
- AND the merge request MUST be blocked.

### Requirement: CI-3 — Drift allowlist skips detection for listed categories

`code-daily-scan check-docs-drift` SHALL read a `.drift-allowlist` file from the mirror root. Each line has the format `<category-stem> <reason> <YYYY-MM-DD>`. Entries whose expiry date has not passed are SKIPPED (not counted as drift). Expired entries are treated as drift.

#### Scenario: Allowlisted entry suppresses drift warning
- GIVEN `docs/.drift-allowlist` contains `state-mutation intentionally modified for FEATURE-X 2026-12-31`
- AND `docs/rules/categories/state-mutation.md` differs from canonical
- WHEN `check-docs-drift --platform=android` runs
- THEN the state-mutation difference is NOT reported as drift
- AND the job exits 0 if all other categories match.

#### Scenario: Expired allowlist entry is treated as drift
- GIVEN `docs/.drift-allowlist` contains `state-mutation legacy drift 2026-01-01` (past date)
- AND `docs/rules/categories/state-mutation.md` differs from canonical
- WHEN `check-docs-drift --platform=android` runs
- THEN state-mutation is reported as drift
- AND the job exits 1.

