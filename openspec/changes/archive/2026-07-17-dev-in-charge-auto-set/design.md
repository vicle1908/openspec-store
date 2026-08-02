# Dev in Charge Auto-Set — Design

## Context

`webhook-receiver` exposes `POST /webhooks/jira/transition`, which parses inbound `jira:issue_updated` webhooks and runs the policy-driven `TransitionGuard` (loaded from `jira-daily-reports/config/reminder-policies.yaml`). The guard handles *reminders* (comments) for missing required fields but does not *set* fields.

`Dev in Charge` (`customfield_11520`, verified single-user picker on 13 next-gen projects + 1 classic project by `jira-skill/scripts/configure_dev_fields.py:verify_dev_in_charge_field()`) is the canonical attribution field used by `jira-daily-reports` for the new `Developer Performance` tab (see `jira-developer-performance-tab`). Today it is set manually; the cron-based `ReminderRunner` prompts the assignee but only on a daily cadence and only for tickets already at risk of going stale. In practice, tickets frequently reach `In Progress` with `Dev in Charge` empty, breaking per-developer reporting and inflating the `unmapped_dev_in_charge` reconciliation counter.

Constraints discovered during research:

- **Webhook path must remain fast.** Jira retries failed deliveries, so the existing handler returns 200 within milliseconds and pushes any expensive work onto background tasks (`asyncio.create_task`). Our setter follows the same pattern: enqueue is O(1), the actual Jira writes happen in a background flush loop.
- **Atlassian Cloud REST API rate limit.** Default per-token budget is 100 RPS burst. Webhook bursts at sprint kickoff can hit 10–50 transitions in a single second. A batch size of 50 per flush tick is well under the budget with headroom for other tenants (the existing `_jql_paginated` helper chunks reads at 150).
- **Loop prevention has three layers** — none of them can be skipped. L1 (in-process TTL dedup) handles webhook re-delivery. L2 (the existing `DedupeStore`) handles duplicate ingress. L3 (read-before-write) handles the case where the field was set by a different code path between webhook arrival and flush.
- **Field schema is configurable** but typically stable. Single-user picker (`schema.type == "user"`) is the current reality across the 13 projects; multi-user (`array` with `items=user`) is a v2 possibility. Auto-discovery via a single GET at boot is cheap and matches `configure_dev_fields.py:verify_dev_in_charge_field()` precedent.
- **No new dependencies.** `PatchedJira.get()`, `put()`, and `issue()` are sufficient. The existing `JiraClientFactory.from_env()` is reused (one client per process, shared between the existing `TransitionGuard` and the new setter).
- **No DBOS scheduler involvement.** The flush loop is a plain `asyncio.create_task` started during `create_app()` and cancelled at shutdown. This matches the pattern used by `_run_gitlab_note_dispatch` / `_run_impact_dispatch` for fire-and-forget webhook side-effects.

Stakeholders: engineering leads who use the `Developer Performance` tab; the `jira-daily-reports` maintainers (no surface area change for them); webhook-receiver operators (one more env var block to tune).

## Goals / Non-Goals

**Goals:**
- Auto-set `customfield_11520` to the actor who performed a `→ "In Progress"` transition, for the 13 configured projects.
- Three-layer loop prevention (L1 in-process TTL, L2 webhook-receiver DedupeStore, L3 read-before-write).
- Schema auto-discovery via single `GET /rest/api/3/field/{field_id}` at boot; cache for process lifetime.
- Time-based background flush loop, configurable interval (default 5s), configurable batch size (default 50).
- Fail-isolated: a setter error must never affect the webhook response or the existing `TransitionGuard`.
- All knobs configurable via `JIRA_DEV_IN_CHARGE_*` env vars with safe defaults.
- Surface setter status in `/health`.
- One structured log event per write attempt with issue key, account id, schema type, previous value.

**Non-Goals:**
- Resetting `Dev in Charge` on `Done` / `Cancelled` transitions (v2 candidate).
- Event-bus publishing for downstream consumers.
- Persistent suppression across restarts.
- Group-picker payload adaptation (probe logs warning if encountered; setter disabled).
- Bulk backfill of historical tickets.
- Per-user opt-out.
- Setting fields other than `customfield_11520`.
- Modifying the existing `TransitionGuard` or `reminder-policies.yaml`.

## Decisions

### 1. Sibling module, not a new policy type

The setter lives at `webhook_receiver/jira_guard/dev_in_charge_setter.py`, separate from `TransitionGuard`. It consumes the same `TransitionEvent` parsed by `parse_webhook_payload()`, but its decision logic is hard-coded (single trigger status, single field) — it does not fit the `Policy` abstraction used by `reminder-policies.yaml`.

Rationale: the policy engine has an escalation ladder (`Suppressor`, `Escalator`, `Tagger`) designed for *reminders*, not field writes. Wrapping the setter as a policy would force the abstraction to handle a fundamentally different shape (write a field, not post a comment) and would muddy the policy audit log.

### 2. Time-based flush, not size-based

The flush loop runs every `JIRA_DEV_IN_CHARGE_FLUSH_INTERVAL_SECONDS` (default 5s) and drains all pending writes up to `JIRA_DEV_IN_CHARGE_BATCH_SIZE` (default 50) per tick.

Rationale: matches the existing `DBOS` scheduler cadence pattern used by `jira-daily-reports` cron jobs. Size-based flushing would introduce a second dimension of tuning (when does a half-full batch get flushed?) without solving a real problem — Jira webhooks are bursty at sprint boundaries but the per-tick drain handles bursts of any size within a few ticks.

### 3. Three-layer loop prevention

| Layer | Mechanism | Scope | Bypass |
|---|---|---|---|
| L1 | In-process `dict[str, float]` keyed by issue key, TTL configurable via `JIRA_DEV_IN_CHARGE_DEDUPE_TTL_SECONDS` (default 10s) | Process lifetime; cleared on restart | None intended; rare >10s downtime is acceptable |
| L2 | Existing `webhook_receiver.DedupeStore` (coverage-sweep change) — but Jira webhook delivery is not currently routed through it | Receives duplicate ingress if both Tailscale + ngrok fire | Selftest header `X-TDT-Selftest: 1` |
| L3 | Read-before-write | Try `event.fields.get(field_id)` first (free, in-memory from webhook payload); fall back to `GET /rest/api/3/issue/{key}?fields={field_id}` only when missing | Cross-process: catches the case where another instance or a manual edit happened between webhook arrival and flush |

**L3 multi-user semantics** (per `PatchedJira.put()` semantics): for single-user fields, skip if `current.accountId == actor_account_id`. For multi-user fields, skip if `actor_account_id in [u.accountId for u in current]`; otherwise **append** `actor_account_id` to the array — never replace the array.

**L1 dedup timing**: the dedup entry is set at `enqueue()` time (not just at `_mark_written()` inside `flush()`), closing the race window where two webhooks for the same issue arrive within one flush tick.

Rationale: any single layer can be defeated by a different failure mode (L1 alone loses on cross-process; L3 alone is too expensive to run on every webhook). The three together cover webhook re-delivery, duplicate ingress, and cross-process races.

### 4. Schema auto-discovery at boot

A single `GET /rest/api/3/field/{field_id}` call at module mount returns the schema. The probe result is cached in a `threading.Lock`-guarded slot. The write payload shape is derived from `schema.type`:

| `schema.type` | `is_multi_user` | Write payload |
|---|---|---|
| `user` | False | `{"fields": {"customfield_11520": {"accountId": "..."}}}` |
| `array` with `items=user` | True | `{"fields": {"customfield_11520": [{"accountId": "..."}]}}` |
| other | False | Probe logs `dev_in_charge_unsupported_schema` WARNING; `_setter` stays `None`; setter disabled |

Rationale: cheap (one call at boot), mirrors `jira-skill/scripts/configure_dev_fields.py:verify_dev_in_charge_field()` (which uses the same GET), and lets the operator change the field ID via `JIRA_DEV_IN_CHARGE_FIELD_ID` without code changes.

### 5. Fail-isolated mount

`mount_dev_in_charge_setter()` is called inside a `try/except` in `create_app()` after `mount_jira_guard(...)`. On any failure (probe fails, env validation fails, etc.) the warning `dev_in_charge_setter_init_failed` is logged and `_setter` stays `None`. `enqueue_dev_in_charge()` is a no-op when `_setter is None`.

Rationale: matches the existing `mount_jira_guard(...)` pattern, which already does the same try/except isolation. A broken setter must never take down the existing guard or the webhook receiver.

### 6. Reuse the same `Jira` client

`mount_dev_in_charge_setter(jira_client)` takes the existing `Jira` instance created by `JiraClientFactory.from_env()` in `create_app()` (already passed to `mount_jira_guard(...)`). This avoids creating a second `requests.Session` (which would double connection-pool memory and trigger a duplicate auth handshake).

Rationale: explicit in `tdt-core/src/tdt_core/clients/jira.py:create_client()` — the pooled `requests.Session` is the single configured adapter; instantiating twice doubles the pool.

### 7. Flush task lifecycle managed by FastAPI lifespan

The flush task is scheduled inside the existing FastAPI `lifespan` async context manager in `api/app.py:create_app()`, not at module-import time. The setter module exposes:

- `async def start_flush_loop() -> None` — called from `lifespan` startup
- `async def stop_flush_loop() -> None` — called from `lifespan` shutdown, performs a final drain

Rationale: `asyncio.get_event_loop()` was deprecated in Python 3.10 and **removed in Python 3.12+**. The project is on Python 3.14 (`deployments/.../python3.14`). Scheduling inside `lifespan` uses `asyncio.get_running_loop()` (the supported replacement) and matches the pattern used by `shutdown_freshness_debouncer()`.

### 8. Shared audit log append

The setter appends a JSONL line to `~/.tdt/logs/jira-reminders.log` (the same audit log used by `TransitionGuard._audit_log()` and the cron `ReminderRunner`) for each `dev_in_charge_set` and `dev_in_charge_set_failed` event. The appended entry includes `source=dev_in_charge_setter` so the cron reconciliation tooling can distinguish from `source=jira_guard`. The append is best-effort; failures log `dev_in_charge_audit_append_failed` WARNING but never propagate.

Rationale: a unified audit trail across the cron and webhook paths lets operators grep one file to answer "what happened to issue X over the past 30 days?" The existing `audit_log_write_failed` log line in `guard.py:84` shows the established pattern.

### 9. Kill switch honors the route's `_enabled` global

The setter's `/health` block reads `_enabled` from `webhook_receiver/jira_guard/routes.py` (a module-level global set at `mount_jira_guard()` time from `settings.jira_guard_enabled`) rather than just checking `_setter is not None`. This ensures `/health` reports the effective runtime state: when the route is disabled, the setter block also reports `enabled=False` even though the setter module is mounted.

Rationale: operators reading `/health` need to see what is *actually happening* in production, not what *could* happen if the kill switch were enabled.

## Architecture

```
Jira Cloud ─── jira:issue_updated ──→ webhook-receiver (FastAPI)
                                            │
                                            ▼
                                parse_webhook_payload()
                                            │
                                            ▼
                                       TransitionEvent
                                            │
                          ┌─────────────────┼─────────────────┐
                          ▼                                   ▼
              TransitionGuard.handle()              enqueue_dev_in_charge(event)
              (existing policy runner)              (NEW — O(1) enqueue)
                          │                                   │
                          ▼                                   ▼
                  GuardResult[]                       _pending dict
                                                                │
                                                                ▼
                                              _flush_loop (asyncio.create_task)
                                              every 5s, batch 50
                                                                │
                                                                ▼
                                              schema.make_write_payload(account_id)
                                                                │
                                                                ▼
                                              PatchedJira.put(/rest/api/3/issue/{key})
```

## Schema probe failure mode

If `GET /rest/api/3/field/{field_id}` returns 404 (field ID stale, e.g. customer re-pinned), `mount_dev_in_charge_setter()` catches it, logs `dev_in_charge_setter_init_failed error=404`, and `_setter` stays `None`. The operator sees the warning in the boot log and updates `JIRA_DEV_IN_CHARGE_FIELD_ID` to the new ID.

## Open questions resolved during design

- **Q: Should the setter share the webhook handler's asyncio loop, or run on its own?** A: Same loop. `create_app()` is sync; we use `asyncio.get_event_loop().create_task()` to schedule the flush task, matching the pattern used by `_run_gitlab_note_dispatch` and `_run_impact_dispatch`.
- **Q: Should the L1 dedup dict be persisted to disk?** A: No for v1. In-memory is sufficient — webhook re-delivery after >10s of process downtime is rare, and the L3 read-before-write catches any cross-process race regardless.
- **Q: Should the setter publish a `dev_in_charge_set` event?** A: No. The existing `Developer Performance` tab reads via a 60-minute JQL poll and reconciles `unmapped_dev_in_charge`. Polling-only consumers per the design decision in §3 v1.
- **Q: Should the flush loop be in DBOS?** A: No. It is a hot loop (5s tick), not a scheduled job. DBOS is for cadence-based workflows; an in-process `asyncio.create_task` is the right primitive.