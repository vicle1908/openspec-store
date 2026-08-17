# agent-docs-sync Delta Specification

## ADDED Requirements

### Requirement: Relative documentation links resolve from the containing document

The system SHALL resolve an ordinary relative Markdown link from the parent
directory of the Markdown document containing that link, rather than from the
repository root.

#### Scenario: Sibling document link

- **GIVEN** `docs/README.md` contains a link to `guide.md`
- **AND** `docs/guide.md` exists
- **WHEN** documentation links are validated
- **THEN** the link SHALL be reported as valid

#### Scenario: Nested parent-relative link

- **GIVEN** `docs/guide/start.md` contains a link to `../api.md`
- **AND** `docs/api.md` exists
- **WHEN** documentation links are validated
- **THEN** the link SHALL be reported as valid

#### Scenario: Missing relative target

- **GIVEN** a document contains a relative link whose resolved target does not exist
- **WHEN** documentation links are validated
- **THEN** the link SHALL be reported as broken
- **AND** the diagnostic SHALL include the resolved path

### Requirement: Local link resolution respects the configured repository boundary

When a repository boundary is explicitly supplied, the system SHALL reject a
local link whose resolved target escapes that boundary.

#### Scenario: Parent traversal escapes the repository

- **GIVEN** a document contains a relative link that resolves outside the configured repository boundary
- **WHEN** documentation links are validated
- **THEN** the link SHALL be reported as broken
- **AND** the diagnostic SHALL identify the boundary escape
