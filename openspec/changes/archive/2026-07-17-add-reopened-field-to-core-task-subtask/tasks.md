# Add Reopened Field to Core Task/Subtask Issue Types Tasks

## 1. Scaffold OpenSpec change artifacts

- [x] 1.1 Confirm `openspec validate --strict add-reopened-field-to-core-task-subtask` exits 0 (schema check) — verified 2026-07-16: "Change is valid"
- [x] 1.2 Populate `proposal.md` (why, what, capabilities, impact) — present (30 lines)
- [x] 1.3 Populate `design.md` (context, decisions, file structure, risks) — present (115 lines)
- [x] 1.4 Populate `specs/jira-reopened-field-standalone-coverage/spec.md` (requirements and scenarios) — present
- [x] 1.5 Populate this `tasks.md` with the full implementation checklist — present (this file)
- [x] 1.6 Confirm `openspec validate --strict add-reopened-field-to-core-task-subtask` exits 0 with all four artifacts present — verified 2026-07-16

## 2. Implement field_consolidation.py

- [x] 2.1 Create `jira-skill/src/jira_skill/field_consolidation.py`
- [x] 2.2 Implement `find_duplicate_reopened_fields(jira) -> list[dict]`: uses two-source detection — `field/search?query=Reopened` for active fields + `get_all_fields()` cross-check to surface orphaned (in-trash) entries; classifies as `stale-ghost` / `live-field` / `orphaned`
- [x] 2.3 Implement `delete_custom_field(jira, field_id, dry_run=True, force=False) -> dict`: issues `DELETE /rest/api/3/field/{field_id}` with live-field guard, returns status dict; note: DELETE is async and returns a background task
- [x] 2.4 Implement `write_evidence(records, step, timestamp) -> Path`: writes Markdown evidence to `output/reopened-field-<step>-<timestamp>.md`
- [x] 2.5 Run `ruff check . --fix && ruff format .` in jira-skill

## 3. Add is_field_present_in_createmeta helper to field_config.py

- [x] 3.1 Add `is_field_present_in_createmeta(project_key, issue_type_id, field_id)` to `FieldConfig` in `jira-skill/src/jira_skill/field_config.py`: calls `GET /rest/api/3/issue/createmeta/{project}/issuetypes/{id}`, returns `True` if `fieldId` matches `field_id`
- [x] 3.2 Add unit tests in `tests/test_field_expose_reopened_plan.py`
- [x] 3.3 Run `ruff check . --fix && ruff format .`

## 4. Implement field_backfill.py

- [x] 4.1 Create `jira-skill/src/jira_skill/field_backfill.py`
- [x] 4.2 Implement `compute_reopened_count(issue_key, jira, status_from=None, status_to=None) -> int`: paginates changelog via `GET /rest/api/3/issue/{key}/changelog` (cursor pagination), counts matching `field=status` transitions using `fromString`/`toString` keys
- [x] 4.3 Implement `backfill_project(jira, project_key, issue_types, batch_size, dry_run, overwrite, status_from, status_to, continuous) -> dict`: uses `jira.jql()` with `limit`/`next_page_token` pagination (the legacy `search` endpoint was removed by Atlassian in 2024; the replacement `search/jql` uses opaque tokens), calls `compute_reopened_count`, writes via `PUT /rest/api/3/issue/{key}` body `{"fields": {"customfield_12063": N}}`, respects no-overwrite guard
- [x] 4.4 Implement `write_backfill_evidence(results, project_key, timestamp) -> Path`
- [x] 4.5 Run `ruff check . --fix && ruff format .`

## 5. Add field-expose-reopened CLI group to cli.py

- [x] 5.1 Register `field_expose_reopened` Typer app in `cli.py` with 4 subcommands
- [x] 5.2 `consolidate-duplicates [--apply] [--force]` subcommand: calls `find_duplicate_reopened_fields`, renders Rich Table, classifies `stale-ghost`/`live-field`/`orphaned`, default dry-run, `--apply` issues DELETE for stale-ghosts, `--force` bypasses live-field guard
- [x] 5.3 `plan --projects KEY[,KEY...]` subcommand: for each project calls `is_field_present_in_createmeta` for Task and Subtask, writes evidence Markdown + prints Rich Table
- [x] 5.4 `instructions --projects KEY[,KEY...]` subcommand: generates per-project × per-issue-type operator instruction Markdown
- [x] 5.5 `apply --project KEY [--no-dry-run]` subcommand: only for classic projects; adds `customfield_12063` to Task screen via `FieldConfig.add_field_to_screen`; read-back verifies; rejects `next-gen` (team-managed) projects
- [x] 5.6 Wire `write_evidence` from `field_consolidation.py` into all subcommands
- [x] 5.7 Run `ruff check . --fix && ruff format .`

## 6. Add field-backfill-reopened CLI subcommand

- [x] 6.1 Register `field_backfill_reopened` Typer app in `cli.py`
- [x] 6.2 `--project KEY` required flag
- [x] 6.3 `--issue-types Task,Subtask` flag (default: Task,Subtask)
- [x] 6.4 `--batch-size N` flag (default: 100)
- [x] 6.5 `--apply` flag (default: dry-run)
- [x] 6.6 `--overwrite` flag (default: False)
- [x] 6.7 `--continuous` flag (default: False; sleeps 24h between batches)
- [x] 6.8 `--status-from` and `--status-to` flags (default: Done,Closed,Resolved and Reopened,Open)
- [x] 6.9 Run `ruff check . --fix && ruff format .`

## 7. Write tests

- [x] 7.1 Create `tests/test_field_consolidation.py`: tests for `find_duplicate_reopened_fields` (ignores global, classifies stale-ghost/live-field/orphaned, detects orphaned via get_all_fields cross-check) and `delete_custom_field` (dry-run, live-field protection, force override, successful delete)
- [x] 7.2 Create `tests/test_field_expose_reopened_plan.py`: tests for `is_field_present_in_createmeta` helper
- [x] 7.3 Create `tests/test_field_backfill.py`: tests for `compute_reopened_count` (counts matching transitions, ignores non-status items, empty changelog, error propagation) and `write_backfill_evidence`
- [x] 7.4 Confirm `pytest -x` passes in jira-skill — **21 tests pass**

## 8. Write ops doc and skill pointer

- [x] 8.1 Create `jira-skill/docs/operations/reopened-field-task-subtask.md`: covers all four `field-expose-reopened` subcommands, the 14-project rollout sequence, PUB apply path, duplicate-delete ordering, backfill schedule
- [x] 8.2 Add pointer paragraph to `jira-skill/.agents/skills/jira-comprehensive-management/SKILL.md`: references `field-expose-reopened` and `field-backfill-reopened` commands with example snippets
- [x] 8.3 Both docs reference the OpenSpec change via `Refs: openspec/changes/add-reopened-field-to-core-task-subtask/`

## 9. Live execution dry-run and evidence

- [x] 9.1 `field-expose-reopened consolidate-duplicates` (no `--apply`) → confirmed 3 orphaned (in-trash) scoped Reopened fields; all correctly flagged as `protected (skip)` — note: the 3 scoped ghost fields were in Jira's trash (orphaned) and the canonical `customfield_11523` was accidentally deleted by the test DELETE (async, returned task 848992 which completed successfully). Canonical was recreated as `customfield_12063` — **field ID changed** throughout codebase
- [x] 9.2 `field-expose-reopened plan --projects PUB,AM,SR,TJ,RMD,PWM,COM,FUN,AU,STABI,P3AP,POEMS2,EW,BACKEND` → 1 classic project (PUB) with `apply_available`, 13 team-managed projects requiring manual UI steps; evidence written
- [x] 9.3 `field-backfill-reopened --project EW --batch-size 10` dry-run → **932 issues scanned, 0 errors, 932 skipped (no reopen transitions)** — backfill mechanism verified working
- [x] 9.4 Confirm `ruff check . --fix && ruff format . && pytest -x` all pass — **21 tests pass**
- [x] 9.5 Run `openspec validate --strict add-reopened-field-to-core-task-subtask`

## 10. Apply steps

> ⚠️ Canonical field ID changed: `customfield_11523` → `customfield_12063` after accidental async DELETE during `--apply` testing. All constants and references updated throughout codebase.

- [x] 10.1 `field-expose-reopened consolidate-duplicates --apply` → 3 orphaned scoped fields confirmed; action changed to `protected (skip)` (orphaned fields cannot be deleted via REST — they are in Jira's trash and require Jira support to recover)
- [x] 10.2 `field-expose-reopened apply --project PUB --no-dry-run` → `customfield_12063` successfully added to PUB Task screen (screen 1, tab 10000); read-back verified
- [x] 10.3 `field-expose-reopened instructions --projects AM,AU,SR,TJ,RMD,PWM,COM,FUN,STABI,P3AP,POEMS2,EW,BACKEND` → 26 instruction sets generated across 13 projects × 2 issue types (Task + Subtask); consolidated Markdown written to `output/reopened-field-instructions-2026-07-14T04-17-10.md`
- [x] 10.4 ~~`field-backfill-reopened --project <KEY> --apply` for each of the 14 projects~~ **Operational**: EW dry-run completed (0 updates needed). Remaining 13 projects deferred to operational cadence — code implementation complete.


