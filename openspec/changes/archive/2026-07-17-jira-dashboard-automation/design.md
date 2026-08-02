# Jira dashboard automation design

## Context

`tdt-core` already exposes five dashboard helpers on `PatchedJira`: `search_dashboards`, `create_dashboard`, `get_dashboard_gadgets`, `add_dashboard_gadget`, and `set_dashboard_gadget_property`. `jira-daily-reports` uses them to build an 8-gadget default dashboard via `delivery/jira_dashboard.py`. However:

- The dashboard capability lives only inside `jira-daily-reports` and is not discoverable from `jira-skill`.
- No validation command exists to confirm a dashboard is actually rendering the intended filter.
- Gadget property automation has a strict supported set: the bundled eight-gadget dashboard is expected to validate cleanly using the Jira Cloud v3 dashboard item property path, and unrecognized gadgets are surfaced as unsupported/best-effort rather than silently treated as success.
- The layout is hardcoded; teams wanting a custom metric set must edit Python code.
- There is no agent-facing skill guidance for Jira dashboard operations.

### Constraints

- Jira Cloud REST API v3 is the primary and only supported persistence path. No Jira Data Center API paths and no legacy dashboard prefs fallback writes.
- Auth via `ATLASSIAN_*` env vars consumed by `tdt_core.clients.jira.JiraClientFactory`.
- No gadget cloning, no per-user or per-group dashboard permissions via API.
- Dashboard item property writes are reliable for the supported built-in gadget set (Filter Results, Pie, Work Item Statistics, Workload Pie Chart, Stats, Created-vs-Resolved, Average Age, Time Since, Resolution Time, Average Time in Status, Time to First Response, Recently Created Chart); unsupported gadget types receive best-effort handling.
- Dashboard update semantics are coarse-grained: a partial dashboard `PUT` can replace omitted permission blocks, so the canonical workflow MUST treat view and edit permissions as explicit state rather than relying on server-side merge behavior.
- The workspace is the monorepo; command must be usable from any target repo context.

### Stakeholders

- Jira operators who need filter-scoped visual dashboards.
- Agent runners who need documented, repeatable dashboard creation and validation.

## Goals / Non-Goals

**Goals:**

- Create a command surface for dashboard lifecycle operations (create, rebuild, list, validate) accessible from `jira-skill`.
- Define a layout model that represents gadget sets as data (not code), enabling YAML-driven dashboard declaration.
- Establish a validation path that confirms gadgets render and filter-backed properties are actually set.
- Make the default dashboard workflow deterministic: if the operator does not provide a filter override, the command uses the configured default filter for the baseline bug/issue dashboard.
- Make the default sharing policy deterministic: dashboards created or updated by the canonical workflow are viewable by all logged-in Jira users and do not grant implicit authenticated edit access.
- Document the supported contract for built-in gadget configuration so operators know which dashboards are guaranteed to be fully configured without manual Jira UI follow-up.
- Add skill guidance for `.agents` so agents can execute dashboard workflows without ad hoc research.

**Non-Goals:**

- Reliable programmatic gadget parameter configuration beyond what Jira Cloud REST API supports natively for unsupported or unrecognized gadgets.
- Per-user or per-group dashboard permissions (Jira Cloud REST API does not support this).
- Dashboard cloning from template dashboards (Jira Cloud REST API does not support this).
- Native Jira CFD gadgets (Atlassian does not provide one; use Sheets-embedded charts instead).
- Moving `jira-daily-reports` dashboard logic into `jira-skill` wholesale (keep existing code; add a shared layer).
- Custom or app-owned dashboard modules (Forge jira:dashboardGadget or Connect jiraDashboardItems). REST v3 cannot register a new gadget module; only built-in gadgets may be placed.

## Decisions

### 1. Command surface lives in `jira-skill`

- Rationale: `jira-skill` is the natural home for Jira-domain CLI commands. `jira-daily-reports` continues using its own dashboard logic for its specific 8-gadget layout.
- Alternative rejected: new standalone CLI (adds another entry point with no benefit).

### 2. Layout as data (YAML), not code

- Rationale: teams can declare dashboard gadget sets in YAML without editing Python. Layouts are portable and versionable.
- Structure: `GadgetSpec` dataclass maps to YAML entries (title, uri, color, column, row, properties).
- Default layout: `jira-daily-reports`-style 8-gadget set for baseline bug/issue dashboards.
- Default filter behavior: when the operator does not provide a filter override, the workflow resolves configured default filters using the same precedence already used elsewhere in `jira-skill` (`JIRA_DEFAULT_FILTER_REGISTRY_ID` / `JIRA_DEFAULT_FILTER_REGISTRY_TAB`, then `JIRA_DEFAULT_FILTER_IDS`, then `JIRA_FILTER_ID`, then `JiraConfig.filter_id`). For JTI CLI calls (`--filter` / `--filters` / `--filter-url`), `JIRA_DEFAULT_FILTER_REGISTRY_ID` also acts as the implicit output destination when no explicit `--output` is provided.
- Dashboard default-filter rule: because a single dashboard create/rebuild action targets one dashboard at a time, the canonical workflow SHALL require that default-filter resolution yields exactly one filter for dashboard commands; if multiple defaults are configured, the CLI MUST fail fast and instruct the operator to pass `--filter-id` explicitly.

### 3. Gadget property policy: supported built-ins must validate fully

- Rationale: live validation on `psplit.atlassian.net` on 2026-06-08 showed the Jira Cloud v3 dashboard item property path can persist the bundled gadget set reliably when the workflow sends the complete payload Jira expects.
- Supported set: Filter Results, Pie Chart, Work Item Statistics, Issue Type Statistics, Created vs. Resolved, Average Age, Time Since, Resolution Time, Average Time in Status, Time to First Response, and Recently Created Chart.
- Write path: the command MUST persist supported gadget configuration through `/rest/api/3/dashboard/{dashboardId}/items/{itemId}/properties/config` only.
- Verification: `validate` SHALL read back the v3 `config` property payload and compare required invariants per gadget profile, including `filterId` or `projectOrFilterId` plus only the gadget-native fields that Jira actually persists for that gadget type.
- On mismatch: supported gadgets are contract failures, not advisory warnings. Manual Jira UI follow-up is reserved for unrecognized or explicitly best-effort gadgets only.

### 4. `filterId` format for gadget properties

- Rationale: live validation on `psplit.atlassian.net` on 2026-06-08 confirmed the durable state for the supported built-in gadgets is readable and verifiable through the v3 dashboard item property payload when the workflow sends the complete config Jira expects.
- Mappings: `filterId` as a string on Filter Results gadgets; `projectOrFilterId` with `filter-<id>` prefix for the supported chart/statistics gadgets. Two-dimensional stats and time-since use the minimal live-verified property set, not padded defaults.
- Therefore the workflow SHALL validate the v3 `config` property contract as the source of truth for the supported built-in set.

### 5. Layout file format: YAML

- Rationale: YAML is readable, supports comments, and is easy to version alongside the dashboard code.
- Schema: `name`, `description`, `gadgets[]` (title, uri, color, column, row, properties).
- Properties are free-form key-value pairs; the operator is responsible for valid keys per gadget type.

### 6. Validation mode

- Rationale: operators need a way to confirm dashboards are configured correctly without opening Jira manually.
- Mode: `validate --dashboard-id` reads the dashboard, fetches gadgets via `get_dashboard_gadgets()`, and for each gadget checks the v3 `config` property for the expected filter ID and required gadget-profile defaults.
- Reports: gadget title, gadget ID, expected vs actual configuration status, and whether the mismatch is required or best-effort.

### 7. Idempotency

- Rationale: running dashboard creation repeatedly should be safe.
- Strategy: `find_or_create_dashboard` checks for exact name match before creating. Rebuild option clears all gadgets before re-adding.

### 8. Sharing policy defaults

- Rationale: real Jira Cloud behavior confirmed that sending only `sharePermissions` updates can clear `editPermissions`, so permission state must be managed deliberately.
- Default view policy: dashboards created or updated by the canonical workflow SHALL be shared to all logged-in Jira users (`loggedin` / authenticated view access).
- Default edit policy: the canonical workflow SHALL NOT grant authenticated edit access by default; edit permissions must be explicit and optional.
- Alternative rejected: inheriting the current `jira-daily-reports` behavior of authenticated edit permissions, because that over-grants edit access and does not match the desired default.

## Risks / Trade-offs

- [Risk] Gadget URIs may break if Atlassian updates gadget plugin versions → Mitigation: URIs are versioned in the code; add monitoring for 404 on `GET /rest/api/3/dashboard/gadgets` after major Jira Cloud updates.
- [Risk] Dashboard item property writes may be accepted but not persist complete gadget state → Mitigation: validation mode reads back the v3 property payload after placement and surfaces mismatches as contract failures for required gadgets.
- [Risk] Dashboard name collision (substring match in search) → Mitigation: `find_or_create_dashboard` uses exact name match on results, not substring search.
- [Risk] Adding dashboard capability to `jira-skill` increases its surface area → Mitigation: the module lives in a dedicated `dashboard/` sub-package; CLI commands are opt-in and isolated.

## Migration Plan

1. Add `jira_skill/dashboard/` module with `GadgetSpec`, layout YAML support, and lifecycle helpers.
2. Add `jira-skill dashboard` Typer command group: `create`, `rebuild`, `list`, `validate`, `dry-run`.
3. Add layout files for baseline bug/issue dashboards.
4. Add agent skill `jira-dashboard` documenting gadget URIs, reliability limits, and validation workflow.
5. Verify all operations against `psplit.atlassian.net` before marking complete.
6. Archive or update the `jira-daily-reports` dashboard command documentation to reference `jira-skill` as the canonical entry point for new dashboards.

## Post-implementation research findings

Live inspection of Jira dashboard `11827` showed a richer native-gadget pattern than the current bundled baseline captures. These notes are recommendations for future native layouts, not a change to the current v3-only implementation.

- **Multi-filter fan-out**: the live dashboard spreads 10 gadgets across 5 saved filters. The biggest gap in our current layout is per-gadget filter override support. Recommendation: add `filterId` as an optional layout field so a single dashboard can mix scopes without code changes.
- **Workload Pie Chart**: Jira Cloud persists `com.atlassian.jira.ext.charting:workloadpie-gadget` cleanly through the v3 item-property path. Recommendation: treat it as a valid native gadget option for effort-centric dashboards.
- **Custom-field pivots**: the live dashboard uses `customfield_*`, `labels`, and `reporter` pivots in pie and stats gadgets. Recommendation: document that layout `properties` may carry stable custom-field IDs directly for `statType`.
- **Trend vs cross-section**: the live dashboard is purely cross-sectional; our baseline is trend-heavy. Recommendation: keep both layout families documented. Use the cross-sectional variant when users want breadth across filters/fields, and the trend-heavy variant when they want age or movement over time.
- **App-owned path**: the archived Forge dashboard proposal remains deferred. The current native gadget path already covers the live feature set observed on 11827, so Forge stays a separate future option for custom rendering rather than the default recommendation.
- **Work Item Statistics**: the gadget directory exposes `com.atlassian.jira.gadgets:stats-gadget` as "Work Item Statistics". Recommendation: bundle a dedicated work-item breakdown layout that uses `statType` pivots such as assignee, components, and labels to complement the status/priority slices already in the baseline dashboard.
- **Flow metrics**: the gadget directory also exposes Resolution Time, Average Time in Status, Time to First Response, and Recently Created Chart. These are the highest-value flow bundle because they answer the operational questions users ask most often: how long issues take to resolve, where they stall, how fast the team responds, and whether new work is accumulating.

## Native Variants Delivered

The following native dashboard variants are now shipped and aligned across code, spec, docs, and skill guidance, ranked by practical value:

1. `default-flow-metrics.yaml` for resolution speed, bottlenecks, first response, and intake monitoring.
2. `default-work-item-breakdown.yaml` for assignee/component/label pivots.
3. `default-workload-reporting.yaml` for effort-oriented dashboards.
4. `default-cross-sectional.yaml` for mixed-filter breadth dashboards.
5. **Release-specific dashboards** for version tracking:
   - `v3-3-54-release-dashboard.yaml` — v3.3.54 release scope
   - `v3-3-55-release-dashboard.yaml` — v3.3.55 release scope
   - `v3-3-56-release-dashboard.yaml` — v3.3.56 release scope
6. Average Number of Times in Status and Voted Work items remain documented but unbundled niche options.

### Release Dashboard Convention

Release dashboards follow naming pattern `v{Major}-{Minor}-{Patch}-release-dashboard.yaml` and include:
- Priority, Status, Issue Type, Assignee distributions
- Resolution Time, Label Breakdown, Recently Created charts
- Work Items table with extended columns (issuetype, issuekey, summary, priority, assignee, status, updated)

Each release dashboard targets issues with the corresponding `Feature_X.X.X` label via JQL filter (e.g., `labels ~ "Feature_3.3.54"`).

## Open Questions

- Should layout files live in `jira-skill/src/jira_skill/dashboard/layouts/` or in a workspace-level config directory? Decision: `jira-skill/src/jira_skill/dashboard/layouts/` bundled with the package, so the layout is always available when the package is installed.
- Should we deprecate the `jira-daily-reports dashboard` command? Decision: no deprecation for now; mark it as using the internal layout reference and point new use cases to `jira-skill dashboard`.
