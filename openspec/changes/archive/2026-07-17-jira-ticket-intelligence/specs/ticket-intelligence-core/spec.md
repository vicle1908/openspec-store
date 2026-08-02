# Ticket Intelligence Core — SDK Specification

> This spec defines the **Python SDK contract** for Jira ticket intelligence analysis
> across the TDT ecosystem. All analysis is importable from `jira_skill.analysis.*`.
> CLI commands and scripts are convenience wrappers over the same SDK modules.


## ADDED Requirements

### Requirement: SDK exposes 10-signal TicketIntelligenceBundle from jira_skill.analysis.*

The ticket-intelligence-core contract documented below SHALL apply unchanged for
this delta. The OpenSpec delta section above is the canonical delta
declaration; the FR-N items and SDK Contract Requirements below are
preserved verbatim from the pre-delta-era authoring of this
specification.

#### Scenario: analyze_snapshot is callable with SnapshotScope and returns deterministic bundle

The ticket-intelligence-core is implemented per the FR-N contract below.

---

### Implemented SDK Surface

### ✅ All core analysis modules (8 modules, 4870 lines)

| Module | Lines | Key Exports |
|--------|-------|-------------|
| `signals.py` | 555 | `RootCauseSignal`, `FixStatusSignal`, `FixStatus`, `PreventionAction`, 9-signal `SignalSet` |
| `rca.py` | 251 | `detect_rca()`, `detect_fix_status()`; imports canonical `RCA_PATTERNS` taxonomy from `extractors/rca_patterns.py` |
| `collector.py` | 670 | `FilterSnapshotCollector`, `collect_from_filter()`, `collect_from_jql()` |
| `sheets_writer.py` | 291 | `SheetsWriter.write_bundle()` — 2-tab output, JSON fallback |
| `analyzer.py` | 1365 | `analyze_snapshot()` — orchestrates all 10 signal extractors |
| `bundle.py` | 433 | `TicketIntelligenceBundle` v1.0 |
| `snapshots.py` | 374 | `SnapshotScope`, `SnapshotIssue`, `SnapshotActor` |
| `filter_registry.py` | 496 | `FilterRegistryReader` — reads filter definitions from Google Sheet |

### ✅ All extractors (6 modules, 842 lines)

| Module | Lines | API |
|--------|-------|-----|
| `extractors/content_priority.py` | 156 | `classify_content_priority(full_text, status, comments) -> ContentPriority` |
| `extractors/module.py` | 213 | `detect_module(summary, description, labels, comments) -> Module` |
| `extractors/platform.py` | 108 | `detect_platform(summary, labels) -> Platform` |
| `extractors/project.py` | 68 | `detect_project(issue_key) -> str` |
| `extractors/text_extractor.py` | 50 | `extract_text(adf, max_len=1200) -> str` |
| `extractors/rca_patterns.py` | 215+ | `RCA_PATTERNS` taxonomy: 10 ordered categories, pattern groups, prevention_actions |

### ✅ CLI (1 module, 990 lines)

`jira_skill/cli.py` — `analyze-filter` Typer command with flags:
- `--filter` (single), `--filter-url` (Jira filter page URL), `--filters` (comma-separated), `--registry`, `--registry-tab`, `--jql`
- `--output`, `--worktree`, `--continuous`, `--incremental`, `--bundle-cache`
- `--output` accepts only a Google Sheets spreadsheet ID. There is no `--output json` mode; omit `--output` to allow JSON fallback when no destination sheet is configured.
- Default-filter mode now preserves registry entry metadata (`Spreadsheet ID`, `Sheet Name`, optional `JQL`) so real-run configured filters write to their dedicated Google Sheets instead of degrading to ID-only execution.
- Successful registry-backed filter runs now persist `Last Analyzed` back to the registry, and registry timestamps are written as timezone-aware ISO 8601 while remaining backward-compatible with legacy `%Y-%m-%d %H:%M:%S` values.
- `--auto` prefers favourite filters first, falls back to recently used visible filters, and falls back again to configured defaults only when Jira exposes no visible filters.
- When an auto-discovered filter also exists in the configured default/registry source, the CLI should preserve that entry's `Spreadsheet ID`, `Sheet Name`, and optional `JQL override` instead of degrading the run to ID-only output routing.

### ✅ Script as SDK wrapper (152 lines)

`scripts/classify_filter_15269.py` — thin wrapper over SDK pipeline:
```python
snapshot = await collect_from_filter(FILTER_ID)
bundle = analyze_snapshot(snapshot, source="...")
writer = SheetsWriter(spreadsheet_id=SID)
writer.write_bundle(bundle, tab_prefix="Production Defects (15269)")
```

### ✅ Tests (15 test files)

| File | Focus |
|------|-------|
| `test_bundle.py` | RootCause + FixStatus signal serialization |
| `test_extractors.py` | All 5 extractor functions |
| `test_cli.py` | CLI flag parsing and orchestration |
| `test_continuous.py` | Continuous mode loop |
| `test_incremental.py` | Incremental JQL building |
| `test_sheets_writer.py` | Bundle→sheet row mapping |
| `test_pipeline_integration.py` | Full pipeline end-to-end |
| `test_classify_filter_wrapper.py` | Legacy script wrapper |
| `test_collector_worktree.py` | Worktree enrichment |
| `test_filter_registry.py` | Registry parsing and row-update persistence |
| `test_jira_pagination_fix.py` | Jira pagination regression coverage |
| `test_gitlab_network_fallback.py` | GitLab outage/Jira-only fallback coverage |
| `test_contract.py` | Canonical bundle contract regression checks |
| `test_collector_gitlab.py` | GitLab collector enrichment behavior |
| `test_cli.py` | Dashboard defaults, creation, rollback, and validation command flows |

---

### Remaining Gaps (What's NOT yet implemented)

| Gap | Spec Section | Priority |
|-----|-------------|----------|
| **Structured SCM intelligence contract hardening** — `scm_evidence.py` now models branch role, MR state, pipeline state, confidence, and evidence traces, and `gitlab_evidence.py` provides GitLab-backed enrichment; remaining work is to promote more of that structured evidence into first-class bundle-level fields instead of relying on downstream string rendering conventions. | 5.10 / 5.11 | HIGH — implementation exists; contract promotion / downstream normalization remains |
| **GitLab provider performance and coverage** — GitLab-backed enrichment now runs through `tdt-core` and collector-level bounded concurrency (`Semaphore(8)` + `asyncio.to_thread()`), but provider-level caching / batching and broader repo-resolution heuristics are still pending. | 5.10 / 5.11 | MEDIUM — correctness path exists; performance can improve further |
| **Fixture updates** — all 8 fixture pairs now include current RCA/FixStatus fields | 5.10 | LOW — complete; keep refreshed when bundle contract changes |
| **Skill docs update** — skill docs reflect 9 signals, CLI examples, `--filter-url`, spreadsheet-wide filter extraction, and registry-driven sheet onboarding; keep synced when future flags or evidence semantics change | 5.18 | LOW — complete for current surface |

---

### Consumer Import Patterns

```python
# Core analysis:
from jira_skill.analysis import analyze_snapshot, TicketIntelligenceBundle
from jira_skill.analysis.collector import FilterSnapshotCollector, collect_from_filter, collect_from_jql
from jira_skill.analysis.rca import detect_rca, detect_fix_status
from jira_skill.analysis.sheets_writer import SheetsWriter
from jira_skill.analysis.filter_registry import FilterRegistryReader

# Extractors (enrichment):
from jira_skill.analysis.extractors import classify_content_priority, detect_module, detect_platform, detect_project, extract_text

# Signals:
from jira_skill.analysis.signals import (
    RootCauseSignal, FixStatusSignal, FixStatus, PreventionAction,
    RiskSignal, BlockingSignal, FreshnessSignal, CapacitySignal,
    CompletenessSignal, InsightSignal, SignalSet,
)

# CLI:
from jira_skill.cli import analyze_filter, list_filters

# Script:
# cd jira-skill && uv run python3 scripts/classify_filter_15269.py --filter 15269
# cd jira-skill && uv run python3 scripts/classify_filter_15285.py
```

---

### SDK Contract Requirements

1. **10 signal types** — `SignalSet` aggregates Risk, Blocking, Freshness, Capacity, Completeness, Insight, Dependency, RootCause, FixStatus, Text / Font Display. All optional (None when not applicable).
2. **Deterministic analysis** — Same `SnapshotScope` → same `TicketIntelligenceBundle`. Fixture-testable.
3. **Versioned Pydantic bundle** — Semantic versioning. Additive changes backward-compatible.
4. **Filter→SnapshotScope** — `FilterSnapshotCollector` accepts filter ID, JQL, or registry entry.
5. **RCA from content** — `detect_rca()` matches ticket text against a priority-ordered taxonomy of 10 categories. Lower priority number wins; ties (priority 4) are broken by list order (Text/Font first, then UI Layout). `detect_rca()` returns a `RootCauseSignal` with the primary category and two additive fields (`four_p_lens` and `secondary_categories`) that were missing from the v1 contract:

   The canonical 10-category taxonomy (as implemented in `extractors/rca_patterns.py`):

   1. **Crash / ANR / Force Close** (priority 1, `four_p_lens: "Plant"`)
   2. **Wrong Data / Incorrect Value** (priority 2, `four_p_lens: "Plant"`): stale cache, wrong exchange rate, calculation defects, input validation, sort/filter ordering
   3. **Silent Exit / No Feedback** (priority 3, `four_p_lens: "Plant"`): tap/click produces no observable effect
   4. **Text / Font Display** (priority 4, `four_p_lens: "Plant"`): font size, system font scaling, Dynamic Type, text too large/small/missing, i18n overflow
   5. **UI Layout / Visual Defect** (priority 4, `four_p_lens: "Plant"`): overlaps, misaligned, cut-off, figma mismatch, `hidden and cannot` (moved from Silent Exit), `disabled` interactive elements, `bold` text rendering
   6. **Performance / Slow Loading** (priority 5, `four_p_lens: "Plant"`)
   7. **Authentication / Authorization** (priority 6, `four_p_lens: "Policies"`)
   8. **Network / API Connectivity** (priority 7, `four_p_lens: "Policies"`)
   9. **Feature Not Working / Missing** (priority 8, `four_p_lens: "Procedures"`)
   10. **General UI/UX Polish — no specific pattern matched** (priority 9, `four_p_lens: "People"`, catch-all)

   **RootCauseSignal v2 fields:**
   - `four_p_lens` (`str | None`): the Xurrent 4P bucket for the primary category. `None` for the unclassified sentinel. Values: `"Plant"` (in-house engineering defects), `"Policies"` (access/auth/network rules), `"Procedures"` (broken feature flows), `"People"` (UX/usability). Used by triage teams to distinguish defect class quickly.
   - `secondary_categories` (`list[str]`): every OTHER RCA category that also matched the content, deduplicated and sorted by priority ascending (highest-confidence secondary first). Empty list when only one category matched. Used for understanding compound issues.

   **Pattern relocations (Option A):**
   - `hidden and cannot` / `data is hidden` / `content is hidden` moved from Silent Exit to UI Layout (data is clipped, not absent)
   - `disabled` (interactive state) added to UI Layout; removed from Silent Exit
   - `bold` (text displayed in bold weight) added to UI Layout as a rendering defect; removed from Feature Not Working
   - `reset` + `filter` (state not resetting) added to Feature Not Working

   **New category (Option C):**
   - `Text / Font Display` (priority 4) captures font size, text size, system font, Dynamic Type scaling issues

   **Unclassified sentinel:** non-empty content that matches no pattern returns `RootCauseSignal(category="General UI/UX Polish — no specific pattern matched", confidence=0.0, four_p_lens=None, secondary_categories=[])`. Empty/whitespace input still returns `None`.
6. **Fix status detection** — `detect_fix_status()` currently checks QA keywords > developer keywords > MR refs > Jira status > worktree commits, but the target contract must evolve toward QA verification > structured SCM intelligence > Jira status > local worktree heuristics.
7. **Evidence layers** — the contract distinguishes deterministic ticket evidence, structured SCM intelligence evidence, and optional semantic enrichment.
8. **Branch semantics** — branch-related evidence must distinguish active testing context, historical fix context, merged-fix references, and unknown branch state when possible.
9. **Platform/module/project enrichment** — Via `extractors.*` detectors on ticket content.
10. **Bundle→Sheets** — `SheetsWriter.write_bundle()` produces 2-tab output (`<prefix> - Classification`, `<prefix> - Summary`) via `tdt_sheets`. For CLI-driven filter runs, `<prefix>` must be human-readable and filter-derived: use sanitized registry/default `Sheet Name` metadata when available, append `(<filter-id>)` when the label does not already include the id, and otherwise fall back to `Filter <id>`. The Classification tab SHALL include the issue's target version when Jira exposes one, sourced from `SnapshotIssue.target_version` and carried through `BundleIssueIdentity.target_version`. The Classification tab renders three distinct evidence columns:
    - **Analysis Evidence** — `code_evidence` from the bundle (commit lines, diff hits, code references)
    - **SCM / Branch Evidence** — `scm_evidence` from the bundle (branch names with structured prefixes, MR state `mr_state:*`, pipeline state `pipeline_state:*`)
    - **Worktree Commits** — entries filtered from `scm_evidence` that contain `"commits mention"` or `"commits touch"`
    The three columns are semantically distinct. In the live Jira path (no structured SCM provider), `scm_evidence` is backfilled from `code_context` entries produced by `FilterSnapshotCollector` that carry structured prefixes. When both evidence sources are absent, all three columns render as empty strings.
11. **Filter registry / spreadsheet extraction** — `FilterRegistryReader` supports both structured registry-row parsing via `read()` and spreadsheet-wide filter extraction via `read_all_filters()`. Spreadsheet-wide extraction scans all tabs (or a caller-provided subset), detects filter IDs from raw numeric cells, Jira filter URLs containing `filter` / `filterId`, and inline labels such as `filter-15285 - Summary`, deduplicates matches, and preserves the first-seen tab metadata for each unique filter.
12. **Unified CLI** — `jira-skill analyze-filter` orchestrates collector → analyzer → writer. `--output` is a destination spreadsheet identifier only; it must reject pseudo-modes such as `json`, and JSON bundle persistence remains fallback behavior rather than an explicit output mode.
13. **Continuous mode** — `--continuous 24h` loop with timestamp logging.
14. **Incremental mode** — `--incremental` filters by `updated >= last_run` JQL.
15. **Worktree fallback** — `--worktree` remains optional local augmentation and fallback, not the strongest source of SCM truth.
16. **Filter URL convenience input** — `--filter-url` should accept a Jira filter page URL, extract a numeric filter identifier from `filter` or `filterId`, and route through the same single-filter execution path as `--filter`.
17. **Default configured real run** — `--use-default-filters` should load the real-run filter set from the spreadsheet source declared in `JIRA_DEFAULT_FILTER_REGISTRY_ID` (scanning the configured tab when `JIRA_DEFAULT_FILTER_REGISTRY_TAB` is set); if that spreadsheet source is unavailable or empty, it should fall back to `JIRA_DEFAULT_FILTER_IDS` (comma-separated) and then `JIRA_FILTER_ID` for single-filter compatibility. Explicit CLI input modes must override these defaults. When the spreadsheet source is available, the CLI must preserve per-filter registry metadata (`Spreadsheet ID`, `Sheet Name`, optional `JQL override`) instead of collapsing the run to bare filter IDs.
18. **Auto-resolve output for ad-hoc input modes** — `--filter`, `--filters`, and `--filter-url` should automatically resolve the JTI workbook as the output destination when `JIRA_DEFAULT_FILTER_REGISTRY_ID` is configured and no explicit `--output` is provided. Resolution order: explicit `--output` → registry entry's own `Spreadsheet ID` → `JIRA_DEFAULT_FILTER_REGISTRY_ID` itself (shared JTI workbook) → `None` (JSON fallback). This eliminates the need to pass `--output` for routine per-filter analysis calls.
19. **Parallel multi-filter execution** — when multiple filters are selected through `--filters`, `--use-default-filters`, `--auto`, or spreadsheet mode via `--registry`, the CLI should schedule per-filter runs concurrently and emit a final summary containing each filter's independent result, including whether canonical sheet output was written or skipped.
20. **Spreadsheet-driven onboarding** — the canonical spreadsheet workflow is no longer limited to one registry tab. Newly added filters can be onboarded either through a structured registry row (`Filter ID`, `Sheet Name`, `Spreadsheet ID`, `Enabled`) or by being present anywhere in the source spreadsheet as a numeric filter ID, Jira filter URL, or inline label. For the current real-run contract, the spreadsheet exposes six active filters, and `--use-default-filters` / `--registry` should analyze those same six filters. If a structured registry entry is enabled but has no `Spreadsheet ID`, the CLI should create a dedicated spreadsheet, persist the new ID back to the registry row, and then write the canonical tabs there. If a registry row already provides a spreadsheet ID, the CLI must reuse it rather than requiring `--output`. Successful registry-backed filter runs should also persist `Last Analyzed` back to the structured registry row using timezone-aware timestamps. The registry `Sheet Name` column is the canonical human-facing label for tab prefixes and should be chosen to minimize operator confusion.
21. **Full filter coverage** — a filter-based run must analyze every issue returned by the resolved filter or JQL at collection time. Multi-filter/default-filter convenience modes must preserve that same full-coverage behavior per selected filter; they must never truncate coverage because of output-routing shortcuts or registry-metadata loss. When Jira emits token-based pagination metadata (`nextPageToken`) instead of `total`, the collector must follow those tokens until exhaustion while still protecting against duplicate pages and zero-progress loops.
22. **Operational logging contract** — long-running live runs must emit actionable progress logs for collection and enrichment. At minimum the implementation should log collector start context, fetched issue counts, enrichment start, periodic GitLab enrichment progress, enrichment summary counts, and final per-filter write status so operators can debug hangs, partial failures, and skipped writes from terminal output alone.
23. **Network-degraded SCM fallback** — when GitLab transport becomes unavailable or exceeds a bounded timeout, the runtime must degrade to Jira-only analysis for the rest of the process rather than repeatedly probing the dead endpoint. The GitLab project-search timeout should be configurable for operator environments with unstable connectivity.
24. **Optional convenience wrappers** — filter-specific scripts such as `classify_filter_15269.py` and `classify_filter_15285.py` remain secondary wrappers over the same SDK pipeline rather than separate implementations.
25. **Registry timestamp compatibility** — `FilterRegistryReader` must write `Last Analyzed` values using timezone-aware ISO 8601 strings and continue to read legacy `%Y-%m-%d %H:%M:%S` registry values as UTC for backward compatibility during migration.
26. **Auto-discovery behavior** — `--auto` should prefer favourite visible Jira filters, then fall back to recently used visible filters, and only fall back to configured defaults when Jira exposes no visible filters to the caller. When an auto-discovered filter matches an entry from the configured default/registry source, the CLI must preserve that entry's `Spreadsheet ID`, `Sheet Name`, and optional `JQL override` so auto mode reuses canonical routing metadata instead of behaving as bare filter-ID execution.
27. **Dashboard config validation contract** — dashboard creation and validation commands must treat the Jira v3 dashboard item `config` property (`rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/config`) as the canonical read/write surface for gadget configuration. Validation SHALL read that v3 property first and compare against the declarative layout/profile contract for each supported gadget. Legacy dashboard prefs (`/rest/dashboards/1.0/{dashboardId}/gadget/{gadgetId}/prefs`) MAY still be written and read only as a compatibility fallback when v3 property readback is unavailable. Validation success MUST therefore mean the canonical v3 config matches the expected gadget contract, not merely that legacy prefs happen to mirror a prior write.
28. **Default-filter exclusion contract (defense in depth)** — `JIRA_DEFAULT_EXCLUDED_FILTER_IDS` (comma-separated Jira filter IDs, digits only, whitespace tolerated) defines a hard exclusion list that `jira_skill.cli._default_filter_entries_from_config()` consults after building default entries from the registry sheet, the `JIRA_DEFAULT_FILTER_IDS` fallback, the legacy `JIRA_FILTER_ID` fallback, and the `JiraConfig.from_env()` fallback. Matching IDs are dropped from every default-filter entry source before they are returned to bulk-mode consumers (`--use-default-filters`, `--auto`, registry mode, dashboard default resolution). The CLI SHALL log a dim status line reporting which IDs were excluded so operators can verify the contract from terminal output. Excluded entries are filtered but never replace the canonical entry metadata of the surviving entries: `Spreadsheet ID`, `Sheet Name`, and `JQL override` survive intact for the kept filters. Unset / empty `JIRA_DEFAULT_EXCLUDED_FILTER_IDS` returns the unmodified list (no exclusions). The hourly `jira-ticket-intelligence-hourly` workflow is structurally immune to this contract because its subprocess invocation hardcodes `--filter-url https://...filter=15285` (single-filter mode), so the exclusion list only ever affects ad-hoc or `--use-default-filters` invocations. Explicit `--filter <id>` invocations MUST still run the named filter even when `<id>` is in the exclude list — the contract is strictly opt-out for bulk modes; per-filter explicit requests always win.
