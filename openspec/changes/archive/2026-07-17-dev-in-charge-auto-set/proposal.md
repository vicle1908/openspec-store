## Why

Today the `Dev in Charge` (`customfield_11520`) Jira field is set **manually** when a developer moves a ticket to `In Progress`. The reminder policies in `jira-daily-reports/config/reminder-policies.yaml` (and the cron-based `ReminderRunner`) prompt users to fill the field when it's empty — but the prompting happens at most once per day per ticket, and only for tickets already at risk of going stale. We routinely see tickets whose `Dev in Charge` is empty days after the developer has already started working on them, which breaks the per-developer reporting in `jira-daily-reports` (e.g. the new `Developer Performance` tab — see `jira-developer-performance-tab` change).

The `webhook-receiver` already runs a `TransitionGuard` policy engine that fires on Jira `jira:issue_updated` webhooks. The guard handles required-field *reminders* (comments) but does not *set* fields. Wiring a sibling module that auto-sets `Dev in Charge` to the actor who performed the `→ In Progress` transition closes the loop in real time, well before the 24-hour reminder cadence, without depending on manual discipline.

## What Changes

- Add a new `dev_in_charge_setter` module in `webhook-receiver/src/webhook_receiver/jira_guard/` that auto-sets `customfield_11520` (configurable via `JIRA_DEV_IN_CHARGE_FIELD_ID`) on transitions into the configurable trigger status (default `In Progress`).
- The setter operates as a sibling to the policy-driven `TransitionGuard`, not as another policy type. It runs against the same set of `jira:issue_updated` webhooks that the existing guard already handles, on the same `Jira` client (no duplicate auth handshake).
- A time-based background flush loop drains the in-memory pending set every `JIRA_DEV_IN_CHARGE_FLUSH_INTERVAL_SECONDS` (default 5s), chunked at `JIRA_DEV_IN_CHARGE_BATCH_SIZE` (default 50) to stay well under Atlassian's 100 RPS burst budget.
- Loop-prevention in three layers:
  - **L1** — per-issue in-process dedup with configurable TTL (`JIRA_DEV_IN_CHARGE_DEDUPE_TTL_SECONDS`, default 10s) so a webhook re-delivery does not double-write.
  - **L2** — the existing webhook-receiver `DedupeStore` (covering GitLab MR hooks) plus Jira's own at-least-once delivery model. The setter is a no-op when the issue's existing `Dev in Charge` already matches the actor.
  - **L3** — read-before-write: on each flush, fetch the current field value via `GET /rest/api/3/issue/{key}?fields={field_id}`; skip the write if the account is already there.
- Schema auto-discovery at boot: a single `GET /rest/api/3/field/{field_id}` returns the field schema; the setter builds the write payload according to whether the field is `user` (single-user picker) or `array` with `items=user` (multi-user picker). The probe result is cached for the process lifetime.
- Project scope is configurable via `JIRA_DEV_IN_CHARGE_PROJECTS` (comma-separated), defaulting to the 13-project set already used by `jira-skill/scripts/configure_dev_fields.py`.
- Six new env vars (all with safe defaults), registered in `~/.tdt/.env` via the existing `tdt_core.env.load_tdt_env()` machinery. `.env.example` does not need updates because defaults work out of the box.
- `/health` endpoint extended with `dev_in_charge_setter` snapshot (enabled, projects, trigger_status, ttl, batch_size).
- One new structured log event per write attempt: `dev_in_charge_set` (success), `dev_in_charge_set_failed` (error), `dev_in_charge_skip_*` (no-op cases), `dev_in_charge_flush` (per-tick summary). Successful writes and failures also append to the shared `~/.tdt/logs/jira-reminders.log` JSONL audit log (used by the existing `TransitionGuard` and the cron `ReminderRunner`) with `source=dev_in_charge_setter`, so operators get a unified audit trail across the cron and webhook paths.
- The setter coexists with the existing `TransitionGuard` without coordination: on a transition to `In Progress` with `customfield_10015` empty, the guard posts a reminder comment about Start Date while the setter writes `Dev in Charge`. The two side-effects cover different fields and do not cancel each other.
- L3 read-before-write is optimized to read from `event.fields` first (free, in-memory) and fall back to `GET /rest/api/3/issue/{key}?fields={field_id}` only when the webhook payload omits the field (rare; depends on webhook scope).
- The flush task is scheduled inside the FastAPI `lifespan` async context manager (not at module-import time), avoiding the Python 3.12+ removal of `asyncio.get_event_loop()`. The setter exposes `start_flush_loop()` and `stop_flush_loop()` async functions called from `lifespan`.

## Capabilities

### New Capabilities

- `dev-in-charge-auto-set`: Real-time auto-assignment of the `Dev in Charge` Jira field to the actor who performs a status transition into the trigger status (default `In Progress`), subject to project allow-list, in-process L1 dedup, read-before-write L3 guard, schema auto-discovery, and time-based batched flush.

### Modified Capabilities

- None. The existing `jira-guard` capability (the policy-driven `TransitionGuard`) is untouched. The new setter is a sibling module mounted alongside it in `create_app()`; both consume the same `TransitionEvent` produced by `parse_webhook_payload()`. No existing requirement in any other spec changes.

## Impact

- `webhook-receiver`:
  - New module `src/webhook_receiver/jira_guard/dev_in_charge_setter.py` with `DevInChargeSchemaProbe`, `DevInChargeSetter`, `_flush_loop`, `mount_dev_in_charge_setter`, `enqueue_dev_in_charge`, `dev_in_charge_health`.
  - One-line call added to `src/webhook_receiver/jira_guard/routes.py` `handle_transition()` after `_guard.handle()` returns.
  - One block added to `src/webhook_receiver/api/app.py` `create_app()` after `mount_jira_guard(...)` to call `mount_dev_in_charge_setter(jira_client)` (sharing the existing client).
  - One entry added to `/health` in `create_app()` exposing the setter snapshot.
  - New unit tests in `tests/jira_guard/test_dev_in_charge_setter.py` covering: enqueue gating (project, trigger_status, L1 dedup), flush chunking, write payload shape for both single-user and multi-user field types, L3 read-before-write skip, probe caching, mount failure isolation.
  - New regression test `tests/regression/test_existing_jira_guard_unchanged.py` confirming `TransitionGuard.handle()` semantics are preserved.
- `tdt-core`: no changes (existing `PatchedJira` exposes `get()` / `put()` / `issue()` methods sufficient for the setter; no new SDK methods needed).
- `jira-skill`: no changes (the field configuration script `configure_dev_fields.py` already verified the field is single-user picker on the 13 projects).
- `jira-daily-reports`: no changes (the new `Developer Performance` tab already reads `customfield_11520` and reconciles `unmapped_dev_in_charge`; this change reduces that count in real time).
- `~/.tdt/.env`: five new optional env vars with safe defaults. `.env.example` does not need updates.
- Mobile apps (`poems-mobile3-ios`, `poems-mobile3-android`), `ai-review`, `mcp-router`, `tdt-sheets`, `code-daily-scan`: not impacted.

## Non-Goals

- Resetting `Dev in Charge` on `Done` / `Cancelled` transitions (v2 candidate; would force a decision matrix on what to reset to).
- Event-bus publishing for real-time downstream consumers (existing `Developer Performance` tab reads via 60-minute JQL poll — sufficient).
- Persistent suppression across restarts (in-memory dedup is sufficient; webhook re-delivery after >10s of downtime is rare).
- Group-picker payload adaptation (auto-discovery logs a warning and disables the setter if encountered; not a current project requirement).
- Bulk backfill of historical tickets missing `Dev in Charge` (separate change `jira-developer-performance-tab` already handles the reconciliation path).
- Per-user opt-out (e.g. some teams wanting manual assignment) — out of scope for v1.
- Setting other fields (Assignee, Story Points, etc.) on the same transition.
- Modifying the existing `TransitionGuard` policies or `reminder-policies.yaml`.