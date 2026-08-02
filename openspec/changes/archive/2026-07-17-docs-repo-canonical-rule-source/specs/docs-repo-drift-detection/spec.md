# Spec: `code-daily-scan` — Docs-Repo Drift Detection

The `poems-mobile3-docs` repository is the **single source of truth** for the team's rulebook, but local mirrors still exist in `poems-mobile3-android/docs/rules/categories/` and `poems-mobile3-ios/docs/technical-debt-scan/categories/`. These mirrors drift over time and have **already drifted** as of the v1.1.0 freeze (verified: 3 of 9 Android category files differ between canonical and mirror). This capability declares how drift is **detected and surfaced** by the scanner; mirror replacement is covered by the companion `docs-repo-mirror-sync` capability.

## ADDED Requirements

### Requirement: D-1 — Scanner emits a drift report per scan

The `code-daily-scan` scanner SHALL compare, for each platform, the canonical docs-repo rule category files against the local mirror in the target repo, and SHALL emit a single `INFO` log line per scan summarising drift findings. The format MUST be:

```
docs_repo_drift=<true|false> platform=<plat> differing_files=<N> identical_files=<M>
```

When drift is detected (`differing_files >= 1`), an additional `WARNING` log line MUST be emitted per differing file, naming both the canonical and mirror paths and their SHA-256 fingerprints (first 12 chars).

#### Scenario: All categories identical between canonical and mirror
- GIVEN the local mirror in `<target_repo>/docs/rules/categories/` contains all 9 canonical files with byte-identical contents (verified by SHA-256)
- WHEN the scanner resolves the platform's rule categories
- THEN the scanner MUST emit exactly one `INFO` log line with `docs_repo_drift=false platform=<plat> differing_files=0 identical_files=9`
- AND MUST NOT emit any `WARNING` lines for that platform.

#### Scenario: Some categories differ
- GIVEN the local mirror in `poems-mobile3-android/docs/rules/categories/architecture-maintainability.md` differs from the canonical `50.RCA/20.AOS/rules/categories/architecture-maintainability.md` (verified via `diff` returning non-empty)
- WHEN the scanner resolves the Android rule categories
- THEN the scanner MUST emit one `INFO` log line with `docs_repo_drift=true platform=android differing_files=1+ identical_files=0-7`
- AND MUST emit one `WARNING` log line `docs_repo_drift_file=architecture-maintainability.md canonical_sha=<12> mirror_sha=<12>` per differing file.

#### Scenario: Mirror is missing entirely
- GIVEN the local mirror folder `poems-mobile3-android/docs/rules/categories/` does NOT exist
- WHEN the scanner resolves the Android rule categories
- THEN the scanner MUST emit `docs_repo_drift=false platform=android differing_files=0 identical_files=0` (treat absence as zero drift; the per-category fallback in S-1 already handles this case)
- AND MUST NOT confuse this with the iOS scenario where the legacy `technical-debt-scan/categories/` still holds 4 files in a different naming convention.

#### Scenario: iOS legacy mirror differs in naming
- GIVEN the legacy iOS local mirror at `poems-mobile3-ios/docs/technical-debt-scan/categories/` contains 4 files (`architecture-maintainability.md`, `crash-prevention.md`, `lifecycle-observers-state.md`, `retain-cycle-memory.md`) with naming that does NOT match the 9-category canonical taxonomy
- WHEN the scanner resolves the iOS rule categories
- THEN the scanner MUST emit `docs_repo_drift=true platform=ios differing_files=4 identical_files=0`
- AND MUST log a `docs_repo_legacy_mirror_detected=true path=<abs-path>` line listing the iOS app repo's `technical-debt-scan/categories/` path
- AND MUST recommend the user run `code-daily-scan sync-rules --platform=ios` (see the `docs-repo-mirror-sync` capability).

### Requirement: D-2 — Drift check is non-blocking

The drift-detection step MUST NOT prevent rule loading or scan continuation. The scanner MUST always prefer the canonical source (per the S-1 contract scenario "primary wins") even when the local mirror is drifted or absent. Drift detection is purely informational in v1.

#### Scenario: Drifted mirror does not block scan
- GIVEN 3 of 9 Android category files differ between canonical and mirror
- WHEN `code-daily-scan dry-run --platform=android` runs
- THEN the scan MUST exit 0
- AND MUST emit the canonical rules for all 9 categories (drift does not change which source wins)
- AND MUST emit the drift report per D-1.

### Requirement: D-3 — Drift check is enabled by default but can be disabled

The drift-detection step SHALL be enabled by default. Operators MAY disable it via a new config key `drift_detection_enabled: bool = True` on each platform's block in `~/.tdt/code-daily-scan.yaml`.

#### Scenario: Drift check disabled via config
- GIVEN `~/.tdt/code-daily-scan.yaml` contains `android.drift_detection_enabled: false`
- WHEN the scanner resolves the Android rule categories
- THEN the scanner MUST NOT emit any `docs_repo_drift=...` or `docs_repo_drift_file=...` lines
- AND the rules MUST still load from the canonical source.

### Requirement: D-4 — Drift detection has a dedicated CLI command

The scanner SHALL expose a `code-daily-scan check-docs-drift` subcommand that performs drift detection without running a full scan. The command MUST exit 0 when all mirrors are identical, exit 1 when any drift is detected, and print a human-readable drift report to stdout.

#### Scenario: All mirrors identical
- GIVEN all mirrors are in sync with the canonical docs repo
- WHEN `code-daily-scan check-docs-drift --platform=android` runs
- THEN the command MUST exit 0
- AND MUST print `drift_status=ok identical=9 differing=0`.

#### Scenario: Drift detected
- GIVEN `poems-mobile3-android/docs/rules/categories/architecture-maintainability.md` differs from canonical
- WHEN `code-daily-scan check-docs-drift --platform=android` runs
- THEN the command MUST exit 1
- AND MUST print a per-file table (filename, canonical_sha, mirror_sha, status).

### Requirement: D-5 — Drift check is wired into CI as a follow-up

A follow-up change tracked in tasks §16.1 (`code-daily-scan-mirror-retirement-v2`, NOT in this change) SHALL add a CI job in each platform repo that runs `code-daily-scan check-docs-drift` on every PR. The job MUST fail-when-drift is detected. For v1 of this change, drift detection is **runtime-only**; CI integration is documented but not implemented.

#### Scenario: No CI integration in v1
- GIVEN a PR to `poems-mobile3-android` that updates a local rule in `docs/rules/categories/`
- WHEN the PR's CI runs in v1
- THEN no drift check fires (the CI integration is the tasks §16.1 follow-up)
- AND the developer is expected to either revert the local-mirror edit OR run `code-daily-scan sync-rules --force --force-clobber` to bring mirrors in line before merge. Drift is logged but does not block CI in v1.

## Cross-references

- Internal: `code_daily_scan.plugins.android.rules_loader.AndroidRulesLoader` (L3 wiring)
- Internal: `code_daily_scan.plugins.ios.rules_loader.IOSRulesLoader` (L3 wiring)
- Internal: `code_daily_scan.config.PlatformConfig` (L3 wiring, new `drift_detection_enabled` field)
- Companion spec: `specs/docs-repo-mirror-sync/spec.md` (D-3 cross-references the `sync-rules` CLI)
- External: `poems-mobile3-android/docs/rules/categories/` (drift target)
- External: `poems-mobile3-ios/docs/technical-debt-scan/categories/` (legacy mirror with different naming)
- External: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/<platform>/rules/categories/` (canonical source)
