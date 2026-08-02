# Tasks: person-capacity-role-ordering

> Implementation order. Each task is independently testable and ends with a commit.

## 1. Module skeleton & role_config

- [x] 1.1 Create `jira_daily-reports/src/jira_daily_reports/person_capacity/` package with `__init__.py` exporting the public API (`RoleBucket`, `RoleConfig`, `load_role_config`, `classify_role`, `sort_person_rows`).
- [x] 1.2 Create `tests/person_capacity/__init__.py` and `tests/person_capacity/conftest.py` with shared `empty_config` and `four_bucket_config` fixtures.
- [x] 1.3 Write failing tests in `tests/person_capacity/test_role_config.py` covering all 6 scenarios in the "Configurable role bucket configuration loading" requirement (no file, env override, malformed YAML, missing key, missing fields, duplicate buckets). Confirmed during research: `pyyaml>=6.0.0` is already a direct dep in `pyproject.toml` line 29 — no `pyproject.toml` change needed.
- [x] 1.4 Implement `jira_daily_reports/person_capacity/role_config.py` with `RoleBucket`, `RoleConfig`, and `load_role_config()` matching the spec.
- [x] 1.5 Verify: `cd jira-daily-reports && uv run pytest tests/person_capacity/test_role_config.py -v` → all green.
- [x] 1.6 Commit: `feat(person-capacity): add role_config module with YAML loading`.

## 2. role_classifier

- [x] 2.1 Write failing tests in `tests/person_capacity/test_role_classifier.py` covering all 6 scenarios in the "Prefix-based role classification" requirement.
- [x] 2.2 Implement `jira_daily_reports/person_capacity/role_classifier.py` with `classify_role()`.
- [x] 2.3 Verify: `uv run pytest tests/person_capacity/test_role_classifier.py -v` → all green.
- [x] 2.4 Commit: `feat(person-capacity): add role_classifier with prefix matching`.

## 3. sorter

- [x] 3.1 Write failing tests in `tests/person_capacity/test_sorter.py` covering all 5 scenarios in the "Two-pass row sorting with role grouping" requirement.
- [x] 3.2 Implement `jira_daily_reports/person_capacity/sorter.py` with `sort_person_rows()` (mutates `no` in place).
- [x] 3.3 Verify: `uv run pytest tests/person_capacity/test_sorter.py -v` → all green.
- [x] 3.4 Commit: `feat(person-capacity): add sorter with two-pass active/inactive role grouping`.

## 4. Operator config template

- [x] 4.1 Create `jira-daily-reports/config/person_capacity_roles.yaml.example` with the seven canonical buckets that mirror the live Sprint 17 roster prefixes (QA, AOS, iOS, Auto, PL, Technical, BA).
- [x] 4.2 Commit: `feat(person-capacity): add example role config`.

## 5. Sprint report sheet integration

- [x] 5.1 Locate the row-ordering block in `jira_daily_reports/reports/sprint_report_sheet.py` (verified during research: lines 723–748; `# ----- Row ordering -----` through the `all_rows: list` assignment).
- [x] 5.2 Wire `sort_person_rows` into the active/inactive split with a `try/except` fallback that preserves the prior behavior.
- [x] 5.3 Verify imports: `uv run python -c "from jira_daily_reports.person_capacity import load_role_config, classify_role, sort_person_rows; print('OK')"`.
- [x] 5.4 Verify no regressions: `uv run pytest tests/reports/ -v --tb=short` → all existing tests still pass.
- [x] 5.5 Commit: `feat(person-capacity): wire role-grouped row ordering into sprint report sheet`.

## 6. Integration test

- [x] 6.1 Write `tests/person_capacity/test_integration_sheet.py` exercising `sort_person_rows` against realistic `_build_person_capacity` row shapes (active + inactive + Other + name-asc within bucket).
- [x] 6.2 Verify: `uv run pytest tests/person_capacity/ -v` → all tests across all 4 files green.
- [x] 6.3 Commit: `test(person-capacity): add end-to-end integration test for role ordering`.

## 7. Pre-archive verification

- [x] 7.1 Run full test suite: `uv run pytest tests/ -v --tb=short` → no failures introduced.
- [x] 7.2 Run linters: `uv run ruff check src/jira_daily_reports/person_capacity/ tests/person_capacity/` and `uv run mypy src/jira_daily_reports/person_capacity/` → clean.
- [x] 7.3 Verify all `applyRequires` artifacts are present and the change is structurally valid: `openspec status --change "person-capacity-role-ordering"` and `openspec validate "person-capacity-role-ordering" --strict`.
- [x] 7.4 Verified live against the Sprint 17 sheet (`1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw`): 39 active rows appear in QA → AOS → iOS → Auto → PL → Technical → BA order (15/8/7/4/3/1/1), all 39 rows have correct role classification, all within-bucket ordering is name-ascending.

## Rollback

- Delete `~/.tdt/person_capacity_roles.yaml` → report reverts to prior behavior (no code revert needed).
- Code-level rollback: revert the wire-in commit (Task 5.2) — rest of the module is dormant without that single call site.