# impact-shared-primitive Specification

## Purpose
TBD - created by archiving change impact-sheet-integration. Update Purpose after archive.
## Requirements
### Requirement: analyze_mr_to_report shared primitive
The system SHALL expose a single async function `analyze_mr_to_report(project_path, mr_iid, mr_url, triggered_by, ticket_key=None, state_dir=None, cache=None, *, payload_metadata=None) -> ImpactReport | None` in `jira_skill.impact.impact_report`. Both webhook-receiver's `_run_pipeline` and `jira-skill`'s `impact mr` CLI command MUST delegate to this function. The function MUST encapsulate the five-step pipeline: cache lookup → fetch MR changes → fetch MR metadata + SHA resolution → `analyze_diff` → `build_impact_report` → cache write.

#### Scenario: Cache hit short-circuits the pipeline
- **WHEN** `RawReportCache.get()` returns a fresh `CachedImpactReport` for the same `(project_path, mr_iid, commit_sha)`
- **THEN** `analyze_mr_to_report` MUST return the cached `ImpactReport`
- **AND** MUST NOT call `fetch_mr_changes`, `fetch_mr_metadata`, or `analyze_diff`

#### Scenario: Cache miss runs the full pipeline
- **WHEN** no fresh cached report exists
- **THEN** `analyze_mr_to_report` MUST fetch the diff, run `analyze_diff`, build the report, write it to the cache, and return it
- **AND** MUST NOT raise if the cache write itself fails (logged and ignored)

#### Scenario: Empty changes return None
- **WHEN** `fetch_mr_changes` returns an empty list
- **THEN** `analyze_mr_to_report` MUST return `None`
- **AND** MUST NOT call `analyze_diff`

### Requirement: SHA resolution fallback order
`analyze_mr_to_report` MUST resolve the commit SHA in this order: `meta.merge_commit_sha`, `meta.squash_commit_sha`, `meta.sha`, then `payload_metadata["last_commit_sha"]`, then `payload_metadata["merge_commit_sha"]`, finally the literal string `"unknown"`. The fallback is required so webhook-receiver can pass payload-derived SHAs as a safety net when GitLab metadata is incomplete.

#### Scenario: Webhook payload fallback works
- **WHEN** `meta.merge_commit_sha` is empty and `payload_metadata["merge_commit_sha"]` is `"abc123"`
- **THEN** the function MUST use `"abc123"` as the SHA passed to `analyze_diff`
- **AND** MUST use `"abc123"[:12]` as the cache filename suffix

#### Scenario: All fallbacks empty
- **WHEN** all SHA sources are empty
- **THEN** the function MUST use the literal string `"unknown"`
- **AND** the cache filename MUST be `<mr_iid>-unknown.json`

### Requirement: Triggered_by provenance
The `triggered_by` argument MUST be persisted into `ImpactReport.triggered_by` so downstream consumers can distinguish the analysis origin. Valid values include: `"webhook"`, `"webhook-open"`, `"webhook-reopen"`, `"webhook-merge"`, `"cli"`, `"sheet-enrichment"`.

#### Scenario: Webhook pipeline marks origin
- **WHEN** webhook-receiver calls `analyze_mr_to_report(..., triggered_by="webhook")`
- **THEN** the returned `ImpactReport.triggered_by` MUST equal `"webhook"`

#### Scenario: Sheet enrichment origin
- **WHEN** `ImpactEnricher` calls `analyze_mr_to_report(..., triggered_by="sheet-enrichment")`
- **THEN** the returned `ImpactReport.triggered_by` MUST equal `"sheet-enrichment"`

