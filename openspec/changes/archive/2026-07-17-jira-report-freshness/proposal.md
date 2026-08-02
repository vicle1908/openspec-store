## Why

`jira-daily-reports sprint-sheet` already produces the sprint report and person capacity tabs, but freshness is still governed by manual runs or cron-only scheduling. That leaves a gap between live Jira/workbook changes and the spreadsheet users rely on for planning and capacity tracking.

## What Changes

- Add a freshness orchestration layer for Jira reporting that combines scheduled refreshes with event-triggered refreshes.
- Keep cron as the durable safety net so report freshness survives missed webhook events or transient outages.
- Use webhook-receiver as the event ingress for Jira-driven refresh triggers, so relevant Jira changes can refresh the sprint report and person capacity together sooner than the next scheduled run.
- Preserve the existing `sprint-sheet` report semantics and workbook layout; this change is about refresh cadence and trigger routing, not report calculations.
- Add deduplication/debouncing so a burst of Jira events does not fan out into repeated sheet writes.
- Make the refresh path explicit and observable with health/logging so operators can tell whether freshness is being driven by schedule, webhook, or both.

## Capabilities

### New Capabilities
- `report-freshness-orchestration`: Hybrid scheduling + webhook-triggered refresh for the `Sprint Report` and `Person Capacity` pair, with debounce, fallback, and operational visibility.

### Modified Capabilities
- `jira-daily-reports`: refresh execution paths and scheduling guidance may gain new trigger modes, but the report content contract remains unchanged.
- `webhook-receiver`: Jira webhook routing may gain a report-refresh dispatch path alongside existing webhook ingress and Jira guard behavior.

## Impact

- `jira-daily-reports`: schedule CLI, sprint-sheet execution, and report delivery orchestration.
- `webhook-receiver`: Jira webhook handling and any new dispatch endpoint or job trigger used to initiate report refreshes.
- `tdt-meta`: OpenSpec docs, runbooks, and operator guidance for keeping sprint report/person capacity current.
- Deployment/runtime docs: cron remains supported, but webhook-driven refresh needs a documented and supportable operating mode.
