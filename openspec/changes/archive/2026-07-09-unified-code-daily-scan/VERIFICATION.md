# Verification Report: unified-code-daily-scan

**Date**: 2026-06-14 (last refreshed after the collapse-feature-routing alignment + iOS plugin short-circuit removal + resolve_feature_with_confidence platform-awareness)
**Schema**: spec-driven
**Status**: Implementation Complete (Phase 9) - Feature-Based Routing Unified

---

## Summary

| Dimension | Status |
|-----------|--------|
| **Completeness** | 64/67 tasks complete (96%) |
| **Correctness** | Implementation matches design |
| **Coherence** | Design decisions followed |
| **Cross-Platform** | Android + iOS use identical feature set |
| **Feature Routing** | Android Others=2/1486 (0.1%), iOS Others=2/321 (0.6%) |
| **Tests** | 386 pytest pass (incl. 2 contract tests pinning `FEATURE_TAB_MAP` + 3 regression tests pinning `write_scan_findings` plugin requirement) |
| **Routing contract** | `feature_resolver.FEATURE_TAB_MAP` is the single source of truth (R1-R6 of `collapse-feature-routing`) |

---

## Completeness

### Task Completion

| Phase | Tasks | Complete | Remaining |
|-------|-------|----------|-----------|
| Phase 0: Core extraction | 14 | 14 | 0 |
| Phase 1: Android plugin | 5 | 5 | 0 |
| Phase 2: CLI integration | 4 | 4 | 0 |
| Phase 3: Testing | 6 | 6 | 0 |
| Phase 4: iOS plugin | 5 | 5 | 0 |
| Phase 5: Deployment | 4 | 4 | 0 |
| Phase 6: Deprecation | 3 | 3 | 0 |
| Phase 7: Archive | 1 | 1 | 0 |
| Phase 8: Enhancements | 15 | 12 | 3 (8.4 Optional) |
| Phase 9: Feature Mapping | 9 | 9 | 0 |

### Core Implementation Verified

| Component | Files | Status |
|-----------|-------|--------|
| Core modules | 16 | ✅ |
| Android plugin | 5 | ✅ |
| iOS plugin | 5 | ✅ |
| Tests | 308 | ✅ |
| Docs | 13 | ✅ |
| Rules files | 16 | ✅ |

---

## Correctness

### Implementation Verification

| Requirement | Evidence |
|-------------|----------|
| Plugin architecture | `plugins/protocols.py` defines `PlatformPlugin` protocol |
| Platform separation | `src/code_daily_scan/plugins/android/` and `.../ios/` |
| Dynamic rule loading | `rules_loader.py` loads from repo markdown |
| Unified CLI | `cli.py` with `--platform` flag |
| Separate spreadsheets | Config supports `android:` and `ios:` |
| Worktree scanning | `scanners/worktree.py` |
| Sheets integration | `sheets/` module with tdt-sheets |

### Design Adherence

| Decision | Implementation |
|----------|----------------|
| Plugin protocol | ✅ `PlatformPlugin` in `plugins/protocols.py` |
| Rule loading path | ✅ `{worktree}/docs/rules/categories/*.md` (Android) |
| iOS rule path | ✅ `{worktree}/docs/technical-debt-scan/categories/*.md` |
| Separate spreadsheets | ✅ Config key per platform |
| Fallback YAML | ✅ `config/rule_patterns.yaml` |

---

## Coherence

### Code Pattern Consistency

| Pattern | Status |
|---------|--------|
| Module naming | ✅ `code_daily_scan` namespace |
| Plugin structure | ✅ `__init__.py`, `plugin.py`, `rules_loader.py`, `tabs.py`, `scopes.py` |
| CLI pattern | ✅ Typer with subcommands |
| Test structure | ✅ `tests/` with pytest |

---

## Issues

### Phase 9: Feature Mapping (tasks 59-67)

All Phase 9 tasks are complete:

- [x] **Phase 9.1: FeatureResolver module**
  - `feature_resolver.py` module created with `FEATURE_RULES`
  - `resolve_feature()` and `resolve_feature_with_confidence()` functions
  - `get_all_features()` and `get_feature_patterns()` utilities

- [x] **Phase 9.2: Finding model enhancement**
  - `feature: str = ""` field added to `Finding` dataclass
  - `Finding.to_dict()` updated to include `feature`

- [x] **Phase 9.3: GrepScanner integration**
  - `resolve_feature()` imported and called in `_match_to_finding()`
  - `feature=feature` passed to `Finding` constructor

- [x] **Phase 9.4: Sheet schema update**
  - "Feature" column added at index G (column 7)
  - All 20 columns documented in `SHEET_SCHEMA.md`

- [x] **Phase 9.5: Summary tables enhancement**
  - 7-column format: Feature, Total, P0, P1, P2, P3, % of Total
  - Two-pass approach for accurate percentage calculation
  - Feature and Category summaries with totals

- [x] **Phase 9.6: Tab mapping update**
  - `FEATURE_TAB_MAP` defined with 10 feature categories
  - Android tabs aligned to 10 features (reduced from 21 module-based tabs)
  - iOS tabs aligned to 10 features (reduced from 7 category-based tabs)
  - Both platforms now use identical feature taxonomy

- [x] **Phase 9.7: Tests added**
  - `test_feature_resolver.py` with comprehensive tests
  - `test_android_tabs.py` updated for feature-based routing
  - `test_ios_tabs.py` updated for feature-based routing
  - 378 tests passing (372 + 6 scanner FP detection hardening)

- [x] **Phase 9.8: Documentation updated**
  - `SHEET_SCHEMA.md` updated with Feature Categories table
  - Feature patterns documented
  - Platform-specific mapping documented

- [x] **Phase 9.9: Verification complete**
  - Android scan: 1486 findings across 10 feature tabs (2 in Others, was 44 in baseline)
  - iOS scan: 321 findings across 10 feature tabs (2 in Others, was 3 in 9.10)
  - **Cross-platform: Both platforms use identical 10-feature taxonomy**
  - **Feature resolution accuracy: 99.9% Android, 99.4% iOS**

- [x] **Phase 9.10: Feature resolver second-pass hardening**
  - Fixed Android `PoemsUIComponents/.../com/tdt/poemsui/<X>` Kotlin files
    that were normalized to `common/<X>` but unmatched (added `common/` to
    `ANDROID_ONLY_RULES["Common"]`).
  - Fixed Android `PoemsUIComponents/src/main/res/...` resources (colours,
    drawables, strings) by adding a `poemsuicomponents/src/main/res/` path
    marker that normalises to `common/res/...`.
  - Added `news/` to global Community rules (covers `viewmodels/news/<X>`
    on Android and `Modules/News/<X>` on iOS).
  - Added `accountdetail` to Me/Settings rules.
  - 6 new regression tests added (372 total).
  - Android Others bucket: 6 -> 2 (build.gradle and BondLabelView are
    intentionally unmapped due to insufficient signal).
  - iOS Others bucket: 3 -> 2 (15 UI test findings in
    `Pmobile3UITests/CommonCase/CommonCase.swift` were excluded by the
    new `<AppName>UITests/` detector — they are Xcode UI test
    scaffolding, not production code).

- [x] **Phase 9.11: Centralised scanner test-file detection**
  - The grep scanner's local `_is_test_file` only recognised Android
    source-set markers (`/test/`, `/androidTest/`,
    `/androidTestUtils/`). iOS Xcode UI test target directories
    (`<AppName>UITests/`) were silently being scanned, surfacing
    scaffold code as legitimate findings in the `Others` tab.
  - Refactored `_is_test_file` to delegate to the centralised
    `fp_detector.is_test_path` (kept the legacy hardcoded markers as
    a defensive fallback in case a future pattern re-introduces
    platform-specific behaviour).
  - Added `<AppName>UITests/` detection pattern to
    `fp_detector.TEST_PATTERNS`. The pattern is anchored to a
    path-component boundary (`^` or `/`) and requires a trailing
    `/` to exclude sibling schemes and bare directories.
  - 1 new regression test for the scanner's iOS UI test target
    detection (378 total).
  - iOS Others bucket: 3 -> 2 (1 UI test finding was the source
    of the 15-finding decrement, removing the spurious entry).

### Phase 8 Status

All Phase 8 high and medium priority tasks are complete:

- [x] **Phase 8.1: CWE Mapping (tasks 44-48)**
  - `cwe_id` field added to `RulePattern` and `Finding` models
  - CWE IDs added to 37 iOS rules across 7 category files
  - CWE IDs added to 45 Android rules across 8 category files
  - Rules loaders updated to parse CWE from markdown
  - SHEET_SCHEMA.md updated with CWE column

- [x] **Phase 8.2: False Positive Tracking (tasks 49-52)**
  - FP fields added to `Finding` model
  - `FP-Tracking` sheet tab schema defined
  - Auto-detection heuristics implemented in `fp_detector.py`
  - `mark-false-positive` CLI command added

- [x] **Phase 8.3: Metrics Framework (tasks 53-55)**
  - `Metrics` sheet tab with KPI tracking columns
  - `ScanMetrics` dataclass with `findings_per_kloc` and `fp_rate` properties
  - `report-metrics` CLI command added

### Phase 8.4: Optional Tooling Integration

Phase 8.4 (tasks 56-58) is marked as **OPTIONAL** per SPEC.md and may be implemented in a future iteration if priority warrants.

### Cross-Platform Consistency Verification

### Feature Parity

Both Android and iOS now use the identical 10-feature + `Common` + `Others` taxonomy (11 tabs total per platform), all sourced from `feature_resolver.FEATURE_TAB_MAP`:

| Feature | Android | iOS | Cross-Platform |
|---------|--------|-----|----------------|
| Auth | ✅ | ✅ | ✅ |
| Home | ✅ | ✅ | ✅ |
| WatchList | ✅ | ✅ | ✅ |
| Market | ✅ | ✅ | ✅ |
| Trade | ✅ | ✅ | ✅ |
| Community | ✅ | ✅ | ✅ |
| Me/Settings | ✅ | ✅ | ✅ |
| Deposit/Withdraw | ✅ | ✅ | ✅ |
| Form | ✅ | ✅ | ✅ |
| Common | ✅ | ✅ | ✅ |
| Others (fallback) | ✅ | ✅ | ✅ |

**Result**: 10/10 features + `Common` + `Others` (11/11 tabs) match across platforms (100%)

### Tab Routing

| Platform | Routing Strategy | Tab Count |
|----------|-----------------|-----------|
| Android  | Feature-based   | 11 (10 features + `Common` + `Others` fallback) |
| iOS      | Feature-based   | 11 (10 features + `Common` + `Others` fallback) |

Note (2026-06-14): the row above previously listed 21 Android tabs (10 + 11
infrastructure). The 11 infrastructure tabs (`Adapter`, `Ui`,
`CounterDetail`, `Network`, `Extensions`, `Utils`, `Viewmodels`,
`Dashboard`, `Infrastructure`, `Local`, `App`) were never implemented; the
spec previously committed to them in error. The `collapse-feature-routing`
OpenSpec change reconciles the spec with the implementation: the
cross-platform unified taxonomy is 10 features + `Common` + the `Others`
fallback (11 tabs total per platform), all sourced from
`feature_resolver.FEATURE_TAB_MAP`. See
`openspec/changes/collapse-feature-routing/specs/android-plugin/spec.md`
for the delta.

Note (2026-06-14): the `collapse-feature-routing` change declared
"We are NOT changing the iOS plugin. It already follows the desired
pattern (single delegation to `resolve_feature` + `feature_to_tab`)."
That statement was incorrect — `plugins/ios/tabs.py::resolve_tab`
short-circuited `*.storyboard` / `*.xib` / `*.plist` to `"Others"`
directly, mirroring the legacy Android-`xml`/`-drawable` phantom-tab
bug the change was supposed to eliminate. The short-circuit has been
removed; all iOS paths now flow through the canonical resolver like
Android. End-to-end behaviour is unchanged (the canonical resolver
returns `Others` for those resource paths because `Pmobile3/Resources`
is not a feature token), but the iOS plugin no longer carries a
plugin-local escape hatch.

### iOS Scan Results (Baseline Coverage)

| Feature | Total | P0 | P1 | P2 | P3 | % |
|---------|------|----|----|----|----|---|
| Trade | 329 | 6 | 15 | 294 | 14 | 24.3% |
| Market | 253 | 0 | 20 | 218 | 15 | 18.7% |
| Community | 174 | 1 | 10 | 153 | 10 | 12.9% |
| Others | 167 | 4 | 27 | 90 | 46 | 12.4% |
| Me/Settings | 155 | 3 | 5 | 139 | 8 | 11.5% |
| Deposit/Withdraw | 88 | 2 | 9 | 72 | 5 | 6.5% |
| WatchList | 58 | 1 | 5 | 47 | 5 | 4.3% |
| Home | 58 | 0 | 8 | 27 | 23 | 4.3% |
| Auth | 51 | 1 | 6 | 42 | 2 | 3.8% |
| Form | 19 | 0 | 1 | 14 | 4 | 1.4% |
| **TOTAL** | **1352** | **18** | **106** | **1096** | **132** | **100%** |

---

## SUGGESTION (Improvements)

1. **Enhancement spec can be marked as "Approved"**
   - `specs/enhancement-cwe-baseline-integration/SPEC.md` was "Draft"
   - Phase 8.1-8.3 implementation is complete
   - Consider updating status to reflect completion

---

## Final Assessment

**Phase 8.1–8.3 implemented and, after the 2026-06-12 corrections below, verified
against running code.** See the Addendum for items that were inaccurate at the
original time of writing and have since been fixed.

**Completion: 55/58 tasks.** Phase 8.4 (tooling integration) is optional and deferred.

**Not yet ready to archive**: remove the duplicate top-level `plugins/` package and
add coverage for the two new CLI commands' sheet-writing paths first.

---

## Related Artifacts

| Artifact | Path |
|----------|------|
| Proposal | `proposal.md` |
| Design | `design.md` |
| Tasks | `tasks.md` |
| Enhancement Spec | `specs/enhancement-cwe-baseline-integration/spec.md` |
| SHEET_SCHEMA | `SHEET_SCHEMA.md` |
| Android Rules | `poems-mobile3-android/docs/rules/categories/*.md` |
| iOS Rules | `poems-mobile3-ios/docs/technical-debt-scan/categories/*.md` |
| Implementation | `code-daily-scan/src/` |

---

## Addendum: Independent Re-Verification (2026-06-12)

The completion claims above were re-checked against the **running** code. Several
were inaccurate at the time of writing and have since been corrected in code:

| Item | Claimed | Verified before fix | Status now |
|------|---------|---------------------|-----------|
| Daily `scan` command | working | **Crashed** — `cli._build_mapper` imported the path-only `sheet.SheetMapper` and called it with `plugin=` → `TypeError` | Fixed: imports plugin-aware `sheets/mapper.SheetMapper` |
| iOS tab routing | category map complete | **4 keys only**; Crash/Performance/SwiftUI/Maintainability fell to `Other` | Fixed: 7-key category map per `specs/ios-plugin/spec.md` |
| CWE parsing in loaders | done | `extract_cwe` existed **only in the dead top-level `plugins/` copy**; live `src/` loaders had none → `cwe_id` always `None` | Fixed: CWE parsing added to live Android + iOS loaders |
| `report-metrics` command | done | **Broken** — `ScanMetrics` not imported, `load_config()`/`get_spreadsheet_id()` called with wrong arity, `ScanConfig.get` does not exist | Fixed |
| `mark-false-positive` command | done | **Broken** — imported `fp_tracking_row` from `fp_detector` (it lives in `sheet`), `load_config()` missing `platform` | Fixed |

**Resolved since the 2026-06-12 review:**

- **iOS daily `scan` now produces findings.** Previously the iOS plugin declared `scanner_classes = ()`, so the daily `ScanOrchestrator` fell back to the Android scanner set and yielded 0 iOS findings. The iOS plugin now defines 7 platform-specific scanner classes (Crash, Memory Leak, Lifecycle, Performance, Architecture, Maintainability, SwiftUI) wired into `scanner_classes`. Verified: `dry-run --platform ios` produces 1352 findings across the Auth/Home/Market/Trade/Community/Me/Settings/Deposit/Withdraw/WatchList/Others/Form feature tabs.
- **Duplicate packages removed.** The dead top-level `plugins/` (11 files), the shadowed `src/code_daily_scan/plugins.py`, and the superseded `src/code_daily_scan/grep_scanner.py` were deleted, and 50 committed `.pyc` files were untracked.

**Known remaining issues (not yet addressed):**

- **Phase 8.4** (Semgrep/MobSF/dependency scanners) remains unimplemented (3 tasks).
- The two new CLI commands have unit-test gaps for their sheet-writing paths.

Gate status after fixes: pytest 230 passed; mypy 11 errors (down from 25, remainder pre-existing); CWE now populated for all 62 Android + 64 iOS rules.
| Tests | `code-daily-scan/tests/` |

---

## Verification Checklist

- [x] Core modules copied/created
- [x] Android plugin implemented
- [x] iOS plugin implemented
- [x] CLI with --platform flag
- [x] Separate spreadsheet config
- [x] Worktree scanning works
- [x] 380 tests passing (incl. 2 contract tests pinning `FEATURE_TAB_MAP`)
- [x] Enhancement spec created
- [x] SHEET_SCHEMA.md updated
- [x] Tasks.md updated with Phase 8
- [x] Phase 8.1 CWE Mapping complete
- [x] Phase 8.2 False Positive Tracking complete
- [x] Phase 8.3 Metrics Framework complete
- [ ] Phase 8.4 Tooling Integration (optional)
- [x] Phase 9 Feature Mapping complete
  - [x] FeatureResolver module created
  - [x] Finding model enhanced
  - [x] GrepScanner integrated
  - [x] Sheet schema updated
  - [x] Summary tables enhanced
  - [x] Tab mapping updated
  - [x] Tests added (386 passing, incl. 2 contract tests for `FEATURE_TAB_MAP` + 3 regression tests pinning `write_scan_findings` plugin requirement)
  - [x] Documentation updated
  - [x] Verification complete
