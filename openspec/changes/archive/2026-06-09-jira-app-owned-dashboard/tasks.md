## 1. Forge app scaffolding

- [ ] 1.1 Create the dedicated Forge repo at `/Users/lekhanhvinh/Developer/tdt/jira-app-owned-dashboard`, including the Forge manifest, bootstrap files, and a working Custom UI entry point.
- [ ] 1.2 Register the initial `jira:dashboardGadget` module and confirm the gadget appears in Jira's dashboard gadget picker on a site where dashboard modules are enabled.
- [ ] 1.3 Add the initial `jira:dashboardBackgroundScript` module scaffold for shared data and refresh fan-out, or document why the first release does not need it yet.
- [ ] 1.4 Verify the app can be installed in a Jira Cloud site with the minimum required scopes for dashboard rendering and data read access, plus the dashboard-module availability gate.

## 2. Dashboard gadget UI

- [ ] 2.1 Implement the dashboard gadget view surface with a summary card and at least one chart or table visualization, sourced from the resolved saved filter.
- [ ] 2.2 Implement the edit surface so gadget settings can be changed inside the dashboard experience and persisted via `view.submit()`.
- [ ] 2.3 Add dashboard context handling for `dashboard.id`, `gadget.id`, `gadgetConfiguration`, and `extension.entryPoint`.
- [ ] 2.4 Add a permission-safe empty/error state for cases where the current user cannot access the underlying Jira data.

## 3. Shared data and refresh

- [ ] 3.1 Implement the dashboard background script data flow for precomputed or shared datasets, if the first release uses shared precomputation.
- [ ] 3.2 Add event-based request/response handling between the gadget and the background script.
- [ ] 3.3 Add caching or aggregation for shared data so multiple gadgets can reuse the same source payload.
- [ ] 3.4 Define the refresh path for live updates and verify that the dashboard can re-render without a full browser reload when supported.

## 4. Jira data contract

- [ ] 4.1 Implement Jira data fetches for the initial dashboard use case using app-scoped access and least-privilege permissions, with a saved-filter resolver input.
- [ ] 4.2 Define the supported source inputs for the first release: saved filter only, with ticket-intelligence bundle support deferred unless needed for the same visual contract.
- [ ] 4.3 Add validation for unsupported or missing source data so the gadget fails safely.
- [ ] 4.4 Document the app-owned state model so the gadget does not depend on Jira legacy gadget prefs and instead uses Forge-managed gadget configuration.

## 5. Verification and rollout

- [ ] 5.1 Add automated tests for view mode, edit mode, background data exchange, permission-safe rendering, and config persistence.
- [ ] 5.2 Run a live Jira Cloud install and validate the gadget picker, edit flow, visualization rendering, and Forge context behavior on an enabled site.
- [ ] 5.3 Capture rollback steps for uninstalling the Forge app or disabling the gadget module if live validation fails.
- [ ] 5.4 Update OpenSpec-linked docs and skills to recommend the app-owned dashboard path for rich visual dashboards, including a pointer from the native dashboard skill to the Forge app repo.
