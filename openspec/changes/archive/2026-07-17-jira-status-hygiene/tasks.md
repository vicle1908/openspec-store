## Status Summary (as of 2026-06-17 live audit)

| Phase | Tasks | Status |
|-------|-------|--------|
| 1 — Taxonomy | 1.1–1.4 | ✅ COMPLETE (v0 + v1 expansion) |
| 2 — Workflow Client | 2.1–2.5 | ✅ COMPLETE |
| 3 — Sheet Bootstrap | 3.1–3.6 | ✅ CODE COMPLETE (sheet must be created) |
| 4 — CLI Module | 4.1–4.9 | ✅ COMPLETE |
| 5 — Dedupe Engine | 5.1–5.6 | ✅ COMPLETE (bug-fixes from live testing applied) |
| 6 — Sheet Live Bootstrap | 6.1–6.3 | ⏳ BLOCKED (sheet not created) |
| 7 — Dedupe Dry-Run | 7.1–7.3 | ⏳ BLOCKED (sheet not created) |
| 8 — Phase A Dedupe | 8.1–8.6 | ⏳ BLOCKED (requires 7) |
| 9 — Phase B Singleton | 9.1–9.5 | ⏳ BLOCKED (requires 6) |
| 10 — Phase C Manifest | 10.1–10.4 | ⏳ BLOCKED (sheet not created) |
| 11 — Phase D Merges | 11.1–11.5 | ⏳ BLOCKED (requires 10) |
| 12 — DBOS Workflow | 12.1–12.4 | ✅ CODE COMPLETE (deploy + confirm 7 runs needed) |
| 13 — Final Verify | 13.1–13.3 | ⏳ BLOCKED (requires all above) |

## Live Audit Findings (2026-06-17)

- **211 projects** audited: 78 standard, 133 need attention
- **750 status records** (not 749 as estimated in proposal)
- **228 clusters** found: 47 with size > 1, 181 singletons
- **Taxonomy coverage**: 8.6% before v1 expansion, **25.1%** after v1 expansion (91 of 362 distinct names)
- **Top unmatched** (after v1): `In Review` (18x), `UAT` (15x), `KIV` (11x), `Backlog` (10x), `On Hold` (9x) — these are project-private or v2 expansion candidates

## Known Issues Fixed During Verification

1. **Bug fix**: `dedupe` was passing `canonical.name` (a status name like `"To Do"`) as `project_key` to `bulk_transition_for_dedupe`. Jira JQL would have been `project = "To Do" AND status = ...` — guaranteed empty. Fixed: added `TeamManagedWorkflowHandler.find_issues_in_status_grouped_by_project(status_id)` that discovers project scope instance-wide via JQL pagination, then calls per-project transitions. Spec updated: `jira-status-dedupe` reflects fan-out-by-project model.

2. **Bug fix**: `signoff` was only writing to `signoff_log` but not updating `project_manifest`. The `merge` gate reads from `project_manifest` — without the update, the gate could never open. Fixed: added `StatusRegistry.update_project_manifest_row()` and rewired `signoff` to update manifest columns. Spec updated: `jira-status-cli` signoff spec reflects dual-write behavior.

3. **Spec drift**: `jira-workflow-client-extensions` spec said `GET /rest/api/3/project/{key}/workflow` and `DELETE /rest/api/3/project/{key}/workflow/statuses/{id}`; live code uses `GET /rest/api/3/project/{key}/statuses` and `DELETE /rest/api/3/statuses/{id}`. Spec updated to match live implementation.

4. **Dedupe spec**: Spec described per-project dedupe scoping; live data showed a cluster contains N distinct `jira_id` values each in different projects. Spec updated with project-fan-out model: `find_issues_in_status_grouped_by_project` → per-project `bulk_transition`.

## Blocker: Google Sheet Creation

Tasks 6–11 require `JIRA_STATUS_REGISTRY_SHEET_ID` to be set in `~/.tdt/.env`. The sheet must be created and shared with the `tdt-sheets` service account. See `openspec/changes/jira-status-hygiene/specs/jira-status-registry-sheet/spec.md` for the 6-tab schema.

## Taxonomy Expansion (v1)

Tasks 1.1–1.4 for taxonomy are done for v0. A new change `expand-status-taxonomy-v1` covers the v1 expansion (14 next-gen + 6 company-managed entries) which improves coverage from 8.6% to 25.1%. The YAML is updated (`tdt-meta/canonical_statuses.yaml`) but the OpenSpec PR has not been merged yet.

## 1. C1 — Taxonomy (tdt-meta)

- [x] 1.1 Create `tdt-meta/canonical_statuses.yaml` with the full taxonomy: 14 `next_gen` entries and 8 `company_managed` entries (v0). ✅ DONE
- [x] 1.2 Add `jira-skill/src/jira_skill/status/taxonomy.py` with `load_taxonomy`, `match_name`, `match_canonical_key`. ✅ DONE
- [x] 1.3 Add `tests/status/test_taxonomy.py` with ≥12 tests. ✅ DONE (57 tests as of v1)
- [x] 1.4 Verify: `uv run pytest tests/status/test_taxonomy.py -v` passes. ✅ DONE

## 2. C4 — Workflow Client Extensions (tdt-core)

- [x] 2.1 Create `tdt-core/src/tdt_core/clients/jira_workflow.py`. ✅ DONE
- [x] 2.2 Add `TeamManagedWorkflowHandler` with `get_statuses`, `bulk_transition`, `bulk_transition_for_dedupe`. ✅ DONE
- [x] 2.3 Add `CompanyManagedWorkflowHandler` with `create_workflow`, `bulk_transition`, `assign_workflow_scheme`. ✅ DONE
- [x] 2.4 Add `tests/test_jira_workflow.py` with ≥15 tests. ✅ DONE (26 tests)
- [x] 2.5 Verify: `uv run pytest tests/test_jira_workflow.py -v` passes. ✅ DONE

## 3. C2 — Sheet Bootstrap (jira-skill)

- [x] 3.1 Create `status_registry` Google Sheet with 6 tabs. ⚠️ Sheet creation is manual (Google Drive API required). Code complete.
- [x] 3.2 Add `jira-skill/src/jira_skill/status/registry.py` with `StatusRegistry`. ✅ DONE
- [x] 3.3 Implement `CatalogRow`, append-only enforcement. ✅ DONE
- [x] 3.4 Add `jira-skill/src/jira_skill/status/cluster.py` with `analyze_clusters`. ✅ DONE
- [x] 3.5 Add tests for registry and cluster. ✅ DONE
- [x] 3.6 Verify: `uv run pytest tests/status/test_registry.py tests/status/test_cluster.py -v` passes. ✅ DONE

## 4. C3 — CLI Module (jira-skill)

- [x] 4.1 Create `status/__init__.py` and register in CLI. ✅ DONE
- [x] 4.2 Add `audit.py` with DBOS registration. ✅ DONE
- [x] 4.3 Add `diff.py`. ✅ DONE
- [x] 4.4 Add `preflight.py`. ✅ DONE
- [x] 4.5 Add `signoff.py` (bug-fixed: updates manifest, not just log). ✅ DONE
- [x] 4.6 Add `merge.py`. ✅ DONE
- [x] 4.7 Add `render_sheet.py`. ✅ DONE
- [x] 4.8 Add tests for commands. ✅ DONE
- [x] 4.9 Verify: `uv run pytest tests/status/test_commands/ -v` passes. ✅ DONE

## 5. C5 — Dedupe Engine (jira-skill)

- [x] 5.1 Add `dedupe.py` with `--dry-run`, `--global-confirm`, `--cluster`. ✅ DONE
- [x] 5.2 Implement dedupe logic (bug-fixed: project-fan-out via `find_issues_in_status_grouped_by_project`). ✅ DONE
- [x] 5.3 Add `classify_singletons.py`. ✅ DONE
- [x] 5.4 Implement idempotency. ✅ DONE
- [x] 5.5 Add tests. ✅ DONE
- [x] 5.6 Verify: `uv run pytest tests/status/test_dedupe.py -v` passes. ✅ DONE

## 6. Integration: Sheet Live Bootstrap

- [ ] 6.1 Run `uv run jira-skill status render-sheet --full` to populate `status_catalog` with all 750 live records.
  **Blocker**: `JIRA_STATUS_REGISTRY_SHEET_ID` not set in `~/.tdt/.env`. Sheet must be created first.
- [ ] 6.2 Review the populated Sheet. Identify records needing human `decision_note` review.
- [ ] 6.3 Run `uv run jira-skill status audit --output tabular` and save output for verification artifact.

## 7. Integration: Dedupe Dry-Run

- [ ] 7.1 Run `uv run jira-skill status dedupe --dry-run` against production. Capture output.
- [ ] 7.2 Verify output shows all 47 duplicate clusters with correct `target_jira_id`, `cluster_size`, and loser IDs.
- [ ] 7.3 Investigate any unexpected data before proceeding.

## 8. Integration: Phase A — Dedupe Execution

- [ ] 8.1 Confirm all sign-off requirements met: review `status_catalog` Sheet for pending human decisions.
- [ ] 8.2 Ensure at least one `instance_admin` sign-off exists in `project_manifest` (global gate).
- [ ] 8.3 Run `uv run jira-skill status dedupe --global-confirm` against production.
- [ ] 8.4 Verify `dedupe_log` has 47 rows (one per cluster).
- [ ] 8.5 Verify `status_catalog` `cluster_size` is now 1 for all clusters.
- [ ] 8.6 Verify `merge_log` has rows for every project-transition pair.
- [ ] 8.7 Run `uv run jira-skill status audit --output tabular` to confirm post-dedupe baseline.

## 9. Integration: Phase B — Singleton Classification

- [ ] 9.1 Run `uv run jira-skill status classify-singletons` against production.
- [ ] 9.2 Review proposed `bucket` classifications in Sheet. Correct mis-classifications.
- [ ] 9.3 Run `uv run jira-skill status classify-singletons --confirm` to apply.
- [ ] 9.4 Verify catalog row count: should be ≤ 100 records after v1 taxonomy expansion (was ≤ 50 in v0 proposal, accounting for v1 additions it may be ~100).
- [ ] 9.5 Verify `dedupe_log` has rows for each alias resolution and garbage cleanup.

## 10. Integration: Phase C — Manifest Sweep

- [ ] 10.1 Run `uv run jira-skill status render-sheet --full` to regenerate `project_manifest`.
- [ ] 10.2 Review `project_manifest`: identify projects with `divergence_count > 0`.
- [ ] 10.3 Sign off for first batch: run `signoff --project <KEY> --role instance_admin` and `--project_admin` for each.
- [ ] 10.4 Verify `signoff_log` has rows for all sign-off events.

## 11. Integration: Phase D — Project-Level Merges

- [ ] 11.1 Run `uv run jira-skill status standardize --projects PDS,PWM,RMD,SR,TJ --dry-run`. Review output.
- [ ] 11.2 Run `uv run jira-skill status standardize --projects PDS,PWM,RMD,SR,TJ --yes-i-understand-this-is-irreversible`.
- [ ] 11.3 Verify `project_manifest.merge_status=completed` for all 5 projects.
- [ ] 11.4 Run `uv run jira-skill status audit --output tabular` — all 5 should show `divergence_count=0`.
- [ ] 11.5 Repeat for 8 CFD-family + DA + STABI projects.

## 12. Daily Audit: DBOS Workflow Registration

- [x] 12.1 Add `jira-status-audit` to `jira-skill/src/jira_skill/schedule.py` (daily 07:00 UTC). ✅ CODE DONE
- [ ] 12.2 Deploy `jira-skill` and confirm DBOS scheduler picks up the new workflow.
- [ ] 12.3 Run manually: `uv run jira-skill status audit`. Confirm it writes to `audit_log`.
- [ ] 12.4 Confirm 7 consecutive daily runs with no false-positive alerts.

## 13. Final Verification

- [ ] 13.1 Run `openspec verify jira-status-hygiene` and confirm CRITICAL count is 0.
- [ ] 13.2 Confirm acceptance criteria:
  - Catalog row count ≤ 100 (v1 revised target; v0 was ≤ 50)
  - `cluster_size == 1` for all rows
  - PDS/PWM/RMD/SR/TJ `divergence_count=0` in `project_manifest`
  - All 200+ projects have `merge_status ∈ {completed, skipped}`
  - 7 daily audit runs, no false positives
  - `signoff_log`, `merge_log`, `dedupe_log` non-empty
  - Zero rows with wrong category
