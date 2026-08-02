## Context

Atlassian's current Jira dashboard modules provide two relevant app-owned options: `jira:dashboardGadget` for the dashboard surface and `jira:dashboardBackgroundScript` for shared data and heavy precomputation. Atlassian documents these as dashboard modules in EAP/open beta, so the implementation must assume site-level availability gating and fail gracefully when the module is not exposed. Their runtime model supports a render URL, configurable view/edit entry points, refresh behavior, and a dashboard context that exposes `gadgetConfiguration`, `dashboard.id`, `gadget.id`, and `extension.entryPoint`. This is a better fit for rich operational dashboards than the built-in Jira gadget path, which still relies on legacy native gadget behavior for persistence and validation.

The new capability should live as a Forge app rather than inside the current native gadget automation path. The current `jira-dashboard-automation` change remains the built-in-gadget contract; this design introduces a separate modern path for app-owned dashboard items.

## Goals / Non-Goals

**Goals:**
- Provide a Jira dashboard surface owned by the app, not by Jira native gadget prefs.
- Support rich information and visualization, including charts, tables, and KPI-style summary cards.
- Support a separate edit mode so a gadget can be configured without leaving the dashboard.
- Support shared data and refresh updates for expensive reads by using a background script when needed.
- Keep the implementation permission-aware and scoped to the active Jira user.
- Treat the Forge dashboard modules as an availability-gated surface and show a clear unsupported state when the site has not opted into the module.

**Non-Goals:**
- Reworking the current native Jira built-in gadget dashboards.
- Recreating every Jira native gadget type.
- Implementing a generalized analytics platform outside Jira dashboards.
- Removing the built-in dashboard automation change or its legacy-compatible behavior.

## Decisions

- Use Forge `jira:dashboardGadget` as the primary surface.
  - Rationale: Atlassian's current dashboard gadget module is the modern app-owned path and supports separate view/edit resources.
  - Alternative rejected: native Jira built-in gadgets, because they keep the legacy persistence boundary and do not solve the app-owned requirement.

- Use `extension.entryPoint` and `gadgetConfiguration` as the runtime switch and config source.
  - Rationale: the Forge runtime already exposes the edit/view entry point and app-owned configuration object, so the gadget should branch on that contract instead of Connect-era `dashboardItem.*` values.
  - Alternative rejected: attempting to preserve Connect-style URL parameters or legacy gadget prefs, because that reintroduces the old persistence contract.

- Use `jira:dashboardBackgroundScript` only when the gadget needs shared state, precomputation, or push-style refresh.
  - Rationale: the background script can emit and receive events, which is useful for expensive Jira reads and multi-gadget coordination.
  - Alternative rejected: per-gadget polling for everything, because it duplicates work and scales poorly for dashboard pages with several gadgets.

- Default to Custom UI for chart-heavy and interactive views; use lighter UI only for simple summaries.
  - Rationale: rich visuals and editing flows are easier to evolve in Custom UI, while simple cards do not need the same complexity.
  - Alternative rejected: trying to force all views into a single UI paradigm, which would either limit charts or overcomplicate simple KPIs.

- Keep the data contract app-owned.
  - Rationale: configuration should live in the app's own storage and context, not in Jira legacy gadget prefs.
  - Alternative rejected: continuing to mirror native gadget prefs, because that preserves legacy dependency and splits the source of truth.

- Make the first release a single gadget family driven by a saved Jira filter.
  - Rationale: this is the smallest execution-ready slice that still proves the modern dashboard path and avoids bundle/source ambiguity.
  - Alternative rejected: supporting multiple gadget variants or multiple source adapters in the first release, because that expands scope before the new dashboard surface is proven.

## Risks / Trade-offs

- [Risk] Forge dashboards add a new app surface to build and deploy -> Mitigation: keep the first version small, with a single dashboard gadget family and a shared data contract.
- [Risk] Forge dashboard modules are EAP/availability-gated -> Mitigation: detect unavailability early and surface a clear unsupported/install guidance message instead of pretending the gadget is available.
- [Risk] Rich visuals can become slow if each gadget fetches Jira independently -> Mitigation: use the background script for shared reads and cache precomputed payloads.
- [Risk] Users may expect native Jira gadget behavior -> Mitigation: document the app-owned dashboard as a separate modern path and keep the native path intact for existing dashboards.
- [Risk] Forge module constraints may limit some interaction patterns -> Mitigation: start with the minimum reliable set: summary cards, charts, tables, edit form, and refresh flow.

## Migration Plan

1. Create a Forge app workspace or dedicated repo for the app-owned dashboard surface.
2. Implement one dashboard gadget with a compact summary view and one chart view.
3. Add an edit mode for config and a background script for shared data.
4. Verify Jira permissions, rendering, refresh behavior, and dashboard-module availability in a live Jira site.
5. Add skill/docs guidance so agents recommend the app-owned path when users want richer dashboards.
6. Keep the built-in dashboard automation intact until the app-owned surface is proven on real dashboards.

## Execution Target

Implement this change in a dedicated Forge repo at `/Users/lekhanhvinh/Developer/tdt/jira-app-owned-dashboard`.
