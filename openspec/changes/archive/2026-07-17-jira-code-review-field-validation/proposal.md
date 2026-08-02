## Why

Currently, issues can be moved from "In Progress" to "Code Review" without populating the "Developer" and "Dev in Charge" fields. This leads to:
- Missing attribution when bugs are found in code review
- Unclear ownership during the review process
- Incomplete tracking for sprint reporting and capacity planning

We need to enforce that these fields are populated before allowing the transition, ensuring data quality and accountability in the workflow.

## What Changes

- Add a new jira-skill CLI command `workflow-validator` that:
  - Discovers custom field IDs for "Developer" and "Dev in Charge"
  - Retrieves workflow information for project(s)
  - Identifies the "In Progress" → "Code Review" transition
  - Adds a Field Required Validator to the transition via Jira Workflow API v3 (`POST /rest/api/3/workflows/update`)
- Support idempotent execution (skip if validator already exists)
- Support dry-run mode for safe preview before applying
- Document the manual Jira UI alternative for teams without API access

## Capabilities

### New Capabilities

- `jira-workflow-validator`: A jira-skill CLI tool that programmatically adds Jira Workflow transition validators via REST API v3. The tool discovers field IDs, finds workflow transitions, and applies `system:validate-field-value` validators with `ruleType: fieldRequired` to enforce required fields before specific status transitions.

  **Specification:** `openspec/specs/jira-workflow-validator/spec.md`

## Integration Verification Notes

**Important Finding:** The PUB project (ID: 11351) currently uses a simplified workflow with only 3 statuses: "To Do", "In Progress", "Done". There is no "Code Review" status or transition in PUB's current workflow.

For this validator to work:
1. The PUB workflow needs to be updated to include a "Code Review" status and transition
2. Or, the validator should be applied to a project that already has a "Code Review" transition (e.g., AM project which has it)

### Verified Working
- Field discovery: `jira-skill workflow discover --all` ✓
- Field discovery by name: `jira-skill workflow discover --field "Developer"` ✓
- All 27 unit tests pass ✓
- Ruff linting passes ✓

### Next Steps for Deployment
1. **For PUB:** First add "Code Review" status/transition to the workflow, then apply the validator
2. **Alternative:** Apply the validator to another project that already has "Code Review" status (e.g., AM, RMD, GWM projects)

## Impact

- **jira-skill**: New CLI module `src/jira_skill/workflow/` with `WorkflowClient`, `FieldDiscovery`, `TransitionValidator` classes
- **jira-daily-reports**: Potential future use of the same validator discovery pattern
- **webhook-receiver**: Extends existing `jira_guard` infrastructure concepts
- **Documentation**: Updated jira-skill QUICK-REFERENCE.md with new commands and created `examples/workflow_validator_examples.py`

## Non-Goals

- Modifying Jira field configurations (required fields globally) - only transition-level validation
- Creating Jira Automation rules (alternative approach, more complex)
- Retroactively filling missing field values on existing issues
- Supporting Jira Server/Data Center (REST API v3 Cloud-specific)
