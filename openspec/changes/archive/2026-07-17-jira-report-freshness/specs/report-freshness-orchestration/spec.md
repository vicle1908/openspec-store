## ADDED Requirements

### Requirement: Keep Jira report freshness hybrid
The system SHALL support a hybrid freshness model for `Sprint Report` and `Person Capacity` that combines scheduled refreshes with webhook-triggered refreshes.

#### Scenario: Report pair is refreshed together
- **WHEN** any supported freshness path runs
- **THEN** the system SHALL refresh `Sprint Report` and `Person Capacity` together from the same execution snapshot
- **AND** it SHALL NOT refresh only one of the two tabs as the normal path

#### Scenario: Scheduled refresh runs
- **WHEN** the configured schedule triggers a report refresh
- **THEN** the system SHALL execute the existing `sprint-sheet` flow and refresh both tabs from a single report snapshot

#### Scenario: Scheduled refresh keeps the pair at least daily-fresh
- **WHEN** the generated cron schedule is the only active freshness path (webhook-triggered refresh disabled)
- **THEN** the scheduled `sprint-sheet` refresh SHALL run at least once per day so the pair is never more than one day stale
- **AND** the schedule SHALL NOT fall back to a weekly-only cadence for the `Sprint Report` + `Person Capacity` pair

#### Scenario: Webhook-triggered refresh runs
- **WHEN** a relevant Jira webhook event indicates report data may have changed
- **THEN** the system SHALL be able to trigger or enqueue the same `sprint-sheet` refresh flow without changing report content semantics
- **AND** the resulting refresh SHALL update both `Sprint Report` and `Person Capacity`

#### Scenario: Webhook is unavailable
- **WHEN** webhook-triggered refresh is unavailable or disabled
- **THEN** the scheduled refresh SHALL continue to function as a fallback and safety net

### Requirement: Preserve report calculation contract
The freshness layer SHALL not change how sprint or person-capacity rows are calculated, only when the existing report execution is invoked.

#### Scenario: Report calculations run unchanged
- **WHEN** a refresh is triggered by schedule or webhook
- **THEN** the system SHALL use the existing report calculations, sheet layout, and reconciliation rules

#### Scenario: Workbook source tabs remain read-only
- **WHEN** the freshness flow triggers a report refresh
- **THEN** it SHALL not modify source Jira planning tabs or mapping tabs
- **AND** it SHALL only write generated report tabs such as `Sprint Report` and `Person Capacity`

### Requirement: Use a single executor boundary for the report pair
The system SHALL use one report executor boundary for the `Sprint Report` and `Person Capacity` pair, and webhook ingress SHALL only request refreshes rather than calculate or write the report itself.

#### Scenario: Webhook ingress receives a freshness event
- **WHEN** `webhook-receiver` accepts a relevant Jira event for freshness
- **THEN** it SHALL hand off or enqueue a refresh request instead of directly rewriting report calculations
- **AND** the actual report write SHALL be performed by the existing report executor path

#### Scenario: Refresh dispatch does not block ingress
- **WHEN** `webhook-receiver` decides to trigger a refresh
- **THEN** it SHALL invoke the report executor as a non-blocking background process and return its webhook response promptly
- **AND** it SHALL NOT run the full report computation inline within the webhook request handler

#### Scenario: A refresh is already running
- **WHEN** a refresh request arrives while a prior refresh for the same report target is still in flight
- **THEN** the system SHALL coalesce or skip the new request rather than starting a concurrent overlapping refresh

#### Scenario: Scheduler invokes the report executor
- **WHEN** the cron schedule fires
- **THEN** the same report executor boundary SHALL be used for the refresh

### Requirement: Treat the report pair as one refresh unit
The system SHALL treat `Sprint Report` and `Person Capacity` as a single refresh unit for orchestration, visibility, and fallback behavior.

#### Scenario: One tab is stale
- **WHEN** either `Sprint Report` or `Person Capacity` is stale
- **THEN** the freshness layer SHALL consider the report pair stale and refresh both together

#### Scenario: Refresh completes successfully
- **WHEN** the refresh unit completes successfully
- **THEN** both tabs SHALL reflect the same freshness run and the same underlying Jira snapshot

#### Scenario: Pair freshness is evaluated
- **WHEN** an operator or health check evaluates freshness
- **THEN** the report pair SHALL be considered fresh only if both tabs were produced by the same successful refresh run

### Requirement: Debounce webhook-triggered refreshes
The system SHALL deduplicate or debounce webhook-triggered refresh requests so bursts of Jira events do not cause repeated sheet writes for the same freshness window.

#### Scenario: Multiple events arrive for one issue
- **WHEN** multiple relevant Jira events arrive within the debounce window
- **THEN** the system SHALL coalesce them into a single report refresh request

#### Scenario: Events for different issues share one refresh window
- **WHEN** relevant events for several different issues arrive within the same debounce window
- **THEN** the system SHALL coalesce them into a single refresh of the report target
- **AND** it SHALL NOT fan out into one refresh per changed issue

#### Scenario: Duplicate delivery occurs
- **WHEN** Jira retries or re-delivers the same event
- **THEN** the system SHALL avoid scheduling duplicate refresh execution for the same effective change window

### Requirement: Scope refresh triggers to relevant Jira events
The system SHALL only consider Jira webhook events that can affect sprint report or person-capacity freshness, evaluated by a dedicated freshness-relevance predicate rather than the status-only transition-guard parser.

#### Scenario: Irrelevant event arrives
- **WHEN** a webhook event cannot affect sprint or capacity output
- **THEN** the system SHALL ignore it for freshness triggering purposes

#### Scenario: Relevant event arrives
- **WHEN** a webhook event can affect issue scope, ownership, estimate, status, or worklog state
- **THEN** the system SHALL allow it to trigger a freshness refresh

#### Scenario: Non-status field change arrives
- **WHEN** a Jira changelog modifies a relevant field other than status, such as assignee, estimate, sprint membership, or worklog
- **THEN** the freshness predicate SHALL treat the event as relevant
- **AND** the system SHALL NOT discard it solely because no status transition occurred

### Requirement: Expose freshness mode for operators
The system SHALL make the refresh source visible through logs and operational output so operators can distinguish scheduled, webhook-triggered, manual, and fallback refreshes.

#### Scenario: Refresh completes
- **WHEN** a report refresh finishes
- **THEN** the system SHALL record whether the refresh was schedule-driven, webhook-driven, manual, or fallback-driven

#### Scenario: Freshness troubleshooting is needed
- **WHEN** an operator inspects the system state or logs
- **THEN** they SHALL be able to determine which freshness path last updated the report

### Requirement: Refresh status SHALL be pair-level
The system SHALL represent freshness state at the report-pair level rather than as two independent tab states.

#### Scenario: One tab lags behind
- **WHEN** `Sprint Report` and `Person Capacity` do not share the same successful refresh run marker
- **THEN** the pair SHALL be considered stale

#### Scenario: Pair refresh marker is available
- **WHEN** the system records a successful refresh
- **THEN** it SHALL attach a shared freshness marker or equivalent run identifier to both tabs or the execution record
