## Context

The `person_capacity_roles.yaml` config file controls row grouping in the Person Capacity tab. The current implementation supports only `role_order: [{bucket, match_prefix}]`. A live roster inspection of the Sprint 17 workbook (sheet `1o5AJA589GElhqwACZn6v5uvFsVfruF25YS9Y_0LJhcw`, tab `Dropdown Keys - Do Not Delete -`) reveals 47 roster rows: 46 real members and 1 sentinel (`All Teams`, no display name). Exactly one member has a mismatched prefix: `BA_HA_USSO` whose display name is `QA Nguyen Thi Ha` and who is visually placed in the QA block of the sheet.

The original design deferred per-member overrides to keep the schema minimal. This change adds the mechanism now.

## Goals / Non-Goals

**Goals:**
- Add optional `overrides` block to `~/.tdt/person_capacity_roles.yaml`
- Overrides take precedence over prefix matching
- Unknown override bucket labels emit a warning and fall back to prefix match (safe degradation)
- Drop the dead `BA` bucket; fix `BA_HA_USSO` via the override mechanism
- Backward-compatible: configs without `overrides` work unchanged

**Non-Goals:**
- Auto-creating buckets from override labels (overrides must target an existing bucket)
- Renaming members in the source spreadsheet (this is an operator/data quality concern outside this code change)
- Supporting regex or glob in override member_key patterns (exact match only)

## Decisions

### D1: Overrides checked before prefix matching

**Choice:** When `classify_role(member_key, config)` is called, the overrides dict is consulted first. If `member_key` is a key in the overrides, the override's `bucket` is returned immediately. Prefix matching is only consulted if there is no override.

**Why:** An override represents an operator's explicit intent to pin a specific member to a specific bucket. The override must win over the automated prefix logic, which may be wrong for that member (as with `BA_HA_USSO`). This ordering is also the most intuitive operator mental model: "this person goes to QA, regardless of their key."

**Alternatives considered:**
- Overrides checked after prefix (post-fix): rejected — this would mean overrides can never fix a wrong prefix match.
- Override bucket can create a new bucket: rejected — unknown bucket labels in overrides are a likely typo; a warning + fallback to prefix is safer.

### D2: Override bucket must be a known bucket label

**Choice:** When `load_role_config()` processes the `overrides` block, each override's `bucket` is validated against the set of bucket labels already declared in `role_order`. Unknown bucket labels emit a WARNING and the override is excluded (the member falls back to prefix matching).

**Why:** An override pointing to a non-existent bucket is almost certainly a typo. Silently ignoring it after a warning is better than crashing the report or silently routing the member to "Other".

**Alternatives considered:**
- Auto-create unknown override buckets: rejected — unknown buckets inserted mid-list would disrupt the configured priority order.
- Hard error on unknown bucket: rejected — too disruptive for a config file; a warning + fallback is operator-friendly.

### D3: Overrides list (not dict) in YAML

**Choice:** The `overrides` block in YAML is a list of `{member_key, bucket}` dicts, matching the `role_order` list-of-dicts style.

**Why:** List-of-dicts is the existing convention in the file. A YAML dict keyed by `member_key` would be more compact but less consistent with the rest of the file and harder to document with inline comments per entry.

### D4: Sentinel row `All Teams` excluded at load time

**Choice:** `load_roster_display_names()` (in `person_worklog_source.py`) already skips rows with empty `jira_nick_name`. The sentinel `All Teams` row (member_key present, jira_nick_name empty) is therefore excluded from the roster and cannot reach `classify_role`.

**Why:** The `All Teams` member has no worklog author identity and exists only as a sheet formatting aid. It must not appear in the Person Capacity tab.

## Risks / Trade-offs

- **[Risk] Override targets unknown bucket → member lands in wrong bucket** → **Mitigation:** Warning log + fallback to prefix match; operator sees the warning and fixes their YAML.
- **[Risk] Duplicate override keys** → **Mitigation:** First-occurrence wins, WARNING emitted for subsequent duplicates (mirrors existing `role_order` behavior).
- **[Risk] Operator forgets to drop dead BA bucket after adding override** → **Mitigation:** Dead bucket with zero members is harmless — it occupies one unused slot in the YAML. The override is the functional fix; the dead bucket is cosmetic.

### D5: Audit CLI reads Dropdown Keys tab directly (not via load_roster_display_names)

**Choice:** The `person-capacity-audit` CLI command reads the `Dropdown Keys - Do Not Delete -` tab directly, bypassing `PERSON_CAPACITY_MAPPING_SHEET_NAME`. This ensures the audit always shows the full canonical roster (47 members) regardless of which tab the report uses (Person Roster = 45 members).

The audit accepts `--sheet <name>` to optionally target a different tab (e.g., `--sheet "Person Roster"` to audit the same source the report uses).

**Why:** `PERSON_CAPACITY_MAPPING_SHEET_NAME` controls the report's input, but it can drift from `Dropdown Keys`. The audit's job is to surface drift — it must read the canonical reference. The `--sheet` flag lets operators compare both tabs side-by-side.

**Sheet format detection:** The audit parses headers case-insensitively (`MEMBERS`, `members`, `Members` all work). This avoids a repeat of the bug where the header was `MEMBERS` but the code checked `c in _member_aliases` case-sensitively.

## Migration Plan

1. Add `RoleOverride` dataclass, `overrides` field, and `classify_role` override check in one PR.
2. Update `config/person_capacity_roles.yaml.example` with the new `overrides` block documented.
3. Operator copies updated example to `~/.tdt/person_capacity_roles.yaml`, removes `BA` bucket, adds `overrides`.
4. **Rollback:** Remove `overrides` block from YAML → behavior reverts to prefix-only (same as today).
5. **Roll-forward:** Edit YAML and reload — no restart needed.
