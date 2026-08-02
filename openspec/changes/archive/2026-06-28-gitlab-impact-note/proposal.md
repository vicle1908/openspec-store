# GitLab MR Impact Note — Proposal

## Why

The current impact-analysis pipeline has a spec/code alignment gap:

1. **Jira posting** fires only on `action=merge` — correct and aligned.
2. **GitLab MR note** does not exist in code — the spec implies one should.
3. **Trigger scope** in `app.py` fires impact analysis only on `action=merge`; the spec intends `open`/`reopen`/`merge`.

This change closes the gap: GitLab MR notes are posted on every non-update MR event (`open`, `reopen`, `merge`), and the Jira comment remains merge-only.

## What Changes

### Current State

- `app.py` action allowlist: `("open", "update", "reopen", "merge")`
- Impact pipeline fires only on `action == "merge"` + `JIRA_IMPACT_WEBHOOK_ENABLED=true`
- No GitLab MR comment posting exists

### Entry Point A — GitLab MR Webhook (Existing, Extended)

When a GitLab MR webhook fires (`action` ∈ {open, update, reopen, merge}):

1. The existing `/gitlab-webhook` handler validates HMAC, deduplicates, and debounces.
2. The action allowlist is extended to include the impact pipeline for non-update events.
3. **For `action` ∈ {open, reopen, merge}:** run the impact-analysis pipeline and post a GitLab MR note (idempotent, edit-in-place).
4. **For `action == "merge"` + `JIRA_IMPACT_WEBHOOK_ENABLED=true`:** additionally post an idempotent Jira ADF comment on the matched ticket.

Rapid `update` bursts are coalesced by the existing inline debouncer (same `project_id + mr_iid` key) — only the last commit fires. `update` events themselves are skipped entirely.

### Entry Point B — On-demand CLI (Existing)

```bash
cd jira-skill && uv run python -m jira_skill impact-ticket SR-3588
```

Unchanged. The CLI posts Jira comments only (no GitLab MR notes).

## Non-Goals

- GitLab MR notes on `update` events (skipped)
- Posting Jira comments on non-merge events
- Changing the `feature-map.yaml` or GitNexus pipeline
- Rich ADF rendering in GitLab (GitLab notes use markdown only)

## Alignment with Existing Systems

- **Feature taxonomy**: unchanged, reused from `code-daily-scan/feature_resolver.py`
- **GitNexus blast-radius**: unchanged, used for symbol-level impact analysis
- **tdt-core GitLab client**: `find_mr_notes` + `upsert_mr_note` added to `tdt_core.clients.gitlab_mr`
- **jira-skill impact module**: new `gitlab_note.py` for markdown conversion
- **webhook-receiver**: `run_gitlab_note_workflow` added alongside `run_impact_workflow`

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| GitLab API rate limit on notes | Fire-and-forget; failures logged but never propagate |
| Duplicate notes on re-run | `upsert_mr_note` finds existing by prefix, edits in place |
| Wrong env var disables silently | `GITLAB_IMPACT_NOTE_ENABLED` logged on startup; `/health` reports status |
| GitLab note visible to all MR participants | Use bot account's PAT (not individual user credentials) |
