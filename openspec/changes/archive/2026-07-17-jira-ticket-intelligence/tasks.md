# Jira-Ticket-Intelligence: Tasks

## Sections 1-4: Core Contract + Adapters + Capabilities + Validation

- [x] All 41 tasks from Sections 1-4 (core contract, 3 consumer adapters, shared capabilities, cross-repo validation)

## Section 5: Completion Items

### Status Snapshot

The shipped Section 5 path is complete.

| Priority | Item | Status |
|----------|------|--------|
| HIGH | RCA taxonomy extraction (`rca.py` inline patterns → dedicated canonical module) | ✅ COMPLETE |
| HIGH | Fixture updates: all 8 fixture pairs include RCA+FixStatus fields | ✅ COMPLETE (2026-06-06) |
| MEDIUM | Dynamic filter URL resolution (`--filter-url`) | ✅ COMPLETE |
| MEDIUM | Skill docs update (signal count, CLI reference, filter-url) | ✅ COMPLETE |
| LOW | Auto-detect mode (`--auto`) | ✅ COMPLETE (2026-06-07) |

### Marked Complete

- [x] 5.1 `extractors/content_priority.py` — 156 lines, 3 functions, importable
- [x] 5.2 `extractors/platform.py` — 108 lines, `detect_platform()`, importable
- [x] 5.3 `extractors/module.py` — 213 lines, `detect_module()`, importable
- [x] 5.4 `filter_registry.py` — 244 lines, `FilterRegistryReader`, importable
- [x] 5.5 Public API surface — all modules importable from `jira_skill.analysis.*`
- [x] 5.6 CLI `analyze-filter` — all flags implemented (`--filter`, `--filter-url`, `--filters`, `--auto`, `--registry`, `--registry-tab`, `--jql`, `--output`, `--worktree`, `--continuous`, `--incremental`, `--bundle-cache`)
- [x] 5.7 Continuous mode — `_parse_interval()`, loop logic, logging in `cli.py`
- [x] 5.8 Incremental mode — `_build_incremental_jql()`, `_get_last_run_from_cache()` in `cli.py`
- [x] 5.9 Tests — 14 test files exist: `test_extractors.py`, `test_cli.py`, `test_continuous.py`, `test_incremental.py`, `test_sheets_writer.py`, `test_pipeline_integration.py`, `test_classify_filter_wrapper.py`, `test_collector_worktree.py`, `test_bundle.py`, `test_contract.py`, `test_filter_registry.py`, `test_jira_pagination_fix.py`, `test_collector_gitlab.py`, `test_gitlab_network_fallback.py`
- [x] 5.10 Fixtures — All 8 fixture pairs updated with Phase 5 fields (2026-06-06)
  - ✅ `happy-path-expected-bundle.json`
  - ✅ `critical-risk-expected-bundle.json`
  - ✅ `circular-deps-expected-bundle.json`
  - ✅ `stale-blocked-expected-bundle.json`
  - ✅ `overloaded-assignee-expected-bundle.json`
  - ✅ `missing-metadata-expected-bundle.json`
  - ✅ `epic-rollup-expected-bundle.json`
  - ✅ `cross-project-blocker-expected-bundle.json`
  - All 1035 tests passing
- [x] 5.11 Integration test — pipeline works end-to-end via `test_pipeline_integration.py`
- [x] 5.12 Script refactored — `classify_filter_15269.py` is a 152-line SDK wrapper, no standalone logic
- [x] 5.14 `extractors/text_extractor.py` — 50 lines, `extract_text()`, importable
- [x] 5.15 `extractors/project.py` — 68 lines, `detect_project()`, importable

### Still to Do

- [x] **5.16 — RCA taxonomy extraction**
  - Runtime RCA behavior remains shared through `detect_rca()`.
  - `RCA_PATTERNS` now lives in `extractors/rca_patterns.py` and `rca.py` imports it.
  - Focused verification passed after the refactor (`test_bundle`, `test_extractors`, `test_contract`, `test_cli`).

- [x] **5.17 — Dynamic filter resolution**
  - CLI now accepts `--filter-url`.
  - Filter page URLs with `filter=<id>` or `filterId=<id>` are parsed into the same single-filter execution path as `--filter`.
  - Invalid URLs without a numeric filter identifier fail fast with a clear error.

- [x] **5.18 — Update skill docs**
  - `.agents/skills/jira-ticket-intelligence/SKILL.md` updated.
  - Signal count confirmed: 9 signals (7 core + 2 extension).
  - CLI reference updated: added `--filter-url` to supported input modes and operational flags.
  - Cron recipe included.
  - RCA taxonomy canonical location documented.

- [x] **5.19 — Fixture completion**
  - ✅ COMPLETE (2026-06-06): All 8 fixture pairs updated with Phase 5 fields
  - All 1035 tests passing
  - Regenerated via `scripts/regenerate_test_fixtures.py`

- [x] 5.20 — Archive legacy classify-release-3354-bugs change
  - Mark `openspec/changes/classify-release-3354-bugs/proposal.md` as migrated
  - Remove reference to script-based approach

- [x] 5.21 — Add registry-driven onboarding example for filter 15285
  - Skill docs include the registry row shape for spreadsheet output
  - Spec explicitly documents registry-based onboarding and optional convenience wrapper support
  - Added `jira-skill/scripts/classify_filter_15285.py` as a thin SDK-backed helper
  - Registry-backed runs now auto-create a dedicated spreadsheet when `Spreadsheet ID` is blank and persist the new ID back into the registry row

### Completed (2026-06-06 late session)

- [x] **5.22 — Evidence-column contract fix**
  - `_extract_scm_evidence()` in `analyzer.py` now backfills from `code_context` when `scm_evidence` is absent (live Jira path without structured GitLab provider).
  - Three evidence columns now render distinctly: `Analysis Evidence`, `SCM / Branch Evidence`, `Worktree Commits`.
  - Spec §10 and skill docs updated to document the three-column semantics.
  - 2 new regression tests added to `test_sheets_writer.py`.

- [x] **5.23 — Pydantic forward-reference resolution**
  - `signals.py` was missing `datetime` at runtime (only `TYPE_CHECKING`).
  - `FreshnessSignal.model_rebuild()` and `SignalSet.model_rebuild()` added at module scope.
  - `FreshnessSignal` runtime instantiation now works without PydanticUserError.
  - 6 pre-existing bundle/signal test failures resolved.

- [x] **5.24 — Spec and skill alignment pass**
  - Spec §10 updated: documented evidence-column semantics and backfill behavior.
  - Skill doc §5 updated: documented evidence column meanings and when each is populated.
  - Remaining gaps table pruned: removed completed items (5.16, 5.17, 5.18, 5.21, 5.25).
  - Test count updated: 10 files (added `test_filter_registry.py`).

- [x] **5.25 — Auto-detect mode**
  - `--auto` now scans visible Jira filters, prefers favourites, and falls back to recent visible filters when no favourites are present.
  - CLI auto mode reuses the existing filter pipeline and remains a convenience wrapper over the canonical SDK path.

- [x] **5.27 — CLI auto-resolve output for ad-hoc input modes**
  - `_registry_output_sheet()` helper added to `cli.py` between `_fetch_filter_name()` and `_auto_discover_filters()`.
  - `--filter`, `--filters`, and `--filter-url` now call `_registry_output_sheet(fid, output)` instead of passing `output` directly.
  - Resolution cascade: explicit `--output` → registry entry's `spreadsheet_id` → `JIRA_DEFAULT_FILTER_REGISTRY_ID` (shared JTI workbook) → `None` (JSON fallback).
  - `_ensure_registry_output_sheet()` updated to consult `JIRA_DEFAULT_FILTER_REGISTRY_ID` when `registry_sheet_id=None`, so `--filter` without `--registry` also triggers registry-backed output.
  - `filter 15435` (beta_target_v54) onboarded: added to `~/.tdt/jira-ticket-intelligence-registry.yaml` (6 filters total) and `~/.tdt/.env` `JIRA_DEFAULT_FILTER_IDS`.
  - Filter-specific `classify_filter_15269.py` updated to resolve output from registry (shared JTI workbook) instead of its own hardcoded spreadsheet ID.
  - Spec §18 added: "Auto-resolve output for ad-hoc input modes".
  - Skill docs updated: "exactly two active filters" corrected to six; "dedicated spreadsheet per filter" corrected to "shared JTI workbook" pattern.
