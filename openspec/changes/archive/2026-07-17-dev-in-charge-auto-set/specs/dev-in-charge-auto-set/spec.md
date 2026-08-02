## ADDED Requirements

### Requirement: Auto-set Dev in Charge on status transitions

The system SHALL auto-set the `Dev in Charge` Jira field (configurable via `JIRA_DEV_IN_CHARGE_FIELD_ID`, default `customfield_11520`) to the account ID of the user who performed a Jira issue status transition into the configurable trigger status (default `In Progress`), for issues belonging to the project allow-list (configurable via `JIRA_DEV_IN_CHARGE_PROJECTS`, defaulting to the 13-project set already used by `jira-skill/scripts/configure_dev_fields.py`).

The setter SHALL run as a sibling to the existing policy-driven `TransitionGuard`, consuming the same `TransitionEvent` produced by `parse_webhook_payload()` from inbound `jira:issue_updated` webhooks.

#### Scenario: A transition into "In Progress" sets Dev in Charge
- **WHEN** a Jira webhook arrives for a `→ In Progress` transition on an issue in an allow-listed project
- **AND** the actor's account ID is present in the webhook payload
- **THEN** the system SHALL enqueue a write of the actor's account ID into the `Dev in Charge` field
- **AND** the write SHALL occur in the next background flush tick (default ≤5 seconds later)
- **AND** the webhook response SHALL be returned within milliseconds (the enqueue is O(1))

#### Scenario: A transition to a non-trigger status is a no-op
- **WHEN** a Jira webhook arrives for a `→ Done` (or any other non-trigger) transition
- **THEN** the system SHALL NOT enqueue a write to the `Dev in Charge` field
- **AND** no `dev_in_charge_set` log event SHALL be emitted for that webhook

#### Scenario: A transition in a non-allow-listed project is a no-op
- **WHEN** a Jira webhook arrives for a transition on an issue whose project key is not in `JIRA_DEV_IN_CHARGE_PROJECTS`
- **THEN** the system SHALL NOT enqueue a write to the `Dev in Charge` field

### Requirement: Three-layer loop prevention

The system SHALL prevent duplicate writes of the `Dev in Charge` field through three independent layers:

| Layer | Scope | Mechanism | Configurable |
|---|---|---|---|
| L1 | In-process per-issue | `dict[str, float]` keyed by issue key with TTL | `JIRA_DEV_IN_CHARGE_DEDUPE_TTL_SECONDS` (default 10s) |
| L2 | Webhook-receiver ingress | Existing `webhook_receiver.DedupeStore` (coverage-sweep change) | Per existing configuration |
| L3 | Read-before-write | Fetch `GET /rest/api/3/issue/{key}?fields={field_id}` and skip the write if the actor is already set | Always on; not configurable |

#### Scenario: A webhook re-delivery within the L1 TTL window is suppressed
- **WHEN** the same `jira:issue_updated` payload arrives twice within `JIRA_DEV_IN_CHARGE_DEDUPE_TTL_SECONDS`
- **THEN** only the first delivery SHALL enqueue a write
- **AND** the second delivery SHALL be suppressed by L1
- **AND** no second `dev_in_charge_set` log event SHALL be emitted

#### Scenario: A write whose actor already matches the current value is suppressed by L3
- **WHEN** the flush tick processes an issue whose current `Dev in Charge` already equals the actor's account ID
- **THEN** the write SHALL be skipped
- **AND** a `dev_in_charge_skip already_set` log event SHALL be emitted
- **AND** the issue SHALL be marked in the L1 dedup window (so re-enqueue within TTL is also suppressed)

### Requirement: Batched, time-based flush

The system SHALL drain pending writes in a background flush loop that:

- Runs every `JIRA_DEV_IN_CHARGE_FLUSH_INTERVAL_SECONDS` (default 5)
- Processes at most `JIRA_DEV_IN_CHARGE_BATCH_SIZE` issues per tick (default 50)
- Issues writes via `PUT /rest/api/3/issue/{key}` with body `{"fields": {"customfield_11520": {...}}}`
- Catches and logs exceptions per-issue so one failure does not block the rest of the chunk

The flush loop SHALL start during `create_app()` startup and SHALL perform a final drain on shutdown.

#### Scenario: A burst of 50 transitions flushes in one tick
- **WHEN** 50 webhook transitions arrive in a single second
- **AND** none of them have been flushed yet
- **THEN** the next flush tick SHALL process all 50 in one chunk
- **AND** the tick SHALL emit one `dev_in_charge_flush` log event with `wrote=50, skipped=0, failed=0`

#### Scenario: A 51st transition within the same window defers to the next tick
- **WHEN** 51 webhook transitions arrive in a single second
- **THEN** the first 50 SHALL be processed in the first tick
- **AND** the 51st SHALL be processed in the next tick

#### Scenario: A write failure on one issue does not block the rest of the chunk
- **WHEN** a `PUT /rest/api/3/issue/{key}` call raises (e.g. 400 Bad Request because the field was removed from the project)
- **THEN** the system SHALL log `dev_in_charge_set_failed` with the error
- **AND** the issue SHALL NOT be marked in the L1 dedup window
- **AND** the remaining issues in the chunk SHALL proceed

### Requirement: Schema auto-discovery

The system SHALL probe the `Dev in Charge` field schema at module mount via a single `GET /rest/api/3/field/{field_id}` call. The probe result SHALL be cached for the process lifetime.

Based on the probed `schema.type`, the system SHALL build the write payload as follows:

| Probed `schema.type` | Write payload |
|---|---|
| `user` | `{"customfield_11520": {"accountId": "..."}}` |
| `array` with `items=user` | `{"customfield_11520": [{"accountId": "..."}]}` |
| other | Setter disabled; warning logged at mount |

#### Scenario: Single-user picker field is auto-detected
- **WHEN** the field schema reports `type=user`
- **THEN** the setter SHALL build write payloads using the single-user shape
- **AND** the mount log SHALL include `schema_type=user is_multi_user=False`

#### Scenario: Multi-user picker field is auto-detected
- **WHEN** the field schema reports `type=array` with `items=user`
- **THEN** the setter SHALL build write payloads using the multi-user shape
- **AND** the mount log SHALL include `schema_type=array is_multi_user=True`

#### Scenario: Unsupported schema type disables the setter
- **WHEN** the field schema reports an unexpected type (e.g. `group`, `option`, `string`)
- **THEN** the system SHALL log `dev_in_charge_unsupported_schema type=<type>` WARNING at mount
- **AND** `_setter` SHALL remain `None`
- **AND** all subsequent `enqueue_dev_in_charge()` calls SHALL be no-ops
- **AND** the webhook handler SHALL continue to function normally

### Requirement: Fail-isolated mount

The system SHALL mount the `Dev in Charge` setter inside a `try/except` block in `create_app()`. On any failure (probe error, env validation error, or unexpected exception), the system SHALL log a `dev_in_charge_setter_init_failed` WARNING and leave `_setter` as `None`. The webhook handler, the existing `TransitionGuard`, and all other FastAPI routes SHALL continue to function normally.

#### Scenario: Mount failure isolates from the webhook handler
- **WHEN** `mount_dev_in_charge_setter()` raises during `create_app()`
- **THEN** the system SHALL log `dev_in_charge_setter_init_failed` with the error
- **AND** the webhook handler SHALL NOT raise
- **AND** the existing `TransitionGuard` SHALL continue to function
- **AND** `/health` SHALL report `dev_in_charge_setter.enabled=False`

### Requirement: Health endpoint exposes setter status

The system SHALL extend the `/health` endpoint response with a `dev_in_charge_setter` block containing:

- `enabled` (boolean)
- `projects` (sorted list of project keys)
- `trigger_status` (string)
- `dedupe_ttl_seconds` (int)
- `batch_size` (int)
- `flush_interval_seconds` (int, when applicable)

When the setter is not mounted, the block SHALL be omitted.

#### Scenario: Healthy setter reports full config in /health
- **WHEN** the setter is mounted and `/health` is called
- **THEN** the response SHALL include `dev_in_charge_setter` with all six fields populated
- **AND** `enabled` SHALL be `True`

#### Scenario: Unmounted setter is absent from /health
- **WHEN** the setter failed to mount
- **THEN** the response SHALL NOT include `dev_in_charge_setter`

### Requirement: Configurable via environment variables

The system SHALL read all knobs from environment variables at module mount time, with safe defaults that match the project's existing convention:

| Env var | Default | Purpose |
|---|---|---|
| `JIRA_DEV_IN_CHARGE_FIELD_ID` | `customfield_11520` | Override the field ID for re-pin scenarios |
| `JIRA_DEV_IN_CHARGE_PROJECTS` | `AM,AU,COM,FUN,GAMI,PDS,PPMT,PUB,PWM,RMD,SR,STABI,TJ` | Comma-separated project keys (case-insensitive) |
| `JIRA_DEV_IN_CHARGE_TRIGGER_STATUS` | `In Progress` | Status name that triggers auto-set |
| `JIRA_DEV_IN_CHARGE_DEDUPE_TTL_SECONDS` | `10` | L1 dedup window |
| `JIRA_DEV_IN_CHARGE_BATCH_SIZE` | `50` | Writes per flush chunk |
| `JIRA_DEV_IN_CHARGE_FLUSH_INTERVAL_SECONDS` | `5` | Time between flush ticks |

#### Scenario: All defaults work without any env var being set
- **WHEN** none of the six env vars are set
- **THEN** the setter SHALL mount successfully with the defaults above
- **AND** the boot log SHALL include `projects=[<13 projects>]` and `trigger_status="In Progress"`

#### Scenario: JIRA_DEV_IN_CHARGE_PROJECTS is parsed as a set
- **WHEN** `JIRA_DEV_IN_CHARGE_PROJECTS` is set to `"am, tj ,com"` (mixed case and whitespace)
- **THEN** the setter SHALL treat the project allow-list as `{"AM", "TJ", "COM"}`
- **AND** issues in those projects (case-insensitive match on the issue key prefix) SHALL be enqueued

### Requirement: Operational-mode warning on unset webhook secret

The system SHALL check whether `JIRA_WEBHOOK_SECRET` is set at module mount time. When it is unset, the system SHALL emit a `dev_in_charge_degraded_mode` WARNING log line noting that HMAC verification is bypassed (per `routes.py:73` — the `if _secret and ...` short-circuit). This applies symmetrically to the existing `TransitionGuard`: both modules share the same conditional HMAC protection.

#### Scenario: Mount with no secret logs a degraded-mode warning
- **WHEN** `JIRA_WEBHOOK_SECRET` is unset at the time of `mount_dev_in_charge_setter()`
- **THEN** the system SHALL emit a `dev_in_charge_degraded_mode` WARNING log
- **AND** the setter SHALL continue to operate (HMAC bypass is the intended behavior for unsigned-webhook deployments, not an error condition)

#### Scenario: Mount with a secret does not log the warning
- **WHEN** `JIRA_WEBHOOK_SECRET` is set
- **THEN** no `dev_in_charge_degraded_mode` log SHALL be emitted

### Requirement: L3 read-before-write uses webhook payload first, GET as fallback

The system SHALL perform the L3 read-before-write check by attempting to read the field's current value from the in-memory `event.fields` dict first. When the webhook payload does not include the field (i.e. `event.fields.get(field_id) is None`), the system SHALL fall back to a `GET /rest/api/3/issue/{key}?fields={field_id}` call.

This optimization avoids one REST API call per write in the common case where the webhook payload includes the field (the default Jira Cloud behavior).

#### Scenario: Webhook payload includes the field — no API call
- **WHEN** `event.fields.get(field_id)` returns a non-None value
- **THEN** the system SHALL use that value for the L3 check
- **AND** SHALL NOT issue a `GET /rest/api/3/issue/{key}` call

#### Scenario: Webhook payload omits the field — fallback to GET
- **WHEN** `event.fields.get(field_id)` returns None
- **THEN** the system SHALL issue a `GET /rest/api/3/issue/{key}?fields={field_id}`
- **AND** SHALL use the response for the L3 check
- **AND** SHALL emit a `dev_in_charge_l3_payload_miss` DEBUG log line so operators can diagnose webhook configuration gaps

### Requirement: L3 semantics differ between single-user and multi-user fields

For **single-user** fields (`schema.type == "user"`), the L3 check SHALL skip the write when `current.accountId == actor_account_id`. For **multi-user** fields (`schema.type == "array"` with `items == "user"`), the L3 check SHALL skip the write when `actor_account_id in [u.accountId for u in current]`. The setter SHALL NEVER replace the existing array — it SHALL only append `actor_account_id` to the array if not already present.

#### Scenario: Single-user field with matching actor is skipped
- **WHEN** the current field value is `{"accountId": "X"}`
- **AND** the actor is `X`
- **THEN** the system SHALL skip the write
- **AND** SHALL emit `dev_in_charge_skip reason=already_set`

#### Scenario: Multi-user field with matching actor in array is skipped
- **WHEN** the current field value is `[{"accountId": "A"}, {"accountId": "B"}]`
- **AND** the actor is `B`
- **THEN** the system SHALL skip the write

#### Scenario: Multi-user field with non-matching actor is appended, never replaced
- **WHEN** the current field value is `[{"accountId": "A"}, {"accountId": "B"}]`
- **AND** the actor is `C`
- **THEN** the system SHALL write `[{"accountId": "A"}, {"accountId": "B"}, {"accountId": "C"}]`
- **AND** SHALL NOT write `[{"accountId": "C"}]` (which would lose A and B)

### Requirement: L1 dedup is set at enqueue time, not just on flush

The system SHALL set the L1 dedup entry at `enqueue()` time, not only at `_mark_written()` time inside `flush()`. This closes the race window where two webhooks for the same issue arrive within the same flush tick.

#### Scenario: Two webhooks for the same issue within one flush tick
- **WHEN** webhook 1 arrives at T=0.0s and enqueues a write for `issue_key`
- **AND** webhook 2 arrives at T=0.05s for the same `issue_key` (e.g. Jira re-delivery)
- **THEN** webhook 2 SHALL be suppressed by L1 immediately
- **AND** only one write SHALL appear in the next flush tick's pending set

### Requirement: Interaction with existing policies

The system SHALL coexist with the existing `TransitionGuard` policy engine without coordination. Both consume the same `TransitionEvent` and operate independently. On a transition to `In Progress` where `customfield_10015` (Start Date) is empty:

1. The `TransitionGuard` SHALL post a reminder comment (via `Tagger.post_mention()`) per the `in_progress_start_date` policy.
2. The `DevInChargeSetter` SHALL enqueue a write of `customfield_11520` to the actor's account ID.
3. Both side-effects SHALL complete within seconds.

The two side-effects cover different fields and do not cancel each other. There is no deduplication between them.

#### Scenario: Both side-effects fire on a transition to In Progress with both fields empty
- **WHEN** a developer moves an issue to `In Progress`
- **AND** `customfield_10015` is empty
- **AND** `customfield_11520` is empty
- **THEN** the user SHALL see a reminder comment about Start Date within 1 second
- **AND** SHALL see `customfield_11520` populated to the actor within 5 seconds
- **AND** the order of the two events is not guaranteed

### Requirement: Flush task lifecycle managed by FastAPI lifespan

The system SHALL schedule the flush task inside the existing FastAPI `lifespan` async context manager in `api/app.py:create_app()`, not at module-import time. The setter module SHALL expose `async start_flush_loop()` and `async stop_flush_loop()` functions called from `lifespan`. This avoids the deprecated `asyncio.get_event_loop()` API (removed in Python 3.12+).

#### Scenario: Flush task starts on app startup
- **WHEN** the FastAPI lifespan startup phase runs
- **THEN** the system SHALL call `await start_flush_loop()`
- **AND** the flush task SHALL begin running at the configured interval

#### Scenario: Flush task performs a final drain on app shutdown
- **WHEN** the FastAPI lifespan shutdown phase runs
- **THEN** the system SHALL call `await stop_flush_loop()`
- **AND** any pending writes SHALL be drained before the task exits
- **AND** the task SHALL NOT leave writes stranded in memory

### Requirement: Audit log append to shared JSONL

The system SHALL append a JSONL line to `~/.tdt/logs/jira-reminders.log` (the same audit log used by the existing `TransitionGuard` and the cron `ReminderRunner`) for each `dev_in_charge_set` and `dev_in_charge_set_failed` event. The append SHALL be best-effort: failures (e.g. permission errors, disk full) SHALL be logged as `dev_in_charge_audit_append_failed` WARNING but SHALL NOT propagate.

The appended line SHALL include `source: "dev_in_charge_setter"` so the cron reconciliation tooling can distinguish from `source: "jira_guard"`.

#### Scenario: A successful write appends to the shared audit log
- **WHEN** `dev_in_charge_set` fires
- **THEN** the system SHALL append a JSONL line to `~/.tdt/logs/jira-reminders.log`
- **AND** the line SHALL include `source=dev_in_charge_setter`, `issue_key`, `account_id`, `prev`, `schema_type`

#### Scenario: An audit append failure does not block the write
- **WHEN** the write to the audit log raises (e.g. PermissionError, OSError)
- **THEN** the system SHALL log `dev_in_charge_audit_append_failed` WARNING
- **AND** the underlying `dev_in_charge_set` SHALL still be considered successful

### Requirement: Health endpoint honors the route's `_enabled` kill switch

The system SHALL report `enabled` in the `/health` block as `_setter is not None AND _enabled`, where `_enabled` is the module-level global from `webhook_receiver/jira_guard/routes.py` (set at `mount_jira_guard()` time from `settings.jira_guard_enabled`). This ensures the reported state matches the effective runtime state.

#### Scenario: Setter mounted but route disabled
- **WHEN** the setter module is mounted (`_setter is not None`)
- **AND** the route's `_enabled` is False
- **THEN** the `/health` response SHALL report `dev_in_charge_setter.enabled = False`

#### Scenario: Setter mounted and route enabled
- **WHEN** the setter module is mounted
- **AND** the route's `_enabled` is True
- **THEN** the `/health` response SHALL report `dev_in_charge_setter.enabled = True`

### Requirement: One structured log event per write attempt

For each `enqueue_dev_in_charge` → flush path, the system SHALL emit exactly one of the following structured log events:

| Event | When |
|---|---|
| `dev_in_charge_set` | Write succeeded; includes `issue`, `account_id`, `prev`, `schema_type` |
| `dev_in_charge_set_failed` | Write raised; includes `issue`, `error` |
| `dev_in_charge_skip` | Write skipped by L3 read-before-write; includes `issue`, `reason="already_set"` |
| `dev_in_charge_skip_no_actor` | Webhook arrived without an actor account ID; includes `issue` |
| `dev_in_charge_flush` | Per-tick summary; includes `wrote`, `skipped`, `failed` |
| `dev_in_charge_schema_discovered` | Boot probe success; includes `field_id`, `field_type`, `is_multi_user` |
| `dev_in_charge_unsupported_schema` | Boot probe found unexpected type; includes `field_type` |
| `dev_in_charge_setter_init_failed` | Mount raised; includes `error` |
| `dev_in_charge_setter_mounted` | Mount succeeded; includes `projects`, `trigger_status`, `ttl_seconds`, `batch_size`, `flush_interval_seconds` |

#### Scenario: Successful write emits dev_in_charge_set
- **WHEN** a write succeeds
- **THEN** the log event SHALL include `issue`, `account_id`, `prev` (list of account IDs currently set), `schema_type` (e.g. `"user"` or `"array"`)

#### Scenario: Failed write emits dev_in_charge_set_failed with the error
- **WHEN** a write raises (e.g. 400 from Jira)
- **THEN** the log event SHALL include `issue` and `error` (string from the exception)

### Requirement: Reuses existing Jira client

The system SHALL receive the `PatchedJira` client as a parameter to `mount_dev_in_charge_setter()` rather than creating a new one via `JiraClientFactory.from_env()`.

#### Scenario: No duplicate Jira client is created
- **WHEN** `mount_dev_in_charge_setter(jira_client)` is called
- **THEN** the system SHALL use the provided `jira_client` for all subsequent calls
- **AND** no second `JiraClientFactory.from_env()` invocation SHALL occur
- **AND** no second `requests.Session` SHALL be created