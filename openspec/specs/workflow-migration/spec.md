# workflow-migration Specification

## Purpose
Reads a team-managed Jira project workflow and creates an equivalent company-managed workflow/scheme in the target project. Covers source workflow probing, target creation, scheme management, and validation.
## Requirements
### Requirement: Read source project workflow structure
The system SHALL read the complete workflow structure from a team-managed Jira project, including all statuses with their categories (To Do, In Progress, Done) and available transitions between statuses.

#### Scenario: Read TJ workflow statuses
- **WHEN** the system reads workflow for project "TJ" (team-managed, id: 11277)
- **THEN** it returns all statuses with their names, IDs, and status categories
- **AND** each status has a category of "new", "indeterminate", or "done"

#### Scenario: Infer transitions from sample issues
- **WHEN** the system queries transitions for sample issues in each status
- **THEN** it returns the available transitions (to-status) for each from-status
- **AND** transitions include the transition ID, name, and target status

#### Scenario: Handle team-managed API limitations
- **WHEN** the team-managed workflow API does not expose full transition details
- **THEN** the system falls back to issue-level transition queries
- **AND** logs a warning about inferred transitions

### Requirement: Create equivalent company-managed workflow
The system SHALL create a new company-managed workflow in Jira with statuses and transitions matching the source project's workflow structure.

#### Scenario: Create workflow with statuses
- **WHEN** the system creates a workflow named "TJ Workflow Copy" for company-managed use
- **THEN** it calls `POST /rest/api/3/workflow` with all source statuses
- **AND** returns the new workflow entity ID

#### Scenario: Add transitions to workflow
- **WHEN** the system adds transitions to the newly created workflow
- **THEN** it calls `POST /rest/api/3/workflows/update` with transition definitions
- **AND** each transition specifies from-status, to-status, and transition name
- **AND** handles version conflicts by re-fetching and retrying

#### Scenario: Handle status name uniqueness
- **WHEN** the system creates a workflow with status names that may already exist globally
- **THEN** it uses the original TJ status names (e.g., "Test Done", not "Test Done (TJ 20260727)")
- **AND** references existing statuses by their numeric ID when the name already exists globally
- **AND** creates new statuses with the original name only when no global duplicate exists
- **AND** logs the resolution strategy for each status name

### Requirement: Status name resolution strategy
The system SHALL resolve status names by checking global existence before creating new records.

#### Scenario: Standard global status reuse
- **WHEN** a status has an existing global ID below 10000
- **THEN** the system references it by numeric ID in the creation payload
- **AND** does NOT create a new status record

#### Scenario: TJ-specific status creation
- **WHEN** a status has no existing global ID (or ID >= 10000)
- **THEN** the system creates a new status with the original TJ name
- **AND** uses a client-generated UUID as the `statusReference`

### Requirement: Workflow name collision avoidance
The system SHALL generate unique workflow and scheme names on every migration run.

#### Scenario: Timestamp-suffixed names
- **WHEN** the system builds the creation payload
- **THEN** the workflow name includes a UTC timestamp suffix (e.g., "TJ Workflow Copy 20260730120000")
- **AND** the scheme name includes a UTC timestamp suffix

#### Scenario: Status name collision retry
- **WHEN** the `/workflows/create` endpoint returns "already in use" for a status name
- **THEN** the system retries with a UUID suffix appended to all collision-causing status names
- **AND** logs the retry attempt

### Requirement: Create and assign workflow scheme
The system SHALL create a new workflow scheme, map all target project issue types to the new workflow, and assign the scheme to the target project.

#### Scenario: Create workflow scheme
- **WHEN** the system creates a workflow scheme for the target project
- **THEN** it calls `POST /rest/api/3/workflowscheme` with the new workflow as default
- **AND** returns the new scheme ID

#### Scenario: Map issue types to workflow
- **WHEN** the system maps issue types to the new workflow
- **THEN** it calls `PUT /rest/api/3/workflowscheme/{id}/issuetype/{type}` for each issue type
- **AND** all issue types in the target project are mapped

#### Scenario: Assign scheme to project
- **WHEN** the system assigns the scheme to the target project
- **THEN** it calls `POST /rest/api/3/workflowscheme/project/switch`
- **AND** handles status mappings for existing issues
- **AND** the target project now uses the new workflow

### Requirement: Dry-run capability
The system SHALL support a dry-run mode that shows what changes would be made without applying them.

#### Scenario: Dry-run shows migration plan
- **WHEN** the user runs migration with `--dry-run` flag
- **THEN** the system displays the source workflow structure
- **AND** displays the target workflow that would be created
- **AND** displays the scheme that would be created
- **AND** displays the issue type mappings
- **AND** does NOT create any workflows or schemes

#### Scenario: Dry-run validates prerequisites
- **WHEN** the user runs migration with `--dry-run` flag
- **THEN** the system checks that the source project exists and is team-managed
- **AND** checks that the target project exists and is company-managed
- **AND** checks that the user has admin permissions on both projects
- **AND** reports any issues found

### Requirement: Error handling and rollback
The system SHALL handle errors gracefully and provide rollback capability.

#### Scenario: Handle API rate limiting
- **WHEN** the Jira API returns a 429 rate limit response
- **THEN** the system waits for the specified retry-after period
- **AND** retries the request up to 3 times
- **AND** raises `RateLimitError` if retries are exhausted

#### Scenario: Handle version conflicts
- **WHEN** the workflow update returns a 409 version conflict
- **THEN** the system re-fetches the workflow to get the current version
- **AND** retries the update with the fresh version number
- **AND** raises `VersionConflictError` if conflict persists after 3 retries

#### Scenario: Rollback on failure
- **WHEN** the migration fails after creating a workflow but before assigning the scheme
- **THEN** the system logs the partially created resources
- **AND** provides instructions for manual cleanup
- **AND** does NOT leave orphaned workflows or schemes

### Requirement: Scheme switch with compatibility payload
The system SHALL send a compatibility payload during scheme switch even when existing issues are not migrated.

#### Scenario: Build scheme switch mappings
- **WHEN** the system calls `switch_project_scheme`
- **THEN** it builds `mappingsByIssueTypeOverride` from the target project's issue types
- **AND** maps each issue type to the new workflow's statuses
- **AND** waits for the async task to complete (120s timeout)

### Requirement: Rollback support
The system SHALL store the original scheme ID and provide rollback capability.

#### Scenario: Rollback available after migration
- **WHEN** the migration completes successfully
- **THEN** the `MigrationResult` includes `original_scheme_id` and `rollback_available=True`
- **AND** the user can reassign the original scheme via `POST /workflowscheme/project/switch`

### Requirement: Validation before apply
The system SHALL validate the migration plan before applying changes.

#### Scenario: Validate source workflow readable
- **WHEN** the system reads the source workflow
- **THEN** it verifies at least one status was found
- **AND** verifies at least one transition was found or inferred
- **AND** raises an error if no workflow structure could be determined

#### Scenario: Validate target project writable
- **WHEN** the system checks the target project
- **THEN** it verifies the project exists and is company-managed
- **AND** verifies the user has project admin or Jira admin permissions
- **AND** verifies the project has issue types that can be mapped

#### Scenario: Validate status compatibility
- **WHEN** the system compares source and target statuses
- **THEN** it identifies any status name mismatches
- **AND** applies the configured mapping for known mismatches
- **AND** warns about any unmapped statuses

