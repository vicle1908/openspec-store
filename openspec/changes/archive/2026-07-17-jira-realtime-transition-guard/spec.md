# Real-Time Jira Transition Guard - Specification

**Status:** Draft
**Version:** 0.1.0
**Date:** 2026-05-22

---

## ADDED Requirements

### Requirement: Real-time Jira transition events are guarded consistently
The workspace SHALL expose a Jira transition webhook guard that verifies HMAC signatures, detects status transitions, applies reminder policies, suppresses duplicates, supports dry-run mode, and reports health.

#### Scenario: A valid transition event is received
- **WHEN** Jira sends a signed `jira:issue_updated` webhook with a status change in the changelog
- **THEN** the guard verifies the signature, evaluates matching reminder policies, and returns HTTP 200

#### Scenario: A request fails signature verification
- **WHEN** the webhook signature is invalid or missing
- **THEN** the guard rejects the request with HTTP 401 and does not process the payload

#### Scenario: A reminder is suppressed or deduplicated
- **WHEN** the matching policy is already satisfied, suppressed, or deduplicated within the cooldown window
- **THEN** the guard returns HTTP 200 without posting a Jira comment

#### Scenario: Health and dry-run state are exposed
- **WHEN** the guard health endpoint is queried
- **THEN** the response reports whether the guard is enabled, dry-run is active, policies are loaded, and the database path is configured

## Functional Requirements

### FR1 — Webhook Endpoint

The service MUST expose `POST /webhooks/jira/transition` accepting Jira Cloud
webhook payloads of type `jira:issue_updated`.

- Content-Type: `application/json`
- Maximum payload size: 1 MB
- Response within 500 ms (p95)
- Returns HTTP 200 on success, including for events that result in no action

### FR2 — HMAC Signature Verification

Every incoming request MUST be verified against the shared secret before any
processing.

- Algorithm: HMAC-SHA256
- Header: `X-Hub-Signature: sha256=<hex>`
- Secret source: `JIRA_WEBHOOK_SECRET` env var
- Failure: respond 401 Unauthorized, log warning, no processing
- Constant-time comparison (`hmac.compare_digest`) to prevent timing attacks

### FR3 — Transition Detection

The guard MUST identify status changes from the webhook `changelog` field.

- Iterate `changelog.items[]`
- Match `field == "status"`
- Extract `fromString` and `toString`
- Skip events with no status change in changelog (return 200, log debug)

### FR4 — Policy Matching

For each detected transition, the guard MUST match against policies whose
`statuses` list contains the new status.

- Policies loaded from `jira-daily-reports/config/reminder-policies.yaml`
- Reload on each request (config drift detection) — acceptable since YAML is
  small and parsing is fast
- Multiple policies may match a single transition (all are evaluated)

### FR5 — Required Field Validation

For each matching policy, the guard MUST check whether the issue has all
`required_fields` populated.

- Field values come from the webhook payload's `issue.fields` (no extra fetch)
- Empty values: `null`, empty string, empty list, missing key
- Custom fields referenced by ID (`customfield_10015`) or alias from policy
- If all required fields present: no action, log info "policy satisfied"

### FR6 — Suppression Reuse

When a violation is detected, the guard MUST consult the same suppression
rules used by the cron runner.

- Source: `jira_daily_reports.reminders.suppression.Suppressor`
- Rules: grace_period, off_hours, weekends, recent_activity, snooze, labels
- If suppressed: respond 200, log skip with reason, no Jira write

### FR7 — Escalation Deduplication

The guard MUST consult the shared escalation database to prevent duplicate
reminders for the same issue + policy within 24 hours.

- Source: `jira_daily_reports.reminders.escalation.Escalator`
- Path: `~/.local/share/jira-daily-reports/reminders.db`
- SQLite WAL mode for concurrent access with cron runner
- If escalator returns "already_reminded": no Jira write, log dedup

### FR8 — Reminder Posting

When all checks pass, the guard MUST post an ADF `@mention` comment on the
issue.

- Use `jira_daily_reports.reminders.tagger.Tagger.post_mention()`
- Target account ID: assignee preferred, actor as fallback
- Message from policy `message_template` with field name interpolated
- Update escalation state after successful post

### FR9 — Dry-Run Mode

The guard MUST support a dry-run mode that performs all checks but skips the
final Jira write.

- Env var: `JIRA_GUARD_DRY_RUN=true` (default for first 2 weeks)
- Logs: `[DRY-RUN] Would tag @<account_id> on <issue_key>`
- Still updates escalation state (so cron doesn't double-remind)

### FR10 — Kill Switch

The guard MUST support a global enable/disable flag.

- Env var: `JIRA_GUARD_ENABLED=false` causes immediate 200 OK with no
  processing
- Useful for incident response without redeploying

### FR11 — Audit Logging

Every webhook event MUST be logged with structured JSON.

- Path: `~/.tdt/logs/jira-reminders.log`
- Same format as cron runner so logs are uniform
- Fields: `timestamp`, `issue_key`, `from_status`, `to_status`,
  `policy_name`, `action`, `reason`, `actor_account_id`, `dry_run`

### FR12 — Idempotency

Re-delivery of the same webhook event (Jira retries up to 5×) MUST NOT cause
duplicate reminders.

- Achieved via FR7 (escalation dedup)
- Webhook ID (if provided) logged for traceability

### FR13 — Health Check

The service MUST expose `GET /webhooks/jira/health` returning 200 with body
including:

- `enabled`: bool
- `dry_run`: bool
- `policies_loaded`: int
- `db_path`: string
- `last_event_at`: ISO 8601 timestamp or null

---

## Non-Functional Requirements

### NFR1 — Performance
- p95 latency ≤ 500 ms end-to-end (from request received to 200 returned)
- p99 ≤ 2 s (covers Jira API call latency for tagger)
- Throughput: ≥ 50 events/min sustained

### NFR2 — Reliability
- Returns 200 for any non-security failure (so Jira doesn't disable webhook)
- Cron runner remains the safety net for missed events
- Service restart cleanly resumes — no in-memory state to lose

### NFR3 — Security
- HMAC verification mandatory; no bypass
- Secret stored only in `~/.tdt/.env` (never in repo)
- Webhook URL not logged in full (last 4 chars only)
- Payload not stored at rest (audit log records summary only)

### NFR4 — Observability
- Structured logs (`~/.tdt/logs/jira-reminders.log`)
- Metrics endpoint (Prometheus-style) at `/metrics` showing:
  - `jira_guard_events_total{action="reminded|suppressed|dedup|none"}`
  - `jira_guard_latency_seconds` (histogram)
  - `jira_guard_errors_total{type="..."}`

### NFR5 — Maintainability
- All Jira-specific code under `webhook_receiver/jira_guard/`
- ≥ 80 % unit test coverage on new modules
- Type hints throughout (mypy strict for new code)
- No new dependencies on top of `tdt-core` + `jira-daily-reports`

---

## Out-of-Scope

- Auto-reverting transitions (strict mode) — humans stay in control
- Slack / email delivery — Phase 5 of intelligent reminders
- Multi-tenant policy routing (different rules per project) — already supported
  by YAML, but no UI / admin tooling planned here
- Web dashboard for browsing reminder history
- ML-based field suggestions ("similar tickets averaged 5 points")

---

## Open Questions

| # | Question | Resolution path |
|---|----------|-----------------|
| Q1 | Public endpoint: ngrok (dev) vs Cloudflare Tunnel (prod)? | Pick during Task 4.5 (deployment) |
| Q2 | Webhook scope: per-project or site-wide? | Start with `project = POEMS2` JQL filter; expand if needed |
| Q3 | Should we register the webhook automatically via Task 4.6, or one-time manual? | Manual one-time for safety; document in runbook |
| Q4 | What happens if `jira-daily-reports` is uninstalled? | Service fails fast at startup with clear error; document |

---

## Acceptance Tests

### AT1 — Happy path
Given a transition `To Do → In Progress` for `POEMS2-100` where `start_date`
is empty and the assignee has not been reminded today,
when Jira posts the webhook,
then within 10 s a comment with `@<assignee>` appears on the issue and an
audit log entry records `action=reminded`.

### AT2 — Suppression: off-hours
Given the same transition at 23:30 local time,
when the webhook fires,
then no comment is posted and the audit log records `action=suppressed
reason=off_hours`.

### AT3 — Dedup
Given two transitions for the same issue + policy within 1 hour,
when both webhooks fire,
then exactly one comment is posted and the second event logs `action=dedup`.

### AT4 — Bad signature
Given a webhook with an invalid HMAC,
when received,
then response is 401, no policy code runs, and a warning is logged.

### AT5 — Cron compatibility
Given the webhook posts a reminder for `POEMS2-100` at 14:00,
when the cron runner runs at 09:00 the next morning,
then the cron runner sees the existing escalation state and does NOT
re-remind the same level.

### AT6 — Disabled
Given `JIRA_GUARD_ENABLED=false`,
when any webhook fires,
then response is 200 OK with no processing and audit log records
`action=disabled`.
