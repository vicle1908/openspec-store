# GitLab Impact Note — Specification

## Overview

This spec covers the GitLab MR note module: the tdt-core write functions (`find_mr_notes`, `upsert_mr_note`) and the jira-skill markdown builder (`build_gitlab_note`, `post_gitlab_note`). The webhook dispatch and integration scenarios are in `jira-impact-analysis/specs/impact-analysis-core/spec.md`.

---

## ADDED Reuses

The following existing code is **referenced but not duplicated**:

| Source | What to reuse | Why |
|--------|--------------|-----|
| `ai-review/gitlab/review_posting.py` | `GitLabReviewPoster.find_existing()` + `post_or_update()` pattern | Proven GitLab MR note idempotency: `marker in note.body` (substring), `notes.create` / `note.save()` |
| `jira_skill.impact.impact_report.build_impact_adf()` | Section list and field names | GitLab markdown builder renders same `ImpactReport` fields into GitLab-flavored markdown |
| `jira_skill.impact.impact_report.ImpactReport` | All fields | Markdown builder receives a fully-populated `ImpactReport`; no new model needed |
| `jira_skill.impact.impact_report.TestFileModel` | `path`, `test_type.value`, `covers_features` | Markdown builder renders these directly from the typed model |
| `webhook_receiver.impact.run_impact_workflow` | DBOS step registration pattern | `run_gitlab_note_workflow` mirrors this exactly; `_run_pipeline` is shared |

---

## ADDED Requirements

### Requirement: GitLab MR Note Writer (tdt-core)
The system SHALL provide `find_mr_notes` and `upsert_mr_note` in `tdt_core.clients.gitlab_mr` using `GitlabClientFactory.from_env()`. The idempotency marker SHALL be `NOTE_PREFIX = "⚠️ Impact Analysis — MR !"` (a visible, human-readable prefix). Idempotency detection uses `body.startswith(NOTE_PREFIX)` (prefix match). `post_gitlab_note` is responsible for prepending the marker to the body before calling `upsert_mr_note`.

#### Scenario: find_mr_notes returns marker-matching notes
- **WHEN** `find_mr_notes(project_path, mr_iid)` is called
- **THEN** it SHALL call `GET /projects/:id/merge_requests/:iid/notes`
- **AND** it SHALL return only notes where `body.startswith(NOTE_PREFIX)`
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
The system SHALL provide `post_gitlab_note(report, project_path, mr_iid, *, factory=None, raw_report_path=None) -> int`. The function MUST orchestrate: find → build body → **prepend `NOTE_PREFIX`** → upsert. The marker is prepended to the body *before* calling `upsert_mr_note` so that `find_mr_notes` can locate the note on re-runs. It MUST catch all exceptions, log `gitlab_note_failed`, and return `-1` without propagating.

#### Scenario: Edit existing note when found
- **WHEN** `find_mr_notes` returns at least one matching note
- **THEN** the function SHALL call `upsert_mr_note(..., note_id=existing[0]["id"])` to edit in place

#### Scenario: Create new note when none found
- **WHEN** `find_mr_notes` returns an empty list
- **THEN** the function SHALL call `upsert_mr_note(...)` without a `note_id` to create a new note

#### Scenario: Exceptions are suppressed
- **WHEN** any GitLab API call raises an exception
- **THEN** the function SHALL log `gitlab_note_failed` with the error message
- **AND** it SHALL return `-1` without re-raising

### Requirement: Webhook Dispatch (webhook-receiver)
The system SHALL fire the GitLab note pipeline on `action` in `("open", "reopen", "merge")` AND when `GITLAB_IMPACT_NOTE_ENABLED=true`. The Jira comment pipeline fires only on `action == "merge"` with `JIRA_IMPACT_WEBHOOK_ENABLED=true`. Both dispatches SHALL be fire-and-forget via `asyncio.create_task`. The GitLab note insertion point SHALL be after the action allowlist passes — parallel to the existing `_run_impact_dispatch` call. The `triggered_by` field extends the existing convention: `"webhook-{action}"` (e.g. `"webhook-open"`). `AppSettings.gitlab_impact_note_enabled` MUST be defined in `webhook_receiver.config.settings` and read from `GITLAB_IMPACT_NOTE_ENABLED` env var (default `False`).

#### Scenario: GitLab note fires on open, reopen, merge
- **WHEN** `action` is `"open"`, `"reopen"`, or `"merge"` AND `GITLAB_IMPACT_NOTE_ENABLED=true`
- **THEN** the system SHALL invoke `run_gitlab_note_workflow` with `action` set correctly

#### Scenario: GitLab note is silent-disabled when env unset
- **WHEN** `GITLAB_IMPACT_NOTE_ENABLED` is unset, empty, or not `"true"`
- **THEN** the GitLab note dispatch SHALL be skipped silently (no log)
- **AND** the `/health` endpoint SHALL report `"gitlab_impact_note_enabled": false`

#### Scenario: Jira comment only fires on merge
- **WHEN** `action == "merge"` and `JIRA_IMPACT_WEBHOOK_ENABLED=true`
- **THEN** the system SHALL also invoke `run_impact_workflow` for Jira comment posting

#### Scenario: Update events are skipped
- **WHEN** `action == "update"`
- **THEN** the system SHALL skip both GitLab and Jira posting entirely

### Requirement: Environment Gates
The system SHALL gate GitLab note posting behind `GITLAB_IMPACT_NOTE_ENABLED`. The `/health` endpoint SHALL report `gitlab_impact_note_enabled`.

#### Scenario: Health reports gate status
- **WHEN** `GITLAB_IMPACT_NOTE_ENABLED` is `"true"`
- **THEN** the `/health` endpoint SHALL report `"gitlab_impact_note_enabled": true`
- **AND** when it is unset or not `"true"` the `/health` endpoint SHALL report `"gitlab_impact_note_enabled": false`

### Requirement: Raw Report Persistence
The system SHALL write the raw JSON `ImpactReport` to `~/.tdt/state/webhook-impacts/{mr_iid}-{sha}.json` for every pipeline run. The GitLab note SHALL include a `View raw report` link.

#### Scenario: Report is written and linked
- **WHEN** the impact pipeline runs for an MR with commit `sha`
- **THEN** the full JSON report SHALL be written to `~/.tdt/state/webhook-impacts/{mr_iid}-{sha}.json`
- **AND** the GitLab note body SHALL include `[View raw impact report](file://{path})`
