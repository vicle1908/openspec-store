# scheduler-webhook-migration Specification

## Purpose

Scheduler webhook migration replaces the legacy debouncers (ReviewDebouncer, FreshnessDebouncer) in webhook-receiver with DBOS DebouncerWrapper, and removes all legacy debouncer files.
## Requirements

_(Baseline: no requirements defined. All requirements are introduced by the `centralized-scheduling-module` change.)_

### Requirement: Replace ReviewDebouncer with DBOS DebouncerWrapper
The `webhook-receiver` SHALL replace its in-memory `ReviewDebouncer` with a DBOS-backed `DebouncerWrapper` from `tdt-core[scheduler]`.

#### Scenario: MR webhook is debounced via DBOS
- **WHEN** a `Merge Request Hook` event arrives at `POST /gitlab-webhook`
- **THEN** the MR review SHALL be debounced using `DebouncerWrapper.debounce(f"mr-{mr_iid}", period_sec=review_debounce_seconds)` instead of the in-memory `ReviewDebouncer`

#### Scenario: Debounce state survives restart
- **WHEN** the webhook-receiver service is restarted
- **THEN** in-flight debounce state SHALL be preserved via DBOS (not lost as with in-memory)

#### Scenario: No asyncio.to_thread workaround
- **WHEN** `schedule_merge_request()` is called
- **THEN** it SHALL NOT use `asyncio.to_thread()` — DBOS workflows are natively async and non-blocking

### Requirement: Replace FreshnessDebouncer with DBOS DebouncerWrapper
The `webhook-receiver` SHALL replace its in-memory `FreshnessDebouncer` with a DBOS-backed `DebouncerWrapper`.

#### Scenario: Freshness event is debounced via DBOS
- **WHEN** a Jira transition event arrives at `POST /webhooks/jira/transition`
- **THEN** the freshness refresh SHALL be debounced using `DebouncerWrapper.debounce(f"fresh-{target}", period_sec=300)`

### Requirement: Remove cleanup_debouncer_task
The hourly `cleanup_debouncer_task()` SHALL be removed — DBOS handles cleanup automatically.

#### Scenario: No manual cleanup loop
- **WHEN** the webhook-receiver starts
- **THEN** there SHALL be no `asyncio.sleep(3600)` cleanup task for debouncer entries

### Requirement: Remove legacy debouncer files
The following files SHALL be removed:
- `webhook-receiver/src/webhook_receiver/core/debouncer.py`
- Debounce logic from `webhook-receiver/src/webhook_receiver/report_freshness.py`

#### Scenario: Legacy files removed
- **WHEN** the migration is complete
- **THEN** `ReviewDebouncer` and `FreshnessDebouncer` classes SHALL no longer exist in the codebase

### Requirement: Webhook response time preserved
The webhook response time SHALL remain under 500ms after migration.

#### Scenario: Response time within limit
- **WHEN** a `POST /gitlab-webhook` request is processed
- **THEN** the response SHALL be returned within 500ms (DBOS debounce is non-blocking)

