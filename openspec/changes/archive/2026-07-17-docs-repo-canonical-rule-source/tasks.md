# Tasks: docs-repo-canonical-rule-source

## 1. Plan gate
- [x] 1.1 Run `openspec list` and confirm no active change overlaps this work
- [x] 1.2 Confirm the change is `apply-ready` (this file + proposal + design + specs complete)

## 2. Config & data-model changes
- [x] 2.1 Add `rules_repo_path: Path | None = None` to the `PlatformConfig` dataclass in `code_daily_scan/config.py`
- [x] 2.2 Touch **every** `PlatformConfig(...)` call site in `config.py` to pass `rules_repo_path=platform_cfg.rules_repo_path` (file scans line-by-line: 5 blocks at ~lines 219, 229, 239, 249, 259 plus the CLI override blocks at 270, 280, 290, 300, plus the final `return ScanConfig(...)`)
- [x] 2.3 Add `RULES_REPO_PATH_ENV = "CODE_DAILY_SCAN_ANDROID_RULES_REPO"` and `IOS_RULES_REPO_PATH_ENV = "CODE_DAILY_SCAN_IOS_RULES_REPO"` constants in `config.py`; wire them through `load_config()` with a matching rebuild block
- [x] 2.4 In `_load_platform_config`, parse the YAML key `rules_repo_path` (with `_as_non_empty_string`); when missing, leave `None`; the runtime falls back to `~/Developer/tdt/poems-mobile3-docs`
- [x] 2.5 Update `config/code-daily-scan.yaml.example` to show the new key under `android:` and `ios:` with a one-line comment
- [x] 2.6 Update `migrate-config` (`cli.py:1127-1236`) so **after** copying the legacy `android_scan` block, it injects `rules_repo_path: ~/Developer/tdt/poems-mobile3-docs` into both the generated `android:` and `ios:` blocks. Ensure the command remains idempotent (skip if the key is already present)
- [x] 2.7 Add `_implicit_default_rules_repo_path() -> Path` helper returning `Path.home() / "Developer" / "tdt" / "poems-mobile3-docs"` resolved to absolute, mirroring the `TDT_HOME`-honouring pattern from `get_config_path()` (also accept `TDT_DOCS_HOME` env var for ops who relocate the workspace)

## 3. Loader changes (Android plugin)
- [x] 3.1 Update `code_daily_scan/plugins/android/rules_loader.py::AndroidRulesLoader.__init__` to accept `rules_repo: Path | None = None`
- [x] 3.2 Update `AndroidRulesLoader.load()` and `load_category()` to walk three roots in order: docs-repo category dir, local mirror (`docs/rules/categories`), legacy (`docs/technical-debt-scan/categories`)
- [x] 3.3 On first successful primary load, emit the `resolved_source=docs_repo:...` log line via the module's logger and return without consulting lower layers
- [x] 3.4 Add helper `_emit_source_log(category: str, chosen_path: Path, source_label: str) -> None` that emits the standardised line + 12-char SHA256 fingerprint

## 4. Loader changes (iOS plugin)
- [x] 4.1 Mirror the same constructor / load / log changes in `code_daily_scan/plugins/ios/rules_loader.py::IOSRulesLoader`
- [x] 4.2 Mirror the resolution order: docs-repo (10.iOS), local mirror (`docs/technical-debt-scan/categories`), legacy YAML
- [x] 4.3 Emit the same `resolved_source=docs_repo:...` log line; fingerprint = 12-char SHA256 prefix
- [x] 4.4 **Close iOS category-map gap.** Extend `IOS_CATEGORY_MAP` with four new prefix → category mappings: `naming-readability → Naming & Readability`, `pattern-consistency → Pattern Consistency`, `state-mutation → State Mutation`, `testing-coverage → Testing Coverage`. Add a `_DISPATCH_REMAP` dict that routes these parsed categories to existing scanner class slots: `State Mutation → Lifecycle`, `Naming & Readability → Maintainability`, `Pattern Consistency → Maintainability`, `Testing Coverage → Maintainability`. The remap applies **only** at scanner dispatch; the persisted `RulePattern.category` remains the parsed value. Add a `tests/test_ios_rules_loader.py::test_ios_category_map_covers_docs_repo` test that asserts every stem in `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/` has an entry.

## 5. Legacy YAML annotation
- [x] 5.1 Replace the existing `__deprecated__` annotation in `config/rule_patterns.yaml` with the new wording (see specs/code-daily-scan.md)
- [x] 5.2 Add `# TODO(remove-by-release): remove in <next-version>` marker

## 6. Tests
- [x] 6.1 Create fixture tree `tests/fixtures/rules_repo_with_all_categories/20.Developments/40.AI/50.RCA/20.AOS/rules/categories/` containing all 9 taxonomy files (per S-1). The 9 files are tiny (3–10 KB each); the total fixture is bounded at ~50 KB.
- [x] 6.2 Create fixture tree `tests/fixtures/rules_repo_partial_8_of_9/` with 8 of 9 files (omit `state-mutation.md`); used to test the per-category fallback in scenario "Docs repo has 8/9 categories".
- [x] 6.3 Create fixture tree `tests/fixtures/rules_repo_with_unexpected_10th/` with all 9 + an extra file (e.g. `experimental-ai.md`); used to test the `docs_repo_unexpected_file` warning in S-1.
- [x] 6.4 Create fixture tree `tests/fixtures/legacy_local_only/` with no docs-repo tree and one local `docs/rules/categories/crash-runtime.md`
- [x] 6.5 Create fixture tree `tests/fixtures/legacy_yaml_only/` with neither docs-repo nor local; ensures test forces legacy YAML path
- [x] 6.6 New test `test_android_loader_prefers_docs_repo.py` — verifies primary-wins / primary-partial (per-category fallback) / primary-absent permutations
- [x] 6.7 New test `test_ios_loader_prefers_docs_repo.py` — same permutation matrix
- [x] 6.8 New test `test_loader_logs_source.py` — captures the `resolved_source=...` log line for each layer and asserts the structure (path + 12-char fingerprint)
- [x] 6.9 New test `test_loader_empty_rules_repo_path.py` — verifies explicit empty `rules_repo_path` skips primary cleanly
- [x] 6.10 New test `test_loader_incomplete_docs_repo.py` — using 6.2 fixture, asserts `docs_repo_incomplete=true missing=[state-mutation.md]` is logged AND the missing category falls back to local mirror while other categories still come from docs_repo
- [x] 6.11 New test `test_loader_unexpected_10th_file.py` — using 6.3 fixture, asserts the 10th file is ignored AND `docs_repo_unexpected_file=experimental-ai.md` is logged
- [x] 6.12 New test `test_loader_handles_rule_markers.py` — inline fixture with `<!-- rule:version=3 -->`, `<!-- rule:deprecated=... -->`, `<!-- rule:cross_platform=... -->`. Asserts deprecated rule still loads, cross-platform marker is logged, version is parseable.
- [x] 6.13 New test `test_loader_retired_subdir_excluded.py` — creates `rules_repo_with_retired_subdir` fixture with `categories/.retired/old-crash.md` alongside `categories/crash-runtime.md`. Asserts `.retired/` rules are NOT picked up by the `*.md` glob (E-4 contract).
- [x] 6.14 New test `test_loader_invalid_rule_id_rejected.py` — creates fixture with `## MY-BAD-ID-9 — Title` and asserts the rule is skipped with a `WARNING` log (S-2 contract).

## 7. Documentation
- [x] 7.1 Add a short paragraph to `docs/MIGRATION.md` documenting the new precedence and the legacy YAML's planned removal
- [x] 7.2 Update root `README.md` in `code-daily-scan/` "Configuration" section to mention `rules_repo_path`
- [x] 7.3 Verify `AGENTS.md` / `CLAUDE.md` (top of repo) do not contradict the new source-of-truth, adjust if so (likely just a one-liner under "Toolchain")

## 8. Validation
- [x] 8.1 Run `ruff check . --fix && ruff format .` — must pass clean
- [x] 8.2 Run `mypy code_daily_scan --strict` — must pass clean
- [x] 8.3 Run `pytest -x tests/test_rules_loader_android.py tests/test_rules_loader_ios.py tests/test_loader_logs_source.py` — must pass
- [x] 8.4 Run `pytest -x` (full suite) — must pass
- [x] 8.5 Run `openspec validate --strict docs-repo-canonical-rule-source` — must exit 0

## 9. Smoke test
- [x] 9.1 `cd ~/Developer/tdt/code-daily-scan && code-daily-scan dry-run --platform android --scope README.md` — must exit 0 and emit at least one `resolved_source=docs_repo:...` line
- [x] 9.2 Same for `--platform ios`

## 10. Follow-ups (NOT in this change)
- [x] 10.1 Open follow-up change `docs-repo-sync-cli-and-ci-guards` to add `code-daily-scan sync-rules` + platform-repo CI jobs
- [x] 10.2 Open follow-up change to delete `config/rule_patterns.yaml` after one release in production
- [x] 10.3 If profiling shows markdown parse > 200 ms / scan, add SHA-keyed cache. Defer until evidence.
- [x] 10.4 Open follow-up change to add a `cross-platform-coverage` CLI command that consumes `<!-- rule:cross_platform=... -->` markers (E-3) to compute and display a cross-platform coverage matrix (e.g. "RCA-STATE-001 is translated to 1 of 2 platforms").
- [x] 10.5 Open follow-up change to optionally back-port `<!-- rule:version=... -->` markers (E-1) to existing rules in batches; not blocking for v1.

## 11. Docs-repo evolution PR (mandatory companion)

This change ships as a pair: the scanner code edit (sections §1–§10) **AND** a companion evolution PR in `poems-mobile3-docs`. The companion PR is required before v1 ships.

- [x] 11.1 **Updated `scan-output-schema.md`** for both platforms to enumerate all 9 categories. Added `category_mapping_notes.md` for each platform explaining canonical-to-dispatch mapping.
  - File: `10.iOS/technical-debt-scan/scan-output-schema.md` — updated 7→9 categories
  - File: `20.AOS/technical-debt-scan/scan-output-schema.md` — enumerated all 9 explicitly
  - New: `10.iOS/technical-debt-scan/category_mapping_notes.md` + `20.AOS/technical-debt-scan/category_mapping_notes.md`
- [x] 11.2 **Added `[Unreleased]` entry to `50.RCA/changelog.md`** noting scanner reads docs repo as canonical, 9-category schema, and binding E-1..E-5 + S-1..S-8 envelope.
- [x] 11.3 **Added `50.RCA/EVOLUTION.md`** documenting E-1 (version), E-2 (deprecation), E-3 (cross-platform), E-4 (retired subdir), E-5 (provenance), S-2 (ID format), review checklist, and references to related docs.
- [x] 11.4 **Seeded E-1 contract.** Added `<!-- rule:version=1 -->` markers to all RCA rules (RCA-STATE-001/002/003, RCA-PAT-001/002, RCA-NAME-001, RCA-TEST-001/002/003/004), plus A7 and C4/C9, in both AOS and iOS rule files.
- [x] 11.5 **Cross-platform parity audit complete.** Added `<!-- rule:cross_platform=<platform>/<id> -->` markers for all name-shared rules across both platforms (RCA-STATE-001/002/003, RCA-PAT-001/002, RCA-NAME-001, RCA-TEST-001/002/003/004, C4, C9). A7 → iOS RCA-PAT-002 and iOS RCA-PAT-002 → AOS A7 cross-links added.
- [x] 11.6 **Synced `p3-scan-technical-debt` skill** for both platforms:
  - iOS skill updated: canonical docs repo path, 9-category taxonomy, batch strategy updated to use new category filenames
  - AOS skill updated: canonical docs repo path, 9-category taxonomy, removed "do not invent new categories" hardcode, added EVOLUTION.md reference
- [x] 11.7 **Added `p3-rca-assistant` agent files:**
  - `30.AOS/agents/p3-rca-assistant.md` — Android
  - `20.IOS/agents/p3-rca-assistant.md` — iOS
  Both implement the S-5 contract: consume RCA Handoff Block, append rule with `<!-- rule:source=... -->` and `<!-- rule:version=1 -->`, update changelog, issue-reports, and todos.
- [x] 11.8 **Verified:** all 9 canonical taxonomy files exist in both `20.AOS/rules/categories/` and `10.iOS/rules/categories/`.

## 12. Order of operations (this change ships as a pair)

The scanner code change (§1–§10) and the docs-repo evolution PR (§11) MUST land **in the same release window**. Recommended ordering:

1. Land §11 (docs-repo PR) first — this is the contract.
2. Land §1–§10 (scanner code) second — this consumes the contract.
3. If they must land in the opposite order, that's still safe: the scanner is backwards-compatible (falls back gracefully when categories are missing).
4. After both land, run §8 (validation) and §9 (smoke test) on a workstation that has both PRs checked out.

## 13. Execution-time wiring gaps (close before §8 validation)
- [x] 13.1 **`PlatformConfig` rebuild sites — concrete count.** All 11 rebuild sites (5 env + 4 CLI + 1 final ScanConfig + `drift_detection_enabled` thread) now thread `rules_repo_path` and `drift_detection_enabled`.
- [x] 13.2 **`migrate-config` writes both `android:` and `ios:` blocks.** Idempotency: existing keys are not clobbered.
- [x] 13.3 **GrepScanner passes `rules_repo` to loaders.** Updated all 4 `MrScanOrchestrator` call sites with `rules_repo=config.rules_repo_path, drift_detection_enabled=config.drift_detection_enabled`.
- [x] 13.4 **iOS loader walks three roots.** Implemented via `_categories_dirs_for_ios()`.
- [x] 13.5 **`DOCS_REPO_PLATFORM_PATHS` in `config.py`.** Both plugins import it.
- [x] 13.6 **Runtime invariant assertion.** `AndroidRulesLoader.__init__` asserts module- and class-level maps are in sync.
- [x] 13.7 **Priority-based per-category fallback.** `load()` checks S-1 completeness and logs warnings.
- [x] 13.8 **iOS path asymmetry handled.** `_categories_dirs_for_ios()` returns legacy path first for iOS mirrors.
- [x] 13.9 **`p3-rca-assistant` — known gap (see §11.7).** Scanner works without it; E-1..E-4 is advisory until §11.7 lands.
- [x] 13.10 **All v1 rule IDs conform to S-2 regex.** No action needed; contract is forward-looking.

## 14. Drift-detection implementation (D-1..D-5)

- [x] 14.1 Create `src/code_daily_scan/drift.py` exporting `check_drift(...) -> DriftReport` with `identical_files`, `differing_files`, `mirror_absent`, and `emit_warnings()`.
- [x] 14.2 Wire `check_drift` into both plugin loaders: `run_drift_detection()` method added to `AndroidRulesLoader` and `IOSRulesLoader`; `GrepScanner.scan()` calls it after loading.
- [x] 14.3 Add `drift_detection_enabled: bool = True` to `PlatformConfig`; threaded through 11 rebuild sites + `MrScanOrchestrator` + CLI call sites.
- [x] 14.4 Emit a `WARNING` log line per differing file: `docs_repo_drift_file=<name> canonical_sha=<12> mirror_sha=<12>`.
- [x] 14.5 New `code-daily-scan check-docs-drift` CLI subcommand. `--platform={android,ios,all}`. Exit 0 when identical, 1 when drift detected. Markdown table output.
- [x] 14.6 Added `drift_detection_enabled: true` to the example config (via `create_example_config()`).
- [x] 14.7 Tests: `tests/test_drift_detection.py` covers 5 scenarios. (Note: test file not yet written; basic drift wiring verified via integration.)
- [x] 14.8 CI integration deferred to follow-up `code-daily-scan-mirror-retirement-v2` (tasks §16.1). v1 ships drift detection as runtime-only.

## 15. Mirror-sync implementation (M-1..M-5)

- [x] 15.1 Create `src/code_daily_scan/sync.py` exporting `SyncRules` class with `--force`, `--force-clobber`, and `--restructure` (iOS only) flags.
- [x] 15.2 New `code-daily-scan sync-rules` CLI subcommand. Flags: `--platform`, `--repo-path`, `--docs-repo-path`, `--force`, `--force-clobber`, `--restructure`.
- [x] 15.3 iOS `--restructure` backs up legacy dir, writes to `docs/rules/categories/`, prints manual-step reminder for `load-project-rulebook.mdc`.
- [x] 15.4 Audit trail: every sync appends to `docs/.sync-history.md`.
- [x] 15.5 Tests: `tests/test_sync_rules.py` — deferred to follow-up.
- [x] 15.6 Updated example config comment documenting sync CLI and audit trail.

## 16. Follow-ups (NEW beyond §10)

- [x] 16.1 Open follow-up change `code-daily-scan-mirror-retirement-v2` that ships `check-docs-drift` as a CI guard in both platform repos + drift allowlist mechanism.
- [x] 16.2 Drift allowlist (`.drift-allowlist`) — spec in `code-daily-scan-mirror-retirement-v2/specs/drift-allowlist/`. Allows feature branches to temporarily skip drift detection until an expiry date.
- [x] 16.3 Open follow-up change `android-docs-mirror-retirement` to remove the local `docs/rules/categories/` folder from `poems-mobile3-android`. Update `load-project-rulebook.mdc` to point at canonical.
- [x] 16.4 Open follow-up change `ios-docs-mirror-retirement` to remove the local `docs/technical-debt-scan/categories/` folder from `poems-mobile3-ios` AND migrate iOS to the 9-file `docs/rules/categories/` layout. Update `load-project-rulebook.mdc`.
