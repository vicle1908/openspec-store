# jira-catalog-collection-and-joiner Specification

## Purpose

Define how the `jira-daily-reports.catalog` package collects usage data from a JQL query against the configured Jira projects, pulls schema metadata from Jira's REST v3 endpoints, and joins the two into a single `CatalogRow` shape. The join is the contract that turns "what does Jira know about?" and "what do tickets actually use?" into a row the team can read.

## Requirements

## ADDED Requirements

### Requirement: The collector MUST use tdt_core.clients.jira for all Jira calls

The collector SHALL obtain its Jira client from `JiraClientFactory.from_env()` (which returns a `PatchedJira` from `tdt_core.clients.jira`). The collector MUST NOT instantiate `atlassian.Jira` directly, MUST NOT use `requests`, and MUST NOT shell out to `acli`. All Jira calls MUST target API version v3.

#### Scenario: The collector builds its client from env

- **WHEN** the collector module is imported
- **THEN** it MUST resolve the client via `JiraClientFactory.from_env()` (which calls `tdt_core.env.load_tdt_env()` and reads `ATLASSIAN_SITE`, `ATLASSIAN_EMAIL`, `ATLASSIAN_ACCESS_TOKEN`)
- **AND** the resolved client SHALL be a `PatchedJira` instance.

### Requirement: The collector MUST page through JQL results using the cursor-paginated helper

The collector SHALL call `jira_daily_reports.client._jql_paginated` (not `jira.jql` directly) to enumerate tickets. The JQL MUST be `project IN ({projects}) AND updated >= -{lookback}d` where `{projects}` is the comma-joined value of `JIRA_CATALOG_PROJECTS` and `{lookback}` is `JIRA_CATALOG_LOOKBACK_DAYS` (default 90). The `fields` argument MUST be a **comma-separated string** (e.g. `"labels,priority,resolution,components,fixVersions,issuetype"` plus the comma-joined IDs from `JIRA_CATALOG_TRACKED_FIELDS`). The collector MUST NOT pass `fields="*all"`.

#### Scenario: The JQL fetches only the lookback window

- **WHEN** `JIRA_CATALOG_LOOKBACK_DAYS=90` and `JIRA_CATALOG_PROJECTS="AM,SR,PWM"`
- **THEN** the collector SHALL call `_jql_paginated` with `jql="project IN (AM,SR,PWM) AND updated >= -90d"`
- **AND** SHALL pass `fields="labels,priority,resolution,components,fixVersions,issuetype"` (comma-separated string)
- **AND** SHALL NOT pass `fields="*all"`.

#### Scenario: Pagination loops on nextPageToken until isLast

- **WHEN** the JQL response carries `nextPageToken` and `isLast: false`
- **THEN** `_jql_paginated` SHALL make a follow-up call passing the token
- **AND** SHALL continue until `isLast: true` or a defensive empty-page guard fires.

### Requirement: The collector MUST pull metadata for all seven catalog kinds from Jira REST v3

The collector MUST call, at minimum, the following endpoints (in this order, with failures logged but non-fatal where noted):

| Kind          | Endpoint                                       | Required |
|---------------|------------------------------------------------|----------|
| Custom Field  | `GET /rest/api/3/field` (filter by `custom:true`) | yes      |
| Label         | aggregate from the same JQL response (no separate endpoint needed) | yes |
| Priority      | `GET /rest/api/3/priority/search`              | yes      |
| Resolution    | `GET /rest/api/3/resolution/search`            | yes      |
| Component     | `GET /rest/api/3/project/{key}/component` (one call per project) | yes |
| Fix Version   | `GET /rest/api/3/project/{key}/version` (one call per project) | yes |
| Issue Type    | `GET /rest/api/3/issuetype/project?projectId={id}` (one call per project) | yes |

If a metadata call fails for a project, the collector SHALL log a `catalog.metadata_warning` and continue with the other kinds; the snapshot SHALL carry a `warnings` list so the CLI can surface partial failures.

#### Scenario: A metadata call for one project fails

- **WHEN** `GET /rest/api/3/project/SR/component` returns HTTP 500
- **THEN** the collector MUST append `catalog.metadata_warning: SR/component HTTP 500` to the snapshot's `warnings` list
- **AND** MUST continue with the other six kinds and the other projects.

#### Scenario: Custom fields are filtered to `custom:true`

- **WHEN** the collector calls `GET /rest/api/3/field`
- **THEN** it MUST drop every entry where `custom != true` (i.e. built-in system fields are not included in the catalog)
- **AND** the resulting list SHALL be the source for the `Custom Field` kind in the joiner.

### Requirement: The joiner MUST produce exactly one row per (Kind, Name) tuple

The joiner SHALL consume the collector's `usage` (per-ticket observations) and `metadata` (per-kind schema info) snapshots, plus the `JIRA_CATALOG_TRACKED_FIELDS` list, and produce a `CatalogSnapshot` containing a `list[CatalogRow]`. The joiner MUST emit one row for every item that is in EITHER the usage or the metadata set, and MUST mark rows that appear in only one source.

Each `CatalogRow` MUST carry:
- `kind: str` — one of the seven allowed `Kind` values
- `name: str` — the Jira display name
- `field_id: str` — for custom fields only
- `type: str` — Jira schema type, where available
- `allowed_values: list[str]` — for select-style fields
- `usage_count: int` — distinct ticket count from the lookback window
- `first_seen: datetime | None` — earliest ticket `updated` carrying the item
- `last_seen: datetime | None` — latest ticket `updated` carrying the item
- `jira_updated: datetime | None` — metadata-side last-update timestamp
- `status: str` — `Active`, `Stale`, or `Removed` per the data-model spec
- `source_projects: list[str]` — distinct project keys
- `source: str` — one of `usage`, `metadata`, `both`
- `issue_keys: tuple[str, ...]` — sorted, deduplicated issue keys for Label and tracked Custom Field rows; empty tuple for all other rows

#### Scenario: A label is used but not in the metadata feed

- **WHEN** the JQL response includes 12 tickets that carry the label `mobile-ios` in the lookback window
- **AND** the metadata feed has no row for that label
- **THEN** the joiner SHALL emit exactly one `CatalogRow(kind="Label", name="mobile-ios", usage_count=12, source="usage")`
- **AND** the row SHALL appear in the catalog tab
- **AND** the row's `issue_keys` SHALL be the sorted, deduplicated tuple of those 12 ticket keys.

#### Scenario: A custom field exists in metadata but no ticket uses it in the window

- **WHEN** `GET /rest/api/3/field` returns a custom field named `Legacy Severity` with `customfield_12345`
- **AND** no ticket in the lookback window uses that field
- **THEN** the joiner SHALL emit exactly one `CatalogRow(kind="Custom Field", name="Legacy Severity", field_id="customfield_12345", usage_count=0, source="metadata")`
- **AND** the row SHALL appear in the catalog tab with `Status = Removed` and `Usage Count = 0`
- **AND** the row's `issue_keys` SHALL be the empty tuple (untracked Custom Field rows do not record issue keys).

### Requirement: The collector MUST record the issue key for every label and tracked-custom-field observation

For every issue returned by the JQL lookback, the collector MUST record the issue's `key` (e.g. `PUB-42`) into the per-label and per-tracked-custom-field usage buckets. The `key` is always present at the top level of the JQL response (it is not a `fields` property). When the same `(label, issue_key)` pair appears multiple times (e.g. an issue that carries the label in two ways, or a JQL pagination artifact), the collector MUST deduplicate within the row by using a `frozenset[str]` accumulator.

The collector MUST NOT record issue keys for system kinds (Priority, Resolution, Component, Fix Version, Issue Type) or for untracked Custom Fields — those buckets are unchanged.

#### Scenario: A label appears on three tickets in the lookback window

- **WHEN** the JQL response includes issues `PUB-42`, `PUB-43`, and `PUB-51` that all carry the label `mobile-ios`
- **THEN** the collector MUST record an entry in `usage.labels["mobile-ios"]` with `count = 3` AND `issue_keys` containing the three keys (deduplicated)
- **AND** the joiner MUST emit a Label row with `issue_keys = ("PUB-42", "PUB-43", "PUB-51")` (sorted lexicographically).

#### Scenario: A tracked custom field appears on two tickets

- **WHEN** `JIRA_CATALOG_TRACKED_FIELDS="customfield_10016"` AND the JQL response includes issues `PUB-7` and `PUB-8` that both have a value for `customfield_10016`
- **THEN** the collector MUST record `usage.custom_fields["customfield_10016"].issue_keys` containing `{"PUB-7", "PUB-8"}`
- **AND** the joiner MUST emit a Custom Field row with `issue_keys = ("PUB-7", "PUB-8")`.

