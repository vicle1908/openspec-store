## ADDED Requirements

### Requirement: Additional sprint-scope tabs are configured by Google Sheets URL

The system SHALL allow additional sprint-scope tabs to be configured by their
Google Sheets URL (containing a `gid`). The system SHALL resolve each `gid` to
its current tab title from spreadsheet metadata at runtime, so configuration
remains valid when tab titles are renamed.

#### Scenario: URL with gid resolves to the current tab title

- **WHEN** an additional tab is configured by a Google Sheets URL containing `gid`
- **THEN** the system SHALL parse the `gid` from the URL
- **AND** it SHALL resolve the `gid` to the current tab title using spreadsheet
  metadata before reading the tab

#### Scenario: gid that no longer exists is skipped

- **WHEN** a configured `gid` does not match any tab in the spreadsheet metadata
- **THEN** the system SHALL skip that tab without aborting the run
- **AND** it SHALL log a warning naming the unresolved gid

#### Scenario: URL without a gid is skipped

- **WHEN** a configured Google Sheets URL carries no `gid` (URL parsing yields no
  grid id)
- **THEN** the system SHALL skip that URL without aborting the run
- **AND** it SHALL NOT treat the absent gid as gid `0`

### Requirement: URL-derived tab rows merge into the extracted sprint scope

The system SHALL merge issue rows from URL-derived tabs into the existing
bucket-tab extraction, preserving issue-key deduplication and per-tab parse-error
reporting.

#### Scenario: Rows from extra tabs are added to the scope

- **WHEN** URL-derived tabs are configured and contain valid issue rows
- **THEN** the system SHALL include those issue keys in the sprint scope
- **AND** it SHALL deduplicate issue keys across all tabs, keeping the first
  occurrence

#### Scenario: Bucket tabs are read before extra tabs for dedup ordering

- **WHEN** an issue key appears in both a bucket tab and a URL-derived extra tab
- **THEN** the system SHALL keep the bucket-tab occurrence (bucket tabs are
  appended to the read order before extra tabs)

#### Scenario: A duplicate gid is resolved once

- **WHEN** the same gid is configured more than once, or resolves to a tab title
  already in the read order
- **THEN** the system SHALL read that tab only once (order-preserving dedup of
  resolved titles)

#### Scenario: Parse errors are reported per tab

- **WHEN** a URL-derived tab contains rows that fail validation
- **THEN** the system SHALL report those parse errors labelled by tab
- **AND** it SHALL continue processing the remaining tabs

#### Scenario: Headerless extra tabs still contribute issue keys

- **WHEN** a URL-derived tab has no header row and the first column contains Jira issue keys
- **THEN** the system SHALL still extract those keys into the sprint scope
- **AND** it SHALL treat the first column as issue_key and the second column as description for parsing

### Requirement: Extra-sheet extraction is opt-in and backward compatible

The system SHALL treat URL-derived extra tabs as optional. When none are
configured, sheet extraction SHALL behave exactly as before.

#### Scenario: No extra tabs configured

- **WHEN** no additional sheet URLs are configured
- **THEN** the system SHALL read only the existing bucket tabs
- **AND** the extracted scope SHALL be unchanged from prior behavior
