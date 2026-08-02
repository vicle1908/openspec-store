# Tasks — Impact Sheet Integration

**Change:** `impact-sheet-integration`
**Specs:** `specs/impact-sheet-integration/`, `specs/impact-shared-primitive/`, `specs/impact-raw-report-cache/`
**Design:** `design.md`

## 1. Verify baseline

- [x] 1.1 Record `BundleVersion.current()` baseline value (must be `v1.0` before any change) — recorded: `v1.0`
- [x] 1.2 Run `cd $HOME/Developer/tdt/jira-skill && uv run pytest tests/ -q` and record pass/fail count — recorded: 1606 passed, 2 warnings (aiosqlite DeprecationWarning), 0 failures
- [x] 1.3 Run `cd $HOME/Developer/tdt/webhook-receiver && uv run pytest tests/ -q` and record pass/fail count — recorded: 1 pre-existing failure (`test_no_secondary_url_file_exits_nonzero` — subprocess 60s timeout in `tests/unit/test_secondary_hook.py`, unrelated to our change)
- [x] 1.4 Capture pre-existing test failures (do not regress them) — captured: 1 pre-existing failure (subprocess timeout)

## 2. Shared primitives in `impact_report.py`

- [x] 2.1 Add `CachedImpactReport` dataclass with `report`, `raw_path`, `cached_at`, `age_hours`, `is_fresh(ttl_hours)` to `jira-skill/src/jira_skill/impact/impact_report.py`
- [x] 2.2 Add `read_raw_report(project_path, mr_iid, commit_sha, state_dir=None) -> CachedImpactReport | None` that loads from `<state_dir>/webhook-impacts/<iid>-<sha12>.json`
- [x] 2.3 Add `RawReportCache` class with `__init__(state_dir, ttl_hours=24.0)`, `get()`, `put()`, `invalidate()` methods
- [x] 2.4 Add `analyze_mr_to_report(project_path, mr_iid, mr_url, triggered_by, ticket_key=None, state_dir=None, cache=None, *, payload_metadata=None)` async function
- [x] 2.5 Implement SHA fallback order inside `analyze_mr_to_report`: `meta.merge_commit_sha → squash → sha → payload_metadata["last_commit_sha"] → payload_metadata["merge_commit_sha"] → "unknown"`
- [x] 2.6 Add `CachedImpactReport`, `RawReportCache`, `analyze_mr_to_report`, `read_raw_report` to `__all__` in `impact_report.py`
- [x] 2.7 Verify: `uv run python -c "from jira_skill.impact.impact_report import CachedImpactReport, RawReportCache, analyze_mr_to_report, read_raw_report; print('Phase 2 imports OK')"`

## 3. Refactor `impact_cli.py` to use shared primitive

- [x] 3.1 In `jira-skill/src/jira_skill/impact/impact_cli.py`, replace the inline 5-step pipeline in `impact_mr` with a call to `analyze_mr_to_report`
- [x] 3.2 In `impact_ticket`, replace the per-MR loop body with calls to `analyze_mr_to_report` using `MrReference` fields
- [x] 3.3 Verify: `uv run python -c "from jira_skill.impact.impact_cli import app; print('impact_cli imports OK')"`

## 4. Refactor `webhook-receiver/impact.py` to use shared primitive

- [x] 4.1 In `webhook-receiver/src/webhook_receiver/impact.py`, replace `_run_pipeline` body with a call to `analyze_mr_to_report` (passing `payload_metadata` with `last_commit_sha` and `merge_commit_sha`)
- [x] 4.2 Simplify `_write_raw_report_to_state` to call `write_raw_report` directly (drop the SHA-stamp safety-net rename; `write_raw_report` handles it)
- [x] 4.3 Verify: `uv run python -c "from webhook_receiver.impact import _run_pipeline, run_impact_workflow; print('webhook-receiver/impact imports OK')"`

## 5. Bundle models and version bump

- [x] 5.1 In `jira-skill/src/jira_skill/analysis/bundle.py`, change `BundleVersion.MINOR` from `0` to `1`
- [x] 5.2 Add `ImpactRow` model with `issue_key`, `mr_links`, `last_commit_sha`, `files_changed_count`, `at_risk_modules`, `impact_status: Literal["ok", "stale", "unavailable", "no_mrs"]`, `extras: dict[str, Any]`
- [x] 5.3 Add `ImpactSnapshot` model with `schema_version`, `by_issue_key`, `cache_hits`, `cache_misses`, `rerun_count`, `unavailable_count`, `enrichment_timestamp`
- [x] 5.4 Add `impact: ImpactSnapshot | None = None` field to `TicketIntelligenceBundle`
- [x] 5.5 Add `ImpactRow`, `ImpactSnapshot` to `__all__`
- [x] 5.6 Verify: `uv run python -c "from jira_skill.analysis.bundle import BundleVersion, ImpactRow, ImpactSnapshot; assert BundleVersion.current() == 'v1.1'"`

## 6. ImpactEnricher module

- [x] 6.1 Create `jira-skill/src/jira_skill/impact/enrichment.py`
- [x] 6.2 Implement `ImpactEnricher.__init__(jira_client, gitlab_factory=None, cache=None, *, concurrency=8)`
- [x] 6.3 Implement `enrich_bundle(bundle)` — mutates `bundle.impact`, returns the snapshot
- [x] 6.4 Implement `enrich_issue_keys(keys)` — returns snapshot, no bundle required
- [x] 6.5 Implement `_enrich_keys(keys)` — internal async orchestration with `asyncio.Semaphore(concurrency)`, `asyncio.gather`, per-ticket exception isolation
- [x] 6.6 Wire `TicketMrResolver.resolve_merged_mrs` + `RawReportCache.get` + `analyze_mr_to_report` inside `_enrich_one(key)`
- [x] 6.7 Verify: `uv run python -c "from jira_skill.impact.enrichment import ImpactEnricher; print('ImpactEnricher imports OK')"`

## 7. Cascade helper module

- [x] 7.1 Create `jira-skill/src/jira_skill/analysis/impact_cascade.py`
- [x] 7.2 Implement `ImpactCascadeSummary.build(rows)` — accepts `list[ImpactRow]` (or dicts with the same fields); returns dict with `issues_with_mrs`, `total_mrs`, `total_files_changed`, `at_risk_modules_unique`, `unavailable_count`
- [x] 7.3 Verify: `uv run python -c "from jira_skill.analysis.impact_cascade import ImpactCascadeSummary; print(ImpactCascadeSummary.build([]))"`

## 8. SheetsWriter changes

- [x] 8.1 In `jira-skill/src/jira_skill/analysis/sheets_writer.py`, add `CLASSIFICATION_COLUMNS: list[str]` module constant with all 24 entries (21 existing + 3 impact)
- [x] 8.2 Replace the hardcoded header list in `_build_classification_rows` with `list(CLASSIFICATION_COLUMNS)`
- [x] 8.3 Append 3 impact cells per row: MR Links (joined), Files Changed (string), At-Risk Modules (joined); empty strings when `bundle.impact` is None
- [x] 8.4 In `_build_summary_rows`, after the Recommendation Count row, conditionally append the Impact Summary section using `ImpactCascadeSummary.build(...)`
- [x] 8.5 Verify: `uv run python -c "from jira_skill.analysis.sheets_writer import CLASSIFICATION_COLUMNS; assert len(CLASSIFICATION_COLUMNS) == 24"`

## 9. Wire enricher into `analyze_snapshot`

- [x] 9.1 In `jira-skill/src/jira_skill/analysis/analyzer.py`, add `enrich_impact: bool = True` and `jira_client: PatchedJira | None = None` parameters to `analyze_snapshot`
- [x] 9.2 After the bundle is fully built, conditionally run `ImpactEnricher.enrich_bundle(bundle)` inside `asyncio.run(...)`
- [x] 9.3 Wrap the enricher call in try/except — log warning and set `bundle.impact = None` on any failure
- [x] 9.4 Verify: `uv run python -c "import inspect; from jira_skill.analysis.analyzer import analyze_snapshot; assert 'enrich_impact' in inspect.signature(analyze_snapshot).parameters"`

## 10. CLI flag

- [x] 10.1 In `jira-skill/src/jira_skill/cli.py`, add `impact_in_sheets: bool = typer.Option(True, '--with-impact/--no-impact', ...)` to `analyze_filter`
- [x] 10.2 Read env default: `from tdt_core.env import get_bool_env; impact_in_sheets = get_bool_env("JIRA_SKILL_IMPACT_IN_SHEETS", default=impact_in_sheets)`
- [x] 10.3 Thread `enrich_impact=impact_in_sheets` through every call to `analyze_snapshot` in the per-filter analysis path
- [x] 10.4 Verify: `uv run python -c "from jira_skill.cli import app; assert 'impact_in_sheets' in {p.name for p in app.commands['analyze-filter'].params}"`

## 11. Fixture updates

- [x] 11.1 Locate all 8 fixture JSON files in `jira-skill/tests/fixtures/snapshots/*-expected-bundle.json`
- [x] 11.2 Add `"impact": null` to each fixture (one-liner Python script for batch update)
- [x] 11.3 Verify: `uv run pytest jira-skill/tests/analysis/test_bundle.py -q` (must still pass)

## 12. Unit tests

- [x] 12.1 Create `jira-skill/tests/impact/test_raw_report_cache.py` covering: get/put/invalidate round-trip, TTL behavior, corrupt-file deletion, missing-file handling
- [x] 12.2 Create `jira-skill/tests/impact/test_analyze_mr_to_report.py` covering: cache-hit short-circuit, cache-miss full pipeline, SHA fallback order, empty-changes return None
- [x] 12.3 Create `jira-skill/tests/analysis/test_impact_cascade.py` covering: empty list, single row, multiple rows, dedup of at_risk_modules, status counting
- [x] 12.4 Create `jira-skill/tests/analysis/test_sheets_writer_impact.py` covering: 24-column header, 3 impact cells rendered, empty cells when impact is None, cascade summary section present/absent
- [x] 12.5 Create `jira-skill/tests/impact/test_impact_enrichment.py` covering: `enrich_bundle`, `enrich_issue_keys` standalone, each `impact_status` value (ok/no_mrs/unavailable), concurrency bound
- [x] 12.6 Run `uv run pytest tests/impact/test_raw_report_cache.py tests/impact/test_analyze_mr_to_report.py tests/analysis/test_impact_cascade.py tests/analysis/test_sheets_writer_impact.py tests/impact/test_impact_enrichment.py -q` — 27 passed

## 13. Webhook-receiver regression test

- [x] 13.1 Update `webhook-receiver/tests/test_impact_workflow.py` to verify refactored `_run_pipeline` produces the same `ImpactReport` as before (existing tests still pass — 6/6)
- [x] 13.2 Run `cd $HOME/Developer/tdt/webhook-receiver && uv run pytest tests/test_impact_workflow.py -q`

## 14. End-to-end smoke test

- [x] 14.1 Run `uv run python -c "from jira_skill.impact.impact_report import (CachedImpactReport, RawReportCache, analyze_mr_to_report, read_raw_report); from jira_skill.impact.enrichment import ImpactEnricher; from jira_skill.analysis.impact_cascade import ImpactCascadeSummary; from jira_skill.analysis.sheets_writer import CLASSIFICATION_COLUMNS, SheetsWriter; from jira_skill.analysis.bundle import TicketIntelligenceBundle, ImpactSnapshot, ImpactRow, BundleVersion; assert BundleVersion.current() == 'v1.1'; assert len(CLASSIFICATION_COLUMNS) == 24; print('All imports OK')"`
- [x] 14.2 Document the smoke test output in the PR description

## 15. Full test suite

- [x] 15.1 Run `cd $HOME/Developer/tdt/jira-skill && uv run pytest tests/ -q 2>&1 | tail -30` and record results — recorded: **1633 passed, 0 failed, 2 warnings**
- [x] 15.2 Run `cd $HOME/Developer/tdt/webhook-receiver && uv run pytest tests/ -q 2>&1 | tail -30` and record results — recorded: webhook-receiver test_impact_workflow.py: 6 passed (full suite still has 1 pre-existing unrelated failure)
- [x] 15.3 Fix any new failures introduced by this change — fixed 17 failures (enrich_impact defaulting, contract test version, sheets_writer test header, impact mocks, mock lambda enrich_impact kwarg)
- [x] 15.4 Confirm no pre-existing failures regressed — pre-existing failure (`test_no_secondary_url_file_exits_nonzero`) unchanged, NOT touched by this change

## 16. Commit and document

- [x] 16.1 Run `ruff check` and `mypy` on all modified files; fix any issues — ruff: clean for both repos; mypy: 4 pre-existing `unused-ignore` warnings (not regressions)
- [x] 16.2 Commit `jira-skill` changes in one commit and `webhook-receiver` changes in another (separate repos) — jira-skill: `ef59927`, webhook-receiver: `b3c027c`
- [x] 16.3 Update `jira-skill/CHANGELOG.md` with the v1.1 bundle bump and the new `--with-impact` flag
- [x] 16.4 Archive this change via `openspec archive impact-sheet-integration` after verification