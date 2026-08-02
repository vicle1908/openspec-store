# Jira dashboard automation tasks

## 1. Shared dashboard module in `jira-skill`

- [x] 1.1 Create `jira_skill/dashboard/` package with layout models, validation helpers, and dashboard lifecycle functions that wrap `PatchedJira` dashboard APIs
- [x] 1.2 Add bundled YAML layout support for a baseline filter-backed dashboard and validate required gadget fields at load time
- [x] 1.3 Add default-filter resolution so the baseline dashboard workflow works without an explicit `--filter-id`
- [x] 1.4 Reuse the existing `jira-skill` default-filter precedence chain and add a single-dashboard guard that errors when multiple default filters are configured
- [x] 1.5 Add unit tests for layout parsing, exact-name dashboard resolution, gadget placement planning, property payload generation, and ambiguous-default-filter failure

## 2. CLI command surface

- [x] 2.1 Add a `dashboard` Typer command group to `jira_skill/cli.py` with `create`, `rebuild`, `list`, `validate`, and `dry-run` workflows
- [x] 2.2 Implement `--name`, `--dashboard-id`, `--filter-id`, `--layout`, and `--dry-run` flags with clear operator-facing error messages
- [x] 2.3 Ensure dashboard create/update defaults to logged-in view sharing and does not grant authenticated edit access unless explicit edit permissions are provided
- [x] 2.4 Add CLI tests covering create, rebuild, validate, dry-run, invalid-layout failure paths, ambiguous-default-filter failure, and the default-sharing behavior

## 3. Validation and reliability reporting

- [x] 3.1 Implement read-back validation using dashboard item `config` properties for placed gadgets and report mismatches per gadget
- [x] 3.2 Add explicit warnings for unsupported or incompletely persisted gadget properties and preserve partial-success summaries
- [x] 3.3 Verify the implementation against `psplit.atlassian.net` with a real saved filter and capture the supported gadget-property mapping in docs/tests
- [x] 3.4 Add a regression check for Jira Cloud dashboard `PUT` semantics so permission blocks are treated as explicit state, not merge-patched state

## 4. Skill and workflow guidance

- [x] 4.1 Create or update a `.agents` Jira dashboard skill documenting supported commands, approved gadget sets, API limits, default filter behavior, and validation workflow
- [x] 4.2 Update `jira-daily-reports` dashboard docs to reference `jira-skill` as the canonical entry point for new dashboard automation work while retaining the existing command as a specialized layout builder
- [x] 4.3 Add example operator workflows for creating a bug dashboard from the default filter and from explicit filter `15269`, then validating the resulting gadget configuration

## 5. Verification and rollout

- [x] 5.1 Run `uv run pytest` for `jira-skill` dashboard-related tests and `ruff`/`mypy` on touched files
- [x] 5.2 Manually validate a created dashboard in Jira Cloud, confirm gadget configuration read-back output, and confirm logged-in view sharing is applied by default
- [x] 5.3 Prepare rollback guidance: remove created gadgets or rebuild the dashboard from a known-good layout if validation fails

## 6. Native variant dashboard extension (multi-filter, custom-field, workload)

- [x] 6.1 Extend the layout YAML schema with an optional `filterId` field per gadget entry and update `GadgetPlacement` dataclass, `_parse_gadget`, and layout tests
- [x] 6.2 Update `_build_gadget_config` and `_expected_config_for_gadget` to accept a per-gadget override filter ID and validate against the correct filter item
- [x] 6.3 Add a `filterId`-aware validation path in `validate_dashboard` so mixed-filter dashboards report the correct per-gadget configuration contract
- [x] 6.4 Create a documented Workload Pie Chart example in `default-workload-reporting.yaml` layout with effort-specific properties (`issuetimetype: timespent`, `statistictype: labels`) alongside existing native gadget types
- [x] 6.5 Create one cross-sectional multi-filter example layout `default-cross-sectional.yaml` using 2-3 saved filters across Pie Charts and Work Item Statistics gadgets, without trend time-series gadgets
- [x] 6.6 Update the validation engine to treat Workload Pie Chart as a recognized supported gadget and surface clean error messages when the filter does not expose the required time-tracking fields
- [x] 6.7 Update `_expected_config_for_gadget` to recognize Workload Pie Chart by its URI pattern and validate `projectOrFilterId`, `issuetimetype`, and `statistictype` fields
- [x] 6.8 Add unit tests for per-gadget filter override, Workload Pie Chart placement and config validation, custom-field pivot validation, and cross-sectional multi-filter layout
- [x] 6.9 Run live verification on a Jira site with a Workload Pie Chart and a multi-filter cross-sectional dashboard, confirm v3 config persistence, and capture any breakage in docs/tests
- [x] 6.10 Update the jira-dashboard skill and spec docs to point to the new layout examples and describe when to use flow/work-item breakdown first, with workload and cross-sectional variants as secondary options
- [x] 6.11 Create default-work-item-breakdown.yaml layout with six gadgets
- [x] 6.12 Probe live gadget-directory support for Resolution Time, Average Time in Status, Time to First Response, Recently Created Chart, Average Number of Times in Status, and Voted Work items
- [x] 6.13 Create default-flow-metrics.yaml layout with four gadgets
- [x] 6.14 Update service validation to recognize the live flow gadget URIs and titles
- [x] 6.15 Add unit tests for the flow-metrics layout and gadget config readback
