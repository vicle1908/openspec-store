## Why

Jira built-in dashboards can be automated, but they still depend on legacy gadget behavior for some native widgets and cannot cleanly express richer, app-owned presentation logic. Atlassian's current Forge dashboard modules provide a modern path for dashboard items on dashboard-enabled Jira sites that can render richer information and visualizations directly inside Jira dashboards, with view/edit modes and optional background scripts for shared data and refresh.

## What Changes

- Define a new Forge-based dashboard capability for Jira Cloud that renders app-owned dashboard gadgets instead of native Jira built-in gadgets.
- Use Forge `jira:dashboardGadget` modules for the dashboard surface and optional `jira:dashboardBackgroundScript` modules for shared data and heavier precomputation.
- Support rich dashboard output such as summary cards, tables, charts, and drill-down views from app-owned data, starting with a single filter-backed gadget family.
- Support separate view and edit modes so dashboard configuration can live inside the app rather than Jira legacy gadget prefs.
- Make the new dashboard path permission-aware and Jira-scoped so users only see data they are allowed to access.
- Keep the existing built-in gadget dashboard path separate; this change is for a modern app-owned dashboard surface, not a rewrite of the current native gadget automation.

## Capabilities

### New Capabilities
- `forge-dashboard-gadgets`: Forge dashboard gadgets, background-script data sharing, view/edit modes, and rich visualization for app-owned Jira dashboards.

### Modified Capabilities
- None.

## Impact

- New Forge app codebase in a dedicated repo (proposed path: `/Users/lekhanhvinh/Developer/tdt/jira-app-owned-dashboard`): manifest, dashboard gadget view/edit UI, background script, and data contract.
- `tdt-meta` docs and skills: dashboard guidance should point to app-owned dashboards as the modern path for rich visualizations.
- Jira API usage: the app will fetch Jira data through Forge-scoped access instead of native gadget prefs.
- Future migration path: existing native dashboard automation can remain for built-in Jira gadgets while the app-owned dashboard capability becomes the preferred route for rich, custom dashboards.
