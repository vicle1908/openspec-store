## Why

POEMS Mobile 3's iOS and Android builds are released through GitLab MRs whose review pipeline
posts back to our local `webhook-receiver` and `ai-review` services. Today the path GitLab uses
is a single Tailscale Funnel endpoint — when that tunnel is down, the edge DERP server stalls,
GitLab's delivery times out, and the entire MR review flow silently fails until someone notices
in a standup. We saw this exact outage on 2026-06-15: a 2+ hour window where every MR hook event
returned `internal error` (TLS handshake to the Tokyo edge never completed) and no code was
being reviewed. There is no automatic failover, no delivery self-test, no alerts, and no
postmortem trail.

This change adds a **defense-in-depth coverage sweep**: a second public URL (ngrok free tier as
the documented hot-spare) that GitLab can deliver to, automatic rotation when the primary
endpoint fails, a periodic GitLab-side self-test that catches silent drops, and dashboards that
make delivery health visible in 10 seconds.

## What Changes

- **Add a redundant public URL** for `webhook-receiver`: the existing Tailscale Funnel
  (`les-mac-mini.tailc6b508.ts.net`) remains primary; ngrok free-tier tunnel becomes the
  **hot spare** that GitLab can be pointed at during a tunnel outage.
- **Add GitLab-side secondary delivery**: each project's webhook is configured with both URLs;
  the secondary URL is enabled only when the primary is known-bad (via a single switch file on
  disk, e.g. `~/.tdt/state/webhook-primary.state`), so we do not double-fire on healthy days.
- **Add a delivery self-test** that runs every 5 minutes from a DBOS scheduled
  workflow inside `webhook-receiver`, hits both endpoints (POST + HEAD for edge
  health), and records the latest result to
  `~/.tdt/state/webhook-selftest-observations.jsonl`; 3 consecutive primary-down
  observations emit a `WEBHOOK_SELFTEST_ESCALATION` structlog event.
- **Add a GitLab hook health dashboard**: a small script that pulls recent `hooks/<id>/events`
  per project, classifies the last 24h by status code, and prints a one-screen table.
- **Add a dead-letter sink** inside `webhook-receiver`: when the receiver itself is healthy
  but the downstream `ai-review` call fails twice in a row, the original payload is written to
  `~/.tdt/state/webhook-deadletter/<timestamp>.json` and a synthetic `dlq.received` event is
  emitted so we can replay it later.
- **Add dedupe by `(project_id, MR IID, event)`** in the receiver so a flapping DERP edge
  that retries a delivery twice does not cause two review runs.
- **Add an `incident-report` skill** that produces a 1-page postmortem from the dashboard
  data + funnel/ngrok logs after a confirmed outage.
- **BREAKING**: the `webhook-receiver` will require the secondary-URL handshake header
  (`X-TDT-Secondary: 1`) on requests coming from the ngrok URL, so the receiver can tell
  primary from secondary deliveries for logging and observability. The header does NOT
  bypass dedupe — both ingresses fire for every MR event in production (GitLab does not
  conditionalize hooks on an external signal), so the receiver MUST apply dedupe
  uniformly to avoid duplicate `ai-review` dispatches and duplicate Jira impact comments.
  The `~/.tdt/state/webhook-primary.state` file is an operator-facing indicator only;
  it changes how `/health/ingress` and the self-test render the active edge but does
  not toggle the GitLab hooks. (No existing consumer sets this header.)

## Capabilities

### New Capabilities

- `webhook-public-ingress-failover`: rules for the Tailscale primary / ngrok hot-spare rotation,
  the `~/.tdt/state/webhook-primary.state` switch, and the secondary-URL handshake header
  contract.
- `webhook-delivery-self-test`: contract for the 5-minute DBOS scheduled workflow,
  what it records to the on-disk observations file, and how it escalates on
  3-consecutive-down.
- `webhook-receiver-dlq`: contract for the dead-letter sink file format, the trigger condition
  (two consecutive downstream failures), and the replay mechanism.
- `gitlab-hook-health-dashboard`: contract for the dashboard script — input (project IDs +
  hook IDs), output (status table), refresh cadence.
- `webhook-incident-report`: contract for the postmortem skill — required inputs, output
  format, and which artifacts it reads.

### Modified Capabilities

- `webhook-ai-review-repo-split`: extend the existing spec to require idempotent handling on
  the receiver side, dedupe by `(project_id, MR IID, event_type)`, and a fixed 30-second
  timeout on the downstream `ai-review` call (currently unbounded).

## Impact

- **Code**:
  - `webhook-receiver/src/tailscale_health.py`: state-file reader + URL resolution
  - `webhook-receiver/src/dlq.py`: dead-letter sink + failure counter
  - `webhook-receiver/src/dedupe.py`: SQLite-backed dedupe by project/MR/event
  - `webhook-receiver/src/selftest.py`: DBOS scheduled workflow for the 5-min self-test
  - `webhook-receiver/src/replay_dlq.py`: DLQ replay script
  - `webhook-receiver/src/gitlab_hook_dashboard.py`: dashboard CLI
  - `tdt-core/clients/gitlab_hooks.py`: add `list_recent_hook_events(project_id, hook_id, n)` helper
- **APIs**:
  - `webhook-receiver` gains two new env knobs: `WEBHOOK_DLQ_DIR` (default
    `~/.tdt/state/webhook-deadletter`) and `WEBHOOK_DEDUPE_DB` (default
    `~/.tdt/state/webhook-dedupe.sqlite`).
  - `ai-review` gains `AI_REVIEW_DOWNSTREAM_TIMEOUT_SECONDS` (default 30).
- **Dependencies**: none new (uses existing `tdt_core.clients.gitlab`, `httpx`,
  DBOS scheduler, and stdlib `sqlite3`).
- **Operations**:
  - The receiver gains 2 new DBOS scheduled workflows (`webhook-selftest`,
    `dlq-reaper`); no new LaunchAgents.
  - ngrok free-tier tunnel kept running as a known-bad-state spare; user switches via the
    `~/.tdt/state/webhook-primary.state` file.
  - Adds 1 new `incident-report` skill.
- **Out of scope (non-goals)**:
  - Cloudflare Tunnel as a third path (deferred — Tailscale + ngrok covers the failure modes
    we saw).
  - Real-time Slack/Teams alerts (the `incident-report` skill + dashboard is sufficient for
    now; full alerting is its own change).
  - Replacing the GitLab webhooks with a CloudEvents broker (too much rewrite for the
    observed failure modes).

## Non-Goals

- No redesign of the GitLab ↔ `webhook-receiver` protocol.
- No move to a hosted/managed ingress service.
- No retroactive replay of the 2026-06-15 outage's lost MR reviews (the underlying MRs were
  merged without AI review; that is a known loss we accept).
