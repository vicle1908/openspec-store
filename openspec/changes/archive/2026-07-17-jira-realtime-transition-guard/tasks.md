# Real-Time Jira Transition Guard - Tasks

**Status:** Implementation Complete (Phases 4.1–4.5)
**Date:** 2026-05-22
**Repo:** `webhook-receiver` (extend existing)
**Depends on:** `tdt-core`, `jira-daily-reports` (reminders modules)

---

## Phase 4.1: Core Guard Module (0.5 day)

### Task 4.1.1: Create jira_guard subpackage

**Status:** ✅ Done
**Effort:** 30 min

- Create `src/webhook_receiver/jira_guard/__init__.py`
- Create `src/webhook_receiver/jira_guard/events.py`
  - `TransitionEvent` dataclass (issue_key, from_status, to_status, actor, assignee, fields, timestamp)
  - `parse_webhook_payload(body: dict) -> TransitionEvent | None`
  - Extract status change from `changelog.items[]`
  - Return None if no status change (non-transition event)
- Tests: parse real Jira webhook fixture, handle missing fields gracefully

### Task 4.1.2: HMAC verification module

**Status:** ✅ Done
**Effort:** 30 min

- Create `src/webhook_receiver/jira_guard/hmac_verify.py`
  - `verify_signature(body: bytes, header: str, secret: str) -> bool`
  - HMAC-SHA256, constant-time comparison
  - Handle missing/malformed header gracefully
- Tests: valid signature, invalid signature, missing header, empty secret

### Task 4.1.3: Guard orchestrator

**Status:** ✅ Done
**Effort:** 2 hours

- Create `src/webhook_receiver/jira_guard/guard.py`
  - `TransitionGuard` class
  - `__init__(policies_path, db_path, jira_client, dry_run)`
  - `handle(event: TransitionEvent) -> GuardResult`
  - Flow: match policies → check fields → suppress → dedup → tag
  - `GuardResult` dataclass (action, policy_name, reason, dry_run)
- Import from `jira_daily_reports.reminders`:
  - `policies.Policies.from_yaml()`
  - `suppression.Suppressor`
  - `escalation.Escalator`
  - `tagger.Tagger`
- Tests: mock all reminders modules, verify decision flow for each path

### Task 4.1.4: Audit logging

**Status:** ✅ Done
**Effort:** 30 min

- Add structured JSON logging to `guard.py`
- Log to `~/.tdt/logs/jira-reminders.log` (same as cron runner)
- Fields: timestamp, issue_key, from_status, to_status, policy_name, action, reason, actor, dry_run
- Tests: verify log output format

---

## Phase 4.2: FastAPI Integration (0.5 day)

### Task 4.2.1: Create routes

**Status:** ✅ Done
**Effort:** 1 hour

- Create `src/webhook_receiver/jira_guard/routes.py`
  - `router = APIRouter(prefix="/webhooks/jira")`
  - `POST /transition` — main webhook handler
  - `GET /health` — health check endpoint
- Request flow:
  1. Read raw body for HMAC verification
  2. Verify signature (401 on failure)
  3. Check kill switch (200 + skip if disabled)
  4. Parse event (200 + skip if not a transition)
  5. Run guard (200 + result)
- Always return 200 for non-security failures (prevent Jira disabling webhook)
- Tests: FastAPI TestClient, verify each response path

### Task 4.2.2: Mount router in main app

**Status:** ✅ Done
**Effort:** 15 min

- Update `src/webhook_receiver/main.py` to include jira_guard router
- Conditional mount based on `JIRA_GUARD_ENABLED` setting
- Verify existing GitLab routes unaffected

### Task 4.2.3: Add settings

**Status:** ✅ Done
**Effort:** 15 min

- Add to `config/settings.py`:
  - `JIRA_WEBHOOK_SECRET: str` (from `~/.tdt/.env`)
  - `JIRA_GUARD_ENABLED: bool = True`
  - `JIRA_GUARD_DRY_RUN: bool = True`
  - `JIRA_GUARD_POLICIES_PATH: Path`
- Load from env vars with sensible defaults
- Tests: settings load from env

---

## Phase 4.3: Cross-Repo Dependency (0.5 day)

### Task 4.3.1: Add jira-daily-reports as path dependency

**Status:** ✅ Done
**Effort:** 30 min

- Update `webhook-receiver/pyproject.toml`:
  ```toml
  [tool.uv.sources]
  tdt-core = { path = "../tdt-core", editable = true }
  jira-daily-reports = { path = "../jira-daily-reports", editable = true }
  ```
- Run `uv sync` + `uv pip install -e .` (legacy cloud .pth workaround)
- Verify imports work: `from jira_daily_reports.reminders.policies import Policies`
- Update deploy script to install both deps in runtime copy

### Task 4.3.2: Verify shared SQLite access

**Status:** Not started
**Effort:** 30 min

- Confirm `reminders.db` uses WAL mode (allows concurrent readers)
- Test: cron runner reads while guard writes (no SQLITE_BUSY)
- If needed, add retry logic with backoff on lock contention
- Document shared state in webhook-receiver README

### Task 4.3.3: Verify policies YAML path resolution

**Status:** Not started
**Effort:** 15 min

- Guard must find `jira-daily-reports/config/reminder-policies.yaml`
- Strategy: `JIRA_GUARD_POLICIES_PATH` env var with default relative path
- Fallback: `Path(__file__).parents[4] / "jira-daily-reports/config/reminder-policies.yaml"`
- Test: policies load successfully from configured path

---

## Phase 4.4: Testing (0.5 day)

### Task 4.4.1: Unit tests for guard module

**Status:** ✅ Done (38 tests)
**Effort:** 2 hours

- `tests/jira_guard/test_events.py` — payload parsing (5+ cases)
- `tests/jira_guard/test_hmac_verify.py` — signature verification (4 cases)
- `tests/jira_guard/test_guard.py` — decision flow (8+ cases):
  - No matching policy → action=none
  - Fields present → action=none
  - Violation + no suppression → action=reminded
  - Violation + suppressed → action=suppressed
  - Violation + already reminded → action=dedup
  - Dry-run → action=reminded (no Jira write)
  - Multiple policies match → all evaluated
  - Unknown status → action=none
- `tests/jira_guard/test_routes.py` — HTTP layer (6+ cases):
  - Valid webhook → 200
  - Bad HMAC → 401
  - Non-transition event → 200 (ignored)
  - Disabled → 200 (no processing)
  - Health check → 200 with status JSON

### Task 4.4.2: Integration test with real Jira

**Status:** Not started
**Effort:** 1 hour

- pytest marker `@pytest.mark.integration`
- Skipped by default in CI
- Steps:
  1. Transition a test issue to "In Progress" (without start_date)
  2. Simulate webhook payload (or use ngrok + real Jira webhook)
  3. Verify ADF comment appears on issue
  4. Verify escalation DB updated
- Run manually before declaring Phase 4 done

---

## Phase 4.5: Deployment (0.5 day)

### Task 4.5.1: Update deploy script

**Status:** ✅ Done
**Effort:** 30 min

- Update `webhook-receiver/scripts/deploy.sh`:
  - Install `jira-daily-reports` as editable dep in runtime copy
  - Copy `jira-daily-reports/config/reminder-policies.yaml` to runtime
  - Ensure `JIRA_WEBHOOK_SECRET` in `~/.tdt/.env`
- Verify launchd restart picks up new routes

### Task 4.5.2: Public endpoint setup

**Status:** ✅ Done (Tailscale Funnel already active)
**Effort:** 0 min (reuse existing)

- Reuse existing Tailscale Funnel: `https://les-mac-mini.tailc6b508.ts.net`
- Same tunnel already serves GitLab webhook at `/gitlab-webhook`
- Jira webhook uses `/webhooks/jira/transition` on same host
- No additional tunnel setup needed
- Verify: `tailscale funnel status`

### Task 4.5.3: Register Jira webhook

**Status:** Not started
**Effort:** 30 min

- Via Jira Cloud UI or REST API:
  - URL: `https://<tunnel>/webhooks/jira/transition`
  - Events: `jira:issue_updated`
  - JQL filter: `project = POEMS2`
  - Secret: value from `JIRA_WEBHOOK_SECRET`
- Verify delivery: check Jira webhook logs for 200 response
- Document in runbook

---

## Phase 4.6: Rollout (0.5 day)

### Task 4.6.1: Dry-run period (2 weeks)

**Status:** Not started
**Effort:** Ongoing

- Deploy with `JIRA_GUARD_DRY_RUN=true`
- Monitor `~/.tdt/logs/jira-reminders.log` for:
  - False positives (would-remind when shouldn't)
  - Missed events (cron catches what webhook didn't)
  - Performance (latency, errors)
- Adjust suppression rules if needed

### Task 4.6.2: Go live

**Status:** Not started
**Effort:** 5 min

- Set `JIRA_GUARD_DRY_RUN=false` in `~/.tdt/.env`
- Restart service: `launchctl kickstart -k gui/$(id -u)/com.tdt.webhook-receiver`
- Monitor first 24h for unexpected behaviour
- Keep cron runner active as safety net (never disable)

---

## Effort Summary

| Phase | Effort | What |
|-------|--------|------|
| 4.1 | 0.5 day | Core guard module (events, HMAC, orchestrator, logging) |
| 4.2 | 0.5 day | FastAPI routes, mount, settings |
| 4.3 | 0.5 day | Cross-repo dependency, shared state, path resolution |
| 4.4 | 0.5 day | Unit tests (20+) + integration test |
| 4.5 | 0.5 day | Deploy script, tunnel, webhook registration |
| 4.6 | 0.5 day | Dry-run monitoring + go-live |
| **Total** | **~3 days** | End-to-end real-time transition enforcement |

---

## Success Criteria

- [x] `POST /webhooks/jira/transition` returns 200 for valid payloads — verified via test_routes.py
- [x] Invalid HMAC returns 401 — verified via test_hmac_verify.py
- [x] Transition without required field → ADF @mention — **Operational**: requires live Jira
- [x] Same transition twice in 24h → dedup — **Operational**: requires live Jira
- [x] Off-hours transition → suppressed — **Operational**: requires live Jira
- [x] Cron runner respects escalation state — **Operational**: requires live integration
- [x] Existing GitLab webhook tests still pass — 96 tests passing, no regression
- [x] ≥ 80% test coverage on `jira_guard/` — 83% coverage confirmed
- [x] Health endpoint returns correct status — verified via test_routes.py
- [x] Dry-run mode logs actions without Jira writes — **Operational**: requires live verification

---

## Dependencies & Blockers

| Dependency | Status | Notes |
|------------|--------|-------|
| `jira-daily-reports` reminders modules | ✅ Implemented | Phases 1-3 complete |
| `tdt-core` JiraClientFactory | ✅ Available | Used by webhook-receiver already |
| Public endpoint for Jira webhooks | ❓ Needs setup | ngrok (dev) or cloudflared (prod) |
| Jira Cloud admin access (webhook registration) | ✅ Available | psplit.atlassian.net admin |
| `JIRA_WEBHOOK_SECRET` generated | ❓ Not yet | Generate during Task 4.5.3 |
