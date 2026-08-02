## Why

The impact-analysis pipeline posts GitLab MR notes with a visible idempotency
marker (`⚠️ Impact Analysis — MR !`) using `tdt_core.clients.gitlab_mr.find_mr_notes`
/ `upsert_mr_note`. The codescan reviewer in `ai-review` uses a hidden
HTML-comment marker (`<!-- code-scan-review -->`) and a parallel
`GitLabReviewPoster` writer.

The two notes are functionally similar (both find-then-upsert with a marker)
but use different marker conventions and matching semantics:

| Concern | Impact (current) | Codescan |
|---------|------------------|----------|
| Marker | `⚠️ Impact Analysis — MR !` (visible prefix) | `<!-- code-scan-review -->` (HTML comment) |
| Match | `body.startswith(marker)` (prefix) | `marker in body` (substring) |
| Writer | `tdt_core.clients.gitlab_mr.{find_mr_notes, upsert_mr_note}` (in `tdt-core`) | `ai_review.gitlab.review_posting.GitLabReviewPoster` (in `ai-review`) |
| Body prepend | `post_gitlab_note` prepends marker | `post_or_update` prepends marker |

This change aligns the impact marker to the codescan-style HTML comment,
without relocating or duplicating any writer. The existing
`tdt_core.clients.gitlab_mr.{find_mr_notes, upsert_mr_note}` infrastructure
is reused — only the marker constant and the matching predicate change.

**Trigger and schedule already match.** The 15-minute `scan-recent-mr` cron
in `agent-core` already drives the same dual-trigger behaviour:
- Webhook events (open / reopen / merge) trigger `run_gitlab_note_workflow`
  via `app.py`.
- `scan-recent-mr` synthesizes webhook payloads for the most-recent MRs and
  POSTs them to `/gitlab-webhook`, hitting the same handler.

No scheduler or trigger changes are needed.

## What Changes

- **Modify** `tdt_core.clients.gitlab_mr`:
  - `NOTE_PREFIX` constant changes from `⚠️ Impact Analysis — MR !` to
    `<!-- tdt-impact-analysis -->` (HTML comment marker, codescan-style).
  - `find_mr_notes` matching changes from `body.startswith(prefix)` to
    `prefix in body` (substring match, codescan-style).
- **Add** `webhook-receiver/src/webhook_receiver/impact_marker_migration.py`:
  one-shot, state-file-gated helper that prepends the new HTML-comment
  marker to any existing legacy note whose body starts with the visible
  prefix. State file at
  `~/.tdt/state/webhook-receiver/impact-marker-migrated.json`.
- **Modify** `webhook-receiver/src/webhook_receiver/impact.py`
  `run_gitlab_note_workflow`: invoke the migration helper before each
  note post (idempotent per MR per host via state file).

The Jira comment posting remains **merge-only**, unchanged.
The `GitLabReviewPoster` in ai-review is **not** modified — codescan's
writer stays as-is. The existing `tdt_core.clients.gitlab_mr.find_mr_notes`
and `upsert_mr_note` continue to exist (still used by other code paths,
and now by impact with the new marker semantics).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `gitlab-impact-note`: Two existing requirements change in marker style
  and matching semantics. Specifically:
  - `### Requirement: GitLab MR Note Writer (tdt-core)` — marker becomes
    HTML comment, matching becomes substring.
  - `### Requirement: GitLab Note Poster (jira-skill)` — prepends the new
    HTML marker.
  - New ADDED requirement: legacy-marker migration (state-file gated).
- `impact-analysis-core`: `### Requirement: GitLab MR Note Posting` —
  marker becomes HTML comment; matching semantics unchanged at the spec
  level (still idempotent edit-in-place). `### Requirement: GitLab
  Markdown Comment Format` — clarify that the marker is added by
  `post_gitlab_note`, not by `build_gitlab_note` (the builder still
  returns a marker-free body).

## Impact

**Affected code (3 repos):**

- `tdt-core` — modify `src/tdt_core/clients/gitlab_mr.py` (marker constant
  + matching predicate). Update `tests/test_gitlab_mr.py` for the new
  marker and substring matching.
- `webhook-receiver` — add `src/webhook_receiver/impact_marker_migration.py`
  and its tests. Modify `src/webhook_receiver/impact.py`
  `run_gitlab_note_workflow` to call the migration helper before each
  post.
- `jira-skill` — no source change. `post_gitlab_note` already prepends
  `NOTE_PREFIX`; once `NOTE_PREFIX` is updated in `tdt-core`, the marker
  on new impact notes changes automatically. Existing tests should be
  updated to match the new marker.

**Affected APIs:** None externally.

**Affected dependencies:** None.

**Affected deployments:** `tdt-core` redeploys (additive — backward-compatible
API surface, new marker). `webhook-receiver` redeploys (additive — new
helper module + invocation). `jira-skill` may redeploy only if its tests
require updates for the new marker.

**Affected runtime behaviour:** One existing impact note (MR 23433, note_id
619577, 122 edits) gains the new HTML-comment marker line at the top of
its body — visible content unchanged. All future MRs get a fresh note with
the HTML-comment marker from the first post.

**Non-goals:**

- Not relocating `GitLabReviewPoster` from `ai-review` to `tdt-core`.
  The codescan writer stays where it is; merging the two writers is a
  separate concern and would conflate two parallel abstractions.
- Not introducing a new `webhook_receiver.gitlab_poster` wrapper.
  `post_gitlab_note` already exists and already prepends the marker;
  the marker constant change in `tdt-core` propagates automatically.
- Not changing the trigger semantics (open / reopen / merge).
- Not changing the merge-only Jira posting behaviour.
- Not removing `tdt_core.clients.gitlab_mr.find_mr_notes` /
  `upsert_mr_note` — they remain the writer.
- Not changing the `15-min scan-recent-mr` cron — already in place and
  already drives the dual-trigger behaviour.
- Not auto-cleaning up legacy notes — migration in-place preserves the
  visible prefix as historical context (the migration prepends a new
  HTML-comment line; the visible prefix line is preserved below it).