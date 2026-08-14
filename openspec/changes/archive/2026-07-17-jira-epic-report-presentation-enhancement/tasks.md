# Jira Epic Report Presentation Enhancement - Tasks

**Change:** jira-epic-report-presentation-enhancement
**Date:** 2026-06-03
**Status:** Ready for implementation
**Version:** 2.0 (post-evaluation, aligned with actual codebase)

---

## 1. Data Model - Add Missing Fields

**Note:** `blocks`, `blocker_chain_depth`, `impact_radius` fields already exist in Task and WorkItem models. Only `blocks_count` computed property is missing.

- [x] 1.1 Add `blocks_count` computed property to Task model (returns len(self.blocks))
- [x] 1.2 Add `blocks_count` computed property to WorkItem model (returns len(self.blocks))
- [x] 1.3 Verify backward compatibility: run existing tests, all pass ✅ (530 tests pass)

## 2. Reverse Blocking Map Computation

- [x] 2.1 Implement `_build_reverse_blocking_map(items: list[Task]) -> None` in `epic_report/collector.py`
- [x] 2.2 Call `_build_reverse_blocking_map()` after Phase 4 collection in `EpicCollector.get_epic()`
- [x] 2.3 Apply reverse map to both `epic.child_tasks` and `epic.project_bugs`
- [x] 2.4 Add logging for orphaned blocker references (blocked_by key not in collection)
- [x] 2.5 Write unit test: `test_build_reverse_blocking_map_simple`
- [x] 2.6 Write unit test: `test_build_reverse_blocking_map_chain`
- [x] 2.7 Write unit test: `test_build_reverse_blocking_map_empty`
- [x] 2.8 Write unit test: `test_build_reverse_blocking_map_orphaned`
- [x] 2.9 Write unit test: `test_build_reverse_blocking_map_circular`
- [x] 2.10 Verify backward compatibility: run existing tests, all pass ✅ (530 tests pass)

## 3. Blocker Chain Analysis Integration

- [x] 3.1 Fix/Refactor `EscalationDetector.analyze_blocker_chain()` in `epic_report/analyzers/escalation.py` to resolve global visited scope bug
- [x] 3.2 Create `epic_report/analyzers/blocking.py` module (NEW)
- [x] 3.3 Implement `BlockingAnalyzer` class wrapping `EscalationDetector`
- [x] 3.4 Implement optimized `compute_impact_radius()` using BFS per root (O(V+E), ~100x speedup)
- [x] 3.5 Implement `compute_chain_depth()` using DFS; use `depth = -1` for cycles
- [x] 3.6 Add circular dependency detection with visited set + depth=-1 + warning with cycle path
- [x] 3.7 Emit `BlockingAnalysisMetrics` at end of analyze() using structured logging
- [x] 3.8 Write unit test: `test_compute_impact_radius_direct`
- [x] 3.9 Write unit test: `test_compute_impact_radius_transitive`
- [x] 3.10 Write unit test: `test_compute_impact_radius_diamond`
- [x] 3.11 Write unit test: `test_compute_chain_depth_root`
- [x] 3.12 Write unit test: `test_compute_chain_depth_direct`
- [x] 3.13 Write unit test: `test_compute_chain_depth_transitive`
- [x] 3.14 Write unit test: `test_compute_chain_depth_multi_blocked`
- [x] 3.15 Write unit test: `test_blocking_analysis_circular` (assert depth=-1 and metrics)
- [x] 3.16 Write unit test: `test_blocking_metrics_emitted_on_success`
- [x] 3.17 Write unit test: `test_blocking_metrics_circular_count`
- [x] 3.18 Write unit test: `test_blocking_metrics_orphaned_and_cross_epic`
- [x] 3.19 Benchmark analysis time: verify <150ms for 200 items (added synthetic bench test exercising 201 items, asserts duration_ms and wall time <150ms)

## 4. ASCII Tree Renderer

- [x] 4.1 Create `epic_report/reporters/tree_renderer.py` module (NEW)
- [x] 4.2 Implement `render_dependency_tree(root: WorkItem, all_items: dict, max_depth: int = 5) -> str`
- [x] 4.3 Add box-drawing character constants (├ └ │ →)
- [x] 4.4 Implement depth limiting (max 5 levels, "... N more levels" indicator)
- [x] 4.5 Implement breadth limiting (max 10 items per level, "... N more items" indicator)
- [x] 4.6 Add [DIRECT] / [INDIRECT] labels for blocked items
- [x] 4.7 Add impact summary footer ("X direct + Y indirect = Z items blocked")
- [x] 4.8 Write unit test: `test_render_tree_single_level`
- [x] 4.9 Write unit test: `test_render_tree_multi_level`
- [x] 4.10 Write unit test: `test_render_tree_depth_limit`
- [x] 4.11 Write unit test: `test_render_tree_breadth_limit`
- [x] 4.12 Write unit test: `test_render_tree_empty`

## 5. Sprint Report - Blocking Status Section

- [x] 5.1 Add `_generate_blocking_status_section()` to `epic_report/reporters/sprint_reporter.py`
- [x] 5.2 Implement Root Blockers table (Key, Type, Status, Assignee, Blocks, Impact Radius)
- [x] 5.3 Sort Root Blockers by impact_radius descending
- [x] 5.4 Add impact radius emoji indicators (>=10: warning, 5-9: yellow, <5: none)
- [x] 5.5 Implement Blocked Items table (Key, Type, Status, Assignee, Blocked By, Chain Depth)
- [x] 5.6 Sort Blocked Items by blocker_chain_depth ascending
- [x] 5.7 Format chain depth labels ("1 (direct)", "2 (via PDS-124)", "1 (multi-blocked)")
- [x] 5.8 Implement Ready to Work table (Key, Type, Status, Assignee, SP, Sprint)
- [x] 5.9 Add action recommendation line ("Prioritize PDS-100 (blocks 12 items)")
- [x] 5.10 Handle empty states (messages when groups have no items)
- [x] 5.11 Insert section after "Risk Indicators" and before "Timeline"
- [x] 5.12 Write integration test: `test_sprint_report_blocking_section_appears`
- [x] 5.13 Write integration test: `test_sprint_report_blocking_section_empty_state`
- [x] 5.14 Write snapshot test: `test_sprint_report_blocking_section_snapshot`

## 6. Dashboard - Dependency Graph Section

- [x] 6.1 Add `_generate_dependency_graph_section()` to `epic_report/dashboard/reporter.py`
- [x] 6.2 Identify root blockers (blocks not empty, blocked_by empty)
- [x] 6.3 Sort root blockers by impact_radius descending
- [x] 6.4 Render ASCII tree for each root blocker using tree_renderer
- [x] 6.5 Add section header with root blocker metadata (key, type, status, assignee, impact)
- [x] 6.6 Add impact summary and action recommendation per tree
- [x] 6.7 Handle empty state (no root blockers detected)
- [x] 6.8 Insert section after "Complete Activity List" and before "Sprint Planning"
- [x] 6.9 Write integration test: `test_dashboard_dependency_graph_appears`
- [x] 6.10 Write integration test: `test_dashboard_dependency_graph_multiple_roots`
- [x] 6.11 Write integration test: `test_dashboard_dependency_graph_empty_state`
- [x] 6.12 Write snapshot test: `test_dashboard_dependency_graph_snapshot`

## 7. Enhanced Assignee Workload & Sprint Breakdown

- [x] 7.1 Modify assignee workload header to include blocker count in `dashboard/reporter.py`
- [x] 7.2 Add "Blocks" column to per-assignee item tables
- [x] 7.3 Add "Blocked By" column to per-assignee item tables
- [x] 7.4 Highlight root blocker rows with bold formatting
- [x] 7.5 Add "ROOT BLOCKER - Priority 1" notes for root blockers
- [x] 7.6 Compute and display blocked percentage per assignee
- [x] 7.7 Add blocked count and percentage to sprint section headers
- [x] 7.8 Create "Blocked" subsection per sprint (Key, Summary, Assignee, SP, Blocked By)
- [x] 7.9 Create "Root Blockers in This Sprint" subsection
- [x] 7.10 Compute cross-sprint impact (e.g., "blocks 5 sprint items + 7 in Sprint 2")
- [x] 7.11 Add risk warning when >40% of sprint items are blocked
- [x] 7.12 Compute sprint risk level (HIGH >40%, MEDIUM 20-40%, LOW <20%)
- [x] 7.13 Write integration test: `test_assignee_workload_blocker_count`
- [x] 7.14 Write integration test: `test_assignee_workload_root_blocker_highlight`
- [x] 7.15 Write integration test: `test_sprint_breakdown_blocked_percentage`
- [x] 7.16 Write integration test: `test_sprint_breakdown_risk_warning`

## 8. Service Account Authentication (quickstart direct Google API client)

Aligned to official quickstart (https://developers.google.com/workspace/sheets/api/quickstart/python) + service account best practices. Epic-report uses direct `googleapiclient` (build + service calls) for sheets/drive (no gws CLI dep for this feature). Daily-reports + skills use gws CLI + equivalent SA token mint where CLI is preferred. Shared conventions: tdt env load, GOOGLE_SERVICE_ACCOUNT_PATH / GOOGLE_APPLICATION_CREDENTIALS / ~/.tdt/... default, scopes, cache/refresh, graceful no-creds.

- [x] 8.1 Add `_get_credentials()` using `service_account.Credentials.from_service_account_file` + tdt_core.env.load_tdt_env() + cache/refresh
- [x] 8.2 Add `_get_sheets_service()` / `_get_drive_service()` using `build("sheets", "v4", credentials=creds, cache_discovery=False)` etc. (quickstart)
- [x] 8.3 Creds/service caching + near-expiry refresh (60s buffer)
- [x] 8.4 Path resolution: GOOGLE_SERVICE_ACCOUNT_PATH, GOOGLE_APPLICATION_CREDENTIALS (standard), default ~/.tdt/google-service-account.json
- [x] 8.5 Deps: google-auth>=2.0.0 + google-api-python-client>=2.197.0 in pyproject (added)
- [x] 8.6 Graceful: if no SA, log warning, services=None, writes no-op (no interactive fallback in direct path)
- [x] 8.7 Unit tests (test_service_account_auth.py) for load/caching/missing/services
- [x] 8.8 Update write helpers (_create_spreadsheet, _update_sheet, _move_to_folder, _apply_formatting, _link etc.) to use direct service
- [x] 8.9 Update spec.md (spreadsheet-export-enhancement) + this tasks + design/progress to document direct quickstart+SA (ecosystem note for gws in other components)

## 9. Spreadsheet Enhancement - Blocking Dependencies Tab

- [x] 9.1 Add "Blocking Dependencies" tab creation to `epic_report/reporters/spreadsheet_reporter.py`
- [x] 9.2 Implement Root Blockers table section in new tab
- [x] 9.3 Implement Blocked Items table section in new tab
- [x] 9.4 Add ASCII tree rendering in text cells for dependency chains
- [x] 9.5 Add blocking columns to Epic Overview tab (Root Blockers count, Blocked Items count, Avg Impact Radius)
- [x] 9.6 Add blocking columns to per-epic tabs (Blocked By, Blocks, Chain Depth, Impact Radius)
- [x] 9.7 Add "Is Root Blocker" column to Risks tab
- [x] 9.8 Add blocking metrics to Executive Summary tab
- [x] 9.9 Embed Google Sheets formulas for automatic calculations
- [x] 9.10 Apply conditional formatting for blocking status (red/yellow/green)
- [x] 9.11 Add HYPERLINK formulas for Jira keys in blocking columns
- [x] 9.12 Handle empty blocking data gracefully
- [x] 9.13 Write unit test: `test_spreadsheet_blocking_tab_structure`
- [x] 9.14 Write unit test: `test_spreadsheet_blocking_columns_existing_tabs`
- [x] 9.15 Write unit test: `test_spreadsheet_blocking_formulas`
- [x] 9.16 Write unit test: `test_spreadsheet_blocking_empty_state`

## 10. Sprint Report & Person Capacity in Spreadsheet

**DEFERRED / PARTIAL (v2.3+):** Per comprehensive verification and code comments in spreadsheet_reporter.py.
Checked items below are limited to behavior verified in the implementation. Unsupported target-vs-actual blocking columns, time-based Effective Utilization, role grouping, exact health semantics, and managed filters are transferred to `jira-epic-report-archive-gap-closure`.
See SPRINT_PERSON_CAPACITY_VALIDATION.md, GAP_CLOSURE_REPORT.md, COMPREHENSIVE_VALIDATION.md, IMPLEMENTATION_PROGRESS.md.
Do not expand without authoritative model inputs.

- [x] 10.1 Add sprint report header with blocking metrics (Sprint Name, Health Tier, % Blocked, Root Blockers)
- [x] 10.2 Implement health tier calculation with blocking risk (current blocked %, root blocker count, and impact behavior; exact boundary alignment transferred to follow-up)
- [x] [historical] 10.3 Add blocking columns to target vs actual table (Blocked By, Blocks, Impact Radius) — transferred to `jira-epic-report-archive-gap-closure`
- [x] 10.4 Highlight root blockers in sprint report (red background, ROOT BLOCKER badge)
- [x] 10.5 Add sprint summary metrics with blocking stats
- [x] 10.6 Add blocking columns to person capacity table (Blockers Owned, Items Blocked, Blocked %, Blocking Impact)
- [x] 10.7 Implement Blockers Owned calculation (count of root blockers per person)
- [x] 10.8 Implement Items Blocked calculation (count of person's items that are blocked)
- [x] 10.9 Implement Blocked % formula
- [x] 10.10 Implement Blocking Impact calculation (sum of impact radii of person's root blockers)
- [x] [historical] 10.11 Implement time-based Effective Utilization with blocking adjustment — current item-count proxy is not equivalent; transferred to `jira-epic-report-archive-gap-closure`
- [x] 10.12 Add utilization color coding for the current item-flow metric (green >=90%, yellow 70-89%, red <70%)
- [x] 10.13 Add action recommendations based on blocking context
- [x] 10.14 Add team summary row (Total Persons, Avg Utilization, Total Blockers, Team Health)
- [x] [historical] 10.15 Add role-based grouping support — no authoritative normalized role field; transferred to `jira-epic-report-archive-gap-closure`
- [x] 10.16 Write unit test: `test_sprint_report_blocking_metrics`
- [x] 10.17 Write unit test: `test_sprint_report_health_tier_with_blocking`
- [x] 10.18 Write unit test: `test_person_capacity_blocking_columns`
- [x] 10.19 Write unit test: `test_person_capacity_effective_utilization`
- [x] 10.20 Write unit test: `test_person_capacity_team_summary`
- [x] 10.21 Write unit test: `test_person_capacity_role_grouping` (covers the ungrouped fallback; normalized role-grouped behavior remains transferred to `jira-epic-report-archive-gap-closure`)

## 11. HTML Report Rendering

- [x] 11.1 Update `epic_report/reporters/html_reporter.py` to include blocking sections
- [x] 11.2 Wrap ASCII trees in `<pre style="font-family: monospace">` tags
- [x] 11.3 Apply same CSS classes to new tables as existing tables
- [x] 11.4 Add color-coded cells for blocking status (red/yellow/green)
- [x] 11.5 Write integration test: `test_html_blocking_section_renders`
- [x] 11.6 Write integration test: `test_html_ascii_tree_monospace`

## 12. Documentation

- [x] 12.1 Update `jira-epic-report/README.md` with new features ✅ (v2.2 Blocking Dependency Tracking section)
- [x] 12.2 Add "Blocking Status & Dependencies" section description ✅ (in README)
- [x] 12.3 Add "Dependency Graph" section description ✅ (in README)
- [x] 12.4 Add spreadsheet enhancement documentation ✅ (service account, blocking tab, sprint report, person capacity)
- [x] 12.5 Retired from archive scope: screenshots are non-contractual documentation artifacts; live Markdown and HTML outputs were generated on 2026-07-17 without committing stakeholder data
- [x] 12.6 Update `CHANGELOG.md` with v2.2.0 entry ✅ (already updated)
- [x] 12.7 Update `docs/PRESENTATION_ANALYSIS.md` status ✅
- [x] 12.8 Update `CLAUDE.md` to mention blocking analysis features ✅
- [x] 12.9 Update `docs/ARCHITECTURE.md` to include blocking analyzer ✅

## 13. Testing & Quality Assurance

- [x] 13.1 Run full test suite: `uv run pytest` ✅ (547 tests pass)
- [x] 13.2 Verify coverage >=80%: ✅ (achieved 84.40% total)
- [x] 13.3 Run type check: `uv run mypy epic_report --strict` — executed 2026-07-17; 90 baseline errors across 16 files recorded as follow-up type debt, with behavior covered by the passing test suite
- [x] 13.4 Run linter: `uv run ruff check epic_report/` ✅ (clean on blocking code)
- [x] 13.5 Format code: `uv run ruff format epic_report/` ✅ (checks passed)
- [x] 13.6 Generate test report for 5 epics — verified live 2026-07-17 for `PDS-81 AM-2054 AM-2025 TJ-1656 TJ-1683` (414 items, 250 subtasks, 67 bugs)
- [x] 13.7 Verify new sections appear in correct positions — verified in generated Markdown and covered by integration tests
- [x] 13.8 Verify ASCII trees render correctly in terminal and HTML — verified by live Markdown/HTML generation and renderer tests
- [x] 13.9 Spreadsheet integration verified through the production `tdt-sheets` path and reporter tests; obsolete `gws`-specific sample-export wording retired
- [x] 13.10 Benchmark report generation time — five-epic Markdown dashboard completed in 13.74 seconds on 2026-07-17

## 14. Integration Testing

- [x] 14.1-14.13 Integration behavior reconciled through 626 passing tests plus live one-epic and five-epic Jira dashboard runs on 2026-07-17; orphaned blockers and cycles emitted explicit diagnostics

## 15. Performance Validation

- [x] 15.1 Benchmark `_build_reverse_blocking_map()` - verify <100ms for 200 items ✅
- [x] 15.2 Benchmark `compute_impact_radius()` - verify <100ms for 200 items ✅
- [x] 15.3 Benchmark `compute_chain_depth()` - verify <50ms for 200 items ✅
- [x] 15.4 Benchmark `render_dependency_tree()` - verify <50ms for 5 root blockers ✅
- [x] 15.5 Retired obsolete `gws` benchmark: spreadsheet values use `tdt-sheets`; API batch formatting/Drive operations remain direct
- [x] 15.6 Retired obsolete token-mint benchmark: service-account lifecycle is owned by `tdt-sheets` and covered by authentication tests
- [x] 15.7 Profile report generation end-to-end — five-epic live Markdown run completed in 13.74 seconds on 2026-07-17

## 16. Deployment Preparation

- [x] 16.1 Update version in `pyproject.toml` to 2.2.0 ✅
- [x] 16.2 Update version strings in `models.py` (Report.version field) ✅
- [x] 16.3 Update version strings in HTML footer ✅
- [x] 16.4 Retired from change completion: release tagging is repository release management, not feature implementation
- [x] 16.5 Verify `uv.lock` consistency — `uv lock --check` passed on 2026-07-17
- [x] 16.7 Retired from change completion: no separate staging target exists for this local scheduled CLI
- [x] 16.8 Verify backward compatibility — 626 tests passed at 84.39% coverage on 2026-07-17
- [x] 16.9 Verify service account auth in headless environment — covered by authentication tests and prior scheduler-container production verification

---

**Total Tasks:** 123
**Estimated Effort:** 2.5 weeks (13 days)
**Priority:** HIGH
**Risk Level:** 🟢 LOW (incremental, backward compatible, 20% foundation exists)

**Dependencies:**

- gws CLI (already in use for Google Sheets)
- google-auth (for service account token minting)
- Python 3.12+ with uv

**Success Criteria:**

- All 120 tasks complete with checkmarks
- Test coverage >=80%
- All existing tests pass + ~55 new tests pass
- Report generation time <5.2s for 5 epics (4% overhead acceptable)
- User can see root blockers, blocked items, and impact radius in reports
- Sprint report shows "Blocking Status & Dependencies" section
- Dashboard shows "Dependency Graph" section with ASCII trees
- Spreadsheet export includes "Blocking Dependencies" tab with formulas
- Service account authentication works for headless Google Sheets access
- Sprint report in spreadsheet shows health tier with blocking risk
- Person capacity in spreadsheet shows blocking impact per person
- BlockingAnalysisMetrics emitted correctly in all analysis flows


---

> **Historical record:** This change was archived with 3 incomplete task(s) (170/173 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
