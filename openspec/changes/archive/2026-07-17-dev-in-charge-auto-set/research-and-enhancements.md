# Research & Spec Enhancement — dev-in-charge-auto-set

**Date:** 2026-07-11
**Author:** Claude (Cursor), per operator request "continue research, enhance and validate spec. explain spec carefully"
**Status:** Memo + spec corrections. The OpenSpec change `dev-in-charge-auto-set` is currently at `4/4 artifacts complete` and `openspec validate --strict` passes; this document captures the discoveries made during deeper code-level research that surface gaps in the v1 spec, with proposed amendments to `proposal.md`, `design.md`, `specs/dev-in-charge-auto-set/spec.md`, and `tasks.md`.

---

## 1. Research findings (with code citations)

### F1. The existing `Policy` model has an unused `custom_field` attribute

`jira-daily-reports/src/jira_daily_reports/reminders/policies.py:56`:

```python
class Policy(BaseModel):
    ...
    custom_field: str | None = None
```

**Implication**: the policy framework already anticipated that a reminder policy might write a custom field. The `custom_field` attribute is currently unused by the runner (`runner.py:_resolve_role()` only reads it for `Role.qa_owner`, not for the action path) and unused by the tagger (`tagger.py` only writes ADF comments). This is a hint that "sibling module, not new policy type" (design Decision 1) may be premature — but it's also not strong enough to reverse: the policy framework's escalation/suppression logic is fundamentally about *reminders*, not field writes. **Recommendation: keep Decision 1, but document the unused `custom_field` attribute in the design as an alternative architecture for v2 if the operator wants tighter integration.**

### F2. The route's HMAC check is OPTIONAL when secret is unset

`webhook-receiver/src/webhook_receiver/jira_guard/routes.py:73`:

```python
if _secret and not verify_signature(body, signature, _secret):
    logger.warning("jira_guard_invalid_signature")
    return JSONResponse({"error": "unauthorized"}, status_code=401)
```

**The `if _secret and` short-circuit**: when `JIRA_WEBHOOK_SECRET` is empty/unset, signature verification is **skipped entirely** and the route accepts unsigned bodies. The existing test confirms this is the intended behavior (`tests/unit/test_jira_guard_routes.py:200` — `test_empty_secret_disables_hmac_check`).

**Implication for the setter**: my spec said "the setter inherits the same HMAC protection as the guard." This is *correct* but incomplete. The setter inherits the same **conditional** HMAC protection — if the secret is unset, neither the guard nor the setter verifies authenticity. **Recommendation: amend the spec to make the HMAC behavior explicit and add a WARNING log on the setter mount if `JIRA_WEBHOOK_SECRET` is empty (degraded-mode operational signal).**

### F3. The webhook payload's `issue.fields` already contains the target field

`webhook-receiver/src/webhook_receiver/jira_guard/events.py:64`:

```python
fields = issue.get("fields") or {}
```

`event.fields` is the full set of fields Jira delivered in the webhook payload. For typical Jira Cloud webhook configurations, this includes the project's screen-tab fields, which includes `customfield_11520` (Dev in Charge) on the 13 configured projects.

**Implication for L3**: my v1 spec calls for `GET /rest/api/3/issue/{key}?fields={field_id}` on every flush tick. That's one REST call per write — fine, but **avoidable**. If `event.fields.get(customfield_11520)` is present in the webhook payload (the common case), the L3 check can read directly from the in-memory dict with zero API calls.

**Tradeoff**: webhook payloads only include fields the webhook is *configured* to deliver. If the project admin has excluded `customfield_11520` from the webhook scope (rare but possible), `event.fields.get(customfield_11520)` returns `None`, and the setter would either:
- (a) skip the write thinking the field is empty, OR
- (b) fall back to a GET, OR
- (c) write anyway (overwriting whatever is there).

**Recommendation: option (b) — try in-memory first, fall back to GET only when missing.** This is a meaningful optimization (saves a REST call per write in the common case) and the fallback keeps correctness in the rare case. **This is a spec amendment.**

### F4. The existing `in_progress_start_date` policy fires on the same trigger

`jira-daily-reports/config/reminder-policies.yaml:17-23`:

```yaml
- name: in_progress_start_date
  role: assignee
  issue_types: [Story, Task, Bug]
  statuses: [In Progress]
  required_fields: [customfield_10015]
  on_transition: true
```

**Implication**: when a developer moves a ticket to `In Progress`, the existing `TransitionGuard` will POST A COMMENT (via `Tagger.post_mention()`) if `customfield_10015` (Start Date) is empty. My setter would set `customfield_11520` (Dev in Charge) on the same transition.

**Order of operations** (from `routes.py:104-108`):
1. Guard runs (`_guard.handle(event)`)
2. Guard posts a reminder comment if Start Date is empty
3. Setter enqueues (after my insertion)
4. Setter writes Dev in Charge in the next flush tick (≤5s later)

**User-facing experience**: on a transition with both fields empty, the user sees two side-effects within 5 seconds: a comment about Start Date, and the Dev in Charge field populated. Neither cancels the other.

**Recommendation: document this in the spec as an "interaction with existing policies" note.** The risk is double-notification fatigue, but since the existing comment covers a different field (Start Date) than what the setter writes (Dev in Charge), the noise is acceptable.

### F5. The `/health` setter block needs to honor the route's `_enabled` kill switch

`routes.py:67-68`:

```python
if not _enabled:
    return JSONResponse({"status": "disabled"}, status_code=200)
```

This early-returns BEFORE the setter would fire. The setter module has its own state (`_setter is not None`) but does not know about `_enabled`.

**Implication**: today, my spec's `/health` block shows `dev_in_charge_setter.enabled = _setter is not None`. But this could be `true` while the route is actually disabled (via `JIRA_GUARD_ENABLED=false`). An operator looking at `/health` would be misled.

**Recommendation: amend the spec so the `/health` block reports `enabled = _setter is not None AND _enabled`.** This requires either (a) exposing `_enabled` from the routes module, or (b) having the setter module know about it via a separate env var. Option (a) is simpler — `_enabled` is already a module-level global in `routes.py`.

### F6. `crud` semantics: PUT replaces, doesn't append

For multi-user fields, `PUT /rest/api/3/issue/{key}` with `{"customfield_11520": [{"accountId": "X"}]}` **replaces** the entire array, not appends. For single-user fields, `PUT` with `{"customfield_11520": {"accountId": "X"}}` replaces the single value.

**Implication for L3 read-before-write**: my v1 spec correctly says "skip the write if the actor is already in the array." This protects against re-writing the same value, but it does NOT protect against *appending*. If Dev in Charge is multi-user, the setter would replace `[{Alice}, {Bob}]` with `[{actor}]`, removing Bob. This is the wrong default behavior for a multi-user field.

**Recommendation: amend the spec — for multi-user fields, the setter MUST only *append* `actor` if not already present, never replace the array.** For single-user fields (the current reality on all 13 projects), replace is correct.

**This is a meaningful behavior change to the L3 algorithm.** Need a new scenario in the spec.

### F7. Race condition between `enqueue` and `flush`

Two webhooks arriving in the same tick for the same issue key:
1. Webhook 1 arrives at T=0.0s, enqueue `{issue_key: POEMS2-1, account_id: Alice}`.
2. Webhook 2 arrives at T=0.05s (e.g. a re-delivery), enqueue no-op (L1 dedup hit on the in-memory `_recent` set, which was just populated by webhook 1).

Wait — `_recent` is populated by `_mark_written` inside `flush()`, not by `enqueue()`. So the L1 dedup window only starts AFTER the first write. A re-delivery at T=4.9s (before the 5s flush tick at T=5.0s) would NOT be suppressed by L1, would NOT be suppressed by L3 (because the field is still empty), and would enqueue a second write.

**Worse**: both writes happen in the same flush tick, so the second write's L3 read-before-write (against the in-memory `event.fields` from webhook 2) sees `None`, proceeds, and overwrites the first write with the same value (no-op but wasteful).

**Recommendation: the L1 dedup should be set in `enqueue()` too**, not just in `_mark_written()`. This closes the race window. **Spec amendment.**

### F8. JSON parsing returns `actor_account_id=""` (empty string), not None

`events.py:80`:

```python
actor_account_id=actor.get("accountId", ""),
```

**Implication**: when the webhook payload has no `user` field (rare, but possible for system-generated transitions), `event.actor_account_id` is the empty string `""`, not `None`. My v1 spec said "skip if actor_account_id is empty" — the check should be `not actor_account_id` (covers both `""` and `None`), not `if actor_account_id is None`. **Minor spec clarification; no behavior change.**

### F9. The `Tagger` class already does error handling I can mirror

`tagger.py:41-55`:

```python
def post_mention(self, issue_key: str, account_id: str | None, message: str) -> bool:
    ...
    try:
        self._jira.add_comment_adf(issue_key, adf_body)
    except Exception:
        logger.exception("Failed to post comment on %s", issue_key)
        return False
    return True
```

**Implication**: the existing `Tagger` uses `logger.exception()` (not `logger.error(...)` with manual `exc_info=True`), returns `False` on error rather than raising, and **does not include the error message in the return value**. My setter spec emits `dev_in_charge_set_failed` with `error=str(exc)` — this is more verbose than the existing pattern.

**Recommendation: align with the existing pattern** — use `logger.exception(...)` for unexpected errors, return a structured result that callers can inspect, and include the issue key in the log but not necessarily the exception string. This keeps log volume consistent across the codebase. **Minor spec clarification.**

### F10. The webhook-receiver already uses `asyncio.get_event_loop()` at module init — but only inside `lifespan`

`api/app.py:744-758`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ...
    yield
    shutdown_freshness_debouncer()
    ...
```

The existing flush loops (e.g. `_flush_loop` in my draft) should ideally be scheduled inside `lifespan`, not during module import. My v1 spec says `create_app()` is sync and uses `asyncio.get_event_loop().create_task()` — but `create_app()` runs at FastAPI construction time, BEFORE the event loop starts. `asyncio.get_event_loop()` at that point may return a loop that isn't running yet, which is `Deprecated since 3.10` and `Removed in 3.12+` in favor of `asyncio.get_running_loop()` (which raises if no loop is running).

**Implication**: my draft's `asyncio.get_event_loop().create_task()` in `mount_dev_in_charge_setter()` is fragile and uses a deprecated API. It works on Python 3.11 (the project is on 3.14 — see `deployments/.../python3.14`), where it's been removed.

**Recommendation: schedule the flush task inside the existing `lifespan` async context manager**, similar to how `shutdown_freshness_debouncer()` is called. The setter module exposes `start_flush_loop()` and `stop_flush_loop()` async functions called from `lifespan`. **This is a meaningful architectural correction.**

### F11. The existing audit log convention is a JSONL at `~/.tdt/logs/jira-reminders.log`

`webhook-receiver/src/webhook_receiver/jira_guard/guard.py:31`:

```python
AUDIT_LOG_PATH = tdt_root() / "logs" / "jira-reminders.log"
```

The existing guard appends JSONL entries to this file with `source=jira_guard`. The cron `ReminderRunner` reads the same file.

**Implication**: my setter could also append to this shared audit log with `source=dev_in_charge_setter`, giving operators one unified audit trail across the cron + webhook paths. **Recommendation: add this as an optional audit append** (writes are best-effort, no exceptions propagate) so v1 has the same audit story as the guard. **Spec amendment — small but valuable for ops.**

### F12. The existing `_freshness_dispatcher` integration is a pattern I should mirror exactly

`routes.py:87-90`:

```python
if _freshness_dispatcher is not None:
    freshness_result = _freshness_dispatcher.enqueue(payload, source="webhook")
    if freshness_result.get("status") in {"accepted", "skipped", "ignored"}:
        logger.info("report_freshness_handled", extra={"result": freshness_result})
```

The freshness dispatcher takes the raw `payload` (not the parsed `event`), enqueues, returns a structured result. My setter takes the parsed `event`. **Both patterns are valid** — taking the parsed event saves a re-parse, but taking the payload is more flexible. **No spec change**, just a design rationale note.

---

## 2. Spec amendments (to be applied)

Based on the 12 findings above, the following amendments improve the v1 spec:

| # | Finding | Amendment |
|---|---|---|
| F2 | HMAC optional mode | Add `Requirement: Operational mode warning` — log WARNING on mount when `JIRA_WEBHOOK_SECRET` is unset |
| F3 | Webhook payload already has the field | Replace L3 read-before-write with: "Try `event.fields` first; fall back to GET only when missing" |
| F4 | Existing policy on same trigger | Add `Note: Interaction with existing policies` in proposal + design |
| F5 | `_enabled` kill switch | Amend `/health` block: `enabled = _setter is not None AND _enabled` |
| F6 | Multi-user array semantics | Amend L3 for multi-user: append-only, never replace |
| F7 | Enqueue/flush race | Amend L1 dedup: set in `enqueue()` not just `_mark_written()` |
| F8 | Empty string vs None | Clarify: check `not actor_account_id` (covers both) |
| F9 | Existing error-handling style | Use `logger.exception(...)` and structured result, not `logger.error(..., error=str(exc))` |
| F10 | `get_event_loop()` deprecated in 3.12 | Move flush task scheduling into `lifespan`, not `mount_*` |
| F11 | Shared audit log | Add optional `dev_in_charge_setter` JSONL append to `~/.tdt/logs/jira-reminders.log` (best-effort) |

## 3. Items that are CORRECT as-is

- **S1**: Three-layer loop prevention (overall architecture). The three layers are real and complementary; F7 just adds nuance to L1.
- **S2**: Sibling module, not new policy type (Decision 1). F1 hints at an alternative but doesn't reverse the call.
- **S3**: Reuse the same `Jira` client. Correct and important.
- **S4**: Schema auto-discovery at boot via single GET. Correct; matches the `jira-skill` precedent.
- **S5**: Time-based flush (5s tick, 50 issues). Correct; matches the project's DBOS cron cadence pattern.
- **S6**: 6 env vars with safe defaults. Correct.
- **S7**: Per-requirement scenarios. The scenario structure is sound; F6 and F7 just add scenarios.

## 4. Spec walk-through (operator-friendly explanation)

This section explains the v1 spec as it currently stands, with the F1-F12 corrections marked. Read this top-to-bottom for a complete understanding.

### 4.1 What is `dev-in-charge-auto-set`?

It's a sibling module to the existing `TransitionGuard` policy engine. When a developer moves a Jira ticket to `In Progress`, the webhook-receiver fires both:
- **Existing `TransitionGuard`**: posts a comment if other fields are missing (e.g. Start Date)
- **NEW `DevInChargeSetter`** (this change): silently writes the actor's account ID into the `Dev in Charge` field

The two modules share the same `TransitionEvent` (parsed from the Jira webhook payload) but have independent logic and independent side-effects.

### 4.2 Why is this a sibling and not a new policy?

The policy framework (`reminder-policies.yaml`) is designed for **reminders** — it has escalation ladders, suppression rules, and an audit log optimized for "did we nudge the assignee?" The setter is fundamentally different: it **writes a field**, not **posts a comment**, and it has no escalation/suppression concept. Adding it as a new policy type would force the policy framework to handle two semantically different actions, complicating the existing abstraction. The cleaner separation is two parallel modules.

### 4.3 What are the three loop-prevention layers?

| Layer | What it does | When it helps |
|---|---|---|
| **L1** | In-memory dict of recently-set issues with TTL = 10s | Webhook re-delivery within 10s (Jira does this on transient errors) |
| **L2** | The existing `webhook-receiver.DedupeStore` (coverage-sweep change) | Both Tailscale + ngrok ingress fire for the same webhook |
| **L3** | Read-before-write: check the current field value, skip if actor already there | Cross-process race: another webhook-receiver instance, a manual edit, or a bulk-fix script |

All three are needed because each handles a different failure mode. **F7 corrects L1** to be set in `enqueue()` not just in `_mark_written()`.

### 4.4 How does L3 work in practice?

**F3 correction**: L3 reads from `event.fields` (the webhook payload) first. This is a free check — no API call. Only when the webhook payload doesn't include `customfield_11520` (rare; depends on project admin's webhook config) does the setter fall back to `GET /rest/api/3/issue/{key}?fields={field_id}`.

**F6 correction**: For single-user fields (the current reality on all 13 projects), if the actor is already the current value, skip. For multi-user fields, if the actor is already in the array, skip. **Never replace the array** — only append.

### 4.5 What gets logged?

Every significant event emits a structured log line with `event=dev_in_charge_*`. Operators can:
- Grep for `event=dev_in_charge_set` to count successful writes
- Grep for `event=dev_in_charge_set_failed` to find errors
- Grep for `event=dev_in_charge_flush` to see per-tick throughput
- Grep for `event=dev_in_charge_skip` to see L3 hits (already-set cases)

Plus, **F11**: the same events also append to `~/.tdt/logs/jira-reminders.log` (the shared JSONL audit log) so the cron `ReminderRunner` reconciliation tooling can also see them.

### 4.6 What's the kill switch?

Two layers:
1. **`JIRA_GUARD_ENABLED=false`** disables the entire route handler (existing behavior). Both the guard and the setter stop firing.
2. **`JIRA_DEV_IN_CHARGE_PROJECTS=""`** would make the setter a no-op (no projects match), but the route is still active. This is a "narrow the scope" knob, not a kill switch.

For a hard kill switch, operators use `JIRA_GUARD_ENABLED=false`. The setter doesn't have its own kill switch; this is intentional (consistent with the existing pattern). **F5 correction**: `/health` reports `enabled = _setter is not None AND _enabled` so operators see the *effective* state.

### 4.7 What's the deployment story?

1. `bash scripts/deploy.sh` from `webhook-receiver/` — ships the new module + test files
2. Restart the webhook-receiver LaunchAgent — picks up the new module
3. The setter is mounted automatically (no env var changes required for defaults)
4. Optionally: append `JIRA_DEV_IN_CHARGE_*` env vars to `~/.tdt/.env` to tune behavior
5. Verify `/health` shows `dev_in_charge_setter.enabled = true` and lists the 13 projects

### 4.8 What's NOT in v1?

Out of scope (per spec non-goals):
- Setting fields OTHER than `customfield_11520` (Assignee, Story Points, etc.)
- Resetting `Dev in Charge` on Done/Cancelled transitions
- Bulk backfill of historical tickets
- Per-user opt-out
- Group-picker payload adaptation
- Event-bus publishing for downstream consumers

These are all reasonable v2 candidates if v1 proves successful.

### 4.9 What are the risks?

| Risk | Likelihood | Mitigation |
|---|---|---|
| Setting the field on a transition where the actor isn't actually the "dev in charge" (e.g. a manager moving the ticket) | Medium | Document the behavior; operators can set `JIRA_DEV_IN_CHARGE_TRIGGER_STATUS` to a different status if needed |
| L3 misreads `event.fields` because the webhook payload doesn't include the field | Low | Fall back to GET (F3) |
| Multi-user field semantics differ from single-user | Low today (single-user everywhere); high if v2 introduces multi-user | Spec covers both (F6) |
| Race condition between two webhook deliveries for the same issue | Very low | L1 dedup set in `enqueue()` (F7) |
| Kill switch in `/health` lies about effective state | Low | `/health` reads `_enabled` from routes module (F5) |
| Python 3.14 deprecation of `asyncio.get_event_loop()` | High | Move flush task to `lifespan` (F10) |

---

## 5. Next steps

1. Apply the 10 spec amendments (F2, F3, F4, F5, F6, F7, F8, F9, F10, F11) to `proposal.md`, `design.md`, `specs/dev-in-charge-auto-set/spec.md`, and `tasks.md`.
2. Re-run `openspec validate --strict dev-in-charge-auto-set` — confirm "Change is valid" still passes.
3. Re-run `openspec status --change dev-in-charge-auto-set` — confirm `4/4 artifacts complete` still holds.
4. Surface this memo to the operator for review before applying the amendments.