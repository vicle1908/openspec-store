# Jira Intelligent Reminders - Proposal

**Status:** Draft  
**Date:** 2026-05-21  
**Author:** lekhanhvinh  
**Placement:** Extend `jira-daily-reports` (Phase 1-3) + NEW `jira-workflow-guard` (Phase 4-5)

---

## Problem

Tickets in POEMS2 regularly reach sprint planning or QA handoff with missing critical fields:
- **No estimation** → sprint capacity planning fails
- **No assignee** on In Progress → accountability gap
- **No start_date** when entering In Progress → velocity metrics broken
- **No end_date** when entering Test Done → cycle time unmeasurable
- **No QA owner** → test handoff delayed
- **No labels** → platform distribution reports inaccurate

Current `missing-info` report in jira-daily-reports identifies gaps passively (markdown output). Nobody acts on it because there's no direct notification to the responsible person.

---

## Proposed Solution

Two-tier system:

1. **Periodic intelligent reminders** (cron-based, extend jira-daily-reports)
   - Daily scan for missing fields
   - Post @mention comments on Jira tickets tagging the responsible person
   - Role-aware routing (dev → estimation, QA → test plan, reporter → acceptance criteria)
   - Escalation ladder (day 1 → owner, day 3 → label, day 5 → manager)
   - Smart suppression (grace period, snooze, off-hours)

2. **Real-time transition enforcement** (webhook-based, new service — Phase 4+)
   - Validate required fields on status transitions
   - Block or warn when moving to In Progress without start_date
   - Block or warn when moving to Test Done without end_date
   - Post immediate @mention if field missing at transition time

---

## Why Now

- Sprint 14 had 12 tickets reach "In Progress" without estimation
- QA reported 8 tickets arrived at "Code Review" without test plan links
- Velocity reports show gaps because start/end dates missing on 40% of tickets
- Team size growing (10+ devs) — peer pressure no longer sufficient

---

## Scope

### In Scope
- @mention tagging via Jira ADF comments
- Per-role field policies (YAML-configurable)
- Escalation ladder with day-N rules
- Smart suppression (grace period, snooze, off-hours)
- Transition field requirements (start_date, end_date)
- CLI commands for manual trigger + dry-run

### Out of Scope
- Slack/email delivery (deferred — no infra)
- Jira automation rule creation (manual setup, documented)
- Custom field creation in Jira (admin task)
- Approval workflows
- Cross-project policies (single project POEMS2 first)

---

## Success Criteria

1. 80% of tickets have estimation before sprint planning
2. 100% of In Progress tickets have start_date within 24h
3. 100% of Test Done tickets have end_date
4. < 5 tickets per sprint reach QA without required metadata
5. Team satisfaction: reminders perceived as helpful, not noisy

---

## Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| Jira Cloud automation rules only | Try first (free, native). Limitations: no escalation, no smart suppression, no audit trail |
| Separate `jira-reminders` repo | Overkill for Phase 1. Revisit if scope grows beyond daily-reports |
| Webhook-only (no cron) | Misses tickets that were already in bad state before webhook installed |
| Manual process (PM checks daily) | Current state. Doesn't scale past 10 devs |

---

## Decision

**Phase 1-3:** Add `reminders/` module to `jira-daily-reports` (cron-based @mentions).  
**Phase 4-5:** Evaluate after 2 weeks. If real-time enforcement needed, create `jira-workflow-guard`.  
**Immediate:** Document Jira automation rules for start_date/end_date as interim solution.
