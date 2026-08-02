## Purpose

Defines which Jira workflow transitions should have the Dev in Charge validator (`customfield_11520`) attached, ensuring consistent enforcement across all team-managed projects.

## Requirements

### Requirement: Validator attachment scope

The Dev in Charge validator SHALL be attached to exactly **one** transition per project: the transition whose `fromStatus` is **"In Progress"** and whose `toStatus` is **"Code Review"** (or the project's equivalent review status, e.g. "CODE REVIEW").

Each project SHALL have at most one transition with the validator. No other transition in any project SHALL carry the Dev in Charge validator.

#### Scenario: Validator on the single correct transition

- **WHEN** a team-managed project has exactly one transition from "In Progress" to "CODE REVIEW" (or "Code Review")
- **THEN** the Dev in Charge validator (`system:validate-field-value` with `fieldsRequired: customfield_11520`) SHALL be attached to that transition and to no other

#### Scenario: Validator removed from non-matching transitions

- **WHEN** a project has the Dev in Charge validator on a transition whose `fromStatus` is NOT "In Progress" (e.g. "Draft", "TEST DONE", "Ready")
- **THEN** that validator SHALL be removed as a remediation step

#### Scenario: No validator on other transitions

- **WHEN** a team-managed project has transitions that do NOT go from "In Progress" to "Code Review"
- **THEN** those transitions SHALL NOT have the Dev in Charge validator attached

### Requirement: Validator behavior

The validator SHALL block the transition if the `Dev in Charge` field (`customfield_11520`) is empty or null.

#### Scenario: Empty Dev in Charge field

- **WHEN** a user attempts to transition an issue from "In Progress" to "Code Review"
- **AND** the `Dev in Charge` field is empty or null
- **THEN** the transition SHALL be blocked
- **AND** the error message SHALL be "Dev in Charge is required when transitioning to Review" (or equivalent)

#### Scenario: Dev in Charge field populated

- **WHEN** a user attempts to transition an issue from "In Progress" to "Code Review"
- **AND** the `Dev in Charge` field is populated with at least one user
- **THEN** the transition SHALL proceed

### Requirement: Project coverage

All team-managed projects in the Sprint 16 scope (AM, AU, FUN, PDS, RMD, SR, TJ) SHALL have the validator applied to their primary Code Review transition.

#### Scenario: Validator present on project

- **WHEN** a project is in the Sprint 16 scope
- **AND** the project has a team-managed workflow
- **AND** the project has a transition to a review status
- **THEN** the Dev in Charge validator SHALL be attached to that transition

#### Scenario: Company-managed project exemption

- **WHEN** a project is company-managed (e.g., PUB)
- **THEN** the Dev in Charge validator scope does not apply
- **AND** the project may use different validation mechanisms

### Requirement: Idempotent application

Applying the validator to a transition that already has it SHALL be a no-op.

#### Scenario: Validator already present

- **WHEN** the `workflow add-validator` command is run on a transition that already has the Dev in Charge validator
- **THEN** the command SHALL report "already configured" and not create a duplicate validator

#### Scenario: Validator not present

- **WHEN** the `workflow add-validator` command is run on a transition that does NOT have the Dev in Charge validator
- **THEN** the command SHALL attach the validator and increment the workflow version
