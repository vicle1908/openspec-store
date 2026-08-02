# Proposal: Restrict Jira Integration to MR-Only Comments

## Problem

Both GitLab projects (`pspl/poems-mobile3-ios` and `pspl/poems-mobile3-android`) have the native Jira Integration configured with **ALL event types enabled**, causing every push, commit, pipeline run, wiki edit, tag push, job change, and note to post comments on linked Jira issues. This creates excessive noise in Jira tickets — a single MR can generate 20+ comments from individual pushes and CI events.

Current event config (both projects):

| Event | Current | Desired |
|-------|---------|---------|
| `merge_requests_events` | ✅ true | ✅ true |
| `comment_on_event_enabled` | ✅ true | ✅ true |
| `commit_events` | ❌ true | **false** |
| `push_events` | ❌ true | **false** |
| `pipeline_events` | ❌ true | **false** |
| `note_events` | ❌ true | **false** |
| `issues_events` | ❌ true | **false** |
| `tag_push_events` | ❌ true | **false** |
| `job_events` | ❌ true | **false** |
| `wiki_page_events` | ❌ true | **false** |
| `confidential_issues_events` | ❌ true | **false** |
| `confidential_note_events` | ❌ true | **false** |

Additionally, `jira_issue_transition_id` is empty — no auto-transitions occur on MR merge, which is correct.

## Solution

Disable all event types except `merge_requests_events` on both GitLab projects. Keep `comment_on_event_enabled=true` so that MR open/update/merge/close events post structured comments to the linked Jira issues.

## MR Linking Strategy

GitLab's native Jira Integration auto-links MRs to Jira issues when issue keys (e.g., `SR-123`, `STABI-559`) appear in:
- MR title (recommended)
- MR description
- Branch name (matches default regex)

No configuration changes needed for linking — it works automatically. This change ensures only the meaningful MR lifecycle events (not every commit/push) appear in Jira.

## Scope

- **Project 231** (`pspl/poems-mobile3-ios`): Update Jira integration via GitLab API
- **Project 232** (`pspl/poems-mobile3-android`): Update Jira integration via GitLab API
- **No source code changes** — only GitLab project settings
- **No Jira configuration changes** — Jira Development Panel continues working

## Success Criteria

- After an MR is created/updated/merged/closed, a comment appears on the linked Jira issue
- Individual commits and pushes do NOT create Jira comments
- Pipeline events do NOT create Jira comments
- Both projects return identical integration config via `glab api projects/{id}/integrations/jira`
