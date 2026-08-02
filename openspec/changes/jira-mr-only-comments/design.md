# Design: Jira MR-Only Comments Integration

## Architecture

The GitLab Jira Integration is a built-in service (not a custom app). Configuration is stored per-project and managed via the GitLab REST API.

```
┌─────────────────────────────────────────────────┐
│                 GitLab (git.ecomedic.vn)        │
│                                                 │
│  Project 231 (iOS)  ──┐  Project 232 (Android)  │
│  Jira Integration     │  Jira Integration       │
│  ┌─────────────────┐  │  ┌─────────────────┐    │
│  │ Events Enabled: │  │  │ Events Enabled: │    │
│  │  ✅ MR only     │  │  │  ✅ MR only     │    │
│  │  ❌ All others  │  │  │  ❌ All others  │    │
│  │  💬 Comments:   │  │  │  💬 Comments:   │    │
│  │     on MR events│  │  │     on MR events│    │
│  └────────┬────────┘  │  └────────┬────────┘    │
└───────────┼───────────┴───────────┼─────────────┘
            │                       │
            │  POST /rest/api/3/    │  POST /rest/api/3/
            │  issue/{key}/comment  │  issue/{key}/comment
            ▼                       ▼
┌─────────────────────────────────────────────────┐
│           Jira (psplit.atlassian.net)            │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  Issue: SR-123                          │   │
│  │  Development Panel                      │   │
│  │  └─ MR !456: Feature XYZ              │   │
│  │     └─ Comment: "MR merged by @user"   │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Configuration Update Strategy

### Current Config (captured 2026-05-20)

Both projects have identical settings:

```json
{
  "active": true,
  "properties": {
    "url": "https://psplit.atlassian.net",
    "username": "lekhanhvinh@phillip.com.sg",
    "jira_auth_type": 0,
    "project_keys": ["PUB","AM","AU","COM","FUN","PWM","RMD","SR","STABI","TJ","P3AP"],
    "jira_issue_transition_id": "",
    "comment_on_event_enabled": true
  },
  "commit_events": true,
  "push_events": true,
  "issues_events": true,
  "confidential_issues_events": true,
  "merge_requests_events": true,
  "tag_push_events": true,
  "deployment_events": false,
  "note_events": true,
  "confidential_note_events": true,
  "pipeline_events": true,
  "wiki_page_events": true,
  "job_events": true,
  "incident_events": false
}
```

### Target Config

Only these flags change to `true`:
- `merge_requests_events`: true
- `comment_on_event_enabled`: true (stays true)

All other `*_events` flags become `false`.

### API Call Pattern

```bash
glab api -X PUT "projects/{project_id}/integrations/jira" \
  -f "active=true" \
  -f "merge_requests_events=true" \
  -f "comment_on_event_enabled=true" \
  -f "commit_events=false" \
  -f "push_events=false" \
  -f "pipeline_events=false" \
  -f "note_events=false" \
  -f "issues_events=false" \
  -f "tag_push_events=false" \
  -f "job_events=false" \
  -f "wiki_page_events=false" \
  -f "confidential_issues_events=false" \
  -f "confidential_note_events=false"
```

**Note:** GitLab's integration API treats omitted fields as "keep current value." We explicitly set all fields to ensure clean state.

## MR Linking Mechanics

### How GitLab Detects Jira Issues

1. **Branch name**: Default regex `([A-Z]+-\d+)` scans branch names
2. **MR title**: Scanned for issue key patterns
3. **MR description**: Scanned for issue key patterns
4. **Commits**: Each commit message scanned for issue keys

### What Appears in Jira

- **Development Panel**: Lists linked MRs with status icons
- **Activity Stream**: Comments from MR lifecycle events:
  - `opened` → "MR !N opened by @user"
  - `approved` → "MR !N approved by @user"
  - `merged` → "MR !N merged by @user"
  - `closed` → "MR !N closed by @user"
  - `updated` → "MR !N updated"

### Why We Keep MR Events Only

MR events are the most actionable for Jira tracking:
- Opening an MR = work ready for review
- Merging an MR = work complete
- Closing an MR = work abandoned

Individual commits and pushes during development create noise without adding value. Pipeline status is already visible in GitLab CI.

## Error Handling

### If Integration API Fails

1. **401 Unauthorized**: PAT expired — regenerate at `git.ecomedic.vn/-/user_settings/personal_access_tokens`
2. **403 Forbidden**: Insufficient permissions — need Maintainer role on project
3. **404 Not Found**: Project ID wrong — verify with `glab project list`

### If Comments Don't Appear in Jira

1. Verify MR title/description contains valid issue key (e.g., `SR-123`)
2. Check Jira integration is active: `glab api projects/{id}/integrations/jira`
3. Check `comment_on_event_enabled` is true
4. Verify Jira account has Create Comments permission on target project
