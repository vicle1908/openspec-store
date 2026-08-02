## ADDED Requirements

### Requirement: ImpactSnapshot field on TicketIntelligenceBundle
The `TicketIntelligenceBundle` model MUST expose an optional `impact: ImpactSnapshot | None = None` field. When `JIRA_SKILL_IMPACT_IN_SHEETS=true` (default) the field SHALL be populated by `ImpactEnricher.enrich_bundle()` inside `analyze_snapshot()`. When the flag is `false`, the field SHALL remain `None`. The bundle version SHALL advance from `v1.0` to `v1.1` to mark the additive extension; v1.0 bundles MUST remain valid when deserialized (impact renders as `None`).

#### Scenario: Bundle v1.1 carries an ImpactSnapshot
- **WHEN** `analyze_snapshot()` is called with `enrich_impact=True` against a Jira filter containing at least one merged-MR-bearing ticket
- **THEN** the returned `TicketIntelligenceBundle` MUST contain `meta.version == "v1.1"`
- **AND** `bundle.impact` MUST NOT be `None`
- **AND** `bundle.impact.by_issue_key` MUST contain a row for each Jira ticket that has at least one MR resolved

#### Scenario: Bundle v1.0 deserializes unchanged
- **WHEN** a serialized v1.0 bundle JSON is loaded via `TicketIntelligenceBundle.from_json()`
- **THEN** `bundle.impact` MUST default to `None`
- **AND** all other v1.0 fields MUST be present with their original values

### Requirement: ImpactRow shape
Each entry in `ImpactSnapshot.by_issue_key` MUST be an `ImpactRow` containing: `issue_key: str`, `mr_links: list[str]`, `last_commit_sha: str | None`, `files_changed_count: int`, `at_risk_modules: list[str]`, `impact_status: Literal["ok", "stale", "unavailable", "no_mrs"]`, and `extras: dict[str, Any]`. The `extras` field MUST be a forward-compatible escape hatch; consumers MUST treat unknown keys as opaque.

#### Scenario: ImpactRow populated from a merged MR
- **WHEN** the resolver finds a merged MR with `merge_commit_sha`, `url`, and the impact pipeline produces a report with 3 changed files and at-risk modules `["payment-core"]`
- **THEN** the row MUST contain `mr_links=["<url>"]`, `last_commit_sha="<sha>"`, `files_changed_count=3`, `at_risk_modules=["payment-core"]`, `impact_status="ok"`

#### Scenario: ImpactRow with no resolved MRs
- **WHEN** the resolver returns no merged MRs for a Jira ticket key
- **THEN** the row MUST contain `mr_links=[]`, `files_changed_count=0`, `at_risk_modules=[]`, `impact_status="no_mrs"`

#### Scenario: ImpactRow with GitLab unreachable
- **WHEN** `analyze_mr_to_report()` raises a transport exception while resolving an MR
- **THEN** the row MUST contain `impact_status="unavailable"`
- **AND** the row MUST still be present in `by_issue_key` so the bundle is complete

### Requirement: Classification tab impact columns
The Classification tab MUST include three new columns appended to the existing 21-column layout: `MR Links`, `Files Changed`, `At-Risk Modules`. The columns MUST be sourced from `bundle.impact.by_issue_key[<issue_key>]` when present. When `bundle.impact is None` or the row is missing for a given issue, the three cells MUST render as empty strings. The total column count SHALL be 24, and `CLASSIFICATION_COLUMNS` MUST be the single source of truth for header ordering.

#### Scenario: Classification tab renders all 24 columns
- **WHEN** `SheetsWriter.write_bundle()` is called against a v1.1 bundle with impact populated
- **THEN** the first row of the Classification tab MUST equal `CLASSIFICATION_COLUMNS` (length 24)
- **AND** the last three headers MUST be `"MR Links"`, `"Files Changed"`, `"At-Risk Modules"`

#### Scenario: Empty impact cells when bundle.impact is None
- **WHEN** `bundle.impact is None` (e.g. flag disabled or enrichment skipped)
- **THEN** each Classification row's last three cells MUST be empty strings
- **AND** no error MUST be raised

### Requirement: Summary tab Impact Summary section
The Summary tab MUST include an `--- Impact Summary ---` section when `bundle.impact is not None`. The section MUST render: `Issues with MRs`, `Total MRs Analyzed`, `Total Files Changed`, `At-Risk Modules (unique across filter)`, `Unavailable`, and `Cache Hits / Misses` metrics computed via `ImpactCascadeSummary.build()`.

#### Scenario: Cascade Summary section rendered
- **WHEN** `bundle.impact` is populated with rows that have a mix of `ok` and `no_mrs` statuses
- **THEN** the Summary tab MUST contain a section header row `["--- Impact Summary ---", ""]`
- **AND** MUST render the six metric rows derived from `ImpactCascadeSummary.build()`
- **AND** the `At-Risk Modules` value MUST be the deduplicated sorted union of `at_risk_modules` across all rows

#### Scenario: Cascade Summary section absent when impact is None
- **WHEN** `bundle.impact is None`
- **THEN** the Summary tab MUST NOT contain the `--- Impact Summary ---` section
- **AND** the Summary tab MUST render only the existing pre-impact rows

### Requirement: analyze_snapshot enrichment wiring
`analyze_snapshot()` MUST accept an `enrich_impact: bool = True` parameter. When `True`, it SHALL construct an `ImpactEnricher` and run `enrich_bundle()` after the deterministic bundle construction completes. The enricher MUST NOT raise into the caller; any per-ticket or pipeline failure MUST be logged and produce `bundle.impact = None`.

#### Scenario: Default-on enrichment
- **WHEN** `analyze_snapshot(snapshot)` is called without `enrich_impact`
- **THEN** the default MUST be `True`
- **AND** `bundle.impact` MUST be populated when the Jira/GitLab APIs are reachable

#### Scenario: Opt-out via parameter
- **WHEN** `analyze_snapshot(snapshot, enrich_impact=False)`
- **THEN** `bundle.impact` MUST be `None`
- **AND** the existing 993 tests for `analyze_snapshot` MUST continue to pass without modification

#### Scenario: Enrichment failure is non-fatal
- **WHEN** `ImpactEnricher.enrich_bundle()` raises an unexpected exception
- **THEN** `analyze_snapshot()` MUST log the exception and return the bundle with `bundle.impact = None`
- **AND** MUST NOT propagate the exception to the caller