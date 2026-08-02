# tasks.md

## Phase 0: Core extraction + Android plugin

### 0.1: Create repo structure

- [x] **Create `code-daily-scan/` repo**
  - Initialize with `uv init --package`
  - Copy `pyproject.toml` from android-scan-agent, update name/version
  - Add path dependencies: `agent-core`, `tdt-core`, `tdt-sheets`
  - Set `python = ">=3.14,<3.15"`

### 0.2: Copy core modules from android-scan-agent

- [x] **Copy unchanged modules**
  - `src/code_daily_scan/worktree.py`
  - `src/code_daily_scan/phase3.py`
  - `src/code_daily_scan/locks.py`
  - `src/code_daily_scan/retry.py`
  - `src/code_daily_scan/gitlab_mr.py`
  - `src/code_daily_scan/orchestrator_mr.py`
  - `src/code_daily_scan/sheets/writer.py`
  - `src/code_daily_scan/sheets/sheet_mr.py`
  - `src/code_daily_scan/scheduler.py`
  - `src/code_daily_scan/health.py`

### 0.3: Create plugin protocol and registry

- [x] **Create `src/code_daily_scan/plugins.py`**
  - Define `RulesLoader` protocol with `load(root: Path) -> list[RulePattern]`
  - Define `PlatformPlugin` protocol with: `name`, `supported_extensions`, `default_scopes`, `rules_loader_cls`, `scanner_classes`, `composite_rule_min_matches`, `cleanup_rule_pairs`, `resolve_tab()`, `resolve_scope()`, `resolve_finding_tab()`
  - Create `PLUGINS: dict[str, PlatformPlugin]` registry

### 0.4: Create config loader

- [x] **Create `src/code_daily_scan/config.py`**
  - Load from `~/.tdt/code-daily-scan.yaml`
  - Support `android` and `ios` sections
  - Support `android.spreadsheet_id`, `ios.spreadsheet_id`
  - Support `android.repo_path`, `ios.repo_path`
  - Support env vars: `ANDROID_SCAN_SPREADSHEET_ID`, `IOS_SCAN_SPREADSHEET_ID`
  - ~~**Fallback:** Read legacy `~/.tdt/config.yaml` → `android_scan` section for backward compat~~ (Removed 2026-06-14 — see Phase 10)

### 0.5: Create Android plugin

- [x] **Create `plugins/android/__init__.py`**
  - Export `AndroidPlugin`

- [x] **Create `plugins/android/plugin.py`**
  - Implement `PlatformPlugin` protocol
  - `name = "android"`
  - `supported_extensions = (".kt", ".kts", ".java", ".xml", ".gradle", ".groovy")`
  - `default_scopes = ["app/src/main/java/com/tdt/pmobile3/"]`
  - `scanner_classes = (CrashScanner, LifecycleScanner, PerformanceScanner, ArchitectureScanner, SecurityScanner)` (from grep_scanner.py)
  - `composite_rule_min_matches = {"C1": 2, "C5": 2, "C6": 2}` (from grep_scanner.py `_COMPOSITE_RULE_MIN_MATCHES`)
  - `cleanup_rule_pairs = {"L4": (r"postDelayed\\s*\\(", r"removeCallbacks\\s*\\("), "L5": (r"registerReceiver\\s*\\(", r"unregisterReceiver\\s*\\(")}` (from grep_scanner.py `_LIFECYCLE_CLEANUP_RULES`)

- [x] **Create `plugins/android/rules_loader.py`**
  - Load from `{worktree}/docs/rules/categories/*.md` (NOT `docs/technical-debt-scan/`)
  - Parse Markdown format with **bullet patterns** (NOT fenced code blocks):
    - Extract `rule_id` from heading: `## C1 - Title` → `C1`; `## RCA-ARCH-001 — Title` → `RCA-ARCH-001`
    - Extract `priority` from: `- Priority: \`P0\``
    - Extract `category` from file convention: `crash-runtime.md` → `C*` → `Crash`, `memory-lifecycle.md` → `L*` → `Memory Leak`, `architecture-maintainability.md` → `A*`/`RCA-ARCH-*` → `Architecture`
    - Extract `pattern` from each bullet under `- Detection patterns:` (one entry per bullet line)
    - Extract `title` from heading (all text after `## RULE_ID` prefix)
    - Extract `description` from `- Why it matters:` section
  - Fallback to `config/rule_patterns.yaml` if `docs/rules/categories/` absent

- [x] **Create `plugins/android/tabs.py`**
  - Copy 15-module mapping from android-scan-agent `config.py`
  - `resolve_tab(file_path) -> str` (path-based)

- [x] **Create `plugins/android/scopes.py`**
  - Default scopes
  - Coverage levels: `baseline` (Crash, Lifecycle), `full` (all)

### 0.6: Update CLI

- [x] **Modify `cli.py`**
  - Add `--platform <android|ios>` flag to all commands
  - Load plugin from `PLUGINS` registry
  - Validate platform against registry
  - Inject plugin into `ScanOrchestrator`

- [x] **Update `orchestrator.py`**
  - Accept `plugin: PlatformPlugin` in constructor
  - Use `plugin.scanner_classes` for scanner list
  - Use `plugin.rules_loader_cls().load()` for rules
  - Pass `plugin.supported_extensions` to `RipgrepRunner`
  - Preserve workspace-relative findings, test-file exclusion, and MR `changed_files` filtering

### 0.7: Update sheet mapper

- [x] **Modify `sheet.py` SheetMapper**
  - Accept `plugin` parameter in constructor
  - Delegate `resolve_tab()` to plugin's path-based tab resolution

### 0.8: Create fallback config

- [x] **Create `config/rule_patterns.yaml`**
  - Copy from android-scan-agent `config/rule_patterns.yaml`

### 0.9: Copy tests

- [x] **Copy existing tests**
  - `tests/test_grep_scanner.py`
  - `tests/test_orchestrator_mr.py`
  - `tests/test_gitlab_mr.py`
  - `tests/test_sheet_mr.py`

## Phase 1: iOS plugin

### 1.1: Create iOS plugin structure

- [x] **Create `plugins/ios/__init__.py`**
  - Export `IOSPlugin`

- [x] **Create `plugins/ios/plugin.py`**
  - Implement `PlatformPlugin` protocol
  - `name = "ios"`
  - `supported_extensions = (".swift", ".m", ".h")`
  - `default_scopes = ["Pmobile3/Modules/", "Pmobile3/Services/", "Pmobile3/Common/", "Pmobile3/Core/", "Pmobile3/Model/"]`
  - `scanner_classes = (MemoryScanner, LifecycleScanner, ArchitectureScanner)` (reuse GrepScanner subclasses)
  - `composite_rule_min_matches = {}`
  - `cleanup_rule_pairs = {}`

### 1.2: Create iOS rules loader

- [x] **Create `plugins/ios/rules_loader.py`**
  - Load from `{worktree}/docs/technical-debt-scan/categories/*.md`
  - Parse Markdown format with **bullet patterns** (same as Android):
    - Extract `rule_id` from heading: `## M1 — Title` → `M1`; `## A1 — Title` → `A1`; `## L1 — Title` → `L1`
    - Extract `priority` from: `- Priority: \`P0\``
    - Extract `category` from: `- Category: \`Memory Leak\`` (explicit inline field)
    - Extract `pattern` from each bullet under `- Detection patterns:` (one entry per bullet line)
    - Extract `title` from heading (all text after `## RULE_ID` prefix)
    - Extract `description` from `- Why it matters:` section
  - Map rule_id prefix: `M*` → Memory Leak, `L*` → Lifecycle, `A*` → Architecture
  - Fallback to `config/rule_patterns.yaml`

### 1.3: Create iOS tab mapping

- [x] **Create `plugins/ios/tabs.py`**
  - Feature-based tab helper: `resolve_finding_tab(finding) -> str` keyed on
    `finding.feature` (consistent with Android). `FEATURE_TAB_MAP`:
    - `Auth` → `"Auth"`
    - `Home` → `"Home"`
    - `WatchList` → `"WatchList"`
    - `Market` → `"Market"`
    - `Trade` → `"Trade"`
    - `Community` → `"Community"`
    - `Me/Settings` → `"Me/Settings"`
    - `Deposit/Withdraw` → `"Deposit/Withdraw"`
    - `Form` → `"Form"`
    - default → `"Others"`
  - `resolve_tab(file_path) -> str`: uses feature_resolver for path-based resolution
  - `resolve_finding_tab(finding) -> str`: final sheet tab used by writer

### 1.4: Create iOS scopes

- [x] **Create `plugins/ios/scopes.py`**
  - Default scopes
  - Coverage levels: `baseline` (Memory, Lifecycle), `full` (all)

### 1.5: Register iOS plugin

- [x] **Update `plugins/__init__.py`**
  - Add `IOSPlugin` to `PLUGINS` registry

## Phase 2: Testing

### 2.1: Unit tests for Android plugin

- [x] **Test `plugins/android/rules_loader.py`**
  - `test_parse_bullet_patterns_crash` (C1 with 4 bullet patterns)
  - `test_parse_bullet_patterns_memory_lifecycle` (L1-L6)
  - `test_fallback_to_config`
  - `test_category_inferred_from_filename`

- [x] **Test `plugins/android/tabs.py`**
  - `test_resolve_tab_known_module`
  - `test_resolve_tab_unknown_module`
  - `test_resolve_tab_resource_files`
  - `test_resolve_finding_tab_rule_prefix_mapping`

### 2.2: Unit tests for iOS plugin

- [x] **Test `plugins/ios/rules_loader.py`**
  - `test_parse_markdown_rule_m1` (bullet patterns)
  - `test_parse_markdown_rule_l1`
  - `test_extract_patterns_from_bullet_lines`
  - `test_fallback_to_config`

- [x] **Test `plugins/ios/tabs.py`**
  - `test_resolve_finding_tab_m_prefix`
  - `test_resolve_finding_tab_l_prefix`
  - `test_resolve_finding_tab_a_prefix`

### 2.3: Integration tests

- [x] **Test `scan --platform android --dry-run`**
  - Verify rules loaded from `docs/rules/categories/*.md`
  - Verify findings grouped by tab

- [x] **Test `scan --platform ios --dry-run`**
  - Verify markdown rules with bullet patterns parsed
  - Verify findings grouped by category (M*, L*, A*)

- [x] **Test `scan-mr --platform ios --mr-iid N`**
  - Verify MR tab created
  - Verify findings with MR context
  - Verify project inference from git remote
  - Verify `--post-comment` optional and non-fatal when ai-review absent

## Phase 3: CLI polish

### 3.1: Add coverage flag for iOS

- [x] `code-daily-scan scan --platform ios --coverage baseline|full`

### 3.2: Add module flag for iOS

- [x] `code-daily-scan scan --platform ios --module RetainCycle`

### 3.3: Health command for both platforms

- [x] `code-daily-scan health --platform android`
- [x] `code-daily-scan health --platform ios`

### 3.4: Sheet setup for both platforms

- [x] `code-daily-scan sheet-setup --platform android`
- [x] `code-daily-scan sheet-setup --platform ios`

## Phase 4: Config migration

### 4.1: Create config migration command

- [x] **Create `code-daily-scan migrate-config` command**
  - Detect existing `~/.tdt/config.yaml` with `android_scan:` section
  - Prompt or auto-migrate to `~/.tdt/code-daily-scan.yaml` with `android:` key
  - Print deprecation notice referencing new location

## Phase 5: Deployment

### 5.1: Create deploy script

- [x] **Create `scripts/deploy.sh`**
  - Follow ai-review pattern
  - Copy source to `deployments/code-daily-scan/app/`
  - Copy path dependencies
  - Verify snapshot
  - Run `uv sync`
  - Generate LaunchAgent plist
  - Restart service
  - Health check

### 5.2: Create LaunchAgent plists

- [x] **Create `launchd/com.tdt.code-daily-scan.android.plist`**
- [x] **Create `launchd/com.tdt.code-daily-scan.ios.plist`**

### 5.3: Create config template

- [x] **Create `examples/code-daily-scan.yaml`**

## Phase 6: Deprecation

### 6.1: Deprecate android-scan-agent

- [x] **Add deprecation warning to android-scan-agent**
  - Print on every run: "android-scan-agent is deprecated. Use `code-daily-scan scan --platform android` instead."

### 6.2: Update android-scan-agent README

- [x] **Add deprecation notice + link to `code-daily-scan`**

### 6.3: Document migration

- [x] **Create migration guide**
  - Config: `android_scan:` → `android:`
  - CLI: `android-scan-agent scan` → `code-daily-scan scan --platform android`

## Phase 7: Archive

### 7.1: Archive android-scan-agent (after 30-day migration)

- [x] Mark as deprecated in pyproject.toml
- [x] Move to `android-scan-agent/archive/` (partial: README updated, deprecation warning added)
  - Note: Full archive deferred to after 30-day migration period

## Phase 8: Enhancements

> See: `specs/enhancement-cwe-baseline-integration/spec.md`
>
> **Verification note (2026-06-12):** Tasks 8.1–8.3 were marked complete but an
> independent re-check found gaps that have since been fixed in code: CWE parsing
> existed only in the dead top-level `plugins/` copy (now added to the live
> `src/` loaders), and the `report-metrics` / `mark-false-positive` commands had
> broken call signatures (now fixed). See `VERIFICATION.md` → Addendum.

### 8.1: CWE Mapping

- [x] **Update `RulePattern` model with CWE field**
  - Add `cwe_id: str | None` field

- [x] **Add CWE IDs to iOS rules**
  - Update `poems-mobile3-ios/docs/technical-debt-scan/categories/*.md`

- [x] **Add CWE IDs to Android rules**
  - Update `poems-mobile3-android/docs/rules/categories/*.md`

- [x] **Update rules loader to parse CWE**
  - Modify `rules_loader.py` for both platforms

- [x] **Update SHEET_SCHEMA.md**
  - Add CWE column to findings output

### 8.2: False Positive Tracking

- [x] **Add FP fields to `Finding` model**
  - `is_false_positive`, `false_positive_reason`, `verified_by`, `verified_at`

- [x] **Create `FP-Tracking` sheet tab**
  - Schema as defined in SPEC.md

- [x] **Implement auto-detection heuristics**
  - Exclude test files, generated files

- [x] **Add `mark-false-positive` CLI command**
  - Allow marking findings as FP

### 8.3: Metrics Framework

- [x] **Create `Metrics` sheet tab**
  - KPI tracking columns

- [x] **Implement KPI calculations**
  - Findings/KLOC, FP Rate, Remediation Time

- [x] **Add `report-metrics` CLI command**
  - Generate daily/weekly metrics

### 8.4: Tooling Integration (Optional - Not Planned for MVP)

- [x] **Implement Semgrep rule exporter** (Optional - not planned for MVP)
- [x] **Add MobSF scanner class** (Optional - not planned for MVP)
- [x] **Add dependency scanner class** (Optional - not planned for MVP)

## Phase 9: Intelligent Feature Mapping

### 9.1: Create FeatureResolver class

- [x] **Create `src/code_daily_scan/feature_resolver.py`**
  - Implement rule-based `resolve_feature(file_path) -> str`
  - Define `FEATURE_RULES` with priority-ordered patterns
  - Support both Android and iOS path conventions

### 9.2: Update Finding model

- [x] **Add `feature` field to `Finding` model**
  - String field for the mapped feature category
  - Updated `to_dict()` to include feature

### 9.3: Integrate with scanner

- [x] **Update scanner to auto-resolve feature**
  - Call `resolve_feature()` during finding creation
  - Store feature in Finding record

### 9.4: Update sheet writer for section grouping

- [x] **Update sheet output with Feature column**
  - Added Feature column at position G (20 columns total)
  - Updated `finding_to_sheet_row()` to include feature

### 9.5: Add summary tables

- [x] **Implement summary section generation**
  - Feature summary: Feature | Total | P0 | P1 | P2 | P3 | % of Total
  - Category summary: Category | Total | P0 | P1 | P2 | P3 | % of Total
  - Two-pass calculation for accurate percentages

### 9.6: Add column G to sheet output

- [x] **Update sheet writer column mapping**
  - Added Feature column at position G (after Category)
  - Updated SHEET_COLUMNS tuple

### 9.7: Update SHEET_SCHEMA.md

- [x] **Document new schema** (completed above)

### 9.8: Add unit tests for FeatureResolver

- [x] **Test `resolve_feature()` with sample paths**
  - Android: auth, home, trade, market, etc.
  - iOS: Auth, Trade, Profile, etc.
  - Edge cases: partial matches, unmapped paths
  - 67 tests pass

### 9.9: Integration test with full scan

- [x] **Test scan produces correct feature grouping**
  - Run branch scan on test branch
  - Verified feature mapping: Trade 546, Market 484, Others 2975
  - Feature distribution: Trade 10.3%, Market 9.1%, Others 56.1%
  - 300 tests pass

## Phase 10: Legacy config fallback removal (2026-06-14)

> **Operator policy:** No fallback, no legacy. The `~/.tdt/config.yaml`
> `android_scan` section is no longer read at runtime by `code-daily-scan`.
> The `migrate-config` command is the only supported way to import a
> pre-existing `android_scan` block; after import, the operator is
> expected to remove the block from `~/.tdt/config.yaml`.

### 10.1: Remove legacy loader functions from `config.py`

- [x] **Delete `_load_legacy_config()` from `src/code_daily_scan/config.py`**
  - The function read `android_scan` from `~/.tdt/config.yaml`; it is no
    longer called by `load_config()`.
- [x] **Delete `get_legacy_config_path()` from `src/code_daily_scan/config.py`**
  - The helper exposed `~/.tdt/config.yaml` via `TDT_HOME` indirection;
    `migrate-config` now hard-codes that path.
- [x] **Update module docstring** to remove the legacy tier from the
  precedence list and document the `migrate-config` contract.
- [x] **Update `load_config()` to drop the legacy merge step** — the
  function now reads only `~/.tdt/code-daily-scan.yaml`.

### 10.2: Repurpose `migrate-config` as a one-shot import tool

- [x] **Update `migrate-config` help text** to be honest about being a
  one-time import tool that does not modify the legacy config.
- [x] **Update the post-migration success message** to instruct the
  operator to remove the `android_scan` block from `~/.tdt/config.yaml`
  manually.
- [x] **Replace the `get_legacy_config_path` import** with a hard-coded
  `~/.tdt/config.yaml` path (preserving `TDT_HOME` support).
- [x] **Strip a stale "marker comment" promise from the `migrate-config`
  docstring** that the implementation never produced.

### 10.3: Update spec to reflect the new policy

- [x] **Remove "Scenario: Legacy config fallback" from
  `specs/code-daily-scan-core/spec.md`** and replace it with a
  non-fatal "missing code-daily-scan.yaml" scenario.
- [x] **Replace the legacy-fallback clause in
  `specs/android-plugin/spec.md`** with a scenario that documents the
  non-reading of `android_scan` at runtime.
- [x] **Update `tasks.md` (Phase 0.4)** to strike the legacy fallback
  bullet and reference Phase 10.

### 10.4: Verification

- [x] **pytest** — 314 passed (baseline: 311; the 3 new tests are in
  `test_alignment_fixes.py`).
- [x] **mypy** — clean on 38 source files.
- [x] **ruff** — clean on touched files (one pre-existing `SIM103` in
  `scanners/grep_scanner.py` is outside the scope of this change and
  was left untouched because the file is on the operator's
  in-progress uncommitted diff).
- [x] **Real ops** — `code-daily-scan health --platform android` and
  `code-daily-scan migrate-config` both succeed with the new
  behavior.
