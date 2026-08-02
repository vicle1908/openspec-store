# GitLab MR Impact Note — Technical Design

## Context

The existing impact-analysis pipeline in `webhook-receiver` fires a GitNexus blast-radius + feature-map analysis on every GitLab MR merge event and posts the result as a Jira ADF comment. Two gaps exist:

1. **No GitLab MR note** — developers must go to Jira to see the impact analysis; GitLab shows nothing.
2. **No early signal on open/reopen** — the analysis only fires on merge, so developers opening an MR get no feedback until after review + merge.

The fix posts a GitLab MR comment on every non-update event (`open`, `reopen`, `merge`) with the full impact analysis in GitLab-flavored markdown. The Jira comment stays merge-only per SPEC-IA-7.

**Stakeholders:** Dev team (MR authors, reviewers), QA (test planning).

## Goals / Non-Goals

**Goals:**
- Post GitLab MR notes on `open`, `reopen`, and `merge` events with the full impact analysis
- Make GitLab MR comments idempotent (edit-in-place on re-run)
- Fire-and-forget: GitLab posting failures must not affect webhook HTTP response
- Align `app.py` dispatch scope with the spec intent

**Non-Goals:**
- GitLab notes on `update` events (skipped; debouncer still coalesces bursts)
- Posting Jira comments on non-merge events
- Changing the feature-map, GitNexus pipeline, or `AnalysisResult` model
- Rich ADF rendering in GitLab (plain markdown only)

## Decisions

### D1: Marker = `NOTE_PREFIX = "⚠️ Impact Analysis — MR !"`

**Decision:** Use an emoji-prefix string as the idempotency marker, prepended to the note body by `post_gitlab_note`.

**Alternatives considered:**
- `<!-- gitlab-impact-analysis -->` (HTML comment): invisible in UI; but `build_gitlab_note` uses `###`-level headings that would appear below the marker, and HTML comments add noise to the API response body
- Plain text prefix without emoji: less distinctive

**Rationale:** `NOTE_PREFIX` is visible but non-intrusive — it uses an emoji warning sign that signals "automated analysis" to developers. The marker appears as the first line of the note body, before the rendered markdown sections, so it does not interfere with the visual layout. `find_mr_notes` uses `body.startswith(NOTE_PREFIX)` for efficient idempotency detection.

**Reference:** `ai-review/gitlab/review_posting.py` uses `<!-- mr-auto-review -->` (HTML comment) for a different system (AI review). The impact note uses a different marker to keep the two systems independent.

### D2: `find_mr_notes` + `upsert_mr_note` in `tdt_core.clients.gitlab_mr`

**Decision:** Add note read/write functions to the existing `gitlab_mr` module alongside `fetch_mr_changes` and `fetch_mr_metadata`.

**Alternatives considered:**
- New module `tdt_core.clients.gitlab_notes`: would require a new file for two small functions
- Inline in `jira_skill/impact/gitlab_note.py`: would couple GitLab API details to the jira-skill SDK

**Rationale:** `gitlab_mr.py` already handles all GitLab MR read operations for the impact pipeline. Adding write operations here follows the same pattern as `fetch_mr_*` — factory injection, optional `factory=` kwarg, consistent sync-then-thread style. Both `jira-skill` and `webhook-receiver` can import from this single module.

### D3: `build_gitlab_note` reads `ImpactReport` fields directly, not ADF nodes

**Decision:** The markdown builder reads `ImpactReport` pydantic model fields and formats them into markdown strings. It is NOT an ADF-to-markdown converter.

**Alternatives considered:**
- Build the ADF document first, then convert ADF → markdown: would require a full ADF traversal; `build_impact_adf` uses a restricted node set (paragraph/text only) that maps imperfectly to GitLab markdown headings and lists
- Render from `AnalysisResult` directly: would duplicate the `build_impact_report` data-transform step

**Rationale:** `build_impact_adf` and `build_gitlab_note` both produce output from the same `ImpactReport` data — but the output formats are completely different (ADF dict vs. markdown string). Rendering from `ImpactReport` fields directly is simpler and more testable than an ADF traversal. The spec defines exact section content per field.

**Reuse:** Section order and field names mirror `build_impact_adf` for consistency. `TestFileModel.path`, `.test_type.value`, `.covers_features` are rendered directly.

### D4: `triggered_by = f"webhook-{action}"` (not just `"webhook"`)

**Decision:** Pass the specific action as part of `triggered_by` so the GitLab note title can omit "merged" and correctly reflect the event type.

**Alternatives considered:**
- Keep `triggered_by = "webhook"` for all events: would require passing `action` separately; `ImpactReport.triggered_by` would lose specificity
- New field `event_type`: adds a new field to `ImpactReport`; `triggered_by` is already a `str` with no type restriction

**Rationale:** `ImpactReport.triggered_by` is `str` with comment `"webhook" | "cli"` — the type doesn't restrict new values. `f"webhook-{action}"` produces `"webhook-open"`, `"webhook-reopen"`, `"webhook-merge"`. The markdown builder uses this to omit "merged" from the title when the event is `open` or `reopen`.

### D5: Workflow insertion point — parallel to `_post_to_jira_tickets`

**Decision:** `run_gitlab_note_workflow` runs the full `_run_pipeline` (same as Jira), then calls `post_gitlab_note` in the same async context. It is not a separate DBOS step from `_run_pipeline`.

**Alternatives considered:**
- Separate DBOS step: would run `_run_pipeline` twice (once per step) — wasteful
- Insert GitLab posting inside `_run_pipeline`: couples GitLab concerns into the shared pipeline; harder to test in isolation

**Rationale:** `_run_pipeline` is the expensive step (GitNexus, feature-map). We only want to run it once. Both Jira and GitLab output share the same `report` object. `run_gitlab_note_workflow` calls `_run_pipeline` internally and then posts to GitLab. This is the same pattern as `_run_impact_workflow` but without the Jira step.

**Note:** `run_impact_workflow` and `run_gitlab_note_workflow` both call `_run_pipeline`. On a `merge` event, both run in parallel fire-and-forget tasks. This means `_run_pipeline` runs twice for merge events. To avoid this duplication, a future refactor could share the pipeline result — but that is out of scope for this change.

### D6: SHA fallback for `open` and `reopen` events

**Decision:** For `open`/`reopen` events, `merge_commit_sha` is absent. Use `meta.sha` (head commit of source branch) as the SHA for the raw report path.

**Rationale:** `_run_pipeline` already falls back to `meta.sha` when `merge_commit_sha` is absent (see `webhook_receiver/impact.py` lines 230-237). The raw report is written to `~/.tdt/state/webhook-impacts/{mr_iid}-{sha}.json` — using `meta.sha` gives a stable, real commit SHA. GitNexus cache keys use this SHA; if the index is stale for `meta.sha`, the stale warning fires per SPEC-IA-7.

### D7: Env var gate: `GITLAB_IMPACT_NOTE_ENABLED`

**Decision:** Gate the dispatch behind `GITLAB_IMPACT_NOTE_ENABLED` (default `false`). The `/health` endpoint reports the gate status.

**Pattern:** Mirrors `JIRA_IMPACT_WEBHOOK_ENABLED` exactly.

**Note:** The gate controls the `asyncio.create_task` dispatch — if disabled, no GitLab API calls are made at all. `run_gitlab_note_workflow` itself has no gate; the gate is in `app.py`.

### D8: `post_gitlab_note` prepends `NOTE_PREFIX` to the body

**Decision:** `post_gitlab_note` builds the markdown body with `build_gitlab_note`, then prepends `NOTE_PREFIX + "\n\n"` to produce the final body passed to `upsert_mr_note`. `upsert_mr_note` stores this prefixed body verbatim.

**Alternatives considered:**
- `upsert_mr_note` prepends the marker: the marker would be in the stored body, but the function signature and docstring would need to document this behavior, making it less of a "pure" write function
- `build_gitlab_note` prepends the marker: pollutes the pure rendering function with idempotency concerns

**Rationale:** `build_gitlab_note` is a pure renderer — it produces clean GitLab-flavored markdown. `post_gitlab_note` is the orchestrator that knows about idempotency. Prepending the marker here keeps the rendering function pure and testable. `upsert_mr_note` receives a body that already has the marker, satisfying `find_mr_notes`'s `startswith` check.

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GitLab API rate limit on notes | Low | Medium | Fire-and-forget; failures logged as `gitlab_note_failed`, never propagate; `-1` returned |
| Note deleted externally → idempotency miss → new note created | Low | Low | `upsert_mr_note` falls back to create path; harmless extra note |
| `_run_pipeline` runs twice on merge events (once per workflow) | Medium | Low | Acceptable for v1; future refactor could share result |
| GitLab PAT lacks `api` scope | Low | High | Use bot account's PAT; `GITLAB_IMPACT_NOTE_ENABLED=false` as escape hatch |
| `open` events: `meta.sha` is source branch HEAD, not merged commit | N/A | N/A | Expected; GitNexus may report "not found" for unindexed commits; stale warning fires per spec |

## Migration Plan

### Deployment

1. Merge code to `main`, deploy all three repos (`tdt-core`, `jira-skill`, `webhook-receiver`)
2. Confirm `/health` reports `gitlab_impact_note_enabled: false` (default)
3. Set `GITLAB_IMPACT_NOTE_ENABLED=true` in `~/.tdt/.env`
4. Redeploy `webhook-receiver`
5. Confirm `/health` reports `gitlab_impact_note_enabled: true`
6. Run smoke replay (Phase 8 tasks)

### Rollback

1. Set `GITLAB_IMPACT_NOTE_ENABLED=false` in `~/.tdt/.env`
2. Redeploy `webhook-receiver` — no GitLab calls are made regardless of event
3. Revert code to previous release if needed

### Sequencing constraint

- Phase 1 (`tdt-core`) must complete before Phase 2 (`jira-skill`) and Phase 3 (`webhook-receiver`)
- Phase 2 and Phase 3 can proceed in parallel after Phase 1
- Phase 5 (jira-skill unit tests) can proceed after Phase 2
- Phase 6 (tdt-core unit tests) can proceed after Phase 1
- Phase 7 (integration) requires Phase 4 complete
- Phase 8 (smoke) requires Phase 7 complete

## Open Questions

| # | Question | Resolution |
|---|----------|-----------|
| OQ1 | Should `open` events with no `meta.sha` (rare edge case) silently skip posting? | If `fetch_mr_metadata` fails, `sha` falls back to `"unknown"`. The raw report path uses this; the note is still posted. Acceptable. |
| OQ2 | Should the GitLab note be editable by non-bot users? | GitLab API: notes created via API are owned by the bot token's user; other users cannot edit. Acceptable — only the bot can update the idempotent note. |
| OQ3 | Future: share `_run_pipeline` result between `run_impact_workflow` and `run_gitlab_note_workflow` to avoid duplicate GitNexus calls on merge? | Out of scope for v1. Filed as a potential optimization. |
| OQ4 | Should there be a separate `gitlab-impact-note` feature-map? | No — the impact analysis is the same for both posting targets. Feature taxonomy is shared. |
