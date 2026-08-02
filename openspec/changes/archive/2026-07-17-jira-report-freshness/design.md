## Context

`jira-daily-reports` already has a stable cron-oriented scheduler and a `sprint-sheet` command that writes both `Sprint Report` and `Person Capacity` from one Jira snapshot. Separately, `webhook-receiver` already provides a production webhook ingress/service boundary for GitLab events and Jira transition guard handling. What is missing is a coherent freshness strategy that keeps the *pair* current soon after relevant Jira changes while still remaining resilient when webhooks are delayed, dropped, or unavailable.

The underlying reporting problem spans two systems and two freshness domains:

- Jira changes can make the sprint report and person capacity stale between scheduled runs, and those two tabs should always be refreshed together from the same snapshot.
- Google Sheets planning data can change without Jira changing, so any freshness solution must retain periodic reconciliation.
- The existing report flow is already validated end-to-end and should not be rewritten; freshness should orchestrate when it runs, not redefine report content.

Stakeholders:

- Engineers and managers who rely on the sheet as a near-current planning snapshot.
- Operators who need an understandable refresh path with predictable failure modes.
- Existing cron-based automation users who need backward compatibility.

## Goals / Non-Goals

**Goals:**
- Keep `Sprint Report` and `Person Capacity` reasonably fresh as an atomic pair with a hybrid trigger model.
- Preserve cron as a durable fallback/safety net.
- Allow relevant Jira webhooks to trigger or enqueue a report refresh that updates both tabs together.
- Prevent duplicate refresh storms from webhook bursts.
- Keep the report content contract and workbook layout unchanged.
- Make freshness mode observable enough for operators to know whether a refresh came from schedule, webhook, or fallback.

**Non-Goals:**
- Redesigning sprint/person-capacity calculations.
- Replacing cron entirely.
- Turning `webhook-receiver` into a generic job runner.
- Adding direct sheet-write logic to arbitrary webhook handlers without a defined refresh boundary.
- Introducing a new external queueing system unless it becomes necessary later.

## Decisions

1. **Hybrid freshness model: cron + webhook**
   - Cron remains the baseline scheduler and backstop.
   - Webhooks accelerate refreshes after relevant Jira changes.
   - Alternatives considered:
     - Cron only: simple, but laggy.
     - Webhook only: responsive, but fragile and incomplete because spreadsheet-side changes are not evented by Jira.
   - Rationale: report freshness depends on both Jira and workbook state, so one mechanism alone is insufficient.

2. **Orchestration lives at the boundary, not in report calculation code**
   - Keep `jira-daily-reports sprint-sheet` as the canonical report executor.
   - Let the freshness layer decide *when* to run it, not *how* to compute rows.
   - Keep `webhook-receiver` ingress-only for freshness triggers; it should dispatch or enqueue a refresh request rather than rewrite report logic.
   - Alternatives considered:
     - Embed webhook handling directly in `jira-daily-reports`: couples CLI/report code to ingress concerns.
     - Add a separate always-on worker service: more complex operationally.
   - Rationale: report correctness and trigger routing should stay decoupled.

3. **The report pair should have one source of freshness truth**
   - Track freshness at the pair level (`Sprint Report` + `Person Capacity`), not per tab.
   - The pair is fresh only when both tabs were produced by the same `sprint-sheet` run.
   - Alternatives considered:
     - Independent tab refreshes: risks drift between the ticket and capacity views.
   - Rationale: operators and stakeholders consume the two tabs together, so freshness should be atomic.

4. **Webhook-triggered refreshes must be debounced/deduplicated**
   - Multiple Jira events for the same issue or sprint window should coalesce into one refresh of the report pair.
   - The debounce window should be configurable and bounded.
   - The debounce key SHALL be the **report target** (the sprint/workbook refresh unit), NOT the issue key. The existing `ReviewDebouncer` keys per `mr_iid`; reusing that granularity would let N changed issues fan out into N refreshes, defeating coalescing. A freshness debouncer SHALL collapse all relevant events within the window onto a single per-target key.
   - Alternatives considered:
     - Debounce per issue key (reuse `ReviewDebouncer` as-is): N issues → N refreshes, defeats the purpose.
     - Fire a refresh on every event: too noisy and expensive.
     - Use a persistent queue as the only dedupe mechanism: more infrastructure than needed for v1.
   - Rationale: the refresh unit is the pair/sprint, so the dedup key must match the refresh unit, not the triggering issue.

5. **Scheduled refresh remains authoritative for recovery**
   - Even if webhook-triggered refresh is enabled, the schedule must still run.
   - The schedule provides recovery from missed events, auth failures, and webhook outages.
   - Alternatives considered:
     - Webhook as primary, cron only as optional: too risky for a workbook used as a planning source of truth.
   - Rationale: this workbook is operational data, so resilience matters more than instant updates.

6. **Refresh mode must be visible in logs/health output**
   - The system should indicate whether a refresh came from cron, webhook, manual invocation, or fallback.
   - Alternatives considered:
     - Silent refreshes with no mode reporting: hard to troubleshoot freshness drift.
   - Rationale: freshness problems often present as staleness, so operator observability is part of the feature.

7. **Webhook scope should be narrowly relevant**
   - Only Jira event classes that can affect sprint report/person-capacity freshness should trigger refresh consideration.
   - Alternatives considered:
     - Trigger on all webhook activity: unnecessary churn.
   - Rationale: keep trigger volume low and relevance high.

8. **Webhook → report dispatch is a non-blocking subprocess, not an HTTP intake**
   - `jira-daily-reports` is a CLI (`@app.command("sprint-sheet")`), not an HTTP service, so there is no intake endpoint to POST to (unlike the GitLab→ai-review path).
   - `webhook-receiver` SHALL spawn a non-blocking background invocation of the existing CLI (`uv run jira-daily-reports sprint-sheet ...`), identical to how cron invokes it, guarded by an in-flight lock.
   - Alternatives considered:
     - Add an HTTP endpoint to `jira-daily-reports`: turns a batch CLI into an always-on service (more ops surface, conflicts with Non-Goals).
     - Run `sprint-sheet` inline inside the webhook handler: heavy Jira fetch + sheet write would block ingress and risk Jira webhook timeouts.
   - Rationale: reuse the proven cron invocation path; keep ingress fast and the report executor unchanged.

9. **Freshness event detection is separate from the transition-guard parser**
   - The existing `jira_guard/events.py:parse_webhook_payload` returns `None` unless the changelog contains a **status** change, so it would silently drop estimate, assignee, worklog, and scope changes that the narrow-webhook-scope decision requires.
   - A dedicated freshness-relevance predicate SHALL inspect the changelog for any field in the relevant set (scope/sprint membership, assignee/ownership, estimate, status, worklog) rather than reusing the status-only guard parser.
   - Alternatives considered:
     - Reuse `parse_webhook_payload` as-is: would miss most freshness-affecting changes.
   - Rationale: the guard parser and the freshness trigger have different relevance contracts; coupling them would under-trigger refreshes.

## Risks / Trade-offs

- [Risk] Webhook-triggered refresh overlaps with cron and causes duplicate writes → Mitigation: debounce window, in-flight guard, and idempotent sheet write behavior; treat the sheet pair as one refresh unit.
- [Risk] Webhook receiver outage causes missed freshness updates → Mitigation: cron remains the safety net and the change must preserve schedule-based refresh.
- [Risk] Triggering refresh too aggressively increases Jira/Sheets API load → Mitigation: narrow event selection and bounded refresh coalescing.
- [Risk] Writing freshness orchestration into the wrong service boundary can create coupling → Mitigation: keep execution in the report repo and routing in the receiver boundary.
- [Risk] Pair freshness can appear healthy while one tab silently lags → Mitigation: treat freshness as stale unless both tabs share the same successful run identifier/timestamp.
- [Risk] Spreadsheet-side planning changes remain invisible to Jira webhooks → Mitigation: preserve periodic schedule and, if necessary, consider later sheet-change triggers as a separate enhancement.

## Migration Plan

1. Define the freshness contract in OpenSpec so the boundary is explicit.
2. Implement a narrow trigger path that can request a `sprint-sheet` refresh without changing report semantics.
3. Preserve existing cron generation and scheduled runs.
4. Add webhook-side dedupe/dispatch rules only for relevant Jira events.
5. Validate with live operations:
   - scheduled refresh still works
   - webhook-triggered refresh works
   - duplicate webhook bursts coalesce
   - sheet output remains unchanged except for freshness cadence
   - both tabs share the same freshness marker/run id after each refresh
6. If webhook dispatch proves unstable, disable webhook-triggered refresh and keep cron-only operation as rollback.

## Resolved Questions

- **Which Jira webhook event set triggers a refresh in v1?** Changelog changes to any of: scope/sprint membership, assignee/ownership, estimate (story points / time estimate), status, and worklog. A dedicated freshness-relevance predicate evaluates these (see Decision 9); the status-only guard parser is NOT reused.
- **Synchronous in-receiver vs enqueue?** Neither inline nor an external queue. `webhook-receiver` spawns a non-blocking background subprocess invoking `jira-daily-reports sprint-sheet` (see Decision 8), guarded by an in-flight lock so a running refresh is not duplicated.
- **Lightweight persistence marker for dedupe across restarts?** Yes. A small local state file records last refresh source, run id, and timestamp so the in-flight guard and debounce survive process restarts.
- **Health endpoint exposes freshness directly?** Yes where practical: surface last refresh source + run id + timestamp via the existing `/health` output so freshness is not inferred only from logs.
- **Where does the freshness marker live?** Both: the shared run id + timestamp is written alongside both generated tabs (or the execution record) AND mirrored in the local state file. The sheet-side marker gives operators in-context truth; the state file supports dedupe/health across restarts.

## Open Questions

- None blocking v1. Spreadsheet-side planning changes remain invisible to Jira webhooks; that gap is covered by the cron safety net and deferred to a possible later sheet-change-trigger enhancement.
