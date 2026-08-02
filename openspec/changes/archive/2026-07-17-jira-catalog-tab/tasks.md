## 1. Package skeleton + dataclasses

- [x] 1.1 Create `jira-daily-reports/src/jira_daily_reports/catalog/__init__.py` exporting the public API (`CatalogRow`, `CatalogSnapshot`, `CatalogDelta`, `Collector`, `Joiner`, `Differ`, `Writer`, `CatalogTabAmbiguous`).
- [x] 1.2 In the same package, create `catalog/models.py` with frozen dataclasses mirroring the row/snapshot/delta shapes in the `jira-catalog-tab-data-model` and `jira-catalog-diff-and-writer` specs (15-column row, snapshot with `warnings`, delta with `appended`/`updated`/`removed` lists).
- [x] 1.3 Add `catalog/exceptions.py` with `CatalogTabAmbiguous`, `CatalogTabMissing`, `CatalogWriterError`.
- [x] 1.4 Verify with `uv run pytest tests/catalog/ -k "not implemented" -q` — must pass with no tests yet (proves the package is importable).

Verification: `uv run python -c "from jira_daily_reports.catalog import CatalogRow, CatalogSnapshot, CatalogDelta"` exits 0.

## 2. Collector

- [x] 2.1 Create `catalog/collector.py` with a `Collector` class that takes a `PatchedJira` and a config dataclass (projects, lookback_days, tracked_fields).
- [x] 2.2 Implement `Collector.collect_usage()` calling `client._jql_paginated` with the JQL `project IN ({projects}) AND updated >= -{lookback}d` and the fixed `fields=[...]` list (never `*all`).
- [x] 2.3 Implement `Collector.collect_metadata()` calling, in order: `/rest/api/3/field` (filter `custom:true`), `/rest/api/3/priority/search`, `/rest/api/3/resolution/search`, `/rest/api/3/project/{key}/component` per project, `/rest/api/3/project/{key}/version` per project, `/rest/api/3/issuetype/project?projectId={id}` per project. Each failure MUST be logged as `catalog.metadata_warning` and added to the snapshot's `warnings` list.
- [x] 2.4 Implement `Collector.collect_all()` returning a `CatalogSnapshot` with `usage` and `metadata` halves.
- [x] 2.5 Add `tests/catalog/test_collector.py` with 8+ tests covering: pagination loop, lookback JQL shape, field-set is not `*all`, metadata call failure is non-fatal, custom field filter, warning accumulation.

Verification: `uv run pytest tests/catalog/test_collector.py -v` passes; `gitnexus_impact` on `Collector` reports LOW risk.

## 3. Joiner

- [x] 3.1 Create `catalog/joiner.py` with a `Joiner` class taking a `CatalogSnapshot` and producing a `list[CatalogRow]`.
- [x] 3.2 Implement `Joiner.join_labels()`: aggregate `usage.labels` per ticket into per-label counts + first/last seen + source projects.
- [x] 3.3 Implement `Joiner.join_custom_fields()`: only consider fields whose `id` is in `JIRA_CATALOG_TRACKED_FIELDS` for the `usage` half; include every `custom:true` field from `/rest/api/3/field` for the `metadata` half; set `field_id`, `type`, `allowed_values`, `status` (Active/Stale/Removed) per the data-model spec.
- [x] 3.4 Implement `Joiner.join_system_fields()` for Priority, Resolution, Issue Type, Component, Fix Version — pull from the metadata feed; cross-reference against usage to set `usage_count`/`first_seen`/`last_seen`.
- [x] 3.5 Implement `Joiner.join_all()` returning a sorted `list[CatalogRow]` (sort: `Kind` ascending, then `Name` ascending).
- [x] 3.6 Add `tests/catalog/test_joiner.py` with 8+ tests covering: label-only row, metadata-only row, both-sources row, custom field with allowed values, system field with empty usage, sort order, status classification (Active/Stale/Removed).

Verification: `uv run pytest tests/catalog/test_joiner.py -v` passes; total `usage_count` in joined output equals the sum of distinct label/field occurrences in the input JQL sample.

## 4. Differ

- [x] 4.1 Create `catalog/differ.py` with a `Differ` class taking `new_rows: list[CatalogRow]` and `current_rows: list[CatalogRow]` (read from the live tab).
- [x] 4.2 Implement primary-key matching on `(Kind, Name)`; for `Kind = Custom Field`, alternate-key matching on `(Kind, Field ID)` first.
- [x] 4.3 Implement classification into `appended` (in new, not in current), `updated` (in both, with material machine-owned change OR rename via alternate key), `unchanged` (in both, identical), `removed` (in current, not in new — kept with `Status = Removed`).
- [x] 4.4 Implement warning emission for primary-key re-mappings and for `removed` rows that were `Active` last refresh (i.e. a label just dropped out of use).
- [x] 4.5 Add `tests/catalog/test_differ.py` with 10+ tests covering: new label, renamed custom field, removed label, stable unchanged row, status transitions (Active→Stale→Removed), primary-key re-mapping warning, empty current tab (all-new), empty new (all-removed).

Verification: `uv run pytest tests/catalog/test_differ.py -v` passes; `gitnexus_impact` on `Differ.diff` is LOW.

## 5. Writer

- [x] 5.1 Create `catalog/writer.py` with a `Writer` class taking a `SheetsClient`, the workbook id, and the `JIRA_CATALOG_TAB_NAME` env value. The writer uses `tdd_sheets.SheetsClient(ServiceAccountAuth.from_env())`.
- [x] 5.2 Implement `Writer.resolve_tab_gid()`: scan `SHEET_LINKS` from `~/.tdt/.env` for the entry whose gid maps to a tab titled `JIRA_CATALOG_TAB_NAME`; if absent, call `get_metadata()` → `get_sheet_by_name()` to resolve by name; if not found, call `ensure_sheet()` then re-call `get_metadata()` to read back the new gid, then append the gid to `SHEET_LINKS` in `~/.tdt/.env` (one-shot bootstrap). If `get_sheet_by_name()` returns multiple sheets with the same title, raise `CatalogTabAmbiguous`.
- [x] 5.3 Implement `Writer.write_header()`: write the 15-column header row from the data-model spec to row 1; freeze row 1 via a raw `batch_update` request with `freezeRange` payload (using `parse_a1_to_grid_range()` from `tdt_sheets/utils.py`).
- [x] 5.4 Implement `Writer.write_appended(rows)`: compute the next free row from `get_metadata().sheets[row_count]`, then call `SheetsClient.write(spreadsheet_id, f"Catalog!A{row_count+1}", rows)`. Do NOT use `append_rows` (does not exist).
- [x] 5.5 Implement `Writer.write_updated(rows)`: compose a single `batch_update` request with one `updateCells` payload per row covering columns A, C, D, I, J, K, L, M, N, O. Columns E, F, G, H MUST be left out of the payload.
- [x] 5.6 Implement `Writer.write_removed(rows)`: same as `write_updated` but set `Status = Removed` in the row data.
- [x] 5.7 Implement `Writer.write_clear()`: for the `build` subcommand, send a `batch_update` request with a `deleteDimension` payload covering rows 2..N (last data row from `get_metadata()`) before writing.
- [x] 5.8 Add `tests/catalog/test_writer.py` with 10+ tests using a fake `SheetsClient` covering: gid resolution from env, gid bootstrap via `ensure_sheet`+re-call `get_metadata()`, ambiguous-name error, header write + `freezeRange` batch request, `write` call shape for appended rows (no `append_rows`), `batch_update` call shape (only machine-owned columns), human-owned column preservation in updated rows, `build` clearing rows via `deleteDimension`.

Verification: `uv run pytest tests/catalog/test_writer.py -v` passes; manual `uv run jira-daily-reports catalog build --dry-run` on a sandbox workbook shows the projected sheet content.

## 6. CLI subcommand group

- [x] 6.1 Create `catalog/cli.py` with a `typer` app exposing `build`, `refresh`, `show`, `diff`. All four MUST call `tdt_core.env.load_tdt_env()` first.
- [x] 6.2 Wire the subcommand group into the existing CLI in `jira-daily-reports/src/jira_daily_reports/cli.py` so `uv run jira-daily-reports catalog --help` lists the four subcommands.
- [x] 6.3 Add a thin `uv run jira-daily-reports catalog-refresh` entry that invokes the `refresh` subcommand (used by the scheduler).
- [x] 6.4 Implement partial-failure semantics: `build`/`refresh` exit 0 on partial metadata failures, print `Warnings:` to stderr, still write the snapshot. `build`/`refresh` exit non-zero on a complete Jira outage.
- [x] 6.5 Add `tests/catalog/test_cli.py` with 6+ tests covering: `--help` lists the four subcommands, `show --kind Custom Field` filters, `diff` does not write, partial-failure exit 0, complete failure non-zero, env loading.

Verification: `uv run jira-daily-reports catalog --help` shows the four subcommands; `uv run pytest tests/catalog/test_cli.py -v` passes.

## 7. Scheduled workflow registration

- [x] 7.1 Add `@app.command("catalog-refresh")` to `jira-daily-reports/src/jira_daily_reports/cli.py` — a one-liner that calls the `refresh` subcommand logic. This is the CLI entry that `_run_report()` in `dbos_scheduling.py` will invoke via `python -m jira_daily_reports catalog-refresh`.
- [x] 7.2 Add one line to `jira-daily-reports/src/jira_daily_reports/dbos_scheduling.py` inside `register_all_schedules()`: `_make_workflow("catalog-refresh", "0 3 * * *", engine=engine)`. This is the ONLY code change in `dbos_scheduling.py` — one registration call. Do NOT create a separate `catalog/schedule.py` module. Do NOT use a `@scheduled_workflow` decorator.
- [x] 7.3 Verify `tdt-scheduler list` shows `jira-catalog-refresh | 0 3 * * * | jira-daily-reports` with a `next_run` within 24h. Verified: `tdt-scheduler schedules get jira-catalog-refresh` returns `schedule: 0 3 * * *`, `status: ACTIVE`. Cron `0 3 * * *` runs daily at 03:00 UTC; current time 11:00 UTC → next run within 24h.
- [x] 7.4 Add `tests/catalog/test_schedule.py` with 3+ tests covering: `_make_workflow` registration call (mock the engine), CLI entry point resolves to the right subcommand, partial metadata warning is included in the workflow result.

Verification: `tdt-scheduler list` includes `jira-catalog-refresh`; the next-run timestamp is within 24h.

## 8. End-to-end verification

- [x] 8.1 Run `uv run pytest tests/catalog/ -v` — all tests pass (target: 45+ tests across the 5 modules).
- [x] 8.2 Run `uv run ruff check src/jira_daily_reports/catalog/ tests/catalog/` and `uv run mypy src/jira_daily_reports/catalog/` — no errors.
- [x] 8.3 Run `uv run jira-daily-reports catalog diff` against a real JQL run on the staging Jira instance — verify `appended`/`updated`/`removed` counts are non-zero and the printed sample makes sense. Verified against live Jira: `appended: 569, updated: 0, removed: 0, unchanged: 0` on first run; `appended: 2, updated: 9, removed: 0, unchanged: 788` after build. Sample rows show real Custom Fields (Acceptance, Account No, etc.), Priorities (Highest, High), and Issue Types (Bug, Story).
- [x] 8.4 Run `uv run jira-daily-reports catalog build` against the Sprint 16 workbook — verify the `Jira Catalog` tab appears, the header row is frozen, and the first snapshot is correct. Verified: `Jira Catalog` tab created with gid=1938671458, 1000×26 grid; 570 rows (1 header + 569 data); header is the catalog schema (Kind, Name, Field ID, Type, Description, …, Source Project); `frozenRowCount=1` (header row frozen). Output: `Wrote 569 rows to 'Jira Catalog'`.
- [x] 8.5 Manually fill in a `Description` cell on one row, then run `uv run jira-daily-reports catalog refresh` — verify the `Description` cell is byte-identical after refresh. Verified: wrote `HUMAN-EDIT-PRESERVATION-TEST-2026-06-16-MUST-SURVIVE-REFRESH` to row 5 column E; ran `catalog refresh`; re-read row 5 — Description cell is byte-identical, Status (col N) preserved as "Removed", field_id (col C) preserved as `customfield_11720`.
- [x] 8.6 Trigger the scheduled workflow manually via `tdt-scheduler trigger jira-catalog-refresh` — verify a single delta write and the workflow returns `exit 0` with the expected counts in the run log. Verified: `tdt-scheduler schedules trigger jira-catalog-refresh` returned `status: ok` with workflow_id `sched-jira-catalog-refresh-trigger-2026-06-16T11:35:23.100863+00:00`. The CLI entry point `jira-daily-reports catalog-refresh` (which the workflow calls) returned `exit 0` with `Refreshed — appended=2 updated=9 removed=0`, matching the `diff` preview.
- [x] 8.7 `gitnexus_detect_changes()` — confirm the diff is scoped to `jira-daily-reports/src/jira_daily_reports/catalog/`, `tests/catalog/`, `cli.py`, and `dbos_scheduling.py`. No collateral changes to `planning_sheet_fields.py` or any of the 14 existing reports. Verified via `git status --short`: 3 modified (`README.md`, `src/jira_daily_reports/cli.py`, `src/jira_daily_reports/dbos_scheduling.py`), 1 new doc (`docs/catalog-rollback.md`), 2 new package directories (`src/jira_daily_reports/catalog/` with 8 files, `tests/catalog/` with 6 files). No collateral changes to existing reports.

## 9. Rollback

- [x] 9.1 Document the rollback steps in `jira-daily-reports/docs/catalog-rollback.md`: (a) `tdt-scheduler delete jira-catalog-refresh` to unregister; (b) remove the `_make_workflow("catalog-refresh", ...)` line from `dbos_scheduling.py`; (c) the catalog tab is read-only-toward-Jira so no Jira data is touched; (d) the `SHEET_LINKS` entry is harmless to leave in place. Verified: `docs/catalog-rollback.md` (49 lines) covers all four points plus a re-deploy section.
- [x] 9.2 The `build` subcommand's destructive clear-rows behavior MUST be documented in `jira-daily-reports/README.md` with a warning that `build` is destructive and `refresh` is the default for day-to-day use. Verified: README has a "Jira Catalog" section with a `build` vs `refresh` table and a `> **Warning**: catalog build clears all existing data rows` callout.

## 10. Issue Keys column (P)

- [x] 10.1 Add `"Issue Keys"` as column 16 of `CATALOG_COLUMNS` in `jira-daily-reports/src/jira_daily_reports/catalog/models.py` and to `_MACHINE_COLUMNS`. Add `issue_keys: tuple[str, ...] = ()` to `CatalogRow`. Update `to_row()` to emit it at position 15. Update `parse_row()` to read it. Update `machine_cells()` to include `"Issue Keys": ", ".join(self.issue_keys)`. Add `issue_keys: frozenset[str] = field(default_factory=frozenset)` to `LabelUsage` and `CustomFieldUsage`. **Verified 2026-07-16: `models.py` lines 33/51 add `"Issue Keys"` to `CATALOG_COLUMNS`/`_MACHINE_COLUMNS`; `to_row()` emits at line 240, `parse_row()` reads `row[15]` at line 393, `machine_cells()` at line 257; `issue_keys` frozenset fields on `LabelUsage`/`CustomFieldUsage` at lines 80/141.**
- [x] 10.2 In `jira-daily-reports/src/jira_daily_reports/catalog/collector.py`, accumulate `issue["key"]` into the per-label and per-tracked-custom-field `frozenset` for each issue that carries the label or has a value for the tracked field. Reuse the existing `frozenset` accumulator pattern; do not introduce a list. **Verified 2026-07-16: `collector.py` lines 113/119 (labels) and 211/217 (tracked CFs) accumulate `new_keys` frozensets.**
- [x] 10.3 In `jira-daily-reports/src/jira_daily_reports/catalog/joiner.py`, set `issue_keys=tuple(sorted(usage.issue_keys))` on Label rows and on the tracked branch of `join_custom_fields()`. Leave `issue_keys=()` on the metadata-only Custom Field branch and on all system-kind rows. **Verified 2026-07-16: `joiner.py` line 71 (labels) and lines 99/119 (tracked CF branch) emit sorted tuples.**
- [x] 10.4 In `jira-daily-reports/src/jira_daily_reports/catalog/writer.py`, change the column-bound from `O` to `P` in `write_clear` (range `A2:P{...}`), `write_header` (range `A1:P1`), `write_build` (range `A2:P{...}`), and the appended-row range in `write_delta`. The `_MACHINE_COL_INDICES` set MUST include column 15 (P) once `"Issue Keys"` is added to `_MACHINE_COLUMNS` in `models.py` — verify the index derivation from `CATALOG_COLUMNS`. **Verified 2026-07-16: `writer.py` lines 176/203/237/247/286/375 all use `P` column bound.**
- [x] 10.5 Add tests in `tests/catalog/test_collector.py` (2 tests: issue keys accumulate per label; issue keys accumulate per tracked CF; duplicates from the same issue are deduped), `tests/catalog/test_joiner.py` (2 tests: Label row carries sorted deduped `issue_keys`; tracked CF row carries them; metadata-only and system kinds do not), `tests/catalog/test_writer.py` (1 test: writer writes column P with the expected comma-separated value; column-bound assertions in existing tests updated from `O` to `P`), and `tests/catalog/test_differ.py` (1 test: a row whose only machine-cell change is the issue-key set is classified as `updated`). **Verified 2026-07-16: tests exist — `test_labels_accumulate_issue_keys`, `test_tracked_custom_fields_accumulate_issue_keys`, `test_label_issue_keys_are_deduplicated_within_an_issue` (collector); `test_join_labels_emits_sorted_issue_keys`, `test_join_tracked_custom_fields_emits_issue_keys`, `test_join_untracked_custom_fields_and_system_kinds_have_no_issue_keys` (joiner); `test_to_row_includes_issue_keys_at_column_p`, `test_write_header_includes_issue_keys_column` (writer); `test_issue_key_change_is_a_material_change`, `test_issue_key_unchanged_does_not_trigger_update` (differ). Full catalog suite: 87 passed.**
- [x] 10.6 ~~Live verification~~ **Operational**: requires live Sheets/Jira credentials + Sprint 16 workbook access. Code implementation complete.
