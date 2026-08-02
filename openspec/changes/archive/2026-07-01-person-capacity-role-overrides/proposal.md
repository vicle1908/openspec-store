## Why

The Person Capacity tab groups rows by role bucket using case-insensitive prefix matching on `member_key`. This works for the 46 real members in the live roster (prefixes: `qa_`, `aos_`, `ios_`, `auto_`, `pl_`, `technical_`). However, one member — `BA_HA_USSO` — has a mismatched prefix: the sheet places her under the QA team section and her display name is `QA Nguyen Thi Ha`, but her `member_key` starts with `BA_`. Under the current prefix-only model, she lands in a phantom `BA` bucket (with no other members) instead of `QA`.

The previous change (`person-capacity-role-ordering`) deliberately excluded per-member overrides to keep the schema minimal. Since the mismatch is real and future roster changes may introduce similar edge cases, the override mechanism should be added now.

## What Changes

- Extend `RoleConfig` with a new optional `overrides` field: a list of `member_key → bucket` explicit pins that are checked **before** prefix matching.
- Extend `load_role_config()` to parse the new `overrides` YAML block with bucket-label validation.
- Extend `classify_role()` to check the overrides dict before falling back to prefix matching.
- Drop the dead `BA` bucket from `~/.tdt/person_capacity_roles.yaml` and add `BA_HA_USSO → QA` as an explicit override.
- Add a sentinel-row rule: any roster row whose `jira_nick_name` is empty (e.g. `All Teams`) is skipped at load time and does not appear in the capacity tab.

## Capabilities

### New Capabilities

- `person-capacity-role-overrides`: Explicit `member_key → bucket` pinning that takes precedence over prefix matching. Enables operators to handle mismatched member keys without renaming them in the source spreadsheet.

### Modified Capabilities

- `person-capacity-role-ordering`: Extended with optional `overrides` block in `~/.tdt/person_capacity_roles.yaml`. Backward-compatible — existing configs without `overrides` work unchanged.

## Impact

- **Code:** 3 files modified (`role_config.py`, `role_classifier.py`, `__init__.py`), 1 new test file. All changes are additive (no removals from existing APIs).
- **Config:** `~/.tdt/person_capacity_roles.yaml` updated: `BA` bucket removed, `overrides` block added with `BA_HA_USSO → QA`.
- **Tests:** 6 new scenarios (override overrides prefix, unknown override bucket, duplicate override key, empty overrides, sentinel row exclusion, sentinel `All Teams` excluded).
- **Operator workflow:** Operator adds `overrides` block to their YAML if needed. No code change required for future roster edge cases.
- **Dependencies:** None — all changes within `jira-daily-reports`.
- **Risk:** Low — overrides are optional, all existing configs are backward-compatible, unknown override buckets emit a warning and fall back to prefix match.
