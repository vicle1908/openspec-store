# jira-catalog Specification

## Purpose

Build and maintain a Jira issue catalog in the sprint spreadsheet — a summary tab showing aggregated metadata (labels, components, priorities, statuses) with clickable issue key lists for each category.

## Requirements

### Requirement: Build catalog from sprint data

The system SHALL read all issue keys from the sprint bucket tabs and fetch their metadata (labels, components, priority, status, assignee) via Jira API. It SHALL aggregate by each metadata dimension and produce a catalog tab in the spreadsheet.

#### Scenario: Catalog build with labels
- **WHEN** the sprint contains 50 tickets with various labels
- **THEN** the catalog tab lists each unique label with a comma-separated, sorted, deduped list of issue keys

### Requirement: Issue Keys column

The catalog tab SHALL include an `Issue Keys` column (column 16) containing hyperlinked issue keys for each category row.

#### Scenario: Label row has associated tickets
- **WHEN** a label row has 10 associated tickets
- **THEN** the Issue Keys cell contains 10 hyperlinked keys sorted alphabetically

### Requirement: Catalog refresh schedule

The system SHALL register a `catalog-refresh` schedule with cron `0 3 * * *` (daily at 3 AM) to keep the catalog current.

#### Scenario: Nightly refresh
- **WHEN** the catalog refresh schedule fires
- **THEN** the system re-reads sprint data and rebuilds the catalog tab

### Requirement: Catalog show command

The system SHALL provide a `catalog show --kind <dimension>` CLI command to display catalog contents in the terminal.

#### Scenario: Show label catalog
- **WHEN** the operator runs `kbs catalog show --kind Label`
- **THEN** the system prints a table of labels with their associated issue key counts
