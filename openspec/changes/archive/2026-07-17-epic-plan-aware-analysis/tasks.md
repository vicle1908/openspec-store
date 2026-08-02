## 1. Apply Gate And Baseline

- [x] 1.1 In both `tdt-sheets` and `jira-epic-report`, confirm `epic-plan-aware-analysis` is the active change, inspect `git status`, and record pre-existing unrelated changes without reverting them.
- [x] 1.2 Run GitNexus upstream impact analysis for every existing function, class, or method implementation will modify; stop for user confirmation on HIGH or CRITICAL impact.
- [x] 1.3 Capture targeted baseline results for `tdt-sheets` client/backend/models and epic-report config, CLI, models, analyzers, and spreadsheet reporter tests.

## 2. Add Public TDT Sheets Grid Snapshot

- [x] 2.1 Add frozen public snapshot models for spreadsheet/sheet identity, locale/timezone, resolved range, merge ranges, and coordinate-bearing effective/formatted cell values without exposing raw API dictionaries.
- [x] 2.2 Add `SheetsClient.read_grid_snapshot(...)` and the backend protocol contract; implement one bounded, field-masked `spreadsheets.get` read in `SDKBackend` using existing request tracking, service caching, and error translation.
- [x] 2.3 Make unsupported backends fail explicitly with `BackendNotAvailableError` or `NotImplementedError`; do not return incomplete snapshots or alter existing backend-equivalence contracts.
- [x] 2.4 Add SDK/client/model tests for field masking, grid offsets and empty cells, merges, locale/timezone, translated failures, and unsupported backend behavior.
- [x] 2.5 Run targeted and full `tdt-sheets` tests, `ruff`, formatting, and strict mypy before integrating the consumer.

## 3. Protect Workbook Source Tabs

- [x] 3.1 Add failing reporter tests proving `Epic Plan` and an arbitrary stakeholder tab are never included in clear, rewrite, rename, format, or delete requests.
- [x] 3.2 Refactor managed-sheet ownership so synchronization deletes only obsolete titles positively identified in the static managed-output allow-list and preserves every protected/unmanaged tab.
- [x] 3.3 Preserve stale dynamic per-epic tabs without durable ownership metadata; prove Jira-key-like title patterns alone never authorize deletion.
- [x] 3.4 Prove an obsolete static managed output tab may still be removed without affecting source/unmanaged tabs.
- [x] 3.5 Run targeted spreadsheet guard/reporter suites before live integration.

## 4. Configuration And Plan Models

- [x] 4.1 Add typed `[epic_plan]` configuration for `enabled`, `sheet_name`, bounded tab-relative `snapshot_range` (default `A1:ZZ500`), additive API deployment aliases, and per-Jira-key `activity` plus optional `release_version` mappings.
- [x] 4.2 Normalize Jira mapping keys; validate non-empty mappings/aliases and a finite range belonging to the configured tab; preserve Jira-only compatibility when the section is absent or disabled.
- [x] 4.3 Add plan-domain models for source references, diagnostics, precision, windows, sprint overlaps, release targets/gates, extraction states, and `EpicPlanContext` without repurposing Jira-owned fields.
- [x] 4.4 Add `PlanAwareEpicAnalysis` so every requested epic has one explicit state when enrichment is enabled; reserve `EpicPlanContext` for `MATCHED` results and never encode a business state as `None`.
- [x] 4.5 Add config/model tests for absent sections, valid mappings, disambiguators, invalid entries, precision, optional API deployment, states, and serialization.

## 5. Read-Only Workbook Snapshot

- [x] 5.1 Implement an Epic Plan reader over public `SheetsClient.read_grid_snapshot(...)` and resolved `config.output.spreadsheet_url`; do not access private backends, add a raw Google client, or add a dependency.
- [x] 5.2 Read one configured bounded snapshot per run, translate it into plan transport models reused for all epics, and emit `SNAPSHOT_BOUNDARY_REACHED` when non-empty data touches the final configured row or column.
- [x] 5.3 Translate permission, missing-tab, malformed-snapshot, unsupported-backend, rate-limit, and network failures to stable source-unavailable diagnostics without secrets or workbook dumps.
- [x] 5.4 Add reader tests proving one snapshot is reused, scheduled environment URL resolution is honored through `AppConfig`, and the plan-reader interface exposes no write operation.

## 6. Epic Plan Structural Parser

- [x] 6.1 Add sanitized fixtures for the observed hierarchy, `DLC Visibility`, UAT/Beta, month-only release, `Not ready yet`, `0-Jan`, year crossing/ambiguity, duplicate APP rows, and explicit API Deployment.
- [x] 6.2 Implement case-folded/collapsed-whitespace exact header aliases for Version, No, Major Activities, Teams, resources, person-days, Start, End, and date axis without coordinate fallback.
- [x] 6.3 Parse merged sprint headers from effective calendar dates and parse merged/inherited release groups with deterministic `DAY`, `MONTH`, or `UNSPECIFIED` precision and year resolution.
- [x] 6.4 Enforce row boundaries: non-empty `No` starts a major activity, non-empty Version starts a release group, and child inheritance never crosses either boundary.
- [x] 6.5 Parse exactly one APP development row, approved explicit API deployment rows, UAT/Beta parent-plus-dated-QA-child gates, and unknown phases with provenance; reject ambiguity rather than merging silently.
- [x] 6.6 Derive all inclusive APP sprint overlaps, retaining full sprint and overlap ranges.
- [x] 6.7 Ignore colors, formulas, notes, summaries, and formatting; emit stable source-located diagnostics for malformed hierarchy, dates, intervals, and ambiguous year.
- [x] 6.8 Assert the accepted fixture values: development 2026-07-07 to 2026-07-30, Sprint 18/19 overlaps, release 3.3.56 on 2026-09-05, UAT/Beta, and absent API deployment.

## 7. Explicit Epic Matching

- [x] 7.1 Implement exact normalized activity matching keyed by configured Jira epic, with optional exact release-version disambiguation and no fuzzy fallback.
- [x] 7.2 Return deterministic `MATCHED`, `UNMAPPED`, `NOT_FOUND`, and `AMBIGUOUS` extraction results; map global read/structural failures to `SOURCE_UNAVAILABLE` or `PARSE_INVALID` for every requested epic.
- [x] 7.3 Add matcher tests for normalization, missing mapping, stale title, duplicate activity, release disambiguation, forbidden fuzzy matches, and one result per requested epic.

## 8. Plan-Aware Analysis

- [x] 8.1 Capture one run-level `as_of`; use `_resolve_workspace_timezone()` for comparisons and workbook timezone for source decoding, emitting an informational mismatch diagnostic when they differ.
- [x] 8.2 Implement deterministic signals for development not started on plan, development-window overrun, and exact-day release target passed; suppress rules lacking evidence or precision.
- [x] 8.3 Add readiness context for target release, UAT, Beta, explicit/absent API deployment, Jira completion, and blocker evidence without claiming planned gates completed.
- [x] 8.4 Add boundary, completion, month/unspecified target, blockers, absent API, timezone mismatch, and degraded-state tests.

## 9. Generation Pipeline Integration

- [x] 9.1 Integrate one optional snapshot/parse/match/analyze pass into `generate` after resolved configuration/Jira collection and before report construction/rendering, without extra Jira queries or a second run.
- [x] 9.2 Keep `scheduled-run` as the existing thin dispatcher so manual and scheduled paths share URL resolution, `as_of`, extraction, analysis, and rendering.
- [x] 9.3 Extend `Report`/JSON with additive optional `plan_analyses` keyed by epic; omit the field when enrichment is disabled and preserve all legacy field meanings.
- [x] 9.4 Add orchestration/CLI tests for disabled, matched, source unavailable, parse invalid, per-epic partial failure, JSON, and manual/scheduled parity.

## 10. Delivery Plan Analysis Output

- [x] 10.1 Add the managed tab with the specified stable columns: Jira Key, Jira Link, Summary, Jira Status, Jira Progress, Plan State, Development Window, Development Sprint Overlaps, Target Version, Target Date, Target Precision, API Deployment, UAT, Beta, Readiness, Alignment Signals, Diagnostics, Source As Of, Source Timezone.
- [x] 10.2 Render sprint overlaps in chronological line-separated entries; render month precision without days and absent API exactly as `Not specified in Epic Plan`.
- [x] 10.3 Keep every requested epic visible with Jira actuals and explicit non-matched state rather than blanks or guesses.
- [x] 10.4 Add row/format, multi-sprint, source-preservation, unknown-tab preservation, and generated-output readback tests.

## 11. Observability And Documentation

- [x] 11.1 Emit exactly one `INFO` `epic_plan_run_summary` event per enabled run through `epic_report.plan`, including identifiers, counts for all states/severities, and read/parse/match/analyze/output/total durations.
- [x] 11.2 Update `jira-epic-report/README.md` and `docs/CONFIGURATION.md` for config, mapping, precision, API-row-only semantics, fallback, timezone ownership, and tab ownership.
- [x] 11.3 Update relevant epic-report/scheduler and `tdt-sheets` skill guidance for plan-aware scheduled output, public grid snapshots, and the read-only source contract without changing cadence.
- [x] 11.4 Add sanitized config for `RMD-4160 -> DLC Visibility`; keep real `~/.tdt` config uncommitted.

## 12. Quality And Spec Verification

- [x] 12.1 Run targeted tests throughout, then full `tdt-sheets` and `jira-epic-report` pytest suites with coverage for new snapshot/parser/analyzer branches.
- [x] 12.2 Run `ruff check . --fix`, `ruff format .`, and strict mypy in both affected Python repos; fix only introduced diagnostics.
- [x] 12.3 Run `openspec validate epic-plan-aware-analysis --strict` and `openspec validate --all --strict`; resolve conflicts with official `scheduled-epic-report`, `tdt-sheets-library`, or active epic-report changes.
- [x] 12.4 Run GitNexus `detect_changes` in each affected repo and confirm only expected client, config, parser, analyzer, report, and reporter flows changed.
- [x] 12.5 Run required Python/code review agents plus security and silent-failure review where relevant; address confirmed findings.

## 13. Live Verification And Deployment

- [x] 13.1 Snapshot workbook tab metadata/checksums needed for preservation proof, then perform read-only extraction for `RMD-4160 -> DLC Visibility` and compare every required field with the fixture.
- [x] 13.2 Add `[epic_plan]` mapping to the operator's `~/.tdt/epic-report-config.toml` only after tests pass; verify it remains outside version control.
- [x] 13.3 Rebuild scheduler with `docker compose up --build -d scheduler`; run dependency-integrity and health checks without the destructive compose smoke script.
- [x] 13.4 Trigger one real `epic-report scheduled-run`, inspect inherited logs, and read back `Delivery Plan Analysis` while proving `Epic Plan` and unknown tabs are unchanged.
- [x] 13.5 Observe the next natural `daily-epic-report` tick and confirm DBOS success plus plan-aware output/log freshness.
- [x] 13.6 Verify rollback with a temporary disabled config, confirm Jira-only generation and source preservation, then restore approved operator configuration.

## 14. Review Remediation And Follow-Up

- [x] 14.1 Use Python 3 exception tuples in the new plan reader and touched SDK error translator; regression coverage covers ValueError, TypeError, and KeyError translation, including invalid `Retry-After` handling.
- [x] 14.2 Preserve one Delivery Plan Analysis row per requested Jira epic, including an explicit `NO_ANALYSIS` placeholder when an analysis result is unexpectedly absent.
- [x] 14.3 Propagate managed spreadsheet synchronization, clear, and write failures so stale or partial output cannot be reported as a successful refresh; focused failure-path tests cover each operation.
- [x] 14.4 Keep plan telemetry exactly once and document that output duration measures the complete Phase 4 generation/write wall time for every format.
- [x] 14.5 Update operator guidance for degraded source/output behavior and the shared service-account read/write requirement without exposing credentials or changing schedule cadence.
- [x] 14.6 Record pre-existing multi-exception clauses in `agent.py`, `sprint.py`, `sprint_reporter.py`, and `utils.py` as baseline debt for a separate cleanup change; the affected repositories currently target Python 3.14 and the clauses are outside this feature's touched paths.
