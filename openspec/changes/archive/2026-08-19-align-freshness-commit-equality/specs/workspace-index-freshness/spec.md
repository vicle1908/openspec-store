## MODIFIED Requirements

### Requirement: Observable refresh status

The workspace SHALL provide a status command and bounded timestamped logs. For GitNexus and Graphify, the primary freshness classification SHALL be derived by comparing the recorded indexed revision against the current repository HEAD. Timestamp recency SHALL NOT be used as the primary freshness signal.

#### Scenario: Human status is requested

- **WHEN** a developer runs `knowledge-status.sh`
- **THEN** it SHALL list every inventoried repository and eligible worktree
- **AND** it SHALL report provider, recorded indexed revision, current HEAD, freshness classification, last refresh, dirty state, and watcher state
- **AND** freshness classification SHALL be **FRESH** only when the recorded indexed revision equals the current HEAD

#### Scenario: Machine status is requested

- **WHEN** a developer runs `knowledge-status.sh --json`
- **THEN** it SHALL emit valid bounded JSON
- **AND** each provider row SHALL include `indexedSha`, `headSha`, `freshness`, and `freshnessRule` fields
- **AND** `freshnessRule` SHALL be `commit_equality` when classification is derived from SHA comparison, or `missing_recorded_revision` when no recorded revision was available
- **AND** freshness SHALL be **FRESH** only when `indexedSha == headSha`

#### Scenario: Refresh log is inspected

- **WHEN** a developer inspects the refresh log
- **THEN** entries SHALL include timestamp, canonical target, provider, status, duration, target revision, and indexed revision where available
- **AND** logs SHALL be rotated to a bounded size
