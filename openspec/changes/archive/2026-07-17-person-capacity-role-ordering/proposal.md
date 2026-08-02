## Why

The Person Capacity tab in the sprint report workbook currently lists every roster member ranked by hours worked (active first, inactive last, hours desc within active). This makes per-person metrics easy to read, but **makes team-level capacity reasoning hard** — QA, AOS (Android Ops), iOS, Auto, PL (Project Lead), Technical, and BA members are interleaved by hours. The TDT team needs rows grouped by role bucket so a stakeholder can see each team's capacity at a glance, with bucket order configurable per environment.

The Sprint 17 workbook (sheet `1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw`) uses underscore-prefixed member keys: `QA_Nhung`, `AOS_HungKm`, `iOS_SyThanh`, `Auto_Sai prakash`, `PL_Andrew`, `Technical_Vincent`, `BA_HA_USSO`. The role-bucket design must match these conventions.

## What Changes

- Add a new `jira_daily_reports.person_capacity` package with three modules:
  - `role_config.py` — `RoleBucket` and `RoleConfig` dataclasses + YAML loader
  - `role_classifier.py` — `classify_role(member_key, config) -> str`
  - `sorter.py` — `sort_person_rows(rows, config) -> list[dict]`
- Add `config/person_capacity_roles.yaml.example` operator-facing starter config.
- Wire `sort_person_rows` into `jira_daily_reports/reports/sprint_report_sheet.py` after the active/inactive split, so rows are renumbered 1..N after role-grouping.
- Add unit + integration tests under `tests/person_capacity/`.
- Ship a zero-config fallback: if `~/.tdt/person_capacity_roles.yaml` is absent or malformed, fall back to name-only sort within each active/inactive block (no behavior change for operators who don't opt in).

**No breaking changes** for existing operators — the default empty config preserves the current hours-desc / name-asc ordering.

## Capabilities

### New Capabilities

- `person-capacity-role-ordering`: Configurable role-bucket row grouping in the Person Capacity tab. Covers YAML config loading, prefix-based role classification, and two-pass active/inactive sorting with renumbering.

### Modified Capabilities

- *(none)* — The existing `jira-daily-reports` capability spec covers JQL pagination and search-helper contracts. Row ordering is presentation logic and not covered there, so no delta spec is needed.

## Impact

- **Code:** New module `jira_daily_reports/person_capacity/` (~3 small files). Single wire-in site in `reports/sprint_report_sheet.py`.
- **Config:** New operator file `~/.tdt/person_capacity_roles.yaml` (opt-in). Env override `PERSON_CAPACITY_ROLE_CONFIG` for testing or non-standard paths.
- **Tests:** New `tests/person_capacity/` package with 4 test files covering config loading, classifier, sorter, and end-to-end integration.
- **Operator workflow:** Drop the example file into `~/.tdt/`, edit bucket prefixes to match the roster, deploy. No code changes required to add/remove buckets.
- **Dependencies:** PyYAML (already a dependency of `jira-daily-reports`). No new external deps.
- **Risk:** Low — defensive `try/except` around `sort_person_rows` invocation preserves the current behavior if anything in the new module fails at runtime.
