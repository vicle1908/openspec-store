# Proposal: Impact Sheet Integration

## Why

The `jira-ticket-intelligence` skill (`analyze-filter`) writes two tabs per Jira filter: Classification (21 columns of ticket-level signals) and Summary (per-filter aggregates). The impact-analysis pipeline produces code-level impact reports (changed files, at-risk modules, recommended tests, coverage gaps), but today only posts them as Jira ADF comments. Impact data never reaches the sheets that dev/QA/PM already read.

Three gaps:

1. **Per-ticket: no impact in sheets** — the Classification tab has no MR-level or code-level data.
2. **No cascade summary** — devs/QA/PMs each need different views of feature-wide blast radius, but no aggregate exists.
3. **Impact runs independently of JTI** — `analyze-filter` and `jira impact ticket` share no state; impact is recomputed ad-hoc per ticket.

Research-validated duplication findings (2026-06-28) also surfaced that **two near-identical orchestration paths** (in `webhook-receiver` and `jira-skill` CLI) repeat the same fetch → analyze_diff → build_impact_report pipeline, and the impact report cache has a writer but no reader. Solving the integration gap is the right moment to extract the shared primitive and unify the cache.

## What Changes

- **Add `ImpactSnapshot` to `TicketIntelligenceBundle`** — optional, populated when `JIRA_SKILL_IMPACT_IN_SHEETS=true` (default).
- **Add 3 impact columns** to the Classification tab: MR Links, Files Changed, At-Risk Modules.
- **Add an Impact Summary section** to the Summary tab with team-aware cascade aggregates.
- **Extract a shared `analyze_mr_to_report` primitive** in `impact_report.py` that both webhook-receiver and the CLI now call (~80 LOC of duplication eliminated).
- **Add `RawReportCache` class** with `read_raw_report` + age-check — currently the cache is write-only.
- **Add `ImpactEnricher`** that bridges `TicketMrResolver` + `analyze_mr_to_report` + cache, callable both standalone and inside `analyze_snapshot`.
- **Add `ImpactCascadeSummary` pure helper** that any consumer (SheetsWriter, dashboards, epic-report) can reuse.
- **Add CLI flag** `--with-impact/--no-impact` to opt out per run.

No **BREAKING** changes. Bundle bumps from v1.0 to v1.1 (additive optional field). All existing tests remain green.

## Capabilities

### New Capabilities

- `impact-sheet-integration`: enriches `TicketIntelligenceBundle` with merged-MR impact data and renders three new Classification columns plus a Cascade Summary section in the Summary tab.
- `impact-shared-primitive`: a single `analyze_mr_to_report()` async function used by webhook-receiver, jira-skill CLI, and the new enricher — eliminating duplicated fetch → analyze_diff → build_impact_report orchestration.
- `impact-raw-report-cache`: a `RawReportCache` class wrapping the on-disk JSON cache with read/age-check/invalidate, replacing the write-only `write_raw_report` standalone function.

### Modified Capabilities

None. The existing `impact-analysis-core` and `gitlab-impact-note` specs are **unchanged** — this change adds new consumers and reuses the existing `ImpactReport` model without modifying its requirements. The `TicketIntelligenceBundle` version bumps from v1.0 to v1.1 (additive), but no spec-level requirement changes.

## Impact

| Area | Impact |
|------|--------|
| `jira-skill/impact/impact_report.py` | +120 LOC (4 new symbols); zero removal |
| `jira-skill/impact/impact_cli.py` | -30 LOC (refactor to use shared primitive) |
| `webhook-receiver/impact.py` | -50 LOC (refactor to use shared primitive) |
| `jira-skill/analysis/bundle.py` | +40 LOC (2 models + version bump) |
| `jira-skill/analysis/sheets_writer.py` | +35 LOC (column constant + 3 cells + cascade section) |
| `jira-skill/analysis/analyzer.py` | +15 LOC (enricher wiring) |
| `jira-skill/impact/enrichment.py` | **New** +150 LOC (`ImpactEnricher`) |
| `jira-skill/analysis/impact_cascade.py` | **New** +30 LOC (`ImpactCascadeSummary`) |
| `jira-skill/cli.py` | +5 LOC (CLI flag) |
| Bundle fixtures (8 files) | Add `"impact": null` (1 LOC each) |
| New test files (5) | +600 LOC across 5 test modules |
| **Net code change** | **+310 / -80 = +230 LOC** |
| **Duplication eliminated** | **~80 LOC** of orchestration removed across 2 repos |

**External consumers:**

- `jira-epic-report` (separate change) can now call `ImpactEnricher.enrich_issue_keys(...)` standalone — no bundle construction required (~5 LOC consumer-side change).
- Dashboard consumers (CLI / `code-daily-scan`) can call `ImpactCascadeSummary.build(rows)` for feature-wide blast radius aggregation without depending on Google Sheets.

**Risk:**

- GitLab API calls per ticket (1–2 per Jira issue) when `enrich_impact=True`. Mitigated by `RawReportCache` (24h TTL) and `concurrency=8` semaphore.
- New failure modes (GitLab unreachable, stale index) are captured in `ImpactRow.impact_status` and never raise.

**Rollback:** Set `JIRA_SKILL_IMPACT_IN_SHEETS=false`. Bundle remains valid with `impact=null` and the 3 columns render as empty strings.