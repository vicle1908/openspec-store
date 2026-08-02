# Spec: code-daily-scan — Docs-Repo as Canonical Rule Source

## MODIFIED Requirements

### Requirement: Platform plugins load rules from Markdown categories

The platform plugins for `android` and `ios` SHALL resolve a list of rule-category roots in **priority order** (docs-repo first, local mirror second, legacy YAML third) and load rules from the highest-priority root that contains at least one matching markdown file **for the requested category**. The plugin MUST validate that the resolved docs-repo rules folder contains all 9 taxonomy files (per the cross-team contract S-1) before treating it as authoritative. If fewer than 9 files are present, the plugin SHALL fall back to the local mirror **for the missing categories only** (not for the whole folder) and emit a `docs_repo_incomplete=true` log line identifying the missing categories.

**Critical:** this is a behavioural change from today's `load_category()` / `load()` methods, which currently **concatenate** results across all available roots. After this change, the methods MUST NOT concatenate; they MUST return the union of (primary_root_results, fallback_root_results_for_missing_categories_only).

#### Scenario: Docs repo is reachable and has the category
- GIVEN a `ScanConfig` whose `rules_repo_path` points at a `poems-mobile3-docs` checkout whose `20.Developments/40.AI/50.RCA/20.AOS/rules/categories/crash-runtime.md` exists
- WHEN `AndroidRulesLoader.load_category("Crash")` is invoked
- THEN the loader MUST return at least the rules found in that markdown file
- AND MUST NOT consult any other root for this category
- AND MUST emit a logger line `resolved_source=docs_repo:<absolute path>` with a 12-char SHA256 prefix of that file's bytes.

#### Scenario: Docs repo has 8/9 categories, missing one
- GIVEN a `poems-mobile3-docs` checkout whose `20.AOS/rules/categories/` contains 8 of the 9 required files (missing `state-mutation.md`)
- WHEN `AndroidRulesLoader.load_category("State Mutation")` is invoked
- THEN the loader MUST fall back to the local mirror `target_root/docs/rules/categories/state-mutation.md`
- AND MUST emit `docs_repo_incomplete=true missing=[state-mutation.md]` followed by `resolved_source=local_mirror:<path>` for that specific category
- AND all other categories MUST still resolve from `docs_repo:` (no global fallback).

#### Scenario: Docs repo reachable but category missing there, present in local mirror
- GIVEN the docs-repo path exists but contains no `crash-runtime.md`
- AND the platform repo's `docs/rules/categories/crash-runtime.md` does
- WHEN `AndroidRulesLoader.load_category("Crash")` is invoked
- THEN the loader MUST return the rules from the local mirror
- AND MUST emit a logger line `resolved_source=local_mirror:<absolute path>`.

#### Scenario: Docs repo unreachable, legacy YAML only
- GIVEN the docs-repo path does not exist
- AND no `target_root/docs/rules/categories/` exists
- WHEN the scanner requests category `Crash` on Android
- THEN the loader MUST fall back to `code-daily-scan/config/rule_patterns.yaml`
- AND MUST emit a logger line `resolved_source=legacy_yaml:rule_patterns.yaml`
- AND the scan MUST complete with exit code 0 in `dry-run` mode (fallback is an acknowledged degraded mode, not an error).

#### Scenario: `rules_repo_path` explicitly empty
- GIVEN the operator sets `rules_repo_path: ""` (or env `CODE_DAILY_SCAN_ANDROID_RULES_REPO=""`)
- WHEN the loader runs
- THEN it MUST skip Priority 1 entirely and use the existing local-mirror then legacy-YAML chain unchanged.

### Requirement: ScanConfig exposes rules_repo_path

`PlatformConfig` (Android and iOS variants) SHALL expose a `rules_repo_path` field of type `Path | None`, defaulting to `None`. When `None`, the runtime SHALL resolve it to `~/Developer/tdt/poems-mobile3-docs` as the implicit default.

#### Scenario: Config file provides the path
- GIVEN `~/.tdt/code-daily-scan.yaml` contains `android.rules_repo_path: ~/Developer/tdt/poems-mobile3-docs`
- WHEN `ScanConfig` is materialised for the android platform
- THEN `config.rules_repo_path` SHALL equal the expanded `Path` of that value.

#### Scenario: Config file omits the path
- GIVEN `~/.tdt/code-daily-scan.yaml` has no `rules_repo_path` key
- WHEN `ScanConfig` is materialised
- THEN `config.rules_repo_path` SHALL equal the expanded `Path("~/Developer/tdt/poems-mobile3-docs").resolve()`.

### Requirement: Legacy `rule_patterns.yaml` retained with new deprecation note

`code-daily-scan/config/rule_patterns.yaml` SHALL remain in place for one release. Its top-level YAML key named `__deprecated__` SHALL contain a string-valued annotation worded:

> "rule_patterns.yaml is a legacy fallback used only when (a) platform-specific docs/*/categories/*.md are missing AND (b) the configured rules_repo_path is absent or contains no matching category. Edit the docs/*/categories/*.md inside the configured `rules_repo_path` (default: ~/Developer/tdt/poems-mobile3-docs/20.Developments/40.AI/50.RCA/<plat>/rules/categories/) as the source of truth. This file is incomplete (missing RCA-*, testing, and iOS rules) and will be removed in the next release."

A `# TODO(remove-by-release): remove in <next-version>` comment SHALL appear in the YAML header (kept inside a YAML comment, not as a key).

#### Scenario: Annotation text reflects new precedence
- GIVEN this change has been applied
- WHEN an operator reads the first 200 bytes of `code-daily-scan/config/rule_patterns.yaml`
- THEN the file MUST contain a `__deprecated__:` line (YAML) whose value mentions `rules_repo_path`
- AND the file MUST contain a `# TODO(remove-by-release):` line as a YAML comment.

#### Scenario: Legacy YAML still loadable
- GIVEN the docs-repo path is unavailable AND the local mirror is empty
- WHEN the loader falls back to `rule_patterns.yaml`
- THEN loading MUST return at least the rules encoded in the YAML (regression-only — no behaviour change vs. today).

## ADDED Requirements

### Requirement: Migrate-config writes the new key

The `code-daily-scan migrate-config` command SHALL ensure both `android` and `ios` blocks in the generated `~/.tdt/code-daily-scan.yaml` include `rules_repo_path: ~/Developer/tdt/poems-mobile3-docs` so newly migrated operators default to canonical loading. If the key is already present (idempotent re-run after manual edit), the command MUST NOT clobber it.

#### Scenario: Generate a fresh config from a legacy block
- GIVEN no `~/.tdt/code-daily-scan.yaml` exists
- AND `~/.tdt/config.yaml` contains an `android_scan:` block
- WHEN `code-daily-scan migrate-config` runs
- THEN the generated `android:` block MUST include `rules_repo_path: ~/Developer/tdt/poems-mobile3-docs`
- AND the `ios:` block MUST be created even when no legacy iOS section exists, and MUST include the same `rules_repo_path` key with a default `repo_path: ~/Developer/tdt/poems-mobile3-ios` placeholder.

#### Scenario: Migrate-config is idempotent on existing key
- GIVEN a destination `~/.tdt/code-daily-scan.yaml` already contains `android.rules_repo_path: /custom/path`
- WHEN `code-daily-scan migrate-config` runs
- THEN the existing `rules_repo_path` value SHALL be preserved (no clobber).

#### Scenario: Migrate-config injects key when missing
- GIVEN a destination file with `android:` block but no `rules_repo_path`
- WHEN the command runs (after §2.6 in `tasks.md` is applied, which performs an explicit inject instead of the legacy pure-dump)
- THEN `android.rules_repo_path` MUST equal `~/Developer/tdt/poems-mobile3-docs`.

### Requirement: IOS_CATEGORY_MAP covers all docs-repo categories

`IOS_CATEGORY_MAP` in `code_daily_scan/plugins/ios/rules_loader.py` SHALL contain prefix entries for every markdown file stem under `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/`. At minimum the four missing prefixes — `naming-readability`, `pattern-consistency`, `state-mutation`, `testing-coverage` — SHALL be added.

#### Scenario: All docs-repo iOS category files resolve
- GIVEN a fixture docs-repo iOS rules tree containing all 9 markdown files (one per docs category)
- WHEN `IOSRulesLoader.load_category(...)` is invoked once per docs category
- THEN each call MUST return at least one rule (no silent drops).

#### Scenario: Persisted category vs scanner dispatch
- GIVEN an iOS rule markdown file whose `Category:` field is `State Mutation`
- WHEN the rule is parsed into a `RulePattern`
- THEN `rule.category` MUST equal `State Mutation` (the value RCA reports expect)
- AND the scanner-dispatch remap table MUST route `State Mutation` → `Lifecycle` (the existing `IOSLifecycleScanner.category`).

### Requirement: Resolution precedence is observable at runtime

Every scanner run SHALL emit, via the standard Python logger at INFO level, **at minimum one** log line per rule category saying which source was selected. The emitted line MUST include the resolved absolute path of the chosen file (or `rule_patterns.yaml` for the legacy layer) and a 12-character SHA-256 fingerprint derived from that file's bytes.

#### Scenario: All three layers present
- WHEN the loader resolves category `Crash`
- AND primary (docs repo), local mirror and legacy YAML all exist for it
- THEN the logger MUST contain exactly one line for that category mentioning the primary path and its fingerprint.

#### Scenario: Two layers missing
- WHEN only the legacy YAML exists for a category
- THEN the logger MUST contain exactly one line for that category mentioning `legacy_yaml:rule_patterns.yaml` and its fingerprint.

### Requirement: Tests cover all three load paths

The test suite MUST exercise each of the four precedence permutations (primary-wins, primary-partial, primary-absent, primary-empty) using the fixture directories described in `design.md`.

#### Scenario: Primary wins for all categories
- GIVEN fixture `rules_repo_with_all_categories/`
- WHEN `AndroidRulesLoader.load()` is invoked
- THEN it MUST return rules for every category found in the primary root
- AND MUST NOT touch any other root.

#### Scenario: Primary empty, local mirror wins
- GIVEN fixture `legacy_local_only/`
- WHEN `AndroidRulesLoader.load()` is invoked
- THEN it MUST return rules from the local mirror
- AND MUST log `resolved_source=local_mirror:...`.

#### Scenario: Only legacy YAML available
- GIVEN fixture `legacy_yaml_only/`
- WHEN `AndroidRulesLoader.load()` is invoked
- THEN it MUST return rules from `rule_patterns.yaml`
- AND MUST log `resolved_source=legacy_yaml:...`.

## REMOVED Requirements

*None for this change. The legacy `rule_patterns.yaml` is **retained** for one release; removal is a follow-up change.*

## Cross-references

- Internal: `code_daily_scan.plugins.android.rules_loader.AndroidRulesLoader.load_category`
- Internal: `code_daily_scan.plugins.ios.rules_loader.IOSRulesLoader.load_category`
- Internal: `code_daily_scan.config.PlatformConfig`
- External docs contract: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/10.iOS/rules/categories/`
- External docs contract: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/20.AOS/rules/categories/`
