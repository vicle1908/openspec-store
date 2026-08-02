## ADDED Requirements

### Requirement: Optionally expand planned scope with Jira-linked issues

The system SHALL support an opt-in step that expands the planned issue-key set
with the Jira-linked issues of issues in a configured source project (default
`PUB`). Expansion SHALL be disabled by default and SHALL NOT change behavior when
disabled.

#### Scenario: Expansion disabled by default

- **WHEN** linked-ticket expansion is not enabled
- **THEN** the system SHALL use only the issue keys extracted from the sheets
- **AND** it SHALL NOT query Jira for issue links

#### Scenario: Expansion seeded from source-project issues

- **WHEN** linked-ticket expansion is enabled
- **THEN** the system SHALL read the `issuelinks` of planned issues belonging to
  the configured source project
- **AND** it SHALL add the linked issue keys to the planned key set before the
  sprint JQL is built

#### Scenario: No source-project issues in the planned set

- **WHEN** expansion is enabled and the planned set has no issues in the
  configured source project
- **THEN** the system SHALL make no link query (no source keys to seed)
- **AND** it SHALL use the planned key set unchanged

#### Scenario: Source issues with no links

- **WHEN** the seeded source-project issues carry no `issuelinks`
- **THEN** the system SHALL leave the planned key set unchanged
- **AND** it SHALL report an expansion count of zero

### Requirement: Linked-ticket expansion includes all link types except clones

The system SHALL include linked issues of every link type except the clone link
type (`Cloners`, i.e. "clones" / "is cloned by"). The set of excluded link types
SHALL be configurable, defaulting to the clone link type only.

#### Scenario: Clone links are excluded

- **WHEN** a planned issue has a linked issue via the clone link type
- **THEN** the system SHALL NOT add that cloned issue to the planned key set

#### Scenario: Non-clone links are included

- **WHEN** a planned issue has linked issues via non-clone link types
  (e.g. split, blocks, blocked by, relates)
- **THEN** the system SHALL add those linked issue keys to the planned key set

#### Scenario: Both inward and outward links are followed

- **WHEN** a source issue has both inward and outward non-clone links
- **THEN** the system SHALL add the keys from both link directions

#### Scenario: Exclusion is matched by link-type name

- **WHEN** a link's type name matches an entry in the configured excluded link
  types
- **THEN** the system SHALL exclude that link's target regardless of direction

### Requirement: Linked targets may belong to any project

The system SHALL include linked target issues regardless of their project. Only
the source side of expansion SHALL be restricted to the configured source
project.

#### Scenario: Cross-project linked target is included

- **WHEN** a planned source-project issue links to an issue in a different project
  via a non-clone link type
- **THEN** the system SHALL include that cross-project linked issue key

### Requirement: Expansion preserves dedup and dry-run semantics

The system SHALL deduplicate the expanded key set and SHALL NOT perform any Jira
writes during expansion. Reading issue links SHALL be permitted in dry-run. The
expanded set SHALL preserve the order of the original planned keys, appending
newly discovered linked keys after them.

#### Scenario: Expanded keys are deduplicated

- **WHEN** expansion produces a linked issue already present in the planned set
- **THEN** the system SHALL keep a single occurrence of that key
- **AND** the original planned keys SHALL retain their position ahead of newly
  added linked keys

#### Scenario: A linked target equal to a planned key adds nothing

- **WHEN** a non-clone link points back to an issue already in the planned set
- **THEN** the system SHALL NOT duplicate that key

#### Scenario: Source keys are batched within the Jira query limit

- **WHEN** the source-project planned set exceeds the per-query key limit
- **THEN** the system SHALL fetch `issuelinks` in chunks within the limit
- **AND** it SHALL union the linked keys across all chunks

#### Scenario: Dry-run reads links without writing

- **WHEN** linked-ticket expansion runs in dry-run mode
- **THEN** the system SHALL read issue links to compute the expanded scope
- **AND** it SHALL NOT create or modify any Jira filter, board, or issue
