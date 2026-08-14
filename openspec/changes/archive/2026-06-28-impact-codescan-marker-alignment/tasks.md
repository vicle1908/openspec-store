# Impact Codescan-Marker Alignment — Tasks

## 1. Update `tdt-core.clients.gitlab_mr` marker + matching

- [x] 1.1 In `tdt-core/src/tdt_core/clients/gitlab_mr.py`, change `NOTE_PREFIX` from `"⚠️ Impact Analysis — MR !"` to `"<!-- tdt-impact-analysis -->"`.
- [x] 1.2 In the same file, change `find_mr_notes` matching predicate from `body.startswith(prefix)` to `prefix in body`.
- [x] 1.3 Update `tdt-core/tests/test_gitlab_mr.py` so all `NOTE_PREFIX`-based assertions use the new HTML marker (substring matching).
- [x] 1.4 Run `cd tdt-core && uv run pytest tests/test_gitlab_mr.py -v` — expect all pass.
- [x] 1.5 Run `cd tdt-core && uv run pytest tests/ -v` — expect full suite pass.
- [x] 1.6 Run `cd tdt-core && uv run ruff check src/ tests/ && uv run mypy src/ tests/` — expect no errors. (Pre-existing mypy warnings on test_gitlab_mr.py:181-182 are unrelated to this change.)
- [x] 1.7 Commit: `feat(tdt-core): align impact marker to codescan HTML-comment style`.

## 2. Add webhook-receiver one-shot marker migration

- [x] 2.1 Create `webhook-receiver/tests/test_impact_marker_migration.py` with unit tests: prepends marker, noop when no legacy note, idempotent per MR, logs+returns False on API error, skips already-migrated notes.
- [x] 2.2 Run baseline to confirm `ModuleNotFoundError`.
- [x] 2.3 Create `webhook-receiver/src/webhook_receiver/impact_marker_migration.py` with `LEGACY_MARKER_PREFIX`, `DEFAULT_STATE_FILE`, `migrate_legacy_impact_note(...)`. State file at `~/.tdt/state/webhook-receiver/impact-marker-migrated.json`.
- [x] 2.4 Run `cd webhook-receiver && uv run pytest tests/test_impact_marker_migration.py -v` — expect all pass.
- [x] 2.5 Commit: `feat(webhook-receiver): one-shot migration for legacy impact marker`.

## 3. Invoke migration in `webhook-receiver.impact.run_gitlab_note_workflow`

- [x] 3.1 Run baseline: `cd webhook-receiver && uv run pytest tests/test_impact_workflow.py -v`.
- [x] 3.2 In `webhook-receiver/src/webhook_receiver/impact.py`, add a call to `migrate_legacy_impact_note` immediately before the existing `post_gitlab_note` call inside `run_gitlab_note_workflow`. Run the migration in `asyncio.to_thread` with a fresh `GitlabClientFactory` based poster.
- [x] 3.3 Suppress all exceptions from the migration call (log `impact_marker_migration_unexpected_error` and continue). Migration failures MUST NOT prevent `post_gitlab_note` from running.
- [x] 3.4 Run `cd webhook-receiver && uv run pytest tests/test_impact_workflow.py tests/test_impact_marker_migration.py -v` — expect all pass.
- [x] 3.5 Run `cd webhook-receiver && uv run ruff check src/ tests/ && uv run mypy src/ tests/` — expect no errors.
- [x] 3.6 Commit: `feat(webhook-receiver): invoke legacy-marker migration before impact note post`.

## 4. Update jira-skill tests for new marker

- [x] 4.1 In `jira-skill/tests/impact/test_gitlab_note.py`, update any assertions on `NOTE_PREFIX` to use the new HTML marker.
- [x] 4.2 Run `cd jira-skill && uv run pytest tests/impact/test_gitlab_note.py -v` — expect all pass.
- [x] 4.3 Run `cd jira-skill && uv run pytest tests/ -v` — expect full suite pass.
- [x] 4.4 Commit: `feat(jira-skill): align impact marker to codescan HTML-comment style` (also updated the local `NOTE_PREFIX` constant in `src/jira_skill/impact/gitlab_note.py:48`, which was a duplicate of the tdt-core one).

## 5. End-to-end verification

- [x] 5.1 Trigger a synthetic webhook for an open MR (or any recent MR) — expect HTTP 200. **Requires deploy — see below.**
- [x] 5.2 Check webhook-receiver logs: `tail deployments/webhook-receiver/logs/webhook-receiver.stdout.log | grep -E "gitlab_note|impact_marker"` — expect sequence: `impact_marker_migration_done` (for legacy MRs, one-time) → `gitlab_note_edited` (idempotent).
- [x] 5.3 Open MR in GitLab UI: verify exactly one impact note exists, body now starts with `<!-- tdt-impact-analysis -->` (visible only in source). Legacy prefix line is preserved below.
- [x] 5.4 Trigger `scan-recent-mr` manually: `cd webhook-receiver && uv run python -m webhook_receiver.scan_recent_mr_cli --limit 5` — verify `impact_marker_migration_done` does NOT fire again (state-file gate works). New MRs get `gitlab_note_created` with the HTML marker.
- [x] 5.5 Verify codescan note is unaffected (separate marker `<!-- code-scan-review -->`, separate note).

> **Deploy done.** Verified on MR 23433 (pspl/poems-mobile3-android):
> - Deployed via `bash scripts/deploy.sh` (PID 28719, healthy at port 8080)
> - Migration fired for note 619577: `<!-- tdt-impact-analysis -->\n⚠️ Impact Analysis — MR !\n...` (new marker prepended, legacy prefix preserved below)
> - State file populated: `{"migrated": ["pspl/poems-mobile3-android!23433"]}`
> - Re-run: `impact_marker_migration_skipped_already_migrated` logged (idempotent ✓)
> - Codescan note id=619275 unchanged: still `<!-- code-scan-review -->` marker

## 6. OpenSpec archive

- [x] [historical] 6.1 Verify the change is apply-ready: `openspec status --change impact-codescan-marker-alignment`.
- [x] [historical] 6.2 After deploy + verification, run `openspec archive impact-codescan-marker-alignment` to move the change to `openspec/changes/archive/`.
- [x] [historical] 6.3 Verify the archived change contains all 4 artifacts (proposal, design, specs, tasks).


---

> **Historical record:** This change was archived with 3 incomplete task(s) (27/30 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
