## Context

POEMS Mobile 3 ships iOS and Android through GitLab MRs at `git.ecomedic.vn` (projects 231 and
232). Every MR action posts a webhook to a single public URL —
`https://les-mac-mini.tailc6b508.ts.net/gitlab-webhook` — served by a Tailscale Funnel
listener in front of our local `webhook-receiver` (FastAPI on `127.0.0.1:8080`), which then
dispatches to `ai-review` (FastAPI on `127.0.0.1:8090`) over loopback.

The 2026-06-15 outage made the brittleness obvious: Tailscale's Tokyo DERP edge returned
`SSL_connect SYSCALL returned=5` to GitLab's webhook probes for ~2 hours. GitLab retried, then
logged `internal error` and moved on. Our `webhook-receiver` and `ai-review` were healthy
the entire time — the failure was purely on the ingress path. No alerts fired, no dashboard
showed the outage, and we discovered it manually during a standup.

The fix we shipped in the same incident (re-enabling the funnel via
`/Applications/Tailscale.app/Contents/MacOS/Tailscale funnel --bg 8080`) restores delivery
but leaves us one DERP hiccup away from the same blind spot. This design adds the layers
needed to detect, route around, and postmortem such failures.

## Goals / Non-Goals

**Goals:**

- A second public URL that GitLab can be pointed at when Tailscale is degraded, with
  a single-switch rotation.
- A self-test loop that runs every 5 minutes and records a status event in agentmemory.
- A dead-letter sink so a downstream `ai-review` outage does not silently drop MR reviews.
- A health dashboard that summarizes the last 24h of hook deliveries per project in one
  table.
- A postmortem skill that produces a 1-page report from the dashboard + funnel/ngrok logs.
- Idempotency so a flapping DERP edge that retries a delivery does not cause two reviews.

**Non-Goals:**

- Cloudflare Tunnel as a third ingress path.
- Real-time Slack/Teams alerts (the dashboard + postmortem skill is the v1 path; real
  alerting is its own change).
- Replacing GitLab webhooks with a CloudEvents broker or NATS-based bus.
- Replaying the 2026-06-15 lost reviews (the underlying MRs were merged; we accept the loss).
- Any change to the `ai-review` reviewer selection / prompt logic (orthogonal to ingress).

## Decisions

### D1. ngrok free tier as the documented hot spare, with a critical caveat

- **Decision**: Keep Tailscale as the always-on primary. Run ngrok as a known-bad-state
  spare — the ngrok agent stays up so the hostname is reserved. The
  `~/.tdt/state/webhook-primary.state` file is an operator-facing indicator that
  changes how `/health/ingress` and the self-test loop target the public edge; it does
  **NOT** toggle the GitLab hooks.
- **Critical caveat (added 2026-07-01 after the XRP-56 incident)**: GitLab does not
  conditionalize a project webhook on an external file or signal. Once the primary
  hook (id 32 on project 231, 33 on 232) and the secondary hook (id 42 on 231, 43 on
  232) are installed with `merge_requests_events: true`, **both fire for every MR
  event**. The state file flip is informational only. Idempotency is therefore the
  receiver's sole defense against duplicate dispatches — the dedupe key
  (`project_id`, `MR IID`, `event_type`) MUST be applied uniformly to both ingresses.
  See D2 and the `webhook-public-ingress-failover` spec for the corrected contract.
- **Why keep ngrok even though it always fires**: Free ngrok URLs change on agent
  restart unless you pay; we cannot rely on double-firing through both URLs as a
  steady-state load-shedding mechanism. ngrok is documented as the failover target
  if the Tailscale edge goes down — operators may edit `webhook-primary.state` to
  point self-test at the ngrok URL during an outage. The on-disk state file lets the
  on-call person re-target the self-test in 5 seconds from any terminal.
- **Alternatives considered**:
  - Always-on dual delivery with dedupe on both sides — **adopted** (this is the
    steady-state reality; both hooks are installed and firing, so the receiver MUST
    dedupe both). The original 2026-06 draft of D1 assumed only one hook fires at a
    time and the state file toggles them; that assumption was incorrect and has been
    corrected above.
  - Cloudflare named tunnel with stable hostname — rejected for v1; adds a third
    credential and a new dependency, and Tailscale + ngrok already covers the failure
    modes we observed.
  - Toggle `merge_requests_events` on the secondary hook from the state file via a
    periodic reconciler — deferred to a follow-up OpenSpec (`secondary-hook.py
    enable`/`disable` + a DBOS scheduled workflow); the simpler fix (dedupe on
    both ingresses) is shipped in this change.

### D2. Secondary-URL handshake header to distinguish primary vs. secondary traffic

- **Decision**: When GitLab is delivering to the ngrok URL (secondary), GitLab's webhook
  configuration adds the header `X-TDT-Secondary: 1` (we control the GitLab project
  webhook config). The receiver reads this header to:
  - Log the delivery as `ingress=secondary` for the dashboard and incident-report skill.
  - Tag agentmemory observations with `ingress=secondary` so postmortems can quantify
    how much traffic arrived via the hot-spare path.
  - **NOT** bypass the dedupe check. Both ingresses fire for every MR event in
    production (GitLab does not conditionalize a project webhook on an external file or
    signal — once a hook is installed with `merge_requests_events: true`, it fires
    unconditionally). The header is observability metadata, not a permission. See
    `webhook-public-ingress-failover` and `webhook-ai-review-repo-split` specs for the
    corrected contract; the `state file flip` only changes how `/health/ingress` and
    the self-test target the public edge.
- **State directory bootstrap**: `~/.tdt/state/` does NOT exist today. The receiver
  must `mkdir -p` the parent directory on first write (same pattern as
  `CircuitBreaker._ensure_state_file()` at `webhook-receiver/src/webhook_receiver/core/circuit_breaker.py:44-47`).
  Three files live there:
  - `webhook-primary.state` (text file, 1 token)
  - `webhook-dedupe.sqlite` (binary, opened with `Path.parent.mkdir(parents=True, exist_ok=True)`)
  - `webhook-deadletter/` (directory, created on first DLQ write)
- **Why a single header is the cheapest disambiguator**: A header is cheaper than
  parsing source IPs (which drift as Tailscale/ngrok edge IPs change). It does NOT
  grant a dedupe bypass — that was the original draft of this decision and was
  rolled back after the 2026-06-27 → 2026-07-01 incident on XRP-56 (12 MRs
  produced duplicate impact postings; see `incident-report` skill archives).
- **Alternatives considered**:
  - Match by `X-Forwarded-For` source IP — rejected: ngrok free tier edge IPs are
    subject to change without notice.
  - Separate path (`/gitlab-webhook-secondary`) — rejected: the dead-letter path would
    need to mirror and the receiver would have two near-identical routes.
  - Toggle `merge_requests_events` on the secondary hook from the state file
    (`secondary-hook.py enable` / `disable`) — deferred to a follow-up OpenSpec;
    the simpler fix is to apply dedupe to both ingresses (shipped in this change).

### D3. SQLite-backed dedupe keyed by `(project_id, MR IID, event_type)`

- **Decision**: A small SQLite DB at `~/.tdt/state/webhook-dedupe.sqlite` with a single
  table `(project_id INTEGER, mr_iid INTEGER, event_type TEXT, last_seen_at INTEGER)`
  and a TTL of 10 minutes. The receiver checks/inserts on every GitLab webhook; a hit
  returns `200 OK` without dispatching to `ai-review`.
- **What already exists**: `ai-review` has an in-memory `IdempotencyRegistry`
  (`src/ai_review/services/idempotency.py`) keyed by
  `sha256(project:mr_iid:action:commit_sha)` with a 3600s TTL. **The receiver-side
  dedupe is a *backstop*, not a replacement** for that registry:
  - The ai-review registry is lost on `ai-review` restart (in-memory only). The
    receiver-side dedupe survives both restarts.
  - The receiver-side dedupe avoids making a network call at all, reducing load on
    ai-review during retry storms.
  - Different TTLs (10 min vs 60 min) cover different failure modes; 10 min is the
    GitLab retry window, 60 min is the ai-review long-tail.
- **Why 10 min TTL**: The observed retry mode is "GitLab retries the same event 3 times
  in 60s when the first delivery hits TLS black-hole". A 10-minute TTL is wide enough
  to cover GitLab's full retry window and narrow enough that a real follow-up event
  (push, new comment) is not blocked.
- **Alternatives considered**:
  - In-memory LRU — rejected: state vanishes on `webhook-receiver` restart, which
    happens during deploys.
  - Redis — rejected: TDT has no Redis service in the hot path today; the SQLite file
    is in `~/.tdt/state/` and is covered by Time Machine.

### D4. Dead-letter trigger: 2 consecutive downstream failures

- **Decision**: If the `webhook-receiver` calls `ai-review` and gets a non-2xx response
  twice in a row for the same `(project_id, MR IID, event_type)`, the second
  failure writes the original payload to
  `~/.tdt/state/webhook-deadletter/<UTC-timestamp>.json` and emits a
  `dlq.received` event into agentmemory.
- **Why**: One failure is transient (network blip, restart). Two in a row indicates the
  downstream is genuinely broken and we should not keep retrying into the void — but
  we should not lose the payload either. The 2-failure threshold is high enough to
  ignore noise, low enough to DLQ within a single GitLab retry cycle.
- **Alternatives considered**:
  - Immediate DLQ on first failure — rejected: too noisy during routine restarts.
  - Exponential-backoff retry queue — rejected: `ai-review` already has its own
    retry-once policy; layering another queue adds complexity for no observed benefit.

### D5. 30-second downstream timeout on `ai-review` dispatch

- **Decision**: `ai-review` calls take 5-15s for routine reviews but can stretch to 60s+
  for codex/claude probes when both are slow. Cap the receiver's downstream call at
  30s. On timeout, treat it as a failure (counts toward the DLQ trigger).
- **What exists today**: the receiver already exposes
  `ai_review_dispatch_timeout_seconds` (env `AI_REVIEW_DISPATCH_TIMEOUT_SECONDS`,
  default **2.0s**) via `httpx.Timeout` at `app.py:152-155`. We are **changing the
  default from 2.0s to 30s** — this is a behavioral change, but 2.0s was insufficient
  for the codex/claude probes we saw today (where `reviewer_probes` returned errors
  including "Reading additional input from stdin..."). The env var name stays the
  same; the default bumps. Production deploys can keep the existing 2.0s by setting
  the env explicitly.
- **Why**: Without a cap, a stuck downstream holds the GitLab HTTP request open past
  GitLab's own timeout, causing GitLab to retry, which can flood the receiver and turn
  one stuck review into 10 stuck reviews. With too low a cap (2.0s), every codex probe
  that thinks for >2s gets killed.
- **Alternatives considered**:
  - Fire-and-forget dispatch (return 200 immediately, process in background) — rejected:
    loses the GitLab `X-Handoff-Id` correlation we rely on for the dashboard, and
    surfaces a "success" to GitLab when in fact the review never started.
  - Adaptive timeout based on reviewer — rejected: too much code path for the value.

### D6. Self-test loop owned by the central DBOS scheduler, not a separate LaunchAgent

- **Decision**: The central `tdt-scheduler serve` daemon (in the
  `agent-core` container) registers a DBOS scheduled workflow
  (`engine.scheduled_workflow(cron="*/5 * * * *", name="webhook-selftest")`)
  that runs `webhook_receiver.selftest_cli` as a subprocess. The daemon
  is the always-on host for ALL DBOS schedules (per centralize-scheduling
  Decision 4). Registering the workflow in the receiver process was
  tried first but the receiver is uvicorn (request-driven) — it has no
  worker thread to drain the internal DBOS queue, so the workflows
  accumulated as stuck `ENQUEUED` rows (31 backlog rows in production
  before the fix). The workflow:
  1. Reads the primary URL from `~/.tdt/state/webhook-primary.state`.
  2. POSTs a synthetic Merge Request Hook (header `X-TDT-Selftest: 1`) to
     `<primary>/gitlab-webhook` (the receiver is mounted at
     `/gitlab-webhook`, not the root) — the request physically leaves
     the host, traverses the Tailscale DERP / ngrok edge, and returns.
  3. Cross-checks the public URL by issuing a HEAD request to detect edge-healthy-
     but-tunnel-down cases (the 06-15 outage pattern: loopback health ≠ edge health).
  4. Appends the observation to `~/.tdt/state/webhook-selftest-observations.jsonl`
     (capped at 720 lines = 60 hours of history at 5min cadence).
  5. If the last 3 observations are all `primary_status=down`, writes
     `escalation: true` and emits a `WEBHOOK_SELFTEST_ESCALATION` structlog event.
- **Why DBOS, not a LaunchAgent**: A LaunchAgent would be a separate process with its
  own supervision, agentmemory dependency, and 3 new failure modes (agent not
  loaded, agentmemory down, cron drift). DBOS scheduled workflows give us:
  - **Durable execution**: the self-test survives receiver restarts (PostgreSQL-backed
    schedule history) — a missing run is itself a signal, not a silent gap.
  - **Existing observability**: `engine.get_status()` already exposes
    `schedule_count` and `dbos_connected`; the dashboard reuses that endpoint.
  - **No new process to supervise**: the self-test inherits the receiver's
    `launchd` `KeepAlive=true` and restarts on crash.
  - **No agentmemory dependency**: the observations file is a plain JSONL on disk —
    the dashboard, the incident-report skill, and the self-test itself all read
    the same file with no network round-trip.
- **Why "in-receiver" still tests the public edge**: The self-test request physically
  leaves the host. The Tailscale DERP / ngrok edge is a network element between
  GitLab and the receiver — the test must traverse that path to be meaningful. The
  receiver being down causes the self-test POST to time out, which is **exactly the
  signal we want** — the observation line records `down` and counts toward the
  3-consecutive-down escalation. No information is lost.
- **Alternatives considered**:
  - Self-test from inside the receiver as a periodic in-process task (no DBOS) —
    rejected: durable execution and the existing `apply_schedules` plumbing are
    worth the small extra cost; the only thing the DBOS layer adds is
    `with_scheduler("webhook-selftest")` and a cron string.
  - LaunchAgent `com.tdt.webhook-selftest.plist` — rejected: separate process
    adds a new supervision surface, requires a second `tdt-tools/` script
    (which is not an established convention in the workspace), and the
    agentmemory dependency introduces a network round-trip on every probe.
  - GitLab-side webhook health (the `hooks/<id>/events` API) — adopted as the
    secondary signal in the dashboard (Task 9) but not the primary one, because
    GitLab's events list has its own lag (we saw 30-90s during the 06-15 outage).

### D7. Postmortem skill reads from agentmemory + `hooks/<id>/events` + funnel/ngrok logs

- **Decision**: New `incident-report` skill at `.agents/skills/incident-report/SKILL.md`.
  It takes a time window (start/end ISO timestamps) and a project ID, and emits a
  markdown report with: timeline, top failure modes, affected MRs, what was reviewed
  vs. what was lost, and recommended follow-ups.
- **Why**: A scripted postmortem is reproducible, runnable by anyone, and the report
  can be pasted into the team's Slack/Jira. Manual postmortems get skipped when
  pressure is high.
- **Alternatives considered**:
  - Just a CLI script — rejected: a skill integrates with the agent's existing
    skill-discovery flow and is invocable from the chat UI.

## Risks / Trade-offs

- **[ngrok free-tier URL drift]** → Mitigation: Document the rotation procedure
  (restart agent, update GitLab hooks) in `docs/operations/webhook-failover.md`. v2 of
  this change will add a stable hostname via the ngrok paid plan if drift becomes a
  weekly problem.
- **[State file corruption / accidental flip]** → Mitigation: the state file is
  checked into the `~/.tdt/state/` Time-Machine-backed directory; the dashboard
  reports the current value of the state file in its header line so a flipped state
  is visible immediately.
- **[DLQ disk usage]** → Mitigation: the DLQ dir is capped at 10,000 files; oldest
  files are pruned on every successful replay. A DBOS scheduled workflow `dlq-reaper`
  (cron `0 3 * * *`) registered in the central scheduler enforces the cap
  via a `webhook_receiver.dlq_reaper_cli` subprocess.
- **[Self-test false positives during funnel restarts]** → Mitigation: 3 consecutive
  failures (15 min of self-test windows) are required before the dashboard marks the
  primary as "down" — one missed self-test is treated as noise.
- **[ngrok agent adds CPU/memory overhead]** → Mitigation: ngrok agent is a single
  static binary that uses ~30MB RAM idle; the free tier has no rate limit on the agent
  itself.

## Migration Plan

1. Land the receiver changes (`dedupe.py`, `dlq/`, `tailscale_health/`) and the
   `ai-review` timeout change behind a feature flag
   (`WEBHOOK_DEDUPE_ENABLED`, `WEBHOOK_DLQ_ENABLED`, `AI_REVIEW_DOWNSTREAM_TIMEOUT_SECONDS`).
2. Enable the flags in `~/.tdt/.env` for the local dev environment first; run
   `webhook-receiver` + `ai-review` for 48 hours with `glab` test deliveries to
   confirm dedupe is hitting and DLQ is empty.
3. Roll the same flags into the deployed LaunchAgents
   (`com.tdt.webhook-receiver.plist`, `com.tdt.ai-review.plist`) — no new env vars
   needed, only flip the existing ones from `false` to `true`.
4. Install the ngrok agent + auth token (one-time), add the secondary URL to all
   GitLab project webhooks with the `X-TDT-Secondary: 1` header.
5. Install the `com.tdt.webhook-selftest.plist` LaunchAgent and the
   `incident-report` skill.
6. Update `docs/operations/webhook-failover.md` with the rotation procedure.

**Rollback**: Each feature is a single env var flip (`false` disables it). The receiver
restarts pick up the new value within 5 seconds. No data is destroyed on rollback —
the DLQ dir and dedupe DB are left in place for inspection.

## Open Questions

- **OQ1**: Should the dashboard also surface Jira-side webhook health? Currently the
  same `webhook-receiver` handles Jira transitions; if Jira webhooks start failing
  silently, the dashboard as designed will not show it. Defer to v2 unless
  `jira-realtime-transition-guard` is also red.
- **OQ2**: How long should the DLQ keep payloads before pruning? The 10,000-file
  cap is an estimate; the real rate depends on MR throughput.
- **OQ3**: Do we want the `incident-report` skill to optionally create a Jira issue
  with the postmortem body? Useful but adds a Jira-write path; defer to v2.
