## MODIFIED Requirements

### Requirement: GitLab MR Note Posting
The system SHALL post a GitLab MR note containing the full impact analysis rendered as GitLab markdown on every non-update MR event (action ∈ {open, reopen, merge}). The note SHALL be idempotent: on re-run, the existing TDT note SHALL be edited in place rather than appended. The idempotency marker SHALL be the HTML-comment string `<!-- tdt-impact-analysis -->` (defined in `tdt_core.clients.gitlab_mr.NOTE_PREFIX`). The marker is prepended by `jira_skill.impact.gitlab_note.post_gitlab_note` before calling `upsert_mr_note` — it is NOT present in the output of `build_gitlab_note`. Idempotency detection uses substring match (`NOTE_PREFIX in body`). The GitLab posting SHALL be fire-and-forget and SHALL NOT block or delay the webhook response. Failures SHALL be logged but SHALL NOT propagate as errors to the caller.

The Jira comment posting remains merge-only per SPEC-IA-7.

#### Scenario: open event posts GitLab note
- **WHEN** an MR transitions to opened
- **THEN** the system SHALL post the impact analysis as a GitLab MR note
- **AND** the system SHALL NOT post a Jira comment (no merged commit SHA available yet)
- **AND** `triggered_by` SHALL be set to `"webhook-open"`

#### Scenario: reopen event posts GitLab note
- **WHEN** an MR is reopened
- **THEN** the system SHALL post the impact analysis as a GitLab MR note
- **AND** `triggered_by` SHALL be set to `"webhook-reopen"`

#### Scenario: merge event posts both
- **WHEN** an MR is merged
- **THEN** the system SHALL post the impact analysis as a GitLab MR note
- **AND** `triggered_by` SHALL be set to `"webhook-merge"`
- **AND** the system SHALL post an idempotent Jira ADF comment on the matched ticket

#### Scenario: update event is skipped
- **WHEN** `action = "update"`
- **THEN** the system SHALL skip both GitLab and Jira posting entirely
- **AND** the debouncer SHALL coalesce rapid update bursts (only the latest fires)

#### Scenario: idempotency prevents duplicates
- **WHEN** the same MR fires a second time with the same action
- **THEN** the system SHALL edit the existing GitLab MR note in place
- **AND** SHALL edit the existing Jira comment in place (already implemented)

#### Scenario: marker is an HTML comment
- **WHEN** the GitLab note is posted
- **THEN** the body SHALL begin with `<!-- tdt-impact-analysis -->\n` (added by `post_gitlab_note`, not by `build_gitlab_note`)
- **AND** the body SHALL NOT contain the legacy visible prefix `⚠️ Impact Analysis — MR !` as a marker (legacy notes are migrated in place by `webhook_receiver.impact_marker_migration`)

### Requirement: GitLab Markdown Comment Format
The GitLab MR note body MUST be GitLab Flavored Markdown produced by `build_gitlab_note` in `jira_skill.impact.gitlab_note`. The function reads `ImpactReport` pydantic model fields directly and formats them as markdown — it is NOT an ADF-to-markdown converter. The note MUST contain the same information sections as the Jira ADF comment (staleness warning, title, stats, affected features, at-risk modules, changed files, recommended tests, coverage gaps, unmapped paths, raw report link) but rendered as GitLab markdown. The idempotency marker SHALL NOT be present in the output of `build_gitlab_note` — it is prepended by `post_gitlab_note` before calling `upsert_mr_note`. The title SHALL use `###` heading level and SHALL include the " merged" suffix when `triggered_by == "webhook-merge"`, omitting it for `webhook-open` and `webhook-reopen`.

#### Scenario: Markdown section structure
- **WHEN** the note body is rendered from an `ImpactReport`
- **THEN** the body SHALL contain a `### Impact Analysis — MR !{mr_iid}` title line
- **AND** a stats line `"Analyzed {n} changed files across {m} features in {ms}ms. Cache: {hits} hits / {misses} misses."`
- **AND** an `**Affected Features:**` line listing `resolved_features`
- **AND** an `**At-Risk Modules:**` line listing `at_risk_modules` (or `none`)
- **AND** a `### Changed Files ({n})` section rendering each `ChangedFileModel` as `- \`{path}\` ({feature_tags}, +{lines_added}/-{lines_removed}, symbols: {symbols_extracted})`
- **AND** a `### Recommended Tests ({n})` section rendering each `TestFileModel` as `- \`{path}\` ({test_type.value}) — covers {covers_features}`
- **AND** a `**Coverage Gaps:**` line when `coverage_gaps` is non-empty
- **AND** a `**Unmapped Paths ({n}):**` line when `unmapped_paths` is non-empty
- **AND** a `[View raw impact report](file://{path})` link when `raw_report_path` is provided
- **AND** empty optional sections SHALL be omitted entirely

#### Scenario: Staleness warning is included
- **WHEN** `gitnexus_index_stale == True`
- **THEN** the note SHALL prepend a bold warning: "**⚠️ GitNexus index may be stale** — N symbols not found. Run `gitnexus analyze` to refresh."

## ADDED Requirements

### Requirement: Legacy Impact Marker Migration (webhook-receiver)
The system SHALL provide `webhook_receiver.impact_marker_migration.migrate_legacy_impact_note(...)` that prepends the new HTML-comment marker to any existing GitLab MR note whose body starts with the legacy visible prefix `⚠️ Impact Analysis — MR !`. The function MUST be invoked from `webhook_receiver.impact.run_gitlab_note_workflow` before each call to `post_gitlab_note`. The function SHALL be gated by a state file at `~/.tdt/state/webhook-receiver/impact-marker-migrated.json` (format `{"migrated": ["<project_path>!<mr_iid>"]}`) — once a key exists, subsequent calls for the same MR SHALL be no-ops.

#### Scenario: Migration prepends marker to legacy note
- **WHEN** `migrate_legacy_impact_note(project_path, mr_iid, poster)` is called
- **AND** the MR has a note whose body starts with `⚠️ Impact Analysis — MR !`
- **AND** that body does not contain `<!-- tdt-impact-analysis -->`
- **AND** the state file does not yet contain the key `{project_path}!{mr_iid}`
- **THEN** it SHALL prepend `<!-- tdt-impact-analysis -->\n` to that note's body
- **AND** it SHALL call `note.save()` on the updated note
- **AND** it SHALL add `{project_path}!{mr_iid}` to the state file
- **AND** it SHALL log `impact_marker_migration_done` with `project_path`, `mr_iid`, `note_id`

#### Scenario: Migration is a no-op when already migrated
- **WHEN** `migrate_legacy_impact_note` is called
- **AND** the state file already contains the key `{project_path}!{mr_iid}`
- **THEN** it SHALL return `False` without calling the GitLab API

#### Scenario: Migration is a no-op when note already has new marker
- **WHEN** `migrate_legacy_impact_note` is called
- **AND** the MR has a note starting with the legacy prefix
- **AND** that note's body already contains `<!-- tdt-impact-analysis -->`
- **THEN** it SHALL skip that note (no save)

#### Scenario: Migration logs and returns False on API failure
- **WHEN** `migrate_legacy_impact_note` is called
- **AND** any GitLab API call raises
- **THEN** it SHALL log `impact_marker_migration_failed` with the failure stage
- **AND** it SHALL return `False`
- **AND** it SHALL NOT re-raise the exception