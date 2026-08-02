# Design — Impact Sheet Integration

**Companion to:** `proposal.md`
**Specs:** `specs/impact-sheet-integration/spec.md`, `specs/impact-shared-primitive/spec.md`, `specs/impact-raw-report-cache/spec.md`

## Context

The TDT ecosystem has three independent analysis paths that touch the same Jira + GitLab APIs but share no state:

1. **`jira-skill` CLI** (`impact mr`, `impact ticket`) — interactive analysis, writes JSON cache + posts Jira ADF comments.
2. **`webhook-receiver`** (`run_impact_workflow`, `run_gitlab_note_workflow`) — DBOS-scheduled on MR merge, writes JSON cache + posts Jira ADF comments and GitLab MR notes.
3. **`jira-ticket-intelligence` skill** (`analyze_filter`) — sheets-first; writes Classification + Summary tabs.

Research-validated findings from 2026-06-28 surface duplication and missing primitives:

| # | Finding | Resolution |
|---|---------|------------|
| F1 | `write_raw_report` exists; no reader | New `read_raw_report` + `RawReportCache` class |
| F2 | Two near-identical pipelines in `webhook-receiver` and CLI | Extract `analyze_mr_to_report` shared primitive |
| F3 | Cache age-check would re-implement mtime | `RawReportCache` owns read + TTL check |
| F4 | `SheetsWriter._build_classification_rows` has 21 hardcoded columns | `CLASSIFICATION_COLUMNS` constant |
| F5 | Cascade aggregation would bloat writer | `ImpactCascadeSummary` pure helper |
| F6 | Epic-report/dashboards may also want impact | `ImpactEnricher` callable standalone |
| F7 | `ImpactRow` shape opinionated | `ImpactRow.extras` forward-compat field |

Stakeholders: dev (mobile engineers), QA (test plan owners), PM (sprint-level rollups).

## Goals / Non-Goals

**Goals:**

- Sheet-level rendering of per-ticket merged-MR impact and per-filter cascade summary.
- Eliminate the ~80 LOC of duplicated orchestration between `webhook-receiver` and `jira-skill` CLI.
- Provide a single `RawReportCache` interface so writer and reader use the same lifecycle.
- Reusable impact aggregation (cascade summary) usable outside Google Sheets.
- Backward-compatible bundle version bump (v1.0 → v1.1 additive).
- Operator opt-out via `JIRA_SKILL_IMPACT_IN_SHEETS=false` env or `--no-impact` flag.

**Non-Goals:**

- Re-designing the existing `ImpactReport` model — only adds readers.
- Real-time impact push (events, webhooks) — sheets are written at analysis time only.
- Cross-repo cascade aggregation — each row stays scoped to one MR's repo.
- Replacing `jira impact ticket` or `jira impact mr` — they remain operational CLIs.

## Decisions

### D1. Shared primitive `analyze_mr_to_report` lives in `jira-skill`

**Decision:** Add `analyze_mr_to_report(project_path, mr_iid, mr_url, triggered_by, ticket_key=None, state_dir=None, cache=None, *, payload_metadata=None)` to `jira_skill.impact.impact_report`. Both `webhook-receiver`'s `_run_pipeline` and `jira_skill.impact.impact_cli:impact_mr` delegate to it.

**Why here:** The cache naming convention (`webhook-impacts/<iid>-<sha>.json`) and `ImpactReport` schema are already owned by `jira-skill`. Importing the primitive into `webhook-receiver` preserves the existing dependency direction (webhook-receiver depends on jira-skill).

**Alternatives considered:**
- *Move the primitive into `tdt-core`*: rejected — requires lifting `ImpactReport` and the cache layout into a shared library, expanding the blast radius.
- *Duplicate but factor out via callback*: rejected — increases coupling; the new code is clearer as a flat function.

### D2. `RawReportCache` wraps both read and write

**Decision:** Add `RawReportCache.get()`, `put()`, `invalidate()` methods around the existing `write_raw_report`. The default state dir is `$TDT_HOME/state/webhook-receiver/webhook-impacts/` (matches the convention already used by webhook-receiver).

**Why a class:** Single-instance ownership of `ttl_hours` and `state_dir` parameters avoids threading them through every call site. Tests can construct a `RawReportCache(state_dir=tmp_path, ttl_hours=0)` to bypass TTL.

**TTL semantics:** `get()` returns `None` when the file is missing OR when `age_hours >= ttl_hours`. `put()` overwrites unconditionally. Stale files are not deleted by `get()` (only corrupt files are).

### D3. `ImpactEnricher` is callable standalone

**Decision:** `ImpactEnricher` exposes both `enrich_bundle(bundle)` and `enrich_issue_keys(keys)`. The latter does not require a `TicketIntelligenceBundle` and is the public entry point for epic-report, dashboards, and any future consumer.

**Why standalone:** Epic-report currently constructs ad-hoc MR→ticket mappings via `TicketMrResolver` directly. By making the enricher reusable, we replace ~80 LOC of duplicate MR-resolution-and-impact-aggregation logic across two consumers with a single ~30 LOC call.

**Failure isolation:** Each `_enrich_one(key)` runs inside an `asyncio.Semaphore` (default 8). Failure paths produce `ImpactRow(impact_status="unavailable")` and never raise into the caller.

### D4. `CLASSIFICATION_COLUMNS` constant is the single source of truth

**Decision:** Move the 24-column header list to a module-level `CLASSIFICATION_COLUMNS: list[str]` constant in `sheets_writer.py`. Header construction and per-row cell alignment both reference it. Tests assert against `len(CLASSIFICATION_COLUMNS)` rather than hardcoded `24`.

**Why a module constant:** Pydantic models for the layout would be over-engineered; a flat list with named entries is more readable and matches the existing `_build_classification_rows` style.

### D5. `ImpactCascadeSummary.build()` is a pure function

**Decision:** Add `ImpactCascadeSummary.build(rows: list[ImpactRow]) -> dict[str, Any]` in a new module `jira_skill.analysis.impact_cascade`. The function does NOT import Google Sheets, pydantic, or asyncio — it's a plain Python aggregation.

**Why outside `SheetsWriter`:** SheetsWriter's job is to translate data into row tuples. Aggregation logic belongs to the data layer so any consumer (SheetsWriter, epic-report dashboards, JSON exports) can call it.

### D6. Bundle version bumps MINOR only

**Decision:** `BundleVersion.MINOR = 1`. The `impact` field is added with `default=None`; existing v1.0 consumers see no change. New v1.1 consumers see the optional `impact` field.

**Why not MAJOR:** The spec says "MAJOR when removing or renaming fields." Adding an optional field is the textbook MINOR case.

### D7. `ImpactRow.extras` is a forward-compat escape hatch

**Decision:** `ImpactRow.extras: dict[str, Any] = Field(default_factory=dict)`. Consumers MUST treat unknown keys as opaque. The schema_version field on `ImpactSnapshot` bumps when `ImpactRow` required fields change — `extras` exists so we don't need to bump it for new optional columns.

**Why a dict and not typed fields:** If we later add `recommended_tests: list[str]` (or any other impact-related signal), the only change is a writer expression that emits a new column from `row.extras["recommended_tests"]`. No bundle migration, no consumer breakage.

### D8. Feature flag, not rollout gating

**Decision:** `JIRA_SKILL_IMPACT_IN_SHEETS=true` (default) plus `--no-impact` CLI override. Operators flip the env var to disable instantly. No DBOS step or feature-flag service needed.

**Why env flag:** The bundle's `impact=None` default already handles the disabled state cleanly — no empty cells when impact is absent. The risk surface is minimal because the enricher is read-only and idempotent.

## Architecture

```
jira-skill analyze-filter --filter 15269
  │
  ├─→ collect_from_filter(15269) → SnapshotScope
  │
  ├─→ analyze_snapshot(snapshot, enrich_impact=True)
  │     │
  │     └─→ _build_bundle() → TicketIntelligenceBundle (impact=None)
  │     │
  │     └─→ ImpactEnricher.enrich_bundle(bundle)        [async, in thread pool]
  │           │
  │           ├─→ For each issue:
  │           │     ├─→ TicketMrResolver.resolve_merged_mrs(key)
  │           │     ├─→ For each MR:
  │           │     │     ├─→ RawReportCache.get(...)           ← hit? return
  │           │     │     ├─→ analyze_mr_to_report(...)         ← miss, run pipeline
  │           │     │     │     ├─→ fetch_mr_changes
  │           │     │     │     ├─→ fetch_mr_metadata → SHA resolve
  │           │     │     │     ├─→ analyze_diff
  │           │     │     │     ├─→ build_impact_report
  │           │     │     │     └─→ RawReportCache.put(report)
  │           │     │     └─→ aggregate → ImpactRow
  │           │     └─→ ImpactSnapshot(by_issue_key={...})
  │           │
  │           └─→ Returns ImpactSnapshot (mutates bundle.impact)
  │
  └─→ SheetsWriter.write_bundle(bundle, ...)
        │
        ├─→ _build_classification_rows()
        │     header = CLASSIFICATION_COLUMNS  # 24 entries
        │     for each issue: 21 existing cells + 3 impact cells
        │
        └─→ _build_summary_rows()
              ImpactCascadeSummary.build(rows)  # pure helper
              cascade dict → rows
```

Standalone use:

```
ImpactEnricher(jira).enrich_issue_keys(["PROJ-1", "PROJ-2"])
  → ImpactSnapshot (no bundle required)
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **Per-ticket GitLab API calls** (1–2 calls per Jira issue) when `enrich_impact=True` | `RawReportCache` 24h TTL; `concurrency=8` semaphore; opt-out via `--no-impact` |
| **Cache corruption causes silent reruns** | `RawReportCache.get()` deletes corrupt files; `impact_workflow_pipeline_failed` log emitted on every rerun |
| **Bundle v1.1 fixtures must be updated** | Add `"impact": null` to all 8 fixture JSON files; documented in tasks Phase 11 |
| **Tests touching `_run_pipeline` break when webhook-receiver is refactored** | New `test_analyze_mr_to_report.py` regression tests; legacy test patterns preserved |
| **Operator forgets to set env var and gets impact column latency** | Default is `True` per design decision D8; CLI flag is explicit. Document in `jira-skill/CHANGELOG`. |
| **`ImpactRow.extras` becomes a dumping ground** | Code review convention: extras keys MUST map to a column in `CLASSIFICATION_COLUMNS` or to a Summary section metric; otherwise require a spec delta |
| **Concurrent writes to same cache file** | Single-process semantics; `concurrency=8` is below the per-process fd limit; tests use `tmp_path` isolation |

## Migration Plan

### Pre-deploy

1. Run `uv run pytest tests/ -q` in `jira-skill` and `webhook-receiver`. Record baseline.
2. Verify `BundleVersion.current()` returns `"v1.0"` before deploy.

### Deploy order

1. **`jira-skill` first**: Push Phase 1–8 changes (cache, enricher, bundle models, writer, analyzer). Bundle v1.1 lands with `impact=null` everywhere until the analyzer runs.
2. **`webhook-receiver` second**: Push Phase 3 refactor. This is independent of step 1 — the shared primitive is backward-compatible.
3. **CLI flag**: Push Phase 9 — `--with-impact/--no-impact` becomes available.

### Rollback

- **Single knob:** `JIRA_SKILL_IMPACT_IN_SHEETS=false`. Bundle still validates; writer renders empty cells.
- **CLI:** `--no-impact` flag opts out per run.
- **Schema:** Drop `bundle.impact` requires v2.0 + 8-fixture migration — NOT recommended.
- **Cache:** `RawReportCache.invalidate()` removes specific entries; bulk purge via `rm ~/.tdt/state/webhook-receiver/webhook-impacts/*.json`.

### Smoke verification post-deploy

```bash
cd $HOME/Developer/tdt/jira-skill && uv run jira-skill analyze-filter --filter 15269
# Expect: Classification tab has 24 columns; Summary tab has Impact Summary section.
```

## Open Questions

- **Q1**: Should the cascade summary also be exposed as a Slack message for QA? — Defer to a future change.
- **Q2**: Do we want a `--impact-only` mode that writes only the Impact Summary section (skipping Classification)? — Defer until real-world usage reveals a need.
- **Q3**: When `extras` keys become a real column, do we bump `schema_version` or stay at 1.0? — Current decision: bump only when required fields change. Add as a follow-up spec delta if real-world usage changes this rule.