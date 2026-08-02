# Jira Intelligent Reminders - Specification

**Status:** ✅ Implemented  
**Version:** 0.1.0  
**Date:** 2026-05-21

---

## 1. Overview

Active reminder system that posts @mention comments on Jira tickets with missing required fields, with role-aware routing, escalation ladder, and smart suppression. Optional real-time transition enforcement via webhook (Phase 4+).

---

## 2. Functional Requirements

### FR1: Policy Definition (YAML DSL)

**Priority:** Critical  
**Status:** ✅ Implemented

**Description:** Field-required policies defined in version-controlled YAML, loadable per project.

**Acceptance Criteria:**
- [ ] YAML policy file at `config/reminder-policies.yaml` (or per-project)
- [ ] Pydantic schema validates: name, role, issue_types, statuses, required_fields, escalation
- [ ] Schema validation fails fast with clear error on malformed YAML
- [ ] Hot-reload: re-read YAML on each cron run (no daemon restart needed)
- [ ] Per-project policies: `policies/{project_key}.yaml`

**Verification:**
```bash
uv run jira-daily-reports remind --validate-policies
# Expected: "All policies valid" or specific error
```

### FR2: @mention Tagging via ADF

**Priority:** Critical  
**Status:** ✅ Implemented

**Description:** Post Jira comments with proper @mentions using Atlassian Document Format so notifications fire.

**Acceptance Criteria:**
- [ ] `Tagger.post_mention(issue_key, account_id, message)` method
- [ ] Uses ADF JSON structure (mention node, not plain `@username` text)
- [ ] Resolves account_id from assignee field (no extra API call)
- [ ] Falls back to plain `@username` text if account_id unresolvable
- [ ] Verifies mention triggered notification (Jira returns mention metadata)

**Verification:**
```bash
uv run jira-daily-reports remind --policy estimation --issue POEMS2-100 --dry-run
# Expected: Shows ADF body that would be posted
```

### FR3: Escalation Ladder

**Priority:** High  
**Status:** ✅ Implemented

**Description:** Day-N rules that escalate severity if issue stays in bad state.

**Acceptance Criteria:**
- [ ] Default ladder: day 1 (silent), day 2 (tag owner), day 4 (add label), day 6 (tag manager), day 8 (tag team lead)
- [ ] Per-policy override of ladder
- [ ] State persisted in SQLite (`~/.local/share/jira-daily-reports/reminders.db`)
- [ ] `Escalator.next_action(issue_key, policy)` returns ActionType enum
- [ ] Idempotent: re-running same day produces same action
- [ ] Resolution tracking: when field appears, mark resolved, reset counter

**Verification:**
```bash
uv run jira-daily-reports remind --show-history --policy estimation
# Expected: Table of issues, days-in-violation, current escalation level
```

### FR4: Smart Suppression

**Priority:** High  
**Status:** ✅ Implemented

**Description:** Skip reminders that would be perceived as spam.

**Acceptance Criteria:**
- [ ] Grace period: skip if issue created < N hours ago (configurable per policy)
- [ ] Off-hours: skip outside 9 AM - 6 PM local timezone
- [ ] Weekends: skip Saturday/Sunday
- [ ] Recent activity: skip if assignee commented in last 24h
- [ ] Snooze: skip if owner posted `@bot snooze 2d` in comments
- [ ] Issue type filter: drafts, sub-tasks of estimated parents, spike tickets
- [ ] Label filter: `do-not-remind`, `wip-exception`

**Verification:**
```bash
uv run jira-daily-reports remind --policy estimation --explain POEMS2-100
# Expected: "Skipped: weekend" or "Action: tag_assignee (day 3)"
```

### FR5: Role-Aware Routing

**Priority:** High  
**Status:** ✅ Implemented

**Description:** Route reminders to the right person based on field type and role.

**Acceptance Criteria:**
- [ ] `assignee` role: tag the issue assignee (default for dev fields)
- [ ] `qa_owner` role: tag user from custom field (for QA fields)
- [ ] `reporter` role: tag the reporter (for acceptance criteria)
- [ ] `manager` role: tag manager from Atlassian org chart (escalation only)
- [ ] `lead` role: tag team lead from project config (final escalation)
- [ ] Fallback: if role resolves to None, log warning, skip

**Verification:**
```bash
uv run jira-daily-reports remind --resolve-roles --issue POEMS2-100
# Expected: assignee=alice@..., qa_owner=bob@..., manager=charlie@...
```

### FR6: Dry-Run Mode

**Priority:** Critical  
**Status:** ✅ Implemented

**Description:** Default to dry-run for first 2 weeks. Show what WOULD happen without actually posting.

**Acceptance Criteria:**
- [ ] `--dry-run` flag (default: true for first 2 weeks via env var)
- [ ] Lists all actions that would be taken
- [ ] Shows ADF body for each comment
- [ ] No API writes performed
- [ ] Output format: terminal (rich table) + markdown report

**Verification:**
```bash
uv run jira-daily-reports remind --dry-run
# Expected: "Would tag @alice on POEMS2-100 (missing story_points)"
# No actual comment posted
```

### FR7: Audit Log

**Priority:** High  
**Status:** ✅ Implemented

**Description:** Every action logged with full context for compliance/debugging.

**Acceptance Criteria:**
- [ ] Log entry per action: timestamp, issue_key, policy_name, action_type, account_id, success
- [ ] Stored in SQLite alongside escalation state
- [ ] CLI: `remind --audit-log --since 7d` shows recent activity
- [ ] Export: `remind --audit-log --export csv > audit.csv`

**Verification:**
```bash
uv run jira-daily-reports remind --audit-log --since 1d
# Expected: Table with timestamp, issue, action, status
```

### FR8: Cron Integration

**Priority:** Critical  
**Status:** ✅ Implemented

**Description:** Run automatically on schedule, independent of manual invocation.

**Acceptance Criteria:**
- [ ] Cron schedule: weekdays 9:00 AM
- [ ] Integrated with existing `jira-daily-reports schedule` command
- [ ] Failure mode: log error, retry next cycle, don't crash cron
- [ ] Output: write summary to `~/reports-out/reminders-{date}.md`

**Verification:**
```bash
uv run jira-daily-reports schedule | grep remind
# Expected: cron entry for 'remind' command at 9 AM weekdays
```

### FR9: Transition Enforcement (Phase 4 — DEFERRED)

**Priority:** Medium  
**Status:** ❌ Deferred to Phase 4

**Description:** Real-time validation when ticket status changes.

**Acceptance Criteria (when implemented):**
- [ ] FastAPI server in NEW `jira-workflow-guard` repo
- [ ] Receives Jira webhook on `jira:issue_updated` event
- [ ] On transition to In Progress: require start_date or post immediate @mention
- [ ] On transition to Test Done: require end_date (or duedate)
- [ ] Optional: revert transition if `enforce_strict: true` in policy
- [ ] Webhook signature validation (HMAC-SHA256 with secret)

---

## 3. Non-Functional Requirements

### NFR1: Performance
- Cron run completes in < 60 seconds for 200 tickets
- Single API call per JQL query (paginated)
- Batch comment posts where possible (Jira allows bulk via REST)

### NFR2: Reliability
- Idempotent: same input → same output
- State persisted across runs
- Failed actions retried next cycle (max 3 attempts)

### NFR3: Observability
- Structured logging (timestamp, issue, policy, action, success)
- Metrics: actions_per_day, suppression_rate, resolution_rate
- Dry-run reports inspectable

### NFR4: Configurability
- All thresholds in YAML (no hardcoded magic numbers)
- Per-policy override of suppression rules
- Per-project override of role resolution

### NFR5: Security
- No secrets in policy YAML
- Jira credentials from `~/.tdt/.env` only (via tdt-core)
- SQLite DB user-readable only (chmod 600)

---

## 4. Out of Scope (Phase 1-3)

- Slack/email/Teams delivery (no infrastructure configured)
- Approval workflows (manager approves transition)
- ML-based estimation suggestions
- Cross-project policy aggregation (single project first)
- Web dashboard
- Mobile app integration

---

## 5. Migration & Rollout

**Week 1:** Deploy in dry-run mode. Manual review of would-be actions.
**Week 2:** Enable for 1 policy (estimation) on 1 project (POEMS2). Monitor adoption.
**Week 3:** Enable remaining policies if Week 2 well-received.
**Week 4:** Evaluate Phase 4 (real-time enforcement) based on residual gaps.

---

## 6. Success Metrics

After 1 month:
- 80% of tickets have estimation before sprint planning
- 100% of In Progress tickets have start_date within 24h
- 100% of Test Done tickets have end_date
- < 5 tickets per sprint reach QA without metadata
- < 2 complaints per week about reminder frequency
- Resolution rate (action → field filled) > 70%
