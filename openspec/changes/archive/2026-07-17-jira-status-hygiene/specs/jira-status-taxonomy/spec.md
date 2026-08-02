# jira-status-taxonomy Specification

## Purpose

Define the canonical status taxonomy: the authoritative list of allowed status records across the `psplit.atlassian.net` Jira instance, organized by project style (next-gen / team-managed vs. classic / company-managed).

## ADDED Requirements

### Requirement: Canonical taxonomy structure

The canonical taxonomy SHALL be defined in `tdt-meta/canonical_statuses.yaml` with two top-level maps: `next_gen` and `company_managed`. The file MUST be version-controlled and PR-reviewed. It MUST NOT contain Jira IDs — IDs are allocated by Jira at runtime.

#### Scenario: Canonical taxonomy YAML has two top-level maps and no Jira IDs
- **WHEN** `tdt-meta/canonical_statuses.yaml` is loaded at startup
- **THEN** the loader SHALL find exactly two top-level maps: `next_gen` and `company_managed`
- **AND** the loader SHALL reject any keys that look like Jira IDs (numeric IDs that match an existing Jira status record)

### Requirement: Next-gen (team-managed) canonical statuses

The `next_gen` section SHALL contain exactly 14 canonical status entries:

- `draft`: name "Draft", category `new`, aliases: `["draft"]`
- `todo`: name "To Do", category `new`, aliases: `["to do", "todo", "TO DO", "To Do"]`
- `in_progress`: name "In Progress", category `indeterminate`, aliases: `["in progress", "IN PROGRESS"]`
- `code_review`: name "Code Review", category `indeterminate`, aliases: `["code review", "CODE REVIEW"]`
- `api_review`: name "API Review", category `indeterminate`, aliases: `["api review"]`
- `fe_qa_review`: name "FE/QA Review", category `indeterminate`, aliases: `["fe/qa review", "FE/QA Review"]`
- `pm_review`: name "PM Review", category `indeterminate`, aliases: `["pm review"]`
- `deploy_dev`: name "Deploy in DEV", category `indeterminate`, aliases: `["deploy in dev", "DEPLOY IN DEV", "Deploy in Dev"]`
- `deploy_sandbox`: name "Deploy to Sandbox", category `indeterminate`, aliases: `["deploy to sandbox", "Deploy to Sandbox"]`
- `sit`: name "SIT", category `indeterminate`, aliases: `["sit", "SIT"]`
- `test_done`: name "Test Done", category `indeterminate`, aliases: `["test done", "TEST DONE"]`
- `ready`: name "Ready", category `indeterminate`, aliases: `["ready", "Ready"]`
- `rejected_duplicated`: name "Rejected/Duplicated", category `done`, aliases: `["rejected/duplicated", "REJECTED/DUPLICATED"]`
- `done`: name "Done", category `done`, aliases: `["done", "DONE"]`

#### Scenario: Lookup by name
- **WHEN** a status name is matched against the taxonomy using case-insensitive comparison
- **THEN** the system SHALL return the matching canonical entry if the name appears in the `aliases` list of any `next_gen` entry

#### Scenario: Lookup by canonical key
- **WHEN** a status is looked up by its YAML key (e.g. `next_gen.done`)
- **THEN** the system SHALL return the full entry with `canonical_name` and `category`

#### Scenario: Unknown name returns no match
- **WHEN** a status name has no match in any `next_gen` aliases
- **THEN** the system SHALL return `None` for that style

### Requirement: Company-managed canonical statuses

The `company_managed` section SHALL contain exactly 8 canonical status entries:

- `backlog_draft`: name "BacklogDraft", category `new`, aliases: `["backlogdraft"]`
- `new`: name "New", category `new`, aliases: `["new"]`
- `selected_for_development`: name "Selected for Development", category `new`, aliases: `["selected for development"]`
- `clarified`: name "Clarified", category `indeterminate`, aliases: `["clarified"]`
- `development_in_progress`: name "Development in Progress", category `indeterminate`, aliases: `["development in progress"]`
- `ready_for_uat`: name "Ready for UAT", category `indeterminate`, aliases: `["ready for uat"]`
- `uat_in_progress`: name "UAT In Progress", category `indeterminate`, aliases: `["uat in progress"]`
- `deployment_ready`: name "Deployment Ready", category `indeterminate`, aliases: `["deployment ready"]`

#### Scenario: Clarified status category
- **WHEN** a status named "Clarified" is classified
- **THEN** its category SHALL be `indeterminate` (not `new` or `done`)

### Requirement: Category enum

Every canonical entry SHALL have a `category` field whose value is one of exactly: `new`, `indeterminate`, `done`. The taxonomy SHALL NOT contain any other category values.

#### Scenario: Category invariant
- **WHEN** the taxonomy YAML is loaded
- **THEN** every entry's `category` field SHALL be one of `new`, `indeterminate`, or `done`

### Requirement: Alias expansion

The taxonomy SHALL be loaded by the CLI at startup and used to match live Jira status records. Matched names SHALL be normalized to the canonical `canonical_name` value regardless of the case or punctuation in the Jira record.

#### Scenario: Case-insensitive match
- **WHEN** a Jira record has name `"TO DO"` (uppercase)
- **THEN** it SHALL match the `todo` entry and be mapped to canonical name `"To Do"`

#### Scenario: Alias variants
- **WHEN** a Jira record has name `"In Progress"`
- **THEN** it SHALL match `in_progress` and be mapped to canonical name `"In Progress"`
- **WHEN** a Jira record has name `"IN PROGRESS"`
- **THEN** it SHALL also match `in_progress` and be mapped to `"In Progress"`

### Requirement: Taxonomy immutability after review

After the taxonomy is PR-reviewed and merged, it is immutable for the purposes of the dedupe operation. New entries MUST be added via a separate OpenSpec change.

#### Scenario: Adding new canonical status
- **WHEN** a project requires a new canonical status not in the taxonomy
- **THEN** a separate OpenSpec change SHALL be created to propose the addition
- **AND** the dedupe operation SHALL NOT create new canonical entries unilaterally
