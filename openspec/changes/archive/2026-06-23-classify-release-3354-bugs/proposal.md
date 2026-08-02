# Release 3.3.54 Bug Classification — RCA + Prevention

**Status:** Complete — 246/246 tickets with RCA + Prevention
**Entry point:** `cd $HOME/Developer/tdt/jira-skill && uv run jira-skill analyze-filter --filter 15269 --output <spreadsheet-id>`

> Historical note: the original release-specific script (`scripts/classify_filter_15269.py`) now delegates to the shared `jira_skill.analysis` SDK pipeline
> (`collect_from_filter()`, `analyze_snapshot()`, `SheetsWriter`, and reusable extractor/RCA helpers).
> It is retained as a convenience entrypoint, not a separate implementation path.

## Google Sheet (2 tabs)

| Tab | GID | What It Covers |
|-----|-----|----------------|
| **Mainflow3.3.54** | 200255358 | 246 issues × 19 columns — raw classification with project, content priority, module, platform, fix status, merged status |
| **Filter 15269 Analysis** | 367804524 | 6-section comprehensive report: Executive Summary → All 246 tickets with RCA + prevention → P0/P1 detail → 10-item Prevention Plan → RCA×Prevention mapping |

**Base URL:** https://docs.google.com/spreadsheets/d/1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8/edit

## Corrected Risk (content-based, not Jira labels)

| Risk | Count | Note |
|------|-------|------|
| 🚨 P0 — CRITICAL | 3 | Crash, wrong financial data, API failure |
| 🔴 P1 — MUST FIX | 5 | Navigation broken, input blocked, PMP not updating |
| 🟡 P2 — SHOULD FIX | 72 | Layout regressions, text/label, minor regressions |
| ⚠️ IN REVIEW | 99 | MRs exist, awaiting approval/merge |
| ✅ RESOLVED | 67 | Already fixed, verified or awaiting retest |

## 13 Root Cause Categories

| RCA | Count | % | Prevention |
|-----|-------|---|------------|
| Platform parity — iOS vs Android | 113 | 45.9% | Visual regression suite + paired QA |
| Fixed in code, not re-verified | 64 | 26.0% | Retest latest build, close |
| General UI/UX Polish | 31 | 12.6% | Standard QA review |
| Layout regression — hidden/overlapping | 25 | 10.2% | Visual regression at 3 sizes |
| sp/dp unit mismatch | 9 | 3.7% | Lint rule: forbid sp on labels |
| UI state not synced after action | 8 | 3.3% | Reset UI state on dialog dismiss |
| API missing field — silent exit | 6 | 2.4% | Validate API response completeness |
| Tab/filter state leak | 4 | 1.6% | Clear adapter on tab change |
| PMP callback not wired | 4 | 1.6% | Wire callbacks to all UI elements |
| Missing softInputMode | 4 | 1.6% | Lint rule: adjustPan on BottomSheet |
| Crash — no bounds check | 2 | 0.8% | Monkey test + crash guard |
| Hardcoded string | 2 | 0.8% | Lint rule: flag hardcoded strings |
| BottomSheet gesture conflict | 1 | 0.4% | Swipe-to-dismiss test |

## 10 Global Prevention Actions

| # | Action | Effort | Timeline |
|---|--------|--------|----------|
| 1 | Cross-platform visual regression test suite | HIGH | Q3 |
| 2 | Lint rule: softInputMode=adjustPan on BottomSheets | LOW | This sprint |
| 3 | Lint rule: forbid sp on non-body text labels | LOW | This sprint |
| 4 | Defensive: validate API error response completeness | MEDIUM | Next sprint |
| 5 | Pattern: reset UI state on dialog dismiss | LOW | This sprint |
| 6 | Audit: wire PMP callbacks to all UI elements | MEDIUM | Next sprint |
| 7 | Monkey test automation on crash-prone screens | MEDIUM | Before release |
| 8 | Paired Android+iOS QA review before branch cut | LOW | Every sprint |
| 9 | Clear adapter/dropdown state on tab change | LOW | This sprint |
| 10 | Refactor: common ConfirmBottomSheet component | MEDIUM | Next sprint |

## Architecture

```text
jira-skill/
  scripts/
    classify_filter_15269.py    ← convenience wrapper over shared SDK pipeline
  src/jira_skill/analysis/
    collector.py                ← filter/JQL snapshot collection
    analyzer.py                 ← canonical bundle generation
    sheets_writer.py            ← canonical output tabs
    extractors/                 ← reusable content/platform/module/project helpers
    rca.py                      ← RCA + fix-status helpers
  data/
    filter_15269_classified.json ← full classified dataset
```

**Dependencies:** `jira-skill` → `tdt-core` (Jira API) + `tdt-sheets` (Google Sheets)
**Auth:** `~/.tdt/.env` → `GOOGLE_SERVICE_ACCOUNT_PATH` + `ATLASSIAN_*`
**Worktrees:** `poems-mobile3-android-3.3.54` + `poems-mobile3-ios-3.3.54`
