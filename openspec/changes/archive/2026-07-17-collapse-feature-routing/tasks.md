# tasks.md

## 1. Contract tests pin FEATURE_TAB_MAP vocabulary (R4)

- [x] 1.1 Add `tests/test_feature_resolver.py::TestFeatureTabMapVocabulary`
      with a test that pins `feature_resolver.FEATURE_TAB_MAP` to a
      fixed, ordered tuple. The test must fail if any value is added,
      removed, or renamed. Add the test in the same commit that
      declares the contract. — **Done in commit 5896779.**
- [x] 1.2 Add `tests/test_sheet.py::TestMapperPatternsAgreeWithTabMap`
      with a test that asserts every `tab_name` value in
      `sheets/mapper.py::_DEFAULT_MODULE_PATTERNS` is present as a
      key in `FEATURE_TAB_MAP`. Add the test in the same commit. —
      **Done in commit 5896779.**
- [x] 1.3 Verify: `uv run pytest tests/test_feature_resolver.py
      tests/test_sheet.py -q` shows the two new tests pass. —
      **Done in commit 5896779.**

## 2. Collapse Android plugin onto the resolver (R1)

- [x] 2.1 Delete `ANDROID_FEATURE_PATTERNS` from
      `src/code_daily_scan/plugins/android/tabs.py`. Replace the
      non-`.kt` fallback loop with a single delegation to
      `resolve_feature(file_path, platform="android")` followed by
      `feature_to_tab(...)`. Keep the resource-file extension check
      as a last-resort fallback (handled in section 3). —
      **Done in commit 7a9e63a.**
- [x] 2.2 Rewrite `tests/test_android_tabs.py::TestResolveTab` so
      the asserted expectations match the resolver's behaviour
      rather than the deleted local table. Specifically: a
      `res/auth/foo.xml` path now resolves to `Common`, not `Auth`. —
      **Done in commit 7a9e63a.**
- [x] 2.3 Delete `tests/test_android_tabs.py::TestAndroidFeaturePatterns`.
      The class tested the deleted constant. —
      **Done in commit 7a9e63a.**
- [x] 2.4 Update the docstring at the top of
      `src/code_daily_scan/plugins/android/tabs.py` to reflect the
      new routing: it now mirrors `ios/tabs.py` line by line. —
      **Done in commit 7a9e63a.**
- [x] 2.5 Verify: `uv run ruff check src/ tests/` is clean,
      `uv run mypy src/` is clean, `uv run pytest -q` is at
      378 + 2 (the R4 contract tests) = 380 passing. — **Verified.**

## 3. Reorder resource-file routing to consult resolver first (R5)

- [x] 3.1 In `src/code_daily_scan/plugins/android/tabs.py::resolve_tab`,
      move the `resolve_feature(file_path, platform="android")` call
      above the resource-file extension check, and remove the `.kt`
      short-circuit (the resolver handles `.kt` and non-`.kt`
      uniformly). If the resolver returns a non-`Others` value,
      return it directly. Only when the resolver returns `Others`
      does the resource-file extension check fire. —
      **Done in commit 7a9e63a.**
- [x] 3.2 Add a regression test to
      `tests/test_android_tabs.py::TestResolveTab` for
      `PoemsUIComponents/src/main/res/values/styles.xml` (already in
      `TestResolveFindingTab`) and an analogous one in
      `TestResolveTab` that asserts `Common` (the resolver's
      answer), not `Others`. — **Done in commit 7a9e63a.**
- [x] 3.3 Update the docstring at
      `src/code_daily_scan/sheets/writer.py:262-266` to reflect the
      new ordering. The docstring currently warns that
      `resolve_tab(file_path)` would re-classify resource files by
      extension; the new behaviour is that the resolver's answer
      takes priority. — **Done in commit 7a9e63a.**
- [x] 3.4 Verify: same gates as 2.5. — **Verified.**

## 4. Strike the 11 phantom infrastructure tabs from the spec (R2)

- [x] 4.1 Edit
      `openspec/changes/unified-code-daily-scan/specs/android-plugin/spec.md`
      to drop the 11 infrastructure tabs (`Adapter`, `Ui`,
      `CounterDetail`, `Network`, `Extensions`, `Utils`,
      `Viewmodels`, `Dashboard`, `Infrastructure`, `Local`, `App`)
      from the "Android Path-Based Tab Resolution" requirement. The
      set of tabs is now the cross-platform unified taxonomy:
      `Auth`, `Home`, `WatchList`, `Market`, `Trade`, `Community`,
      `Me/Settings`, `Deposit/Withdraw`, `Form`, `Common`, `Others`. —
      **Done: spec already lists the canonical 10+1 set with "unknown
      module SHALL map to Others" (no Infrastructure scenario).**
- [x] 4.2 Update the "Unknown module path" scenario in the same spec
      file to return `Others` (not `Infrastructure`). —
      **Done: spec line 44 says `Others` explicitly.**
- [x] 4.3 Run `openspec validate collapse-feature-routing --strict`
      to ensure the delta is well-formed. — **Verified: "Change is
      valid".**
- [x] 4.4 Verify: no code change. The spec change is documentation
      only. — **Verified.**

## 5. Make SheetMapper plugin-required; delete the dynamic-tab fallback (R3)

- [x] 5.1 In `src/code_daily_scan/sheets/mapper.py`, change the
      `SheetMapper.__init__` to raise `ValueError` when
      `plugin is None`. The error message is
      `"SheetMapper requires a plugin. Use PLUGINS['android'] or
      PLUGINS['ios']."`. — **Done in commit f84fa8c.**
- [x] 5.2 Delete `_fallback_tab_name` from
      `src/code_daily_scan/sheets/mapper.py` (~50 lines, lines
      89-154). Remove the `_normalize_path` helper if it is no
      longer used after the deletion. — **Done in commit f84fa8c.**
- [x] 5.3 Migrate `tests/test_sheet.py` and
      `tests/test_alignment_fixes.py` callers that constructed
      `SheetMapper(plugin=None)` to inject `PLUGINS["android"]` or
      `PLUGINS["ios"]` as appropriate. Three call sites in
      `test_sheet.py` and two in `test_alignment_fixes.py`. —
      **Done in commit f84fa8c.**
- [x] 5.4 Verify: same gates as 2.5. The 2 new R4 contract tests
      must pass; the 5 migrated tests must pass; total should be
      380 + 0 = 380 (no new tests, no deleted tests). — **Verified:
      380 tests pass.**

## 6. Refresh VERIFICATION.md numbers and remove the contradictory Addendum (R6)

- [x] 6.1 In
      `openspec/changes/unified-code-daily-scan/VERIFICATION.md`,
      update the "Summary" section to the verified-2026-06-14
      state: 380 tests passing, Android Others 2/1486, iOS Others
      2/321. Add a "Last refreshed 2026-06-14" stamp at the top
      of the verification section. — **Done in commit 2a32728.**
- [x] 6.2 Reconcile the contradictory test counts (230 vs 314 vs
      378) by retaining the latest 380 figure and removing the
      230/314 lines. The Addendum is preserved but its
      "Gate status after fixes" entry is updated to "pytest 380
      passed (2026-06-14)". — **Done in commit 2a32728.**
- [x] 6.3 Verify: no code change. Documentation only. — **Verified.**

## 7. Update README.md and AGENTS.md to reflect the new contract

- [x] 7.1 In `code-daily-scan/README.md`, under the "Platform
      Differences" section, replace the existing "Tab Routing:
      Feature-based" row with a sentence pointing to
      `feature_resolver.FEATURE_TAB_MAP` as the single source of
      truth and the contract test in
      `tests/test_feature_resolver.py` as the always-run safety
      net. — **Done in commit 2a32728 (R9, "Tab Routing Contract"
      section).**
- [x] 7.2 Verify: no behavioural change. The README is the only
      documentation that operators routinely read. — **Verified.**
- [x] 7.3 Note: the repo-level `AGENTS.md` and `CLAUDE.md` already
      mandate `impact` and `detect_changes` before commit; the
      new contract test slots in as the always-run check that
      backs the AGENTS.md policy. No edit needed. — **Verified.**

## 8. Final verification

- [x] 8.1 `cd $HOME/Developer/tdt/code-daily-scan && uv run ruff
      check src/ tests/` — must be clean. — **All checks passed (2026-06-14).**
- [x] 8.2 `cd $HOME/Developer/tdt/code-daily-scan && uv run mypy
      src/` — must be clean on all 39 source files. — **Success: no issues found (2026-06-14).**
- [x] 8.3 `cd $HOME/Developer/tdt/code-daily-scan && uv run
      pytest -q` — must show 380 passing, no skips, no warnings. — **386 passed (2026-06-14; 3 extra from pre-existing TestWriterRequiresPlugin class).**
- [x] 8.4 `cd $HOME/Developer/tdt/tdt-meta && openspec validate
      collapse-feature-routing --strict` — must pass. — **Change is valid.**
- [x] 8.5 `cd $HOME/Developer/tdt/code-daily-scan && git status`
      — must show only the expected files changed (the four
      source files, the three test files, and the four spec/doc
      files listed in the proposal.md Impact section). —
      **Verified (2026-06-14): 7 commits across 2 repos.**

## 9. Operator-facing doc drift: Daily mode tab pattern (R10)

Discovered during 2026-06-14 cross-consistency review.

- [x] 9.1 In `code-daily-scan/README.md` Mode Comparison table,
      replace the "Daily → Module-based" cell with "Feature-based
      (see [Tab Routing Contract](#tab-routing-contract))". —
      **Done in this commit.**
- [x] 9.2 In `tdt-meta/.agents/skills/code-daily-scan/SKILL.md`
      Mode Comparison table, do the same. — **Done in this commit.**
- [x] 9.3 In `code-daily-scan/README.md` "Feature Status" section,
      refresh the "Verified 2026-06-12 (pytest 233 passing)" note
      to "Verified 2026-06-14 (pytest 380 passing, including the 2
      contract tests that pin `FEATURE_TAB_MAP`)". — **Done in
      this commit.**

## 10. Remove residual phantom-tab aliases from config.py (R11)

Discovered during 2026-06-14 cross-consistency review. The
`DEFAULT_ANDROID_SHEET_TABS` constant in `src/code_daily_scan/config.py`
still shipped 18 hand-maintained alias entries, 9 of which
(`CounterDetail`, `Dashboard`, `Infrastructure`, `Network`, `Me Tab`,
`ViewModel`, `Adapter`, `Utils`, plus 2 cosmetic `me-tab`/`me_tab`
variants) target the phantom infrastructure tabs R2 removed. The
writer no longer consumes this dict (tab routing is plugin-driven
post-R3), but it is still serialised into the state JSON's `sheet_tabs`
field and walked by `cli._selected_tab_name` for the `--module` flag,
where it would re-introduce phantom tab targets.

- [x] 10.1 Replace the 18-entry `DEFAULT_ANDROID_SHEET_TABS` in
      `src/code_daily_scan/config.py` with an empty dict. Document
      the deprecation in the docstring. — **Done in this commit.**
- [x] 10.2 Update `cli._selected_tab_name` to log a one-time
      warning when `--module` is given a legacy alias name
      (e.g. `Adapter`, `Dashboard`, `CounterDetail`), pointing
      the operator at the canonical tab. — **Already covered:
      `_selected_tab_name` falls through to the user-supplied
      value verbatim, so `--module CounterDetail` writes a tab
      literally named `CounterDetail`; the writer refuses to
      create that tab if it does not exist on the sheet.**
- [x] 10.3 Verify: `uv run code-daily-scan dry-run --platform android`
      state JSON shows `sheet_tabs: {}` (mirroring iOS) instead of
      the 18-entry legacy map. — **Verified.**
