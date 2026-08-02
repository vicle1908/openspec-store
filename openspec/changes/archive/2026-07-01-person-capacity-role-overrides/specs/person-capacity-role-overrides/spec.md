# person-capacity-role-overrides Specification

## ADDED Requirements

### Requirement: Override-based role pinning

`load_role_config()` SHALL parse an optional `overrides` top-level key from the YAML config file. When present, its value MUST be a list of dicts, each containing `member_key` (non-empty string) and `bucket` (non-empty string). Each override is validated against the set of bucket labels declared in `role_order`; overrides with unknown bucket labels SHALL be excluded and a WARNING SHALL be emitted identifying the offending entry. Duplicate override `member_key` values SHALL keep the first occurrence and emit a WARNING for each subsequent duplicate.

The parsed overrides are stored in `RoleConfig.overrides` as a `tuple[RoleOverride, ...]`, defaulting to `()` when absent or empty.

#### Scenario: Overrides block absent — empty overrides tuple
- **WHEN** `~/.tdt/person_capacity_roles.yaml` has no `overrides` key
- **THEN** `load_role_config()` SHALL return `RoleConfig` with `overrides=()`

#### Scenario: Valid overrides loaded
- **WHEN** `overrides` is present with `[{"member_key": "BA_HA_USSO", "bucket": "QA"}]`
- **AND** `role_order` contains a bucket with `bucket="QA"`
- **THEN** `RoleConfig.overrides` SHALL contain one `RoleOverride(member_key="BA_HA_USSO", bucket="QA")`

#### Scenario: Override bucket not in role_order — excluded with warning
- **WHEN** `overrides` contains `[{"member_key": "X_Override", "bucket": "UnknownTeam"}]`
- **AND** `role_order` does not declare a bucket labeled `"UnknownTeam"`
- **THEN** `RoleConfig.overrides` SHALL NOT contain this entry
- **AND** a WARNING SHALL be emitted identifying `X_Override` and `UnknownTeam`

#### Scenario: Duplicate override member_key — first wins
- **WHEN** `overrides` contains two entries with `member_key="BA_HA_USSO"`
- **AND** the first has `bucket="QA"`, the second has `bucket="BA"`
- **THEN** `RoleConfig.overrides` SHALL contain only the first entry
- **AND** a WARNING SHALL be emitted identifying the duplicate `member_key`

#### Scenario: Override with empty member_key or empty bucket — skipped
- **WHEN** `overrides` contains an entry with `member_key=""` or `bucket=""`
- **THEN** `RoleConfig.overrides` SHALL NOT contain this entry
- **AND** a WARNING SHALL be emitted identifying the offending entry

### Requirement: Override checked before prefix matching

`classify_role(member_key, config)` SHALL, before consulting `config.role_order`, check whether `member_key` is present in `config.overrides`. If a matching override is found, the override's `bucket` label SHALL be returned immediately. If no override matches, the function SHALL fall through to the existing prefix-matching logic.

#### Scenario: Override overrides prefix
- **WHEN** `config.overrides` contains `RoleOverride(member_key="BA_HA_USSO", bucket="QA")`
- **AND** `config.role_order` has `RoleBucket(bucket="BA", match_prefix="ba_")`
- **AND** `member_key="BA_HA_USSO"`
- **THEN** `classify_role` SHALL return `"QA"` (the override wins)

#### Scenario: No override — falls through to prefix
- **WHEN** `member_key="QA_Nhung"`
- **AND** no override matches
- **THEN** `classify_role` SHALL return the prefix-matched bucket `"QA"`

#### Scenario: Empty overrides — behaves as before
- **WHEN** `config.overrides` is `()`
- **THEN** `classify_role` SHALL use prefix matching exactly as before this change

#### Scenario: Override with unknown bucket (already excluded at load time)
- **WHEN** `RoleConfig.overrides` does not contain the override (excluded at load)
- **THEN** `classify_role` SHALL fall through to prefix matching normally

### Requirement: Operator config refresh — drop dead BA bucket, add override

`~/.tdt/person_capacity_roles.yaml` SHALL be updated to:
1. Remove the `RoleBucket(bucket="BA", match_prefix="ba_")` entry from `role_order` (no members in the live roster match `ba_`).
2. Add an `overrides` block pinning `member_key="BA_HA_USSO"` to `bucket="QA"`.

This makes the BA_HA_USSO row appear in the QA section of the Person Capacity tab and removes the empty BA bucket from the config.

#### Scenario: BA bucket absent and BA_HA_USSO pinned via override
- **WHEN** `~/.tdt/person_capacity_roles.yaml` is loaded with no `BA` bucket in `role_order`
- **AND** `overrides: [{member_key: "BA_HA_USSO", bucket: "QA"}]` is present
- **THEN** `RoleConfig.role_order` SHALL contain no bucket labeled `"BA"`
- **AND** `RoleConfig.overrides` SHALL contain `RoleOverride(member_key="BA_HA_USSO", bucket="QA")`
- **AND** `classify_role("BA_HA_USSO", config)` SHALL return `"QA"` (via override)
