## MODIFIED Requirements

### Requirement: GitLab MR Note Writer (tdt-core)
The system SHALL provide `find_mr_notes` and `upsert_mr_note` in `tdt_core.clients.gitlab_mr` using `GitlabClientFactory.from_env()`. The idempotency marker SHALL be `NOTE_PREFIX = "<!-- tdt-impact-analysis -->"` (an HTML-comment marker, codescan-style — NOT a visible prefix). Idempotency detection SHALL use substring match (`prefix in body`) — NOT prefix match (`startswith`). This aligns with the `GitLabReviewPoster` marker convention used by the codescan reviewer in `ai-review`. `post_gitlab_note` is responsible for prepending the marker to the body before calling `upsert_mr_note`.

The visible Unicode prefix `⚠️ Impact Analysis — MR !` SHALL NOT be used for any new notes (legacy notes with that prefix are migrated in place via `webhook_receiver.impact_marker_migration`).

#### Scenario: find_mr_notes returns notes containing the marker
- **WHEN** `find_mr_notes(project_path, mr_iid)` is called
- **THEN** it SHALL call `GET /projects/:id/merge_requests/:iid/notes`
- **AND** it SHALL return only notes where `NOTE_PREFIX in body` (substring match)
- **AND** each returned dict SHALL contain `id` (int), `body` (str), and `author` (str)

#### Scenario: upsert_mr_note creates when note_id is None
- **WHEN** `upsert_mr_note(project_path, mr_iid, body, note_id=None)` is called
- **THEN** it SHALL call `POST /projects/:id/merge_requests/:iid/notes` with `{"body": body}`
- **AND** it SHALL return the created note's `id`

#### Scenario: upsert_mr_note edits when note_id is provided
- **WHEN** `upsert_mr_note(project_path, mr_iid, body, note_id=55)` is called
- **THEN** it SHALL call `GET /projects/:id/merge_requests/:iid/notes/55`
- **AND** it SHALL set `note.body = body` and call `note.save()`
- **AND** it SHALL return the updated note's `id`

#### Scenario: Note with HTML-comment marker is located by substring
- **WHEN** an MR has a note whose body starts with `<!-- tdt-impact-analysis -->`
- **AND** `find_mr_notes(project_path, mr_iid)` is called
- **THEN** that note SHALL be returned (substring `<!-- tdt-impact-analysis -->` matches `body`)

### Requirement: GitLab Markdown Builder (jira-skill)
The system SHALL provide `build_gitlab_note(report: ImpactReport, raw_report_path: Path | None = None) -> str` in `jira_skill.impact.gitlab_note`. The function MUST render an `ImpactReport` as GitLab Flavored Markdown. It reads `ImpactReport` fields directly — it is NOT an ADF-to-markdown converter. The body SHALL NOT contain the idempotency marker (that is prepended by `post_gitlab_note` before calling `upsert_mr_note`). The title SHALL use `###` heading (not `**`) and SHALL include "merged" when `triggered_by == "webhook-merge"` and omit it for `webhook-open` and `webhook-reopen`.

#### Scenario: Staleness warning is prepended
- **WHEN** `report.gitnexus_index_stale == True`
- **THEN** the body SHALL prepend `**⚠️ GitNexus index may be stale** — {report.cache_misses} symbols not found. Run \`gitnexus analyze\` to refresh.`

#### Scenario: Changed files section renders from ImpactReport fields
- **WHEN** `report.changed_files` is non-empty
- **THEN** the body SHALL include a `### Changed Files ({n})` section
- **AND** each entry SHALL be rendered as ``- \`{cf.path}\` ({", ".join(cf.feature_tags)}, +{cf.lines_added}/-{cf.lines_removed}, symbols: {", ".join(cf.symbols_extracted)})``

#### Scenario: Recommended tests section renders from TestFileModel fields
- **WHEN** `report.test_files_to_run` is non-empty
- **THEN** the body SHALL include a `### Recommended Tests ({n})` section
- **AND** each entry SHALL be rendered as ``- \`{tf.path}\` ({tf.test_type.value}) — covers {", ".join(tf.covers_features)}``

#### Scenario: Empty optional sections are omitted
- **WHEN** any optional section (changed files, tests, coverage gaps) is empty
- **THEN** that section SHALL be omitted entirely

#### Scenario: Raw report link is appended
- **WHEN** `raw_report_path` is provided
- **THEN** the body SHALL append `[View raw impact report]({raw_report_path})` as the final line

### Requirement: GitLab Note Poster (jira-skill)
The system SHALL provide `post_gitlab_note(report, project_path, mr_iid, *, factory=None, raw_report_path=None) -> int`. The function MUST orchestrate: find → build body → **prepend `NOTE_PREFIX`** (the HTML-comment marker `<!-- tdt-impact-analysis -->`) → upsert. The marker is prepended to the body *before* calling `upsert_mr_note` so that `find_mr_notes` can locate the note on re-runs via substring match. It MUST catch all exceptions, log `gitlab_note_failed`, and return `-1` without propagating.

#### Scenario: Edit existing note when found
- **WHEN** `find_mr_notes` returns at least one matching note (substring match on `<!-- tdt-impact-analysis -->`)
- **THEN** the function SHALL call `upsert_mr_note(..., note_id=existing[0]["id"])` to edit in place
- **AND** the resulting note body SHALL begin with `<!-- tdt-impact-analysis -->\n` followed by the rendered markdown

#### Scenario: Legacy note containing both markers is correctly located
- **WHEN** an MR has a note whose body is `<!-- tdt-impact-analysis -->\n⚠️ Impact Analysis — MR !\n\n<rendered markdown>`
- **AND** `find_mr_notes(project_path, mr_iid)` is called
- **THEN** that note SHALL be returned (substring `<!-- tdt-impact-analysis -->` matches `body`)
- **AND** `post_gitlab_note` SHALL edit it in place (preserving the legacy prefix line below the new marker line)

#### Scenario: Create new note when none found
- **WHEN** `find_mr_notes` returns an empty list
- **THEN** the function SHALL call `upsert_mr_note(...)` without a `note_id` to create a new note
- **AND** the new note body SHALL begin with `<!-- tdt-impact-analysis -->\n` followed by the rendered markdown

#### Scenario: Exceptions are suppressed
- **WHEN** any GitLab API call raises an exception
- **THEN** the function SHALL log `gitlab_note_failed` with the error message
- **AND** it SHALL return `-1` without re-raising

## ADDED Requirements

### Requirement: Legacy Impact Marker Migration (webhook-receiver)
The system SHALL provide `webhook_receiver.impact_marker_migration.migrate_legacy_impact_note(...)` that prepends the new HTML-comment marker to any existing GitLab MR note whose body starts with the legacy visible prefix `⚠️ Impact Analysis — MR !`. The function MUST be invoked from `webhook_receiver.impact.run_gitlab_note_workflow` before each call to `post_gitlab_note`. The function SHALL be gated by a state file at `~/.tdt/state/webhook-receiver/impact-marker-migrated.json` (format `{"migrated": ["<project_path>!<mr_iid>"]}`) — once a key exists, subsequent calls for the same MR SHALL be no-ops. The function MUST never raise; on any exception, it SHALL log `impact_marker_migration_failed` with the failure stage and return `False`.

#### Scenario: Migration prepends marker to legacy note
- **WHEN** `migrate_legacy_impact_note(project_path, mr_iid, poster)` is called
- **AND** the MR has a note whose body starts with `⚠️ Impact Analysis — MR !`
- **AND** that body does not contain `<!-- tdt-impact-analysis -->`
- **AND** the state file does not yet contain the key `{project_path}!{mr_iid}`
- **THEN** it SHALL prepend `<!-- tdt-impact-analysis -->\n` to that note's body
- **AND** it SHALL call `note.save()` on the updated note
- **AND** it SHALL add `{project_path}!{mr_iid}` to the state file
- **AND** it SHALL log `impact_marker_migration_done` with `project_path`, `mr_iid`, `note_id`
- **AND** it SHALL return `True`

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