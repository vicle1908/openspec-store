# jira-status-registry-sheet Specification

## Purpose

Define the `status_registry` Google Sheet schema: the canonical data store for the live status catalog, per-project manifest, and append-only audit trails.

## ADDED Requirements

### Requirement: Sheet ownership and auth

The `status_registry` Sheet SHALL be managed exclusively by `tdt-sheets` using `SheetsClient` with `ServiceAccountAuth.from_env()`. No manual Sheet edits by humans except for `decision_note` cells in `status_catalog` and sign-off cells in `project_manifest`.

#### Scenario: Sheet write via tdt-sheets
- **WHEN** the CLI writes to any tab of `status_registry`
- **THEN** it SHALL use `SheetsClient` from `tdt-sheets`
- **AND** auth SHALL follow the 3-level fallback (Service Account → ADC → key file)

#### Scenario: Human edits are restricted
- **WHEN** a human edits a cell in `status_catalog`
- **THEN** only the `decision_note` column (column K) SHALL be editable by humans
- **AND** all other columns SHALL be written exclusively by the CLI

### Requirement: Tab 1 — status_catalog (749 rows)

The `status_catalog` tab SHALL have the following columns (A through P):

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | `jira_id` | integer | Status record numeric ID (primary key) |
| B | `name` | string | Current display name in Jira |
| C | `category` | enum | `new`, `indeterminate`, `done` |
| D | `in_use` | boolean | ≥1 issue currently has this status |
| E | `used_by_projects` | integer | Count of distinct projects referencing this record |
| F | `duplicate_cluster_id` | string | UUID grouping records with same (name_lc, category); null for singletons |
| G | `cluster_size` | integer | How many records share this `duplicate_cluster_id`; null for singletons |
| H | `is_canonical_target` | boolean | True for the 1 record-per-cluster that survives dedupe |
| I | `canonical_key` | string | Key into taxonomy YAML (e.g. `next_gen.done`) |
| J | `tier` | enum | `1`=duplicate cluster member, `2`=singleton-in-use, `3`=project-private, `4`=garbage |
| K | `bucket` | enum | For singletons only: `mislabeled`, `alias`, `keep`, `garbage` |
| L | `decision_note` | string | Human judgment; only column editable by humans |
| M | `canonical_id` | integer | Target Jira ID after merge; null until merge plan is set |
| N | `merged_at` | datetime | When this record was merged into `canonical_id`; null until done |
| O | `sheet_updated_at` | datetime | Last time this row was updated by the CLI |

#### Scenario: Duplicate cluster grouping
- **WHEN** two status records share the same (name_lc, category)
- **THEN** they SHALL have the same `duplicate_cluster_id` (UUID)
- **AND** exactly one of them SHALL have `is_canonical_target=true`

#### Scenario: Canonical target selection
- **WHEN** `is_canonical_target=true` is assigned
- **THEN** it SHALL be the record with `max(used_by_projects), min(jira_id)` within the cluster
- **AND** this assignment SHALL be deterministic and reproducible

#### Scenario: Singleton classification
- **WHEN** a record has `cluster_size=null` (singleton)
- **THEN** its `bucket` column SHALL be one of: `mislabeled`, `alias`, `keep`, `garbage`
- **AND** its `decision_note` column SHALL be non-empty if `bucket=keep`

### Requirement: Tab 2 — project_manifest (~200 rows)

The system SHALL maintain a `project_manifest` tab listing every project plus its configured status catalog source. The tab MUST contain at least the columns below.

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | `project_key` | string | Jira project key (primary key) |
| B | `style` | enum | `next-gen`, `classic` |
| C | `template` | string | Fingerprint name (e.g. `next_gen/mainflow`) |
| D | `target_canonical` | string | Which canonical template this project should adopt |
| E | `canonical_statuses_present` | integer | Target-template statuses already present |
| F | `canonical_statuses_missing` | integer | Target-template statuses absent |
| G | `project_private_count` | integer | Statuses in this project not in any canonical template |
| H | `divergence_count` | integer | Status names not matching canonical (case-insensitive) |
| I | `instance_admin_signoff` | string | Account ID that approved the merge plan |
| J | `instance_admin_signoff_at` | datetime | |
| K | `project_admin_signoff` | string | Account ID that approved the project merge |
| L | `project_admin_signoff_at` | datetime | |
| M | `merge_status` | enum | `pending`, `approved`, `in_progress`, `completed`, `skipped` |
| N | `merge_at` | datetime | |
| O | `notes` | string | |

#### Scenario: Dual-control sign-off
- **WHEN** `merge_status` is set to `approved`
- **THEN** both `instance_admin_signoff_at` and `project_admin_signoff_at` SHALL be non-empty

### Requirement: Tab 3 — merge_log (append-only)

The system SHALL record every status merger with full provenance in `merge_log`. The tab MUST contain at least the columns below and MUST be append-only.

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | `merge_id` | string | UUID for this merge operation |
| B | `project_key` | string | |
| C | `style` | enum | `next-gen`, `classic`, `global` |
| D | `operation` | enum | `bulk_transition`, `workflow_rename`, `workflow_add_status`, `workflow_delete_status`, `workflow_scheme_swap`, `fix_category` |
| E | `from_jira_id` | integer | |
| F | `to_jira_id` | integer | |
| G | `issue_count` | integer | Number of issues transitioned (0 for `fix_category`) |
| H | `operator` | string | Account ID |
| I | `executed_at` | datetime | |
| J | `status` | enum | `success`, `partial`, `failed` |
| K | `error_detail` | string | |

#### Scenario: Pre-write logging
- **WHEN** a Jira API call changes state
- **THEN** a row SHALL be written to `merge_log` with `status=pending` BEFORE the call executes
- **AND** the `status` SHALL be updated to `success`, `partial`, or `failed` after the call completes

#### Scenario: Partial success tracking
- **WHEN** a bulk transition partially succeeds (some issues transitioned, some failed)
- **THEN** the row SHALL have `status=partial`
- **AND** the failed issue keys SHALL be written to `error_detail` as a JSON list

### Requirement: Tab 4 — dedupe_log (append-only)

The system SHALL record every dedupe cluster resolution in `dedupe_log`. The tab MUST contain at least the columns below and MUST be append-only.

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | `dedupe_id` | string | UUID for this dedupe event |
| B | `duplicate_cluster_id` | string | From `status_catalog.duplicate_cluster_id` |
| C | `canonical_name` | string | The name being deduped |
| D | `canonical_category` | enum | |
| E | `records_merged` | integer | Count of source records collapsed into the target |
| F | `target_jira_id` | integer | The surviving record |
| G | `total_issues_transitioned` | integer | Sum of `issue_count` across all affected projects |
| H | `operator` | string | |
| I | `executed_at` | datetime | |

#### Scenario: One dedupe_log row per cluster
- **WHEN** a duplicate cluster is deduped
- **THEN** exactly one row SHALL be appended to `dedupe_log`
- **AND** it SHALL contain the sum of all `issue_count` values from the corresponding `merge_log` rows

### Requirement: Tab 5 — signoff_log (append-only)

The system SHALL record every administrative sign-off event in `signoff_log`. The tab MUST contain at least the columns shown below and MUST be append-only.

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | `signoff_id` | string | |
| B | `project_key` | string | |
| C | `role` | enum | `instance_admin`, `project_admin` |
| D | `account_id` | string | |
| E | `account_display_name` | string | |
| F | `signed_at` | datetime | |
| G | `scope` | string | Human-readable summary of what was signed off |

#### Scenario: Each sign-off appends one row
- **WHEN** an `instance_admin` or `project_admin` approves a project merge plan
- **THEN** exactly one row SHALL be appended to `signoff_log` with `role`, `account_id`, and `signed_at` populated
- **AND** the row SHALL NOT be updated or deleted afterwards

#### Scenario: Signoff row is immutable after write
- **WHEN** the CLI attempts to update or delete an existing row in `signoff_log`
- **THEN** the `SheetsClient` SHALL raise `ValueError` to enforce the append-only contract

### Requirement: Tab 6 — audit_log (append-only)

The system SHALL record one summary row per audit run in `audit_log`. The tab MUST contain at least the columns shown below and MUST be append-only.

| Column | Header | Type | Description |
|--------|--------|------|-------------|
| A | `audit_id` | string | |
| B | `audited_at` | datetime | |
| C | `total_projects` | integer | |
| D | `fully_standard` | integer | Projects with 0 divergence |
| E | `needs_attention` | integer | Projects with divergence > 0 |
| F | `newly_diverged` | integer | Projects clean last audit but divergent now |
| G | `newly_clean` | integer | Projects divergent last audit but clean now |
| H | `report_url` | string | Link to audit detail sheet for this run |

#### Scenario: Each audit run appends exactly one summary row
- **WHEN** a registry audit completes
- **THEN** exactly one row SHALL be appended to `audit_log` summarizing the run's project counts
- **AND** the row SHALL NOT be updated or deleted afterwards

#### Scenario: Audit row carries divergence deltas
- **WHEN** the audit row is written
- **THEN** it SHALL include `fully_standard`, `needs_attention`, `newly_diverged`, `newly_clean`, and a `report_url` pointing to the run's detail sheet

### Requirement: Immutability contract

The system SHALL enforce that only `status_catalog` and `project_manifest` are mutable by the CLI; `merge_log`, `dedupe_log`, `signoff_log`, and `audit_log` are append-only — no updates or deletes are permitted after the row is written.

#### Scenario: Append-only violation prevention
- **WHEN** the CLI attempts to write to `merge_log`, `dedupe_log`, `signoff_log`, or `audit_log`
- **THEN** the operation SHALL be append-only (no `update` or `delete` call)
- **AND** the `SheetsClient` SHALL raise `ValueError` if a non-append operation is attempted
