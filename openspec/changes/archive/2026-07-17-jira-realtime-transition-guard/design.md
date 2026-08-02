# Real-Time Jira Transition Guard - Design

**Date:** 2026-05-22

---

## Module Layout

```
webhook-receiver/src/webhook_receiver/
├── gitlab/                    (existing — GitLab MR review)
│   ├── client.py
│   ├── worktree.py
│   └── routes.py
├── jira_guard/                ← NEW subpackage
│   ├── __init__.py
│   ├── routes.py              (FastAPI router: /webhooks/jira/transition)
│   ├── events.py              (parse Jira webhook payload → TransitionEvent)
│   ├── hmac_verify.py         (HMAC-SHA256 signature verification)
│   └── guard.py               (orchestrate: validate → suppress → escalate → tag)
├── config/
│   └── settings.py            (add JIRA_WEBHOOK_SECRET)
└── main.py                    (mount jira_guard router)
```

---

## Data Flow

### 1. Jira Webhook Payload (incoming)

Jira Cloud sends `jira:issue_updated` with changelog:

```json
{
  "webhookEvent": "jira:issue_updated",
  "issue_event_type_name": "issue_generic",
  "timestamp": 1716364800000,
  "user": {"accountId": "5f...abc", "displayName": "Alice"},
  "issue": {
    "key": "POEMS2-100",
    "fields": {
      "status": {"name": "In Progress"},
      "assignee": {"accountId": "5f...abc", "displayName": "Alice"},
      "priority": {"name": "Medium"},
      "customfield_10015": null,
      "duedate": null,
      "story_points": null
    }
  },
  "changelog": {
    "items": [
      {
        "field": "status",
        "fieldtype": "jira",
        "from": "10000",
        "fromString": "To Do",
        "to": "10001",
        "toString": "In Progress"
      }
    ]
  }
}
```

### 2. TransitionEvent (parsed)

```python
@dataclass
class TransitionEvent:
    issue_key: str
    from_status: str
    to_status: str
    actor_account_id: str
    assignee_account_id: str | None
    fields: dict[str, Any]  # current field values
    timestamp: datetime
```

### 3. Guard Decision Flow

```python
def handle_transition(event: TransitionEvent) -> GuardResult:
    # 1. Load policies matching this transition
    policies = load_policies_for_status(event.to_status)
    if not policies:
        return GuardResult(action="none", reason="no matching policy")

    # 2. For each matching policy, check required fields
    for policy in policies:
        missing = check_required_fields(event.fields, policy)
        if not missing:
            continue  # all fields present, no violation

        # 3. Check suppression
        skip, reason = suppressor.should_skip(event, policy)
        if skip:
            return GuardResult(action="suppressed", reason=reason)

        # 4. Check escalation state (dedup within 24h)
        action = escalator.next_action(event.issue_key, policy)
        if action.type == "already_reminded":
            return GuardResult(action="dedup", reason="reminded today")

        # 5. Post @mention
        tagger.post_mention(
            event.issue_key,
            event.assignee_account_id or event.actor_account_id,
            policy.message_template.format(field_name=missing[0])
        )
        return GuardResult(action="reminded", policy=policy.name)
```

---

## HMAC Verification

Jira Cloud signs webhook payloads with HMAC-SHA256 using the webhook secret:

```python
import hashlib
import hmac

def verify_jira_webhook(body: bytes, signature: str, secret: str) -> bool:
    """Verify Jira webhook HMAC-SHA256 signature.

    Jira sends the signature in the X-Hub-Signature header as 'sha256=<hex>'.
    """
    expected = hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

Secret stored in `~/.tdt/.env` as `JIRA_WEBHOOK_SECRET`.

---

## Shared State with Cron Runner

Both the webhook guard and the cron runner (`jira-daily-reports remind`) share:

| Resource | Path | Access Pattern |
|----------|------|----------------|
| Policies YAML | `jira-daily-reports/config/reminder-policies.yaml` | Read-only at request time |
| Escalation DB | `~/.local/share/jira-daily-reports/reminders.db` | Read-write (SQLite WAL mode) |
| Audit log | `~/.tdt/logs/jira-reminders.log` | Append-only |

SQLite WAL mode allows concurrent reads from cron while webhook writes, without
blocking. The escalator's `next_action()` is already idempotent — calling it
twice for the same issue+policy+day returns the same result.

---

## Dependency Strategy

The webhook-receiver needs access to `jira-daily-reports` reminders modules.
Options:

| Strategy | Pros | Cons |
|----------|------|------|
| **A. Path dependency** (`tdt-core` + `jira-daily-reports` as path deps) | Simple, local-first | legacy cloud .pth issue |
| **B. Import from installed package** | Clean, pip-standard | Requires `uv pip install -e ../jira-daily-reports` |
| **C. Copy shared code** | No cross-repo dep | Drift, duplication |

**Chosen: B** — `webhook-receiver/pyproject.toml` adds `jira-daily-reports` as
a path dependency (same pattern as `tdt-core` dependency). The `.pth` workaround
applies. At runtime (launchd), the deploy script installs both editable deps.

```toml
# webhook-receiver/pyproject.toml
dependencies = [
    "tdt-core",
    "jira-daily-reports",  # for reminders.policies, tagger, suppression, escalation
    ...
]

[tool.uv.sources]
tdt-core = { path = "../tdt-core", editable = true }
jira-daily-reports = { path = "../jira-daily-reports", editable = true }
```

---

## Jira Webhook Registration

One-time setup via Jira Cloud admin or REST API:

```bash
curl -u "$ATLASSIAN_EMAIL:$ATLASSIAN_ACCESS_TOKEN" \
  -X POST \
  -H "Content-Type: application/json" \
  "https://psplit.atlassian.net/rest/api/3/webhook" \
  -d '{
    "url": "https://<your-public-endpoint>/webhooks/jira/transition",
    "webhooks": [{
      "events": ["jira:issue_updated"],
      "jqlFilter": "project = POEMS2"
    }],
    "secret": "<JIRA_WEBHOOK_SECRET>"
  }'
```

Or via Jira UI: Settings → System → Webhooks → Create.

**Public endpoint options:**
- Tailscale Funnel (current): `https://les-mac-mini.tailc6b508.ts.net` — already serving GitLab webhook on same port
- Cloudflare Tunnel (alternative): `cloudflared tunnel --url http://localhost:8080`
- ngrok (dev only): `ngrok http 8080`

---

## Configuration

New settings in `webhook-receiver/config/settings.py`:

```python
# Jira Guard settings
JIRA_WEBHOOK_SECRET: str = ""  # HMAC verification secret
JIRA_GUARD_ENABLED: bool = True  # kill switch
JIRA_GUARD_DRY_RUN: bool = True  # default dry-run for safety
JIRA_GUARD_POLICIES_PATH: Path = Path("../jira-daily-reports/config/reminder-policies.yaml")
```

---

## Error Handling

| Scenario | Response | Side Effect |
|----------|----------|-------------|
| Invalid HMAC signature | 401 Unauthorized | Log warning |
| Malformed payload (no changelog) | 200 OK (ignore) | Log debug |
| Non-status-change event | 200 OK (ignore) | None |
| Policy load failure | 500 Internal | Log error, alert |
| Tagger API failure (Jira down) | 200 OK (retry later) | Log error, cron catches next day |
| SQLite lock contention | Retry 3× with backoff | Log warning |

Always return 200 for non-critical failures to prevent Jira from disabling the
webhook (Jira disables after repeated 4xx/5xx).

---

## Testing Strategy

- **Unit tests:** event parsing, HMAC verification, guard decision logic
- **Integration tests:** mock FastAPI TestClient, verify full request → response
- **Live test:** ngrok + real Jira webhook, transition a test issue, verify comment appears
- **Regression:** existing webhook-receiver GitLab tests still pass
