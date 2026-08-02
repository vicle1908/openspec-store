# webhook-delivery-self-test

## MODIFIED Requirements

### Requirement: A self-test loop MUST run every 5 minutes, owned by the central DBOS scheduler

The central `tdt-scheduler serve` daemon (in the `agent-core` container) MUST
register a DBOS scheduled workflow (`engine.scheduled_workflow(cron="*/5 * * * *")`)
that runs `webhook_receiver.selftest_cli` as a subprocess. The daemon is
the always-on host for ALL DBOS schedules (per centralize-scheduling
Decision 4) — the receiver is request-driven (uvicorn/FastAPI) and has
no worker thread to drain the internal DBOS queue on its own, so
registering the workflow there produces a backlog of stuck `ENQUEUED`
rows. The workflow MUST:

1. Read the primary URL from `~/.tdt/state/webhook-primary.state` (see
   `webhook-public-ingress-failover` spec).
2. POST a synthetic Merge Request Hook to `<primary>/gitlab-webhook`
   (appended path — the receiver is mounted at `/gitlab-webhook`, not
   the root) with header `X-TDT-Selftest: 1` (the receiver MUST skip
   dedupe and dispatch for these requests).
3. **Present the same `X-Gitlab-Token` value the receiver expects.** The
   DBOS registration wrapper (`webhook_receiver.dbos_scheduling:register_all_schedules`)
   reads `GITLAB_WEBHOOK_SECRET` from the scheduler process environment
   and forwards it as the `webhook_secret` argument to
   `webhook_receiver.selftest.webhook_selftest_workflow`. The probe MUST
   carry that value in the `X-Gitlab-Token` header so the receiver's
   token-equality check (which runs BEFORE the `X-TDT-Selftest` bypass
   at `webhook_receiver/api/app.py`) accepts the probe. When
   `GITLAB_WEBHOOK_SECRET` is unset or empty, the probe MUST send an
   empty `X-Gitlab-Token` header; the receiver's auth check (`"" == ""`)
   accepts that case for unauthenticated deployments.
4. Cross-check the public edge by issuing a HEAD request to the public
   hostname root to confirm the TLS handshake completes within 5s.
5. Record the observation to the on-disk DLQ-adjacent file at
   `~/.tdt/state/webhook-selftest-observations.jsonl` (one JSON object
   per line, capped at 720 lines = 60 hours at 5min cadence).
6. If the last 3 observations all report `primary_status=down`, write
   an `escalation=true` line and emit a `WEBHOOK_SELFTEST_ESCALATION`
   structlog event.

The self-test request physically leaves the host (Tailscale DERP round-trip or
ngrok edge), so the "test must come from outside" property required for ingress
health is preserved. The receiver being down is itself a signal — DBOS will
record the next successful run after recovery and the dashboard will show the gap.

#### Scenario: Healthy primary is recorded as ok

- **WHEN** the self-test POST returns HTTP 200 within 1500ms AND the HEAD request
  completes within 5000ms
- **THEN** the observation line SHALL be
  `{"primary_status": "ok", "primary_status_code": 200, "primary_latency_ms": <n>, "edge_healthy": true, "ts": "<iso>"}`.

#### Scenario: Unhealthy primary is recorded as down

- **WHEN** the self-test POST returns a non-2xx response or times out after 10s
  OR the HEAD request fails with a TLS or timeout error
- **THEN** the observation line SHALL be
  `{"primary_status": "down", "error": "<reason>", "ts": "<iso>"}`
- **AND** this line SHALL count toward the 3-consecutive-down escalation
  regardless of which sub-check failed.

#### Scenario: Three consecutive down observations escalate to an alert event

- **WHEN** the last 3 self-test observations for the primary URL are all `primary_status=down`
- **THEN** the workflow SHALL write an observation with `escalation: true` AND emit a
  structlog event `WEBHOOK_SELFTEST_ESCALATION: 3 consecutive primary-down observations`.

#### Scenario: Probe presents the configured X-Gitlab-Token when the secret is set

- **GIVEN** `GITLAB_WEBHOOK_SECRET` is set to a non-empty value in the scheduler
  container environment
- **WHEN** the self-test workflow POSTs to `<primary>/gitlab-webhook`
- **THEN** the probe SHALL carry that exact value in the `X-Gitlab-Token` header.

#### Scenario: Probe presents an empty X-Gitlab-Token when the secret is unset

- **GIVEN** `GITLAB_WEBHOOK_SECRET` is unset or empty in the scheduler
  container environment
- **WHEN** the self-test workflow POSTs to `<primary>/gitlab-webhook`
- **THEN** the probe SHALL carry an empty `X-Gitlab-Token` header
  (the receiver accepts `"" == ""` for unauthenticated deployments).