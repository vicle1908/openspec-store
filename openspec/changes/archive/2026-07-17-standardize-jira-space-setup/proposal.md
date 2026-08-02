# Jira Space Setup Standard Proposal

## Why

Jira project and space setup practices are currently spread across ad hoc research notes, one-off alignment documents, completed automation changes, operator memory, and live Jira state. The EW board context confirms that a real project/board pairing already exists (`EW` board `953`) and therefore the standard must explicitly audit existing board/filter wiring, not just greenfield creation assumptions.

## What Changes

- Define a canonical Jira space setup capability that standardizes how TDT provisions or aligns project fields, statuses, boards, filters, dashboards, permissions, and automation metadata.
- Capture a required preflight workflow for identifying project style, choosing a reference project, auditing permissions, and validating live Jira constraints before making changes.
- Standardize the expected output artifacts for a Jira space setup operation: canonical filters, board mappings, field-alignment evidence, dashboard validation results, captured IDs/naming conventions, and explicit setup-readiness outcomes for future automation.
- Document the boundary between what can be automated safely through `jira-skill` / `tdt-core` and what remains blocked or unsupported by the currently validated public Jira Cloud API surface.
- Establish a reusable spec contract that future changes can reference when onboarding or aligning projects such as EW, TJ, PDS, PUB, SR, and similar Jira spaces.

## Capabilities

### New Capabilities

- `jira-space-setup-standard`: Standard workflow, requirements, and evidence contract for provisioning or aligning Jira project/space configuration across the TDT workspace.

### Modified Capabilities

- `ticket-intelligence-core`: Clarify that spreadsheet-backed filter onboarding and canonical filter metadata produced during space setup become supported upstream inputs for ticket-intelligence and dashboard workflows.

## Impact

- `jira-skill`: field configuration, board creation, filter creation, dashboard validation, and permission-checking workflows become subject to a shared standard. Current shipped setup evidence still uses a legacy `manual_follow_up` field name that the future apply step should migrate to the new blocked/unsupported taxonomy.
- `tdt-core`: existing `PatchedJira` transport helpers remain the required Jira Cloud API v3 integration layer for setup automation.
- `jira-daily-reports` and dashboard automation flows inherit stronger expectations around canonical filters and validated dashboard inputs.
- `.agents` Jira/OpenSpec skills gain a stable reference for how agents should research, standardize, and verify Jira space setup work.
- Jira Cloud operator workflows become more repeatable, with explicit blocked/unsupported checkpoints where current API coverage is insufficient.
