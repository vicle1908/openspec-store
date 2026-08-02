# observability-slos

## ADDED Requirements

### Requirement: SLO-1: Webhook Delivery Reliability (Target: 99.5%)

The system SHALL track webhook delivery reliability as an SLO. The SLI is defined as the ratio of `handoff_dispatch_accepted` events to total dispatch attempts within the measurement window. The target is 99.5%, corresponding to a monthly error budget of 3.6 hours (0.5% × 30 days × 24 hours). The measurement window is a 30-day rolling window.

A dispatch attempt is counted when webhook-receiver calls `POST http://127.0.0.1:8090/reviews/gitlab-mr`.

#### Scenario: Successful dispatch increments success counter

- **WHEN** webhook-receiver logs `event="handoff_scheduled"` with a 200-level response from ai-review
- **THEN** the SLO tracker SHALL record this as a success event for SLO-1

#### Scenario: Failed dispatch increments failure counter

- **WHEN** webhook-receiver logs `event="handoff_dispatch_failed"` or the dispatch call raises an exception
- **THEN** the SLO tracker SHALL record this as a failure event for SLO-1

#### Scenario: 30-day availability ratio computed correctly

- **WHEN** SLO-1 is queried
- **THEN** it SHALL return `success_count / (success_count + failure_count)` over the last 30 days

### Requirement: SLO-2: Review Pipeline Latency (Target: 95% within 600 seconds)

The system SHALL track review pipeline latency. The SLI is the percentage of review pipelines completing within 600 seconds (10 minutes) of intake. The target is 95%. The measurement window is a 30-day rolling window.

A pipeline is considered complete when ai-review logs `event="orchestration_completed"` or `event="review_complete"`.

#### Scenario: Intake timestamp recorded

- **WHEN** ai-review receives an intake request and begins orchestration
- **THEN** the SLO tracker SHALL record the `timestamp` of the `event="orchestration_started"` or equivalent intake log event

#### Scenario: Within-threshold completion counted as success

- **WHEN** ai-review logs `event="orchestration_completed"` with `elapsed_seconds <= 600`
- **THEN** the SLO tracker SHALL record this as a success event for SLO-2

#### Scenario: Over-threshold completion counted as failure

- **WHEN** ai-review logs `event="orchestration_completed"` with `elapsed_seconds > 600`
- **THEN** the SLO tracker SHALL record this as a failure event for SLO-2

### Requirement: SLO-3: Scheduler DBOS Connectivity (Target: 99.9%)

The system SHALL track scheduler connectivity. The SLI is the percentage of health checks where `dbos_connected=true` from the tdt-scheduler's `/scheduler/health` endpoint. The target is 99.9%, allowing 43.2 minutes of downtime budget per 30-day window (0.1% × 30 days × 24 hours). The measurement window is a 30-day rolling window.

#### Scenario: Connected check increments success counter

- **WHEN** the health poller reads a snapshot from tdt-scheduler where `dbos_connected=true`
- **THEN** the SLO tracker SHALL record this as a success event for SLO-3

#### Scenario: Disconnected check increments failure counter

- **WHEN** the health poller reads a snapshot where `dbos_connected=false` or the service is unreachable
- **THEN** the SLO tracker SHALL record this as a failure event for SLO-3

### Requirement: Multi-Window Burn-Rate Alerting with Exact Formula

For each SLO, the system SHALL implement multi-window burn-rate alerting. The burn rate for a window is computed as:

```
burn_rate = (error_rate_in_window / allowed_error_rate) / (window_size_seconds / total_window_seconds)

where:
  error_rate_in_window = failures_in_window / total_requests_in_window
  allowed_error_rate = 1 - target (e.g., 0.005 for 99.5%)
  total_window_seconds = 30 days = 2,592,000 seconds
```

Two alert tiers SHALL be evaluated:

**Fast-burn alert (critical):** Fires when `burn_rate >= 14.4` for BOTH the 1-hour window AND the 6-hour window. This indicates the monthly error budget would be exhausted in 1 hour.

**Slow-burn alert (warning):** Fires when `burn_rate >= 3.0` for BOTH the 6-hour window AND the 3-day window. This indicates the monthly error budget would be exhausted in 6 hours.

#### Scenario: Fast-burn alert fires for SLO-1

- **WHEN** SLO-1's burn rate is 18.0 for the 1-hour window AND 15.0 for the 6-hour window
- **THEN** the system SHALL emit a critical alert: `event="slo_burn_alert"`, `slo="webhook-delivery"`, `severity="critical"`, `burn_rate=18.0`, `window="1h+6h"`

#### Scenario: Slow-burn warning fires for SLO-2

- **WHEN** SLO-2's burn rate is 4.5 for the 6-hour window AND 3.2 for the 3-day window
- **THEN** the system SHALL emit a warning alert: `event="slo_burn_alert"`, `slo="review-latency"`, `severity="warning"`, `burn_rate=4.5`, `window="6h+3d"`

#### Scenario: Alert clears when burn rate normalizes

- **WHEN** SLO-1's burn rate falls below 14.4 for both fast-burn windows
- **THEN** the system SHALL emit a resolved alert: `event="slo_burn_resolved"`, `slo="webhook-delivery"`, `burn_rate=X`

### Requirement: SLO Budget Dashboard Page

The observability dashboard SHALL display an SLO budget page (Phase 3) with for each SLO:

- Current 30-day availability ratio as a percentage (e.g., `99.7%`)
- Remaining error budget as both a percentage and absolute time (e.g., `84% remaining / 3.0h of 3.6h`)
- Current burn rate
- Estimated time to budget exhaustion (computed as: `remaining_budget_hours / burn_rate`)

Each SLO SHALL be displayed with a color-coded status: green when budget remaining > 50%, yellow when 20–50%, red when < 20%.

#### Scenario: SLO-3 gauge shows budget at risk

- **WHEN** SLO-3 (scheduler connectivity) is at 99.7% with a burn rate of 2.0
- **THEN** the dashboard SHALL display: ratio `99.7%`, remaining budget `~21h of 43.2h (48%)`, burn rate `2.0x`, estimated exhaustion `~10.5 days` — color-coded yellow

### Requirement: Weekly SLO Summary Logged and Stored

The system SHALL emit a structured `slo_weekly_summary` log event every Sunday at 00:00 UTC. This event SHALL be stored in DuckDB for historical tracking and SHALL contain snapshots of all three SLOs.

The event SHALL include: `event`, `timestamp`, `week_start` (date 7 days ago), `week_end` (date today), and for each SLO: `slo_name`, `slo_ratio`, `budget_remaining_pct`, `budget_exhausted_hours`, `burn_rate`, `status` (ok/warning/critical).

#### Scenario: Weekly summary captures all three SLOs

- **WHEN** the weekly job runs
- **THEN** it SHALL emit: `event="slo_weekly_summary"`, `slo1_ratio=0.997`, `slo1_budget_remaining=0.84`, `slo2_ratio=0.968`, `slo2_budget_remaining=0.61`, `slo3_ratio=0.999`, `slo3_budget_remaining=0.97`
