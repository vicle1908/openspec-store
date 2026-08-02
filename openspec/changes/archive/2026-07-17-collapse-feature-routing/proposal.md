## Why

`code-daily-scan` currently has at least four parallel sources of truth for which
spreadsheet tab a finding lands in: `feature_resolver.FEATURE_RULES` (canonical),
`plugins/android/tabs.py:ANDROID_FEATURE_PATTERNS` (Android plugin-local), and two
fallback tables in `sheets/mapper.py` (`_DEFAULT_MODULE_PATTERNS` and
`_fallback_tab_name`). They have already drifted: 57 of the 63 tokens in
`ANDROID_FEATURE_PATTERNS` have no equivalent in the canonical resolver, and the
mapper fallback emits fabricated TitleCase tab names like `Depositfunds` for
unmapped paths. The spec at `unified-code-daily-scan/specs/android-plugin/spec.md`
also claims 21 Android tabs (10 features + 11 infrastructure) while the
implementation only has 11 (10 features + `Common`). This change collapses the
routing logic to a single source of truth, reconciles the spec, and makes the
contract enforceable by contract tests.

## What Changes

- **Delete** `ANDROID_FEATURE_PATTERNS` from `plugins/android/tabs.py`. The
  Android plugin's `resolve_tab()` will delegate to `resolve_feature()` +
  `feature_to_tab()` exactly like the iOS plugin already does.
- **Add** a new requirement to `code-daily-scan-core` that
  `FEATURE_TAB_MAP` is the single source of truth for tab names and that
  `feature_to_tab()` is the only sanctioned way to map a feature to a tab.
- **Add** two contract tests that pin the `FEATURE_TAB_MAP` vocabulary and
  fail if any of the four tables drift out of sync.
- **Reorder** resource-file routing in `plugins/android/tabs.py` so
  `resolve_feature()` is consulted before the `.endswith()` extension check,
  bringing the code closer to the spec's "Resource files SHALL map to Common"
  requirement.
- **Make** `SheetMapper` plugin-required when used outside tests. The dynamic
  TitleCase tab-name generator in `_fallback_tab_name` is deleted; the few
  legacy test paths that exercise it are migrated to inject a plugin.
- **Update** `android-plugin/spec.md` to drop the 11 phantom infrastructure
  tabs (Adapter, Ui, CounterDetail, Network, Extensions, Utils, Viewmodels,
  Dashboard, Infrastructure, Local, App) and align the unknown-module
  scenario with the `Others` fallback.
- **Refresh** `unified-code-daily-scan/VERIFICATION.md` so the test counts
  and percentages match the current state (378 tests pass, Android Others =
  2/1486, iOS Others = 2/321). Remove the contradictory Addendum numbers
  (230 vs 314 vs 378).
- **Update** `code-daily-scan/README.md` and `code-daily-scan/AGENTS.md` so
  the new contract is documented for the next operator.

No breaking changes for end users: the production CLI path already routes
through `finding.feature` and the resolver, so external behaviour is
unchanged for any path the resolver already understands. The only observable
differences are:

1. A handful of unmapped non-`.kt` paths that the local
   `ANDROID_FEATURE_PATTERNS` table used to bucket into a feature tab
   (e.g. `app/src/main/res/auth/foo.xml` -> `Auth`) will now resolve to
   `Common` (the resolver's answer for the `res/` subtree). The new
   contract test pins this.
2. Legacy callers that constructed `SheetMapper(plugin=None)` will need to
   inject a plugin. The 3 affected tests are migrated; no production code
   path does this.

## Capabilities

### New Capabilities

- `single-source-of-truth-tab-routing`: Enforce that
  `feature_resolver.FEATURE_TAB_MAP` is the only sanctioned source of tab
  names in the codebase, with contract tests pinning its vocabulary.

### Modified Capabilities

- `code-daily-scan-core`: Add a requirement that `feature_to_tab()` is the
  only sanctioned entry point and that `FEATURE_TAB_MAP` is the single
  source of truth. Reference the new contract test.
- `android-plugin`: Drop the 11 phantom infrastructure tabs and the
  `Infrastructure` fallback scenario; align the spec with the 10+1
  implementation that the iOS plugin spec already commits to.

## Impact

- `code-daily-scan/src/code_daily_scan/feature_resolver.py` — no change
  (canonical source stays as-is; gets a docstring note).
- `code-daily-scan/src/code_daily_scan/plugins/android/tabs.py` — delete
  `ANDROID_FEATURE_PATTERNS` (~75 lines), reorder the resource-file check.
- `code-daily-scan/src/code_daily_scan/sheets/mapper.py` — delete the
  `_fallback_tab_name` dynamic-tab machinery (~50 lines); SheetMapper
  without a plugin raises a clear error.
- `code-daily-scan/tests/test_android_tabs.py` — drop
  `TestAndroidFeaturePatterns`; rewrite the 3 resource-file assertions in
  `TestResolveTab` to use the resolver-aligned expectation.
- `code-daily-scan/tests/test_sheet.py` — migrate the 3 callers that
  construct `SheetMapper(plugin=None)` to inject a real plugin.
- `code-daily-scan/tests/test_feature_resolver.py` — add 2 contract tests
  pinning `FEATURE_TAB_MAP` and asserting it agrees with `_fallback_tab_name`
  (deleted) and `_DEFAULT_MODULE_PATTERNS` (still alive for tests).
- `code-daily-scan/src/code_daily_scan/sheets/writer.py` — update the
  docstring at line 262-266 to reflect the new ordering.
- `code-daily-scan/README.md` — add a one-paragraph note on the routing
  contract under the "Platform Differences" section.
- `code-daily-scan/AGENTS.md` and `CLAUDE.md` — already covered by
  GitNexus policy; no change.
- `tdt-meta/openspec/changes/unified-code-daily-scan/specs/code-daily-scan-core/spec.md`
  — add the single-source-of-truth requirement.
- `tdt-meta/openspec/changes/unified-code-daily-scan/specs/android-plugin/spec.md`
  — drop the 11 phantom tabs and the `Infrastructure` scenario.
- `tdt-meta/openspec/changes/unified-code-daily-scan/VERIFICATION.md` —
  refresh the numbers and remove the contradictory Addendum.

## Non-goals

- We are NOT implementing the 11 phantom infrastructure tabs. The
  cross-platform unified taxonomy was the explicit Phase 9 goal
  (VERIFICATION.md line 16: "Cross-platform: Both platforms use identical
  10-feature taxonomy") and the implementation is the contract.
- We are NOT rewriting the Android path normaliser or adding new feature
  tokens. This change is strictly about removing duplication and
  reconciling the spec, not extending coverage.
- We are NOT changing `sheets/mapper.py`'s `_DEFAULT_MODULE_PATTERNS`
  tuple. It is still the legacy/test-only fallback and is brought into
  the contract via R4's test. Removing it is out of scope.
- We are NOT changing the iOS plugin. It already follows the desired
  pattern (single delegation to `resolve_feature` + `feature_to_tab`).
- We are NOT modifying the platform-level `tdt/AGENTS.md` or
  `tdt/CLAUDE.md`. The work stays inside `code-daily-scan` and
  `tdt-meta/openspec`.
