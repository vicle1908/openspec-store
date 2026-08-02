# Jira Intelligent Reminders - Design

**Date:** 2026-05-21

---

## Architecture

```
ecosystem dependency graph:

  tdt-core[jira]
    └── jira-skill (issue, jql, board)
          └── jira-daily-reports
                ├── reports/                  (existing — passive)
                └── reminders/                ← NEW Phase 1-3
                    ├── policies.py           (YAML-loaded rules)
                    ├── tagger.py             (@mention via ADF)
                    ├── escalation.py         (day-N rules)
                    ├── suppression.py        (grace, snooze, off-hours)
                    └── runner.py             (orchestrates daily scan)

  jira-workflow-guard                         ← NEW Phase 4-5 (deferred)
    └── api/server.py                         (FastAPI Jira webhook)
        └── transitions.py                    (start_date, end_date enforcement)
```

---

## Component Design

### 1. Policies (`reminders/policies.py`)

YAML-defined rules per project + role:

```yaml
# config/reminder-policies.yaml
project: POEMS2

policies:
  - name: developer_estimation
    role: assignee
    issue_types: [Story, Task, Bug]
    statuses: [To Do, Selected for Development]
    required_fields:
      - story_points
    grace_period_hours: 24
    escalation:
      day_1: tag_assignee
      day_3: add_label "needs-estimation"
      day_5: tag_manager

  - name: qa_test_plan
    role: qa_owner
    custom_field: customfield_10042
    issue_types: [Story, Task]
    statuses: [Code Review, Ready for QA]
    required_fields:
      - customfield_10043  # test_plan_link
    escalation:
      day_1: tag_qa_owner

  - name: in_progress_start_date
    role: assignee
    statuses: [In Progress]
    required_fields:
      - customfield_10015  # start_date
    on_transition: true   # check immediately when status changes
    grace_period_hours: 1

  - name: test_done_end_date
    role: assignee
    statuses: [Test Done, Done]
    required_fields:
      - duedate  # end_date
    on_transition: true
    grace_period_hours: 1
```

**Loader:** `Policies.from_yaml(path) -> list[Policy]`. Pydantic models for validation.

### 2. Tagger (`reminders/tagger.py`)

Posts @mention comments using Atlassian Document Format (ADF):

```python
def post_mention(jira, issue_key: str, account_id: str, message: str) -> bool:
    """Post a comment with @mention via ADF."""
    body = {
        "type": "doc",
        "version": 1,
        "content": [{
            "type": "paragraph",
            "content": [
                {"type": "mention", "attrs": {"id": account_id}},
                {"type": "text", "text": f" {message}"},
            ],
        }],
    }
    return jira.issue_add_comment(issue_key, body)
```

Resolve `account_id` from assignee field directly (no extra lookup needed for assignee role). For QA owner / manager, lookup via `jira.user_find_by_user_string(query=email)`.

### 3. Escalation (`reminders/escalation.py`)

Track state in local SQLite (`~/.local/share/jira-daily-reports/reminders.db`):

```sql
CREATE TABLE reminder_history (
  issue_key TEXT,
  policy_name TEXT,
  first_detected_at DATETIME,
  last_action_at DATETIME,
  action_count INTEGER,
  current_level INTEGER,  -- 0=silent, 1=tag, 2=label, 3=manager, 4=lead
  resolved_at DATETIME,
  PRIMARY KEY (issue_key, policy_name)
);
```

`Escalator.next_action(issue_key, policy)` returns the action to take based on day-since-first-detected.

### 4. Suppression (`reminders/suppression.py`)

Skip rules:
- **Grace period:** issue created < N hours ago
- **Off-hours:** outside 9 AM - 6 PM local time
- **Weekends:** Saturday/Sunday
- **Recent activity:** owner commented in last 24h
- **Snooze:** owner posted `@bot snooze 2d` in comments
- **Issue types:** drafts, sub-tasks of estimated parents, spike tickets
- **Labels:** `do-not-remind`, `wip-exception`

### 5. Runner (`reminders/runner.py`)

Orchestrates daily scan:

```python
def run_reminders(dry_run: bool = False) -> RunReport:
    policies = Policies.from_yaml("config/reminder-policies.yaml")
    suppressor = Suppressor()
    escalator = Escalator(db_path="~/.local/share/.../reminders.db")
    tagger = Tagger(jira)

    actions: list[Action] = []
    for policy in policies:
        issues = find_violations(jira, policy)  # JQL query
        for issue in issues:
            if suppressor.should_skip(issue, policy):
                continue
            action = escalator.next_action(issue.key, policy)
            if action.type == "tag_assignee":
                if not dry_run:
                    tagger.post_mention(issue.key, ...)
                actions.append(action)

    return RunReport(actions=actions, ran_at=datetime.now())
```

CLI: `jira-daily-reports remind --policy estimation --dry-run`

---

## Key Design Decisions

### D1: Cron over webhook for Phase 1-3
- Periodic scans catch tickets that were ALREADY in bad state
- Webhook only catches future transitions
- Simpler infra (no FastAPI server, no webhook secret rotation)
- Existing `jira-daily-reports` cron infrastructure reused

### D2: YAML policy DSL (not code)
- Non-developers (PMs) can edit policies
- Version-controlled in repo
- Pydantic schema validation prevents typos
- Hot-reload possible (re-read YAML on each cron run)

### D3: SQLite for state (not Redis/Postgres)
- Single-machine cron, no concurrent writes
- File-based, no service to manage
- Survives restarts
- Easy to inspect with `sqlite3`

### D4: ADF mentions (not text @username)
- Jira renders as proper notification (email + in-app)
- Plain `@username` doesn't trigger Jira notifications
- ADF is documented Atlassian standard

### D5: Defer real-time enforcement to Phase 4
- Cron + escalation handles 90% of cases
- Real-time webhook adds operational complexity (FastAPI, secret rotation, deployment)
- Validate Phase 1-3 actually changes behavior before investing in Phase 4

### D6: New repo for workflow-guard (when built)
- webhook-receiver is "MR Auto-Review" — adding Jira webhooks stretches scope
- Separate concern: enforcement vs review
- Clean dependency: jira-workflow-guard depends on tdt-core[jira] + jira-skill

### D7: Don't replace Jira automation rules
- Some teams already have Jira automation set up
- Allow opt-in per-policy: `enforce_via: jira_automation | python | both`
- Document the boundary clearly

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Reminders perceived as spam | Smart suppression, opt-out labels, snooze, off-hours skip |
| False positives on missing fields | Dry-run mode by default for first 2 weeks |
| Custom field IDs vary per project | Per-project YAML policies |
| Jira API rate limits | Respect 429 responses, backoff, batch where possible |
| State DB corruption | Daily backup of reminders.db, idempotent reminder logic |
| YAML policy errors break cron | Pydantic validation at load time, fail-fast with clear error |
| Account ID resolution fails | Cache results, fallback to plain text @username |

---

## Testing Strategy

- **Unit tests:** policies parsing, suppression rules, escalation state machine
- **Integration tests:** mock Jira client, verify ADF comment structure
- **Dry-run mode:** real Jira reads but no writes, manual review for 2 weeks
- **Canary:** enable for 1 policy on 1 project first
- **Audit log:** every action logged with timestamp, issue key, policy, level

---

## Future Extensions (out of scope here)

- Slack DM integration (when SMTP/Slack infra ready)
- Microsoft Teams integration
- Approval workflows (manager approves transition)
- ML-based estimation suggestions ("similar tickets averaged 5 points")
- Cross-project policies (multi-tenancy)
- Web dashboard showing reminder history per person
