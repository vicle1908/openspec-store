## ADDED Requirements

### Requirement: Person Capacity Role Classification

The system SHALL populate the Role column in the Person Capacity tab using `classify_role()` from the `person_capacity` module, which derives roles from `member_key` prefix matching against the YAML config.

### Role Classification Logic

- SHALL load role config from `~/.tdt/person_capacity_roles.yaml` via `load_role_config()`
- SHALL call `classify_role(member_key, config)` to derive role from member_key prefix
- SHALL respect explicit overrides (e.g., `BA_HA_USSO → QA`)
- SHALL fall back to sheet-provided role if `classify_role()` returns "Other"

#### Scenario: Member with matching prefix
- **Given** a roster member with `member_key = "QA_HongPhan"`
- **When** `classify_role()` is called
- **Then** the Role column SHALL be populated with `"QA"`

#### Scenario: Member with explicit override
- **Given** a roster member with `member_key = "BA_HA_USSO"`
- **When** the YAML config contains override `member_key: BA_HA_USSO → bucket: QA`
- **Then** the Role column SHALL be populated with `"QA"` (not `"Other"`)

#### Scenario: Member with no matching prefix or override
- **Given** a roster member with `member_key = "UNKNOWN_Member"`
- **When** `classify_role()` returns `"Other"`
- **Then** the Role column SHALL fall back to the sheet-provided role value (if any)
