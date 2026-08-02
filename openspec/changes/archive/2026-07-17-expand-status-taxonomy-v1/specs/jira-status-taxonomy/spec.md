# jira-status-taxonomy Specification (v1 — additive expansion)

## Purpose

Define the expanded canonical status taxonomy: the authoritative list of allowed status records across the `psplit.atlassian.net` Jira instance, organized by project style (next-gen / team-managed vs. classic / company-managed).

This is the v1 expansion of the original 22-entry taxonomy (14 next-gen + 8 company-managed) defined in `jira-status-hygiene`. The expansion adds 14 next-gen + 6 company-managed entries to cover high-frequency unmatched names found in live audit data.

## ADDED Requirements

### Requirement: Expanded taxonomy structure (incremental)

The canonical taxonomy SHALL be defined in `tdt-meta/canonical_statuses.yaml` with two top-level maps: `next_gen` and `company_managed`. After v1 expansion, `next_gen` SHALL contain exactly 28 entries and `company_managed` SHALL contain exactly 14 entries. The file MUST be version-controlled and PR-reviewed. It MUST NOT contain Jira IDs — IDs are allocated by Jira at runtime.

#### Scenario: Entry count after v1 expansion
- **WHEN** the YAML is loaded after the v1 expansion PR is merged
- **THEN** `len(taxonomy.next_gen)` SHALL be `28`
- **AND** `len(taxonomy.company_managed)` SHALL be `14`

### Requirement: New next-gen entries (v1)

The `next_gen` section SHALL contain the following 8 NEW entries in addition to the original 14:

- `in_review`: name "In Review", category `indeterminate`, aliases: `["in review"]`
- `review`: name "Review", category `indeterminate`, aliases: `["review"]`
- `uat`: name "UAT", category `indeterminate`, aliases: `["uat"]`
- `qat`: name "QAT", category `indeterminate`, aliases: `["qat"]`
- `kiv`: name "KIV", category `new`, aliases: `["kiv"]`
- `on_hold`: name "On Hold", category `indeterminate`, aliases: `["on hold", "on-hold", "hold"]`
- `blocked`: name "Blocked", category `indeterminate`, aliases: `["blocked", "block", "blocker"]`
- `closed`: name "Closed", category `done`, aliases: `["closed"]`
- `completed`: name "Completed", category `done`, aliases: `["completed"]`
- `rework`: name "Rework", category `indeterminate`, aliases: `["rework"]`
- `rejected`: name "Rejected", category `done`, aliases: `["rejected"]`
- `deferred`: name "Deferred", category `new`, aliases: `["deferred"]`
- `in_testing`: name "In Testing", category `indeterminate`, aliases: `["in testing"]`
- `validation`: name "Validation", category `indeterminate`, aliases: `["validation"]`

#### Scenario: UAT lookup
- **WHEN** a status named "UAT" is matched against the next-gen taxonomy
- **THEN** it SHALL return the `uat` entry with canonical_name "UAT"

#### Scenario: On Hold alias lookup
- **WHEN** a status named "On-Hold" or "Hold" is matched against the next-gen taxonomy
- **THEN** it SHALL return the `on_hold` entry with canonical_name "On Hold"

#### Scenario: KIV category
- **WHEN** a status named "KIV" is classified
- **THEN** its category SHALL be `new` (it's a backlog-ish state, not actively in progress)

### Requirement: New company-managed entries (v1)

The `company_managed` section SHALL contain the following 6 NEW entries in addition to the original 8:

- `backlog`: name "Backlog", category `new`, aliases: `["backlog"]`
- `ready_for_launch`: name "Ready for Launch", category `indeterminate`, aliases: `["ready for launch"]`
- `launched`: name "Launched", category `done`, aliases: `["launched"]`
- `resolved`: name "Resolved", category `done`, aliases: `["resolved"]`
- `removed`: name "Removed", category `done`, aliases: `["removed"]`
- `dropped`: name "Dropped", category `done`, aliases: `["dropped"]`

#### Scenario: Backlog lookup
- **WHEN** a status named "Backlog" is matched against the company-managed taxonomy
- **THEN** it SHALL return the `backlog` entry with canonical_name "Backlog"

#### Scenario: Resolved is done
- **WHEN** a status named "Resolved" is classified
- **THEN** its category SHALL be `done` (issues marked resolved are terminal)

### Requirement: Category enum invariant (preserved)

Every canonical entry SHALL have a `category` field whose value is one of exactly: `new`, `indeterminate`, `done`. The taxonomy SHALL NOT contain any other category values.

#### Scenario: Category invariant holds after v1
- **WHEN** the expanded taxonomy YAML is loaded
- **THEN** every entry's `category` field SHALL be one of `new`, `indeterminate`, or `done`

### Requirement: Alias expansion (preserved)

The taxonomy SHALL be loaded by the CLI at startup and used to match live Jira status records. Matched names SHALL be normalized to the canonical `canonical_name` value regardless of the case or punctuation in the Jira record.

#### Scenario: Case-insensitive match still works
- **WHEN** a Jira record has name `"uat"` (lowercase)
- **THEN** it SHALL match the `uat` entry and be mapped to canonical name `"UAT"`

### Requirement: Coverage improvement

After v1 expansion, when `jira-skill status audit` runs against the live instance and counts distinct status names that match the taxonomy, the coverage SHALL be ≥ 20% (up from 8.6% in v0). The exact percentage depends on live data at audit time.

#### Scenario: Coverage improvement is measurable
- **WHEN** the audit runs after the v1 expansion
- **THEN** the count of distinct names matching the union of `next_gen` and `company_managed` taxonomies SHALL be ≥ 20% of all distinct names in the catalog

### Requirement: Backward compatibility

The v1 expansion SHALL NOT remove or rename any existing v0 entry. Existing PRs and audits referencing v0 entries (e.g. `next_gen.todo`, `company_managed.clarified`) SHALL continue to resolve to the same canonical name and category.

#### Scenario: v0 entries still resolvable
- **WHEN** a lookup is performed for `next_gen.todo` or `company_managed.clarified`
- **THEN** the same canonical_name and category as v0 SHALL be returned
