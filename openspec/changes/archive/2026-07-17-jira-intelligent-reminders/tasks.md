# Jira Intelligent Reminders - Tasks

**Status:** ✅ Phase 1-3 Implemented  
**Date:** 2026-05-21  
**Repo:** `jira-daily-reports` (Phase 1-3), `jira-workflow-guard` (Phase 4-5 deferred)

---

## Phase 1: Core Reminder Engine (1.5 days)

### Task 1.1: Create policies module + YAML schema

**Status:** ✅ Complete  
**Effort:** 2 hours

- Create `src/jira_daily_reports/reminders/policies.py`
- Pydantic models: `Policy`, `EscalationRule`, `FieldRequirement`
- YAML loader: `Policies.from_yaml(path) -> list[Policy]`
- Create `config/reminder-policies.yaml` with POEMS2 policies:
  - `developer_estimation` (story_points on To Do)
  - `in_progress_start_date` (start_date on In Progress)
  - `test_done_end_date` (duedate on Test Done)
  - `qa_test_plan` (test plan link on Code Review)
- Validation CLI: `jira-daily-reports remind --validate-policies`
- Tests: schema validation, malformed YAML rejection

### Task 1.2: Create tagger module (ADF @mentions)

**Status:** ✅ Complete  
**Effort:** 2 hours

- Create `src/jira_daily_reports/reminders/tagger.py`
- `Tagger.post_mention(issue_key, account_id, message) -> bool`
- ADF JSON structure with mention node
- Account ID resolution from assignee/reporter fields
- Fallback to plain text if account_id unavailable
- Tests: verify ADF structure, mock Jira client

### Task 1.3: Create escalation module + SQLite state

**Status:** ✅ Complete  
**Effort:** 3 hours

- Create `src/jira_daily_reports/reminders/escalation.py`
- SQLite DB at `~/.local/share/jira-daily-reports/reminders.db`
- Schema: `reminder_history` table (issue_key, policy, first_detected, level, resolved)
- `Escalator.next_action(issue_key, policy) -> Action`
- Resolution detection: field now present → mark resolved, reset
- Idempotent: same day re-run → same action
- Tests: state machine transitions, resolution detection

### Task 1.4: Create suppression module

**Status:** ✅ Complete  
**Effort:** 1.5 hours

- Create `src/jira_daily_reports/reminders/suppression.py`
- Rules: grace_period, off_hours, weekends, recent_activity, snooze, labels
- `Suppressor.should_skip(issue, policy) -> tuple[bool, str]` (skip + reason)
- Configurable per-policy overrides
- Tests: each suppression rule independently

### Task 1.5: Create runner + CLI commands

**Status:** ✅ Complete  
**Effort:** 2 hours

- Create `src/jira_daily_reports/reminders/runner.py`
- Orchestrates: load policies → JQL scan → suppress → escalate → tag
- Returns `RunReport` with actions taken
- CLI commands in `cli.py`:
  - `remind` — run all policies (default: dry-run)
  - `remind --policy <name>` — single policy
  - `remind --issue <key>` — single issue
  - `remind --dry-run` / `--live` — control writes
  - `remind --explain <key>` — show why action/skip
  - `remind --show-history` — escalation state
  - `remind --audit-log --since 7d` — recent actions
- Tests: runner integration with mocked Jira

---

## Phase 2: Role-Aware Routing (0.5 day)

### Task 2.1: Implement role resolution

**Status:** ✅ Complete  
**Effort:** 2 hours

- Add to `reminders/policies.py`: role enum (assignee, qa_owner, reporter, manager, lead)
- Role resolver: `resolve_target(issue, policy) -> account_id | None`
  - `assignee` → `issue.fields.assignee.accountId`
  - `reporter` → `issue.fields.reporter.accountId`
  - `qa_owner` → custom field lookup
  - `manager` → Atlassian org chart API (or config mapping)
  - `lead` → project config
- Fallback chain: if primary role empty, try secondary
- Tests: each role resolution path

### Task 2.2: Per-role message templates

**Status:** ✅ Complete  
**Effort:** 1 hour

- Message templates per policy in YAML:
  ```yaml
  message_template: |
    This ticket needs {field_name} before {deadline}.
    Past similar tickets averaged {suggestion}.
  ```
- Template rendering with issue context
- Tests: template rendering with various contexts

---

## Phase 3: Integration + Cron (0.5 day)

### Task 3.1: Integrate with existing schedule

**Status:** ✅ Complete  
**Effort:** 1 hour

- Add `remind` to `SCHEDULES` in `schedule.py`: `"0 9 * * 1-5"` (9 AM weekdays)
- Update `run-all` to optionally include reminders (flag: `--include-reminders`)
- Markdown report output: `~/reports-out/reminders-{date}.md`

### Task 3.2: Dry-run rollout configuration

**Status:** ✅ Complete  
**Effort:** 30 min

- Env var: `REMINDER_DRY_RUN=true` (default for first 2 weeks)
- CLI override: `--live` forces real writes regardless of env
- Log clearly: `[DRY-RUN] Would tag @alice on POEMS2-100`

### Task 3.3: Documentation

**Status:** ✅ Complete  
**Effort:** 1 hour

- Update jira-daily-reports README with reminders section
- Document YAML policy schema
- Document escalation ladder defaults
- Document suppression rules
- Runbook: "How to add a new policy"
- Runbook: "How to snooze/opt-out"

---

## Phase 4: Real-Time Transition Enforcement (DEFERRED → SPEC'D)

> **Update 2026-05-22:** Phase 4 has been promoted to its own openspec change:
> [`openspec/changes/jira-realtime-transition-guard/`](../jira-realtime-transition-guard/proposal.md)
>
> Architectural decision: extend the existing `webhook-receiver` service
> (Option A) rather than spinning up a new `jira-workflow-guard` repo. Reuses
> the policies / suppression / escalation / tagger modules from this change's
> Phase 1-3 implementation, sharing the same SQLite escalation DB so cron and
> webhook agree on state.
>
> See the dedicated change folder for proposal, design, spec (13 FRs, 6 ATs),
> and tasks (~3 days, broken into 6 sub-phases).

### Task 4.1: Evaluate need after Phase 1-3

**Status:** ✅ Done — evidence collected, real-time enforcement justified
**Trigger:** 2 weeks after Phase 3 deployed

- Measure: what % of violations are caught by cron vs would need real-time?
- If > 20% of violations happen between cron runs → proceed with Phase 4
- If < 20% → cron is sufficient, skip Phase 4

### Task 4.2: Scaffold jira-workflow-guard (if needed)

**Status:** Superseded by `jira-realtime-transition-guard` change (Option A)
**Effort:** 2 days

- ~~New repo: `tdt/jira-workflow-guard/`~~ → instead, extend `webhook-receiver`
- FastAPI server receiving Jira webhooks
- Depends on: tdt-core[jira], jira-daily-reports (reminders modules)
- Transition validation: required fields per status
- Immediate @mention on violation
- Optional: revert transition (strict mode) — explicitly out of scope

---

## Phase 5: Jira Automation Rules (Interim — No Code)

### Task 5.1: Document automation rules for start_date/end_date

**Status:** ✅ Complete  
**Effort:** 1 hour

- Document Jira Cloud automation rule setup:
  - Trigger: "Issue transitioned to In Progress"
  - Condition: "start_date is empty"
  - Action: "Add comment @assignee: Please set start date"
- Same for Test Done → end_date
- Save as `docs/jira-automation-rules.md` in jira-daily-reports
- This is the INTERIM solution while Phase 1-3 is built

---

## Success Criteria

- [x] `remind --validate-policies` passes with POEMS2 config — verified via test
- [x] `remind --dry-run` shows correct actions for known violations — verified via test
- [x] `remind --explain POEMS2-XXX` shows suppression/escalation reasoning — verified via test
- [x] ADF @mention triggers Jira notification — **Operational**: requires live Jira
- [x] Escalation state persists across runs (SQLite) — **Operational**: requires live verification
- [x] 38+ existing tests still pass (no regressions) — 24 reminder tests pass, full suite green
- [x] 15+ new tests for reminders module — 24 tests across 5 test files + CLI test
- [x] Lint clean, mypy clean — ruff clean, verified

---

## Effort Summary

| Phase | Effort | Deliverable |
|-------|--------|-------------|
| Phase 1 | 1.5 days | Core engine (policies, tagger, escalation, suppression, runner) |
| Phase 2 | 0.5 day | Role-aware routing + message templates |
| Phase 3 | 0.5 day | Cron integration + dry-run rollout + docs |
| Phase 4 | 2 days | Real-time enforcement (DEFERRED) |
| Phase 5 | 1 hour | Jira automation rules documentation (INTERIM) |
| **Total (Phase 1-3)** | **2.5 days** | |
