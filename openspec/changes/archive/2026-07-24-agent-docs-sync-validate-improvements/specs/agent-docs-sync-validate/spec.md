## MODIFIED Requirements

### Requirement: Validation

The system SHALL validate doc accuracy with improved performance and usability.

#### Scenario: Parallel validation
- **WHEN** multiple markdown files are being validated
- **THEN** the system SHALL check files concurrently using asyncio.gather()
- **AND** it SHALL complete validation 5-10x faster than sequential processing

#### Scenario: Progress reporting
- **WHEN** validation is running
- **THEN** the system SHALL display progress like "Checking file 3/10..."
- **AND** it SHALL use rich.progress for visual feedback

#### Scenario: Local-only validation
- **WHEN** `--check-local` flag is provided
- **THEN** the system SHALL only check local file links
- **AND** it SHALL skip external HTTP URL validation
- **AND** it SHALL complete faster than full validation

#### Scenario: External link validation
- **WHEN** `--check-external` flag is provided
- **THEN** the system SHALL also check external HTTP URLs
- **AND** it SHALL report HTTP status codes for each link

#### Scenario: Skip image validation
- **WHEN** `--skip-images` flag is provided
- **THEN** the system SHALL skip image link validation
- **AND** it SHALL only validate text links

#### Scenario: Smart default path
- **WHEN** no --path is provided
- **THEN** the system SHALL default to docs/ directory if it exists
- **AND** it SHALL fall back to repo root if docs/ doesn't exist

### Requirement: CLI Options

The system SHALL provide CLI options for selective validation.

#### Scenario: Check local flag
- **WHEN** `--check-local` is provided
- **THEN** the system SHALL set check_external=False
- **AND** it SHALL only validate local file paths

#### Scenario: Check external flag
- **WHEN** `--check-external` is provided
- **THEN** the system SHALL set check_external=True
- **AND** it SHALL validate HTTP URLs

#### Scenario: Skip images flag
- **WHEN** `--skip-images` is provided
- **THEN** the system SHALL set check_images=False
- **AND** it SHALL skip image link validation
