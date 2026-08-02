# Real-Time Jira Transition Guard - Proposal

**Status:** Draft
**Date:** 2026-05-22
**Author:** lekhanhvinh
**Predecessor:** `openspec/changes/jira-intelligent-reminders/` (Phases 1-3 ✅)

---

## Problem

Phases 1-3 of `jira-intelligent-reminders` ship a cron-driven reminder runner
that scans for policy violations once a day at 09:00 weekdays. This works for
most cases, but creates blind spots:

- A developer transitions `POEMS2-100` to **In Progress** at 14:00 without
  setting `start_date`. The cron-based runner won't notice until 09:00 the next
  day — almost 19 hours of un-flagged drift.
- A QA engineer moves a ticket to **Test Done** without setting `duedate`. By
  the time the cron run catches it, sprint metrics already incorporate the
  wrong dates.
- "Just-in-time" reminders are far more effective at changing behaviour than
  next-day reminders. People remember the context of their own action.

The original Phase 4 in `jira-intelligent-reminders/tasks.md` deferred this
work pending evidence that real-time enforcement is needed. Two weeks of cron
operation has produced that evidence: a non-trivial fraction of violations
land between cron runs, and end-of-day reports still surface stale field
omissions that a real-time guard would have caught immediately.

---

## Goal

Catch policy violations within seconds of the offending Jira transition, post
a polite ADF `@mention` comment on the issue, and reuse all the existing
policy / suppression / escalation logic from `jira-daily-reports`.

Out of scope:
- Auto-reverting transitions (strict mode is explicitly deferred — humans stay
  in control of issue status).
- Slack / email delivery (still deferred until Phase 5 of intelligent reminders).
- New policy types beyond the three already shipped.

---

## Architectural Decision: Extend `webhook-receiver` (Option A)

The original design (`jira-intelligent-reminders/design.md` D6) suggested a
new repo `jira-workflow-guard`. After auditing the current infrastructure we
recommend extending `webhook-receiver` instead:

| Factor | New repo (`jira-workflow-guard`) | Extend `webhook-receiver` (chosen) |
|--------|----------------------------------|------------------------------------|
| FastAPI server | Build from scratch | Already running under launchd |
| Deployment | New `~/.tdt-jira-guard/app/` | Existing `~/.tdt-webhook-receiver/app/` |
| Auth + secret rotation | New scaffolding | Existing pattern reused |
| TLS / public endpoint | New ingress | Existing ngrok / reverse proxy |
| Ops surface | +1 service | Same surface |
| Code reuse | Duplicate request plumbing | Reuse routing, settings, audit log |
| Concern separation | Cleanest | Mixed (GitLab MR + Jira transitions) |

The "separation of concerns" cost is the one real downside of Option A. We
mitigate it by:
- Keeping all Jira-transition code under `webhook_receiver/jira_guard/`, a
  self-contained subpackage.
- Routing Jira webhooks at `/webhooks/jira/transition` (different prefix from
  GitLab routes).
- Documenting the boundary in `webhook-receiver/AGENTS.md`.

If the Jira surface grows large enough later (Phase 5 — automated transition
reverts, role routing, multi-tenant policies), splitting `jira_guard/` into a
standalone repo is straightforward — it's already isolated.

---

## High-Level Design

```
Jira Cloud                              webhook-receiver
                                        (existing FastAPI + launchd)

┌──────────────────┐  POST /webhooks/   ┌──────────────────────────────┐
│ Issue transition │  jira/transition   │ jira_guard/                  │
│ status: In Prog  │ ─────────────────→ │  api.py     receive + verify │
│ assignee: alice  │   (HMAC-signed)    │  events.py  parse + classify │
└──────────────────┘                    │  guard.py   policies + skip  │
                                        │             + escalate       │
                                        └─────────────┬────────────────┘
                                                      │ uses (path dep)
                                                      ▼
                                        jira-daily-reports
                                        ├── reminders/policies.py
                                        ├── reminders/tagger.py
                                        ├── reminders/suppression.py
                                        └── reminders/escalation.py
                                                      │
                                                      ▼
                                        tdt-core
                                        └── clients/jira.py (PatchedJira)
                                                      │
                                                      ▼
                                        Jira Cloud REST API
                                        POST /rest/api/3/issue/{key}/comment
                                        (ADF @mention)
```

The new service does not own policy state — it imports the same modules the
cron runner uses, ensuring identical behaviour for "what is a violation" and
"who has been reminded recently".

---

## Why This Works Well

1. **Reuse, not rewrite.** Every policy/suppression/escalation rule already
   tested in `jira-daily-reports` carries over unchanged.
2. **One source of truth for state.** Both runners read/write the same
   `~/.local/share/jira-daily-reports/reminders.db`, so cron and webhook agree
   on "level" and "last_action_at".
3. **Defensive in depth.** Cron continues to run as the safety net even if
   webhooks are dropped, mis-signed, or the service is offline briefly.
4. **Idempotent.** A duplicate webhook delivery for the same transition is a
   no-op because the escalator records the action and suppresses duplicates.
5. **Local-first deployment.** Same launchd-managed runtime under
   `~/.tdt-webhook-receiver/app/` — no new ops to learn.

---

## Success Criteria

- Jira webhooks for issue transitions land at `/webhooks/jira/transition`,
  HMAC-verified, returning HTTP 200 within 500 ms.
- A transition to **In Progress** without `start_date` produces an ADF
  `@mention` comment within 10 s end-to-end (cron → webhook drift < 1 day).
- The same `reminder-policies.yaml` drives both cron and webhook decisions —
  no duplicate policy file.
- Suppression rules (off-hours, snooze label, grace period) apply identically.
- Two transitions for the same issue + policy in 24 h produce at most one
  reminder (escalation state shared with cron).
- ≥80 % unit test coverage on new modules; live test against real Jira
  webhook delivery before declaring done.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Webhook spam from Jira automation rules firing repeatedly | HMAC verification + escalator dedupe |
| Wrong webhook secret deployed → all events 401 | Health check probes the verifier with a known-good fixture |
| Mixing GitLab + Jira concerns in one service | Strict subpackage isolation + routing prefix; ready to split later |
| webhook-receiver downtime drops events | Cron remains the safety net; Jira webhook retries 5× over 24 h |
| Real-time reminder still too noisy | Same suppression rules + 1 h grace per policy (configurable in YAML) |
