## Why

Jira dashboard creation and gadget configuration already exist in the workspace as a partially implemented, partially documented capability split between `tdt-core` dashboard REST helpers, `jira-daily-reports` delivery code, and ad hoc agent knowledge. This makes dashboard automation hard to discover, hard to validate, and easy to misuse when gadget configuration behaves differently across Jira Cloud gadget types.

## What Changes

- Define a workspace-level dashboard automation capability for Jira Cloud dashboards driven by saved filters and validated against Jira Cloud API behavior.
- Establish a canonical command surface in `jira-skill` for dashboard create, rebuild, inspect, validate, and dry-run workflows.
- Specify a layout-driven model for dashboard gadget sets so teams can declare important metric dashboards without hardcoding one fixed report layout.
- Make the default dashboard path explicitly filter-first: when no custom layout or filter override is provided, the command builds the baseline filter-backed dashboard for the configured default filter.
- Make the default sharing policy explicit: dashboards created or updated by the canonical workflow are viewable by all logged-in Jira users, with no implicit authenticated edit permission.
- Document the reliability boundary between API-supported dashboard operations and gadget-type-specific configuration that may require validation or manual fallback.
- Keep the contract strictly on supported built-in Jira Cloud gadgets; do not introduce a new custom dashboard module registration path.
- Add agent skill guidance so `.agents` can consistently recommend the correct workflow, gadget choices, verification steps, and non-goals.

## Capabilities

### New Capabilities
- `dashboard-automation-core`: Jira Cloud dashboard creation, gadget layout declaration, filter-backed configuration policy, validation workflow, and skill-facing operator guidance.

### Modified Capabilities
- `ticket-intelligence-core`: dashboard automation MAY consume filter-driven ticket intelligence outputs and registry metadata, but it does not change the canonical analysis contract.

## Impact

- `jira-skill`: new dashboard-oriented CLI surface and shared layout/configuration helpers.
- `tdt-core`: existing `PatchedJira` dashboard helpers become the required transport layer for the new capability.
- `jira-daily-reports`: native dashboard generation logic becomes an implementation reference and migration source rather than the only dashboard entry point; its current authenticated-edit default is no longer the canonical behavior.
- `.agents` skills: add or update Jira-oriented skill documentation so agents can create, validate, and explain dashboards safely.
- Jira Cloud API usage: dashboard CRUD and gadget lifecycle operations become standardized on REST API v3 with explicit validation, default logged-in view sharing, and documented best-effort limits for gadget property automation.
