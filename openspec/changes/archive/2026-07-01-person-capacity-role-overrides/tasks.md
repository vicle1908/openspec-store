# Tasks: person-capacity-role-overrides

> Implementation order. Each task is independently testable and ends with a commit.

## 1. OpenSpec skeleton

- [x] 1.1 Create `openspec/changes/person-capacity-role-overrides/` with `proposal.md`, `design.md`, `tasks.md`.
- [x] 1.2 Create `specs/person-capacity-role-overrides/spec.md` with all requirement scenarios.
- [x] 1.3 Verify structure is valid by checking all referenced symbols exist in the codebase.

## 2. Extend role_config.py

- [x] 2.1 Add `RoleOverride` dataclass (frozen, `member_key: str`, `bucket: str`) to `role_config.py`.
- [x] 2.2 Add `overrides: tuple[RoleOverride, ...] = ()` field to `RoleConfig`.
- [x] 2.3 Extend `load_role_config()` to parse `overrides` YAML block with:
      - Non-dict item skip + WARNING
      - Empty `member_key` / `bucket` skip + WARNING
      - Unknown bucket validation (skip + WARNING)
      - Duplicate `member_key` first-wins + WARNING
- [x] 2.4 Update the docstring of `RoleConfig` to document the new `overrides` field.
- [x] 2.5 Commit: `feat(person-capacity): add RoleOverride and overrides field to RoleConfig`.

## 3. Extend role_classifier.py

- [x] 3.1 Update `classify_role()` to check `config.overrides` before prefix matching.
- [x] 3.2 Document the override-precedence behavior in the function docstring.
- [x] 3.3 Commit: `feat(person-capacity): check overrides before prefix match in classify_role`.

## 4. Update __init__.py and example config

- [x] 4.1 Add `RoleOverride` to `__init__.py` exports.
- [x] 4.2 Update `config/person_capacity_roles.yaml.example`:
      - Document `overrides` block with comments
      - Remove the dead `BA` bucket entry
- [x] 4.3 Commit: `feat(person-capacity): add overrides documentation to example config`.

## 5. Tests

- [x] 5.1 Add override loading tests in `test_role_config.py`:
      - `test_overrides_loaded_from_yaml`
      - `test_overrides_absent_returns_empty_tuple`
      - `test_override_unknown_bucket_skipped_with_warning`
      - `test_override_duplicate_member_key_first_wins`
      - `test_override_empty_member_key_skipped`
- [x] 5.2 Add override classification tests in `test_role_classifier.py`:
      - `test_override_wins_over_prefix`
      - `test_override_with_empty_config_overrides`
- [x] 5.3 Add integration test in `test_integration_sheet.py`:
      - `test_override_pins_ba_ha_usso_to_qa`
- [x] 5.4 Verify: `cd jira-daily-reports && uv run pytest tests/person_capacity/ -v` → all green.
- [x] 5.5 Commit: `test(person-capacity): add override path tests`.

## 6. Refresh ~/.tdt/person_capacity_roles.yaml

- [x] 6.1 Write new YAML to `~/.tdt/person_capacity_roles.yaml`:
      - Drop `RoleBucket(bucket="BA", match_prefix="ba_")`
      - Add `overrides` block with `BA_HA_USSO → QA`
- [x] 6.2 Commit: (local operator config only — not in repo).

## 7. Pre-archive verification

- [x] 7.1 Run full test suite: `uv run pytest tests/person_capacity/ tests/reports/ -v --tb=short` → no failures.
- [x] 7.2 Run linters: `uv run ruff check src/jira_daily_reports/person_capacity/ tests/person_capacity/ && uv run mypy src/jira_daily_reports/person_capacity/` → clean.
- [x] 7.3 Verify the live sheet still loads correctly with the new overrides: inspect fresh roster output confirms BA_HA_USSO classified as QA.

## 8. Audit CLI

- [x] 8.1 Create `src/jira_daily_reports/person_capacity/cli_audit.py` with:
      - `AuditEntry` and `AuditResult` dataclasses
      - `audit_roster(sheet_client, spreadsheet_id, config, mapping_sheet_name)` — reads sheet directly
      - `print_audit_report(result)` — rich terminal output with bucket bars + detail table
- [x] 8.2 Add `person-capacity-audit` command to `cli.py`:
      - Options: `--spreadsheet`, `--sheet` (default: `Dropdown Keys - Do Not Delete -`), `--json`
      - Reads from canonical `Dropdown Keys` tab by default
      - Wires through to `audit_roster` + `print_audit_report`
- [x] 8.3 Commit: `feat(person-capacity): add person-capacity-audit CLI command`.

## 9. Audit CLI tests

- [x] 9.1 Add `tests/person_capacity/test_cli_audit.py`:
      - `test_all_covered_by_prefix`
      - `test_override_wins_over_prefix`
      - `test_other_bucket_flagged`
      - `test_duplicate_member_key_flagged`
      - `test_missing_display_name_counted`
      - `test_case_insensitive_override`
      - `test_case_insensitive_prefix`
      - `test_sheet_name_customizable`
      - `test_empty_sheet`
      - `test_qualifies_aliases_case_insensitive`
- [x] 9.2 Verify: `uv run pytest tests/person_capacity/test_cli_audit.py -v` → all green.
- [x] 9.3 Commit: `test(person-capacity): add cli_audit tests`.

## 10. Final verification

- [x] 10.1 `jira-daily-reports person-capacity-audit --spreadsheet 1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw` shows 46 covered, 0 other, 1 missing_display (All Teams sentinel).
- [x] 10.2 `jira-daily-reports person-capacity-audit --sheet "Person Roster" --spreadsheet ...` shows 45 covered, 0 other (confirms Person Roster is missing QA_Linh).
- [x] 10.3 `BA_HA_USSO` shows with `○ override` source and QA bucket in the Dropdown Keys audit.

## Rollback

- **Code rollback:** Revert commits from tasks 2–4 → prefix-only behavior restored.
- **Config rollback:** Remove `overrides` block from `~/.tdt/person_capacity_roles.yaml` → BA_HA_USSO returns to `BA` bucket.
- **Forward:** Add/remove override entries in YAML and reload — no restart needed.
