## ADDED Requirements

### Requirement: Platform Plugin Architecture

The system SHALL provide a platform-agnostic scanning core that delegates all platform-specific behavior to a `PlatformPlugin` implementation resolved from a registry keyed by platform name.

The core SHALL NOT contain Android- or iOS-specific logic. Each plugin MUST expose: `name`, `supported_extensions`, `default_scopes`, `rules_loader_cls`, `scanner_classes`, `composite_rule_min_matches`, `cleanup_rule_pairs`, and the methods `resolve_tab()`, `resolve_scope()`, and `resolve_finding_tab()`.

#### Scenario: Resolve a registered platform plugin

- **WHEN** the CLI is invoked with `--platform android` or `--platform ios`
- **THEN** the core SHALL look up the matching plugin in the `PLUGINS` registry and inject it into the orchestrator

#### Scenario: Unknown platform is rejected

- **WHEN** the CLI is invoked with a platform name not present in the registry
- **THEN** the system SHALL exit with a non-zero code and report the unknown platform together with the list of available platforms

### Requirement: Unified CLI Surface

The system SHALL expose a single `code-daily-scan` CLI in which every command accepts a `--platform <android|ios>` option, including `scan`, `scan-mr`, `scan-branch`, `health`, `sheet-setup`, and `migrate-config`.

#### Scenario: Daily scan for a platform

- **WHEN** the user runs `code-daily-scan scan --platform android`
- **THEN** the system SHALL scan the configured Android repository and write findings to the configured Android spreadsheet

#### Scenario: Module-scoped scan

- **WHEN** the user runs `scan --platform <p> --module <tab>`
- **THEN** the system SHALL write only the findings whose resolved tab matches `<tab>`

#### Scenario: Coverage level selection

- **WHEN** the user runs `scan --platform ios --coverage baseline`
- **THEN** the system SHALL scan only the categories defined as the plugin's `baseline` coverage level

### Requirement: Configuration Resolution

The system SHALL resolve configuration with the precedence: CLI flags, then environment variables, then `~/.tdt/code-daily-scan.yaml`, then built-in defaults.

The config file MUST support per-platform `android` and `ios` sections, each providing at least `repo_path` and `spreadsheet_id`. The environment variables `ANDROID_SCAN_SPREADSHEET_ID` and `IOS_SCAN_SPREADSHEET_ID` MUST override the corresponding file value.

The system SHALL NOT read `~/.tdt/config.yaml` or any legacy `android_scan` section at runtime. The `migrate-config` command is the only supported way to import a pre-existing `android_scan` block from `~/.tdt/config.yaml` into `~/.tdt/code-daily-scan.yaml`.

#### Scenario: Per-platform spreadsheet selection

- **WHEN** a scan runs for a platform with `spreadsheet_id` set in its config section
- **THEN** findings SHALL be written to that platform's spreadsheet, independent of the other platform

#### Scenario: Missing code-daily-scan.yaml is non-fatal

- **WHEN** `~/.tdt/code-daily-scan.yaml` is absent and the operator has not run `migrate-config`
- **THEN** the system SHALL fall through to built-in defaults and report `config_present: false` from the `health` command — it SHALL NOT silently read `~/.tdt/config.yaml`

### Requirement: Dynamic Rule Loading From Target Repo

The system SHALL load detection rules from the target repository worktree at scan time using the plugin's `rules_loader_cls`, and SHALL fall back to the bundled `config/rule_patterns.yaml` snapshot only when the repository rule documents are absent.

#### Scenario: Rules read from worktree

- **WHEN** a scan runs and the platform's rule documents exist in the worktree
- **THEN** the system SHALL parse those documents into `RulePattern` objects rather than using the bundled snapshot

#### Scenario: Fallback to bundled snapshot

- **WHEN** the platform's rule documents are missing from the worktree
- **THEN** the system SHALL load rules from `config/rule_patterns.yaml` and mark the run as degraded

### Requirement: Worktree-Based Scanning

The system SHALL run each scan against a git worktree of the target repository, created before scanning and removed after scanning, including cleanup of orphaned worktree entries.

#### Scenario: Worktree lifecycle

- **WHEN** a scan begins
- **THEN** the system SHALL create or reuse a worktree on the configured branch (default `main`), and after the scan completes or fails it SHALL remove the worktree

#### Scenario: Insufficient disk space

- **WHEN** available disk space is below the configured minimum free ratio
- **THEN** the system SHALL decline to create a worktree and report the degraded reason

### Requirement: Single Source Of Truth For Tab Names

The system SHALL treat `feature_resolver.FEATURE_TAB_MAP` as the only sanctioned source of tab names. The function `feature_resolver.feature_to_tab()` SHALL be the only sanctioned way to map a `Finding.feature` value to a tab name. Any other code path that produces a tab name MUST raise an error in tests, and MUST be backed by a test that pins its output to the values in `FEATURE_TAB_MAP`.

The system MUST include a contract test in `tests/test_feature_resolver.py` that asserts `FEATURE_TAB_MAP` is a fixed, ordered set of strings. The test MUST fail if any value in `FEATURE_TAB_MAP` is added, removed, or renamed, forcing the change to be intentional and reviewed.

#### Scenario: Tab name vocabulary is pinned

- **WHEN** a developer adds, removes, or renames a value in `feature_resolver.FEATURE_TAB_MAP`
- **THEN** the contract test in `test_feature_resolver.py` SHALL fail until the test is updated in the same commit

#### Scenario: Mapper fallback is bounded by FEATURE_TAB_MAP

- **WHEN** `sheets/mapper.py:_DEFAULT_MODULE_PATTERNS` is reviewed
- **THEN** every `(fragment, tab_name)` pair in that tuple MUST have `tab_name` present as a key in `FEATURE_TAB_MAP`. A contract test in `tests/test_sheet.py` SHALL enforce this.

### Requirement: SheetMapper Plugin-Required

`SheetMapper` MUST be constructed with a `plugin` argument. Calling `SheetMapper()` with `plugin=None` MUST raise a `ValueError` with a message directing the caller to inject a `PlatformPlugin` instance from `PLUGINS`. The `_fallback_tab_name` dynamic TitleCase generator in `sheets/mapper.py` SHALL be deleted.

#### Scenario: Missing plugin raises clearly

- **WHEN** a caller constructs `SheetMapper()` without a plugin
- **THEN** the constructor SHALL raise `ValueError("SheetMapper requires a plugin. Use PLUGINS['android'] or PLUGINS['ios'].")`

#### Scenario: SheetMapper with a plugin delegates tab resolution

- **WHEN** `SheetMapper(plugin=PLUGINS["android"]).resolve_tab(path)` is called
- **THEN** the result SHALL be identical to `PLUGINS["android"].resolve_tab(path)`. The contract is preserved.

### Requirement: Branch-Scan Tab Name Is Deterministic And Reusable

The system SHALL build the branch-scan destination tab name from
`(source_branch, --feature)` using the canonical convention
implemented in `gitlab_branch._build_tab_name`. The result is
**deterministic** for a given input pair, so the first run creates the
tab via `client.ensure_sheet` and every subsequent run reuses the
same tab via `client.batch_clear` + `client.batch_write` — never
creating a duplicate.

The convention is:

* No `--feature`: `BRANCH-{branch-slug}`
* With `--feature`: `BRANCH-{branch-slug}-{feature-slug}`

Where:

* `{branch-slug}` is the result of `re.sub(r"[^A-Za-z0-9._-]+", "-",
  source_branch).strip("-_")` — slashes collapse to dashes, but
  `.`, `_` and `-` are preserved so semver branches
  (`release/v3.3.54_develop_27_06_2026`) and underscore-suffixed Jira
  names (`develop_newdesignsystem`) round-trip readably.
* `{feature-slug}` is the result of `_normalize_feature_name`:
  path-style prefixes (`modules/`, `Modules/`, `feature/`) and Android
  package markers (`com`, `tdt`, `pmobile3`, `app`, `org`, `io`,
  `poemsmobile3`, `src`, `main`, `java`, `kotlin`, `swift`) are
  dropped; remaining segments are TitleCased and concatenated without
  separators. iOS slash form (`Modules/Profile/Ewallet`), iOS bare
  form (`Ewallet`), Android dot form (`com.tdt.pmobile3.ewallet`) and
  Android slash form (`com/tdt/pmobile3/ewallet`) all collapse to the
  same canonical slug for a given feature.

The contract is pinned by `tests/test_branch_tab_naming.py`; any
change to the convention MUST update those tests in the same commit.

#### Scenario: Subsequent run reuses the same tab

- **WHEN** a branch scan is executed twice with the same `--source-branch` and `--feature` values
- **THEN** both runs SHALL write to the same tab (verified by `sheet_write.tab_name` being equal and by the post-run tab list containing exactly one matching tab)
- **AND** the second run SHALL NOT create a duplicate tab

#### Scenario: Different input forms collapse to the same tab

- **WHEN** the user runs a branch scan with `--feature com.tdt.pmobile3.ewallet` and later the same scan with `--feature ewallet`
- **THEN** both runs SHALL land on the tab `BRANCH-{branch-slug}-Ewallet`

#### Scenario: Semver branch name preserves version info in the tab

- **WHEN** `--source-branch release/v3.3.54_develop_27_06_2026` is used
- **THEN** the tab name SHALL contain the literal segments `v3.3.54` and `develop_27_06_2026` (not `v3-3-54` and `develop-27-06-2026`)

#### Scenario: iOS and Android feature inputs produce a single tab name

- **WHEN** the user runs the same branch scan twice on iOS, once with `--feature Modules/Profile/Ewallet` and once with `--feature ewallet`
- **THEN** both runs SHALL land on the tab `BRANCH-{branch-slug}-ProfileEwallet` (the iOS slash form's segments `Profile` and `Ewallet` survive; the bare form is not the canonical form, so the user is steered toward the slash form by the test contract)

### Requirement: Finding Model And Workspace-Relative Paths

The system SHALL represent each finding with a stable `Finding` model whose `file_path` is workspace-relative (never absolute) and whose final spreadsheet `tab` is resolved via `plugin.resolve_finding_tab(finding)`.

Test and generated files MUST be excluded from findings (for example paths containing `/test/`, `/androidTest/`, `/androidTestUtils/`).

#### Scenario: Workspace-relative path

- **WHEN** a finding is produced for a file in the worktree
- **THEN** the finding's `file_path` SHALL be relative to the repository root, matching the structure of the source repo

#### Scenario: Test files excluded

- **WHEN** a candidate match is located in a test or generated source path
- **THEN** the system SHALL NOT emit a finding for that match
### Requirement: Scanner Pipeline And Phase3 Enrichment

The system SHALL execute the plugin's `scanner_classes` (ripgrep-based grep scanners) using the plugin's `supported_extensions`, applying `composite_rule_min_matches` and `cleanup_rule_pairs`, and SHALL then run Phase3 post-processing for context enrichment, confidence scoring, and token-budget enforcement.

#### Scenario: Composite rule suppression

- **WHEN** a composite rule requires a minimum number of matches in a file and fewer matches are present
- **THEN** the system SHALL NOT emit a finding for that rule in that file

#### Scenario: Cleanup-aware rule suppression

- **WHEN** a cleanup-aware rule's trigger pattern and its matching cleanup pattern both occur in the same file
- **THEN** the system SHALL suppress the finding for that rule

#### Scenario: Token budget enforcement

- **WHEN** Phase3 enrichment would exceed the configured token budget
- **THEN** the system SHALL stop further enrichment and mark the run as degraded rather than overspend

### Requirement: Concurrency Lock

The system SHALL acquire a per-platform lock before scanning and release it afterward, so concurrent scans for the same platform do not run simultaneously.

#### Scenario: Lock already held

- **WHEN** a scan starts for a platform whose lock is already held
- **THEN** the system SHALL exit with code 2 and report the run as skipped (not an error)

### Requirement: Exit Code Contract

The system SHALL use a consistent exit-code contract across commands: `0` success, `1` error, `2` lock held (skip, not error), `3` MR not found.

#### Scenario: MR not found

- **WHEN** an MR-scoped command targets an MR IID that does not exist
- **THEN** the system SHALL exit with code 3
