## ADDED Requirements

### Requirement: Hermes cron freshness reporting SHALL be read-only and inventory-driven

Any Hermes cron job that reports workspace index freshness SHALL consume the approved inventory and the existing status/reporting infrastructure. It SHALL NOT invoke provider mutations (`graphify update`, `gitnexus analyze`) or duplicate the canonical LaunchAgent refresh path.

#### Scenario: Cron freshness report uses approved inventory

- **WHEN** a Hermes cron job reports workspace index freshness
- **THEN** it SHALL consume the reviewed inventory from `knowledge-refresh-inventory.tsv`
- **AND** it SHALL use `knowledge-status.sh --json` or equivalent status infrastructure
- **AND** it SHALL NOT maintain a separate hardcoded repository list

#### Scenario: Cron freshness report does not mutate indexes

- **WHEN** a Hermes cron job reports workspace index freshness
- **THEN** it SHALL NOT invoke `graphify update`, `gitnexus analyze`, or any other index-mutating command
- **AND** index mutation is owned by the canonical central refresh mechanism, invoked by the LaunchAgent (`com.developer.index-refresh`) and approved post-merge dispatchers

#### Scenario: Provider version mismatch is reported honestly

- **WHEN** the installed provider version differs from the spec-pinned version
- **THEN** the freshness report SHALL include both the installed version and the pinned version
- **AND** it SHALL NOT treat the mismatch as a report failure
- **AND** it SHALL NOT silently upgrade or downgrade the provider

#### Scenario: GitNexus timeout uses two independent fields

- **WHEN** the canonical refresh log shows a GitNexus analysis timeout
- **THEN** the freshness report SHALL set `freshness` based on indexed SHA vs HEAD (may be STALE)
- **AND** it SHALL set `operation_status: TIMEOUT`
**AND** `operation_status` SHALL be derived from an `operation_status` field in the canonical `knowledge-status.sh --json` output (extending the canonical status infrastructure)
- **AND** it SHALL NOT treat the timeout as a report failure
- **AND** it SHALL NOT prescribe manual re-indexing with increased timeout (timeout changes are out of scope; the canonical spec requires bounded five-minute execution)

#### Scenario: Dirty-tree skip uses two independent fields

- **WHEN** the canonical refresh log shows a repo skipped due to uncommitted changes
- **THEN** the freshness report SHALL set `freshness` based on indexed SHA vs HEAD (may be STALE)
- **AND** it SHALL set `operation_status: DIRTY_SKIP`
**AND** `operation_status` SHALL be derived from an `operation_status` field in the canonical `knowledge-status.sh --json` output
- **AND** it SHALL NOT treat dirty-tree skip as a refresh failure

#### Scenario: Freshness and operation_status are independent

- **WHEN** a repo has indexed SHA matching HEAD but the last operation timed out
- **THEN** `freshness` SHALL be `FRESH`
- **AND** `operation_status` SHALL be `TIMEOUT`
- **AND** these two fields SHALL NOT conflict

#### Scenario: Canonical mutation path includes both LaunchAgent and post-merge dispatchers

- **WHEN** the freshness report describes the mutation ownership
- **THEN** it SHALL identify both the nightly LaunchAgent (`com.developer.index-refresh`) and the workspace-managed post-merge dispatchers as the canonical mutation owners
- **AND** it SHALL NOT imply that only the LaunchAgent performs mutations
