# Tasks: Jira MR-Only Comments Integration

## Phase 1: Backup Current Config

- [x] [historical] T1.1: Export current iOS (231) integration config
- [x] [historical] T1.2: Export current Android (232) integration config
- [x] [historical] T1.3: Save configs to `openspec/changes/jira-mr-only-comments/backup/` for rollback

## Phase 2: Update Integration Settings

- [x] [historical] T2.1: Run `glab api -X PUT projects/231/integrations/jira` with MR-only config
- [x] [historical] T2.2: Run `glab api -X PUT projects/232/integrations/jira` with MR-only config

## Phase 3: Verify Configuration

- [x] [historical] T3.1: Confirm both projects return `merge_requests_events: true`
- [x] [historical] T3.2: Confirm both projects return `comment_on_event_enabled: true`
- [x] [historical] T3.3: Confirm all other `*_events` flags are `false`
- [x] [historical] T3.4: Confirm `jira_issue_transition_id` remains empty
- [x] [historical] T3.5: Verify smart commits still function (DVCS connector independent of webhook events)

## Phase 4: Validate MR Linking

- [x] [historical] T4.1: Create test MR with Jira issue key in title on iOS or Android repo
- [x] [historical] T4.2: Verify MR appears in Jira Development Panel
- [x] [historical] T4.3: Verify comment appears on Jira issue
- [x] [historical] T4.4: Push a standalone commit (not in MR) — verify NO comment in Jira
- [x] [historical] T4.5: Run pipeline — verify NO comment in Jira

## Phase 5: Update Documentation

- [x] [historical] T5.1: Update `.agents/skills/jira-integration/SKILL.md` to reflect MR-only events
- [x] [historical] T5.2: Update `openspec/changes/jira-gitlab-integration-v3/spec.md` to note this refinement

## Rollback Plan

If issues arise, restore from backup:

```bash
glab api -X PUT "projects/{id}/integrations/jira" \
  -f "commit_events=true" \
  -f "push_events=true" \
  -f "pipeline_events=true" \
  -f "note_events=true" \
  -f "issues_events=true" \
  -f "tag_push_events=true" \
  -f "job_events=true" \
  -f "wiki_page_events=true" \
  -f "confidential_issues_events=true" \
  -f "confidential_note_events=true"
```

Or restore via GitLab UI: Project → Settings → Integrations → Jira → re-enable events → Save.


---

> **Historical record:** This change was archived with 17 incomplete task(s) (0/17 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
