# Tasks: code-daily-scan-mirror-retirement-v2

## Overview

Promote `check-docs-drift` from a runtime-only tool to a CI-enforced
contract in both `poems-mobile3-android` and `poems-mobile3-ios`, with a
`.drift-allowlist` opt-out for feature branches.

- [x] Spec phase: proposal.md + 2 spec files (ci-guard, drift-allowlist) exist
- [x] **T1: Implement `.drift-allowlist` reader in `code-daily-scan`**
  - Add `code_daily_scan/drift_allowlist.py` (parse + expiry check)
  - Update `check_drift()` in `drift.py` to skip entries whose expiry date
    has not passed and whose `category-stem` matches a drift finding
  - Update `DriftReport` to surface skipped-entries as a separate field
- [x] **T2: Add unit tests for allowlist**
  - `tests/test_drift_allowlist.py`: parse test, expiry test, malformed-line test
  - Extend existing `test_rules_repo_config.py` with a smoke test for the
    integration of `check_drift` + allowlist
- [x] **T3: Add `.drift-allowlist` to `poems-mobile3-android/docs/`**
  - Header comment + 0 entries (file is reserved for opt-outs)
- [x] **T4: Add `.drift-allowlist` to `poems-mobile3-ios/docs/`**
  - Header comment + 0 entries
- [x] **T5: Add GitLab CI job in `poems-mobile3-android/.gitlab-ci.yml`**
  - New stage `docs-drift-check`, runs `code-daily-scan check-docs-drift --platform=android`
  - Block merge when drift detected (exit 1)
- [x] **T6: Add GitLab CI job in `poems-mobile3-ios/.gitlab-ci.yml`**
  - New stage `docs-drift-check`, runs `code-daily-scan check-docs-drift --platform=ios`
  - Block merge when drift detected (exit 1)
- [x] **T7: Run `ruff check . --fix && ruff format .`** in `code-daily-scan`
- [x] **T8: Run `mypy code-daily-scan/ --strict`** in `code-daily-scan`
- [x] **T9: Run `pytest -x`** in `code-daily-scan`
- [x] **T10: Run `openspec validate --strict code-daily-scan-mirror-retirement-v2`**
- [x] **T11: `gitnexus detect_changes` on `code-daily-scan`** (CLI surface change)
- [x] **T12: Commit** — single MR in `code-daily-scan` + 2 MRs in
  `poems-mobile3-android` / `poems-mobile3-ios` (separate repos)
- [x] **T13: Archive change** — `openspec archive code-daily-scan-mirror-retirement-v2`

## Note on scope

This change requires multi-repo coordination:

| Repo | Changes |
|------|---------|
| `code-daily-scan` | allowlist reader (T1, T2, T7-T9), tests |
| `poems-mobile3-android` | `.drift-allowlist` (T3), CI job (T5) |
| `poems-mobile3-ios` | `.drift-allowlist` (T4), CI job (T6) |

The T1 (allowlist reader) is the highest-risk change because every CI run
will exercise it on every pipeline.

## Reference

Spec files (already written, validated):

- `specs/ci-guard/spec.md` — requirements CI-1, CI-2, CI-3
- `specs/drift-allowlist/spec.md` — (likely future, format reference)