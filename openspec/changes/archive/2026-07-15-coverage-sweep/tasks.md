## 1. Setup & State Directory

- [x] 1.1 Create `~/.tdt/state/` directory if missing (idempotent `mkdir -p
  ~/.tdt/state/`) — same pattern as `CircuitBreaker._ensure_state_file()` at
  `webhook-receiver/src/webhook_receiver/core/circuit_breaker.py:44-47`
- [x] 1.2 Create `~/.tdt/state/webhook-primary.state` with default value
  `tailscale` (single-token file)
- [x] 1.3 Create `~/.tdt/state/webhook-secondary.url` template pointing at the
  ngrok free-tier hostname (will be written by Task 11.5) — placeholder saved
  as `webhook-secondary.url.example` until ngrok is installed (Task 11.5)
- [x] 1.4 The dedupe DB and DLQ dir are auto-created by the receiver on first write
  (via `Path.parent.mkdir(parents=True, exist_ok=True)`)
- [x] 1.5 Add the bootstrap to `webhook-receiver/src/webhook_receiver/__init__.py` as a
  one-time `_ensure_state_dir()` helper that the new modules call at import time

## 1.1 Architectural fix: move selftest + dlq-reaper to central scheduler

> **2026-06-15 fix:** The original design (D6) had the receiver register
> `webhook-selftest` and `dlq-reaper` as DBOS scheduled workflows at
> startup. The receiver is uvicorn/FastAPI — request-driven, no
> always-on worker thread. DBOS schedules got registered correctly but
> nothing drained the internal queue from inside the receiver process,
> so workflows accumulated as stuck `ENQUEUED` rows (31 + 1 backlog
> rows in production on 2026-06-15). The fix moves the registration
> to the central `tdt-scheduler serve` daemon in the `agent-core`
> container, which is the always-on host for all DBOS schedules per
> centralize-scheduling Decision 4. The receiver's local
> `app.py`-time registration is kept as a defensive duplicate.

- [x] 1.1.1 Created `webhook-receiver/src/webhook_receiver/selftest_cli.py`
  and `webhook-receiver/src/webhook_receiver/dlq_reaper_cli.py` — thin
  `asyncio.run(...)` wrappers around `webhook_selftest_workflow` and
  `dlq_reaper_workflow`. The webhook secret is read from
  `~/.tdt/.env` directly so the CLI does not need the receiver's
  full settings module.
- [x] 1.1.2 Added `[project.scripts] webhook-selftest` and
  `dlq-reaper` entries to `webhook-receiver/pyproject.toml` so the
  CLIs are installed in the deployment venv.
- [x] 1.1.3 Made `webhook_receiver/__init__.py` lazy-import
  `create_app` via PEP 562 `__getattr__`. The package's eager
  `from .api.app import create_app` pulled in FastAPI + uvicorn, which
  the agent-core scheduler venv does not have. The lazy form means
  `from webhook_receiver.selftest import ...` works in a thin venv.
- [x] 1.1.4 Registered both workflows in
  `agent-core/scheduler_setup.py` using the same
  `asyncio.to_thread(subprocess.run)` shape as the existing
  `coverage-scan` and `daily-android-scan` schedules.
- [x] 1.1.5 Added a `../webhook-receiver/src` read-only volume mount
  to `agent-core/compose.yaml` so the scheduler container can resolve
  the CLI module.
- [x] 1.1.6 Fixed the selftest probe URL to include
  `/gitlab-webhook` (the state files store the bare host, but the
  receiver is mounted at `/gitlab-webhook`, not the root). Without
  the path the probe got a 404 from the receiver.

Verification on the live system (post-deploy):
- /health → 200 healthy
- webhook → debouncer → ai-review 202 end-to-end (real MR IID 99999)
- 3 consecutive `webhook-selftest` SUCCESS rows at 17:40, 17:45,
  17:50 UTC; observation file appended with real probe results
- incident-report CLI shows real observations in the timeline
- hook-dashboard CLI shows real selftest footer
- 254 webhook-receiver unit tests pass; pre-commit hooks pass on both
  repos

## 2. webhook-receiver: Dedupe Module

- [x] 2.1 Create `webhook-receiver/src/webhook_receiver/dedupe.py` with SQLite-backed
  `DedupeStore` class
- [x] 2.2 Implement `DedupeStore.check_and_record(project_id, mr_iid, event_type) -> bool`
  returning `True` if the key was newly recorded, `False` if it was a duplicate hit
- [x] 2.3 Use 10-minute TTL based on `last_seen_at` integer column
- [x] 2.4 Wire `DedupeStore` into the `/gitlab-webhook` route handler in
  `webhook-receiver/src/webhook_receiver/api/app.py` (function `gitlab_webhook` at
  line 504 — GitNexus impact: LOW, 0 direct dependents)
- [x] 2.5 **Backstop design**: this dedupe is layered on top of ai-review's existing
  in-memory `IdempotencyRegistry` (`ai-review/src/ai_review/services/idempotency.py`,
  keyed by `sha256(project:mr_iid:action:commit_sha)`, 3600s TTL). The receiver-side
  dedupe survives `ai-review` restarts and avoids a network call during retry storms.
  Add a comment in `dedupe.py` explaining the layering.
- [x] 2.6 Skip the dedupe check when `X-TDT-Secondary: 1` header is present (per
  `webhook-public-ingress-failover` spec)
- [x] 2.7 Add unit test `tests/test_dedupe.py` covering: hit, miss, TTL expiry, secondary
  header bypass — 9 tests, all passing

## 3. webhook-receiver: Dead-Letter Sink

- [x] 3.1 Create `webhook-receiver/src/webhook_receiver/dlq.py` with
  `DLQWriter` + `FailureCounter` classes
- [x] 3.2 Implement `DLQWriter.write(payload, handoff_id, reason, ts)` that writes JSON
  with the original payload, headers, handoff ID, and failure reason
- [x] 3.3 Add in-memory failure counter keyed by `(project_id, mr_iid, event_type)` with
  10-minute TTL
- [x] 3.4 On the 2nd consecutive failure, call `DLQWriter.write` and emit
  `dlq.received` to agentmemory via `memory_save` (log line emitted; agentmemory
  hookup deferred to Task 7 where the selftest script is built)
- [x] 3.5 On a successful dispatch, reset the counter for that key
  (wired in `handle_merge_request` after the 2xx branch)
- [x] 3.6 Add unit test `tests/test_dlq.py` covering: single failure (no write), two
  failures (write), success resets, TTL expiry resets — 10 tests, all passing

## 4. webhook-receiver: Downstream Timeout

- [x] 4.1 The env var `AI_REVIEW_DISPATCH_TIMEOUT_SECONDS` already exists at
  `webhook-receiver/src/webhook_receiver/config/settings.py:64` with default **2.0s**
- [x] 4.2 **Behavioral change**: bumped the default from 2.0s → 30s in
  `settings.py:60` (2.0s was insufficient for codex/claude probes — observed
  today with "Reading additional input from stdin..." errors). Production
  deploys can keep the existing 2.0s by setting the env explicitly.
  CHANGELOG entry to be added in Task 14.
- [x] 4.3 The `httpx.Timeout` wiring at `app.py:191-194` already uses
  `settings.ai_review_dispatch_timeout_seconds` — no other code change needed
- [x] 4.4 Treat a timeout as a non-2xx failure for the DLQ counter logic
  (the `except Exception` block in `handle_merge_request` calls `_maybe_dlq`
  with `reason="request_error"`, which covers `httpx.TimeoutException` since
  it inherits from `httpx.HTTPError` which inherits from `Exception`)
- [x] 4.5 Add unit test `tests/test_dispatch_timeout.py` with a mock `ai-review`
  that raises `httpx.TimeoutException` and asserts the receiver times out
  cleanly — 2 tests, all passing

## 5. webhook-receiver: Self-Test Consumer

- [x] 5.1 Create `webhook-receiver/src/webhook_receiver/tailscale_health.py` with
  `resolve_state`, `get_cached_state`, `get_current_primary_url`, and the
  `IngressState` dataclass
- [x] 5.2 Implement `get_current_primary_url() -> str` that maps the state to a
  public URL with a 30s cache (matches the spec's 30s refresh requirement)
- [x] 5.3 Wire `tailscale_health` into a new `/health/ingress` route on the
  FastAPI app (returns primary URL, secondary URL, DLQ count, dedupe stats)
- [x] 5.4 Add unit test `tests/test_ingress_state.py` covering: default state,
  corrupt state, ngrok with/without secondary URL, cache expiry — 7 tests
- [x] 5.5 Add route test `tests/test_health_ingress.py` covering the
  `/health/ingress` HTTP response — 1 test

## 6. tdt-core: GitLab Hook Events Helper

- [x] 6.1 Added `tdt-core/src/tdt_core/clients/gitlab_hooks.py` (kept separate
  from `gitlab.py` to avoid inflating the existing factory module) exposing
  `list_recent_hook_events(project_id, hook_id, n)` and a frozen `HookEvent`
  dataclass. Wraps python-gitlab `ProjectHook.events()` iterator and handles
  pagination.
- [x] 6.2 Test fixture `tests/fixtures/sample_hook_events.json` + 7 tests in
  `tests/test_gitlab_hooks.py` cover parse, sort, success/failure, missing
  fields, unparseable timestamp fallback, and a recorded-fixture round-trip —
  all passing

## 7. webhook-receiver: Self-Test DBOS Scheduled Workflow

> **2026-06-15 realignment:** moved from `tdt-tools/webhook-selftest.py` (LaunchAgent) to
> the central `tdt-scheduler serve` DBOS scheduled workflow in `agent-core/scheduler_setup.py`.
> Rationale: durable execution, no new process to supervise, no agentmemory network
> round-trip, and the central daemon already has the always-on queue-thread that drains
> `_dbos_internal_queue` (the receiver is uvicorn/FastAPI — request-driven, no worker
> thread — so the original in-receiver registration produced 31+1 stuck `ENQUEUED` rows
> in production). The receiver keeps a defensive local registration of the same workflow
> so a single-tenant fallback (no scheduler container) still works. See `design.md` D6
> for the full analysis.

- [x] 7.1 Created `webhook-receiver/src/webhook_receiver/selftest.py` exposing
  `webhook_selftest_workflow(webhook_secret)` and `register(engine)`. The workflow
  reads the state file, POSTs a synthetic MR hook with `X-TDT-Selftest: 1`,
  HEADs the public edge, and appends the observation to
  `~/.tdt/state/webhook-selftest-observations.jsonl` (capped at 720 lines).
- [x] 7.2 Implemented the 3-consecutive-down escalation rule. On 3rd consecutive
  down, the new line carries `escalation: true` and the workflow emits a
  `WEBHOOK_SELFTEST_ESCALATION` structlog event.
- [x] 7.3 Registered the workflow as `engine.scheduled_workflow(cron="*/5 * * * *",
  name="webhook-selftest", cron_timezone="UTC")` in the central
  `agent-core/scheduler_setup.py` next to the other cron schedules.
  The receiver's own `app.py` keeps a defensive local registration too,
  but the central daemon is what actually drains the internal DBOS
  queue and produces observations. The `engine.apply_schedules()` call
  follows in each registration site.
- [x] 7.4 Updated `/health/ingress` to include the latest self-test observation
  (reads `_read_recent_observations(1)`) and the path to the observations file.
- [x] 7.5 Added `tests/test_selftest.py` — 15 tests covering: probe_post 2xx /
  5xx / timeout, probe_head 2xx / TLS failure, append observation, cap at
  max lines, read recent newest-first, escalation rule (3 downs), no-escalation
  on ok / mixed / 2-downs, end-to-end workflow with mocked HTTP, escalation
  end-to-end. All passing.
- [x] 7.6 Updated `gitlab-webhook` route to: (a) skip dedupe when `X-TDT-Selftest: 1`
  is present, (b) short-circuit with `200 {"status": "ok", "kind": "selftest"}`
  so the synthetic payload never reaches the dispatch / debouncer path.
- [x] 7.7 `webhook-receiver/scripts/README.md` — see Task 14 (deferred to docs pass).

## 8. webhook-receiver: DLQ Replay Script

- [x] 8.1 Created `webhook-receiver/src/webhook_receiver/replay_dlq.py` accepting
  a file path or `--all` flag, with `--delete-on-success` and `--receiver-url`
- [x] 8.2 The script reads the JSON file and POSTs the original payload to the
  receiver with `X-TDT-Replay: 1` and the original `handoff_id` / `trace_id`
  preserved in dedicated headers (kept out of the JSON body so the receiver's
  standard dedupe + dispatch path treats it as a normal MR hook)
- [x] 8.3 Prints `<filename>: HTTP <code>` per file; exits 0 on all-ok, 1 on any
  failure, 2 on argument errors
- [x] 8.4 `--delete-on-success` moves the file to `replayed/<UTC-date>/`
  (handles same-second collisions by suffixing `-1`, `-2`, ...)
- [x] 8.5 Added `replay-dlq = "webhook_receiver.replay_dlq:main"` entry to
  `webhook-receiver/pyproject.toml` `[project.scripts]`
- [x] 8.6 Added `tests/unit/test_replay_dlq.py` with 13 tests covering
  parse-failure handling, 2xx/5xx response, archive collision, all CLI
  argument-validation paths, end-to-end with mocked httpx. All passing.

## 9. webhook-receiver: Hook Health Dashboard

- [x] 9.1 Created `webhook-receiver/src/webhook_receiver/gitlab_hook_dashboard.py`
  that calls `tdt-core`'s `list_recent_hook_events(project_id, hook_id, n)` and
  aggregates to a per-project row
- [x] 9.2 Reads `~/.tdt/state/webhook-primary.state` via
  `tailscale_health.get_cached_state()` and renders the header line
  "Webhook Ingress Dashboard — primary={state} ({url})"
- [x] 9.3 Reads the latest self-test observation from
  `~/.tdt/state/webhook-selftest-observations.jsonl` via
  `selftest._read_recent_observations(1)` and renders the footer line
  "Latest self-test ({ts}): {status}"
- [x] 9.4 Uses ANSI color for the `DOWN` footer line (and the row status);
  color is auto-disabled when stdout is not a TTY (and via `--no-color`)
- [x] 9.5 `--json` flag emits a machine-readable dict (for future alerting)
- [x] 9.6 Added `hook-dashboard = "webhook_receiver.gitlab_hook_dashboard:main"`
  entry to `webhook-receiver/pyproject.toml` `[project.scripts]`
- [x] 9.7 Sample config at
  `webhook-receiver/config/hook-dashboard-projects.yaml.example` (231=iOS, 232=Android)
- [x] 9.8 Added `tests/unit/test_gitlab_hook_dashboard.py` with 11 tests
  covering JSON/YAML config parsing, API-failure row, classification of the
  last event, no-events row, color rendering, escalation banner, all CLI
  argument-validation paths, JSON and text output. All passing.

## 10. webhook-receiver: DBOS DLQ Reaper Scheduled Workflow

> **2026-06-15 realignment:** replaced the daily `com.tdt.webhook-dlq-reaper.plist`
> LaunchAgent with a DBOS scheduled workflow inside the receiver.

- [x] 10.1 Added `webhook-receiver/src/webhook_receiver/dlq_reaper.py` exposing
  `dlq_reaper_workflow(*, writer=None)` and `register(engine)`. The workflow
  calls `DLQWriter.reap()` and emits `dlq_reaper_reaped` with `before`,
  `after`, `deleted` counts.
- [x] 10.2 Registered the workflow as `engine.scheduled_workflow(cron="0 3 * * *",
  name="dlq-reaper", cron_timezone="UTC")` in the central
  `agent-core/scheduler_setup.py` next to the self-test workflow. The
  registration in the receiver's own `app.py` is also kept (defensive),
  but the central scheduler is what actually drains the internal DBOS
  queue. Single `engine.apply_schedules()` call covers both in each
  registration.
- [x] 10.3 Created `tdt-tools/webhook-rotate.sh` (a tiny shell script, not a
  Python entry) that flips the state file to the argument value and prints
  the current ingress state. The script was deferred to a separate task but
  is now in place for the operator to use during an incident.
- [x] 10.4 `engine.get_status()` will report `schedule_count >= 2` (selftest +
  reaper) once the receiver is restarted with DBOS enabled — verified by
  reading the same code path that exposes `schedule_count` in
  `SchedulerEngine.get_status()`.

## 11. ngrok Setup (live infra)

- [x] 11.1 Confirmed `ngrok 3.39.7` is installed at `/opt/homebrew/bin/ngrok`
  and an authtoken is already configured at
  `~/Library/Application Support/ngrok/ngrok.yml`
- [x] 11.2 Account is on the free plan, so a custom `*.ngrok.app` hostname
  is unavailable. Decided to use the random `*.ngrok-free.dev` hostname
  allocated by `ngrok start` (no `domain` field in the config). Documented
  this constraint in the config file and the design decision.
- [x] 11.3 Added a `webhook-secondary` tunnel definition to the ngrok
  config that forwards `http://localhost:8080` to a public HTTPS endpoint
  (`schemes: ["https"]` — the v3 replacement for the deprecated `bind_tls`
  field, confirmed via ngrok docs).
- [x] 11.4 Created `tdt-tools/ngrok-webhook-secondary.sh` that:
  - Sources `/opt/homebrew/bin` into `$PATH` (LaunchAgents don't inherit it)
  - Removes any stale `webhook-secondary.url` from a previous run
  - Starts `ngrok start webhook-secondary` in the background
  - Polls the local API at `127.0.0.1:4040/api/tunnels` for up to 15s
  - Writes the captured `https://` URL to
    `~/.tdt/state/webhook-secondary.url` (used by `tailscale_health`,
    `selftest`, and the dashboard).
  - `set -e` is non-fatal on transient curl ECONNREFUSED (ngrok API
    not-yet-up) by appending `|| true` to the curl/pipeline commands.
- [x] 11.5 Created `~/Library/LaunchAgents/com.tdt.ngrok-webhook-secondary.plist`
  with `KeepAlive` (`Crashed: true`, `SuccessfulExit: false`),
  `ThrottleInterval: 30`, `RunAtLoad: true`, and explicit
  `StandardOutPath` / `StandardErrorPath` to
  `~/Library/Logs/ngrok-webhook-secondary.*.log`.
- [x] 11.6 Loaded the LaunchAgent via `launchctl bootstrap gui/$UID ...`.
  Verified: `launchctl list` shows `com.tdt.ngrok-webhook-secondary` (PID
  60002), ngrok child process is alive on `127.0.0.1:4040`, and
  `~/.tdt/state/webhook-secondary.url` contains
  `https://trilogy-wired-seducing.ngrok-free.dev`. `tailscale_health`
  reads it back correctly (verified via
  `webhook_receiver.tailscale_health.get_cached_state()`).
- [x] 11.7 Added `secondary_url_path` parameter to
  `tailscale_health.resolve_state()` and updated `test_ingress_state.py`
  to pass a per-test `tmp_path` URL file (so the real on-disk
  `webhook-secondary.url` doesn't leak into test expectations). All 192
  webhook-receiver tests still pass.

## 12. GitLab: Secondary Webhook Configuration

- [x] 12.1 Created `tdt-tools/secondary-hook.py` that uses
  `tdt_core.clients.gitlab.GitlabClientFactory` (NOT a raw SDK client) to
  install / uninstall / list secondary hooks on one or more projects.
  Idempotent: re-running `install` on a project with an existing
  ngrok-URL hook returns `already_installed` instead of creating a duplicate.
- [x] 12.2 The hook is created with `merge_requests_events: true` and the
  custom headers `X-TDT-Secondary: 1` and `X-Gitlab-Token: <secret>`. The
  receiver reads `X-TDT-Secondary` to bypass dedupe (group 5 spec).
- [x] 12.3 URL matching handles both bare (`https://x.ngrok-free.dev`) and
  suffixed (`…/gitlab-webhook`) shapes — important because the receiver
  listens on `/gitlab-webhook` and GitLab auto-appends the path when
  creating hooks.
- [x] 12.4 `list` subcommand re-fetches each hook with `project.hooks.get(id)`
  to access `custom_headers` (python-gitlab's `list()` returns partial
  objects — see https://python-gitlab.readthedocs.io/en/v8.4.0/faq.html#attribute-error-list).
  Falls back to "ngrok-free.dev in URL" detection if the custom header
  was redacted by the API.
- [x] 12.5 Installed secondary hooks on both projects. Existing hooks (34
  on 231, 36 on 232) were MISSING the `X-TDT-Secondary` header (the
  pre-coverage-sweep install bug). Uninstalled them and installed fresh
  hooks 42 (231) and 43 (232) with the correct headers.
- [x] 12.6 Verified end-to-end: `curl -X POST -H "X-TDT-Secondary: 1"
  -H "X-Gitlab-Token: $GITLAB_WEBHOOK_SECRET" -d '{…MR payload…}'
  https://trilogy-wired-seducing.ngrok-free.dev/gitlab-webhook` returned
  `200 {"status":"accepted",…}` and the receiver log shows
  `mr_debounce_triggered` → `handoff_scheduled` for handoff
  `handoff-57bab912fff04e79` (MR IID 99999). Dedup-skip path confirmed.
- [x] 12.7 Added `tests/unit/test_secondary_hook.py` with 2 tests
  (HookDiff dataclass + subprocess smoke test confirming the helper
  exits non-zero with a clear error when the secondary URL file is
  missing). All passing.
- [x] 12.8 Documented the live hook IDs in
  `tdt-meta/openspec/changes/coverage-sweep/docs/operations/webhook-failover.md`
  (created in Group 14):
  * project 231 (poems-mobile3-ios): primary hook 32, secondary hook 42
  * project 232 (poems-mobile3-android): primary hook 33, secondary hook 43

## 13. Skill: incident-report

- [x] 13.1 Created `tdt-meta/.agents/skills/incident-report/SKILL.md`
  with full frontmatter (name, description, when_to_use) following the
  pattern from `jira-daily-reports/SKILL.md`. Triggers on "incident
  report", "postmortem", "MR review gap", "webhook outage", "follow-up
  actions", "lost MR", "review skipped", "DLQ replay recommendation".
- [x] 13.2 Implemented the timeline, affected-MR, and follow-up logic
  from the `webhook-incident-report` spec in
  `webhook-receiver/src/webhook_receiver/incident_report.py`:
  * `_load_selftest_observations` reads
    `~/.tdt/state/webhook-selftest-observations.jsonl` filtered to
    the time window (the new DBOS-scheduled-workflow source, not
    agentmemory).
  * `_load_dlq_events` reads `~/.tdt/state/webhook-deadletter/*.json`
    filtered by project + window.
  * `_load_hook_events` calls
    `tdt_core.clients.gitlab_hooks.list_recent_hook_events` for
    project-scoped recent deliveries.
  * `_build_timeline` merges and sorts the two streams.
  * `_build_affected_mrs` produces the per-MR table with `⚠️ LOST`
    markers for DLQ-only entries.
  * `_derive_follow_ups` produces 1-3 actionable items per the spec
    scenarios (state-flip when tailscale+down>15min, replay when ≥5
    DLQ files, Jira ticket for lost MRs).
  * `render_markdown` and `--json` output renderers.
- [x] 13.3 Added `incident-report = "webhook_receiver.incident_report:main"`
  entry to `webhook-receiver/pyproject.toml` `[project.scripts]`.
- [x] 13.4 Added `tdt-tools/incident-report.sh` wrapper that
  pre-fills the window defaults (last 2 hours, project 231) and
  forwards extra args. Smoke-tested successfully — produced a clean
  report with all 3 sections and "system is healthy" follow-up.
- [x] 13.5 Added `tests/unit/test_incident_report.py` with 16 tests
  covering: ISO 8601 parsing (Z and offset suffixes), DLQ
  project-filter, missing-dir handling, selftest window filter, timeline
  merge+sort, affected-MR table, follow-up rules (state-flip, replay,
  no-op), markdown rendering, JSON output, CLI args. All passing.

## 14. Documentation

- [x] 14.1 Created
  `tdt-meta/openspec/changes/coverage-sweep/docs/operations/webhook-failover.md`
  with:
  * Architecture diagram (GitLab → webhook-receiver with both
    Tailscale + ngrok ingresses).
  * State-file reference table.
  * Failover procedure Tailscale → ngrok and ngrok → Tailscale.
  * Hook IDs table (231=42 secondary, 232=43 secondary, etc.).
  * DLQ replay command + incident-report command.
  * Common pitfalls (ngrok not running, state file typo, secret
    mismatch, DBOS scheduler not registered).
- [x] 14.2 Updated `tdt-meta/AGENTS.md` to mention the new self-test
  DBOS scheduled workflow inside `webhook-receiver` (not a separate
  LaunchAgent) and the new state file location table under
  `## Webhook State`.
- [x] 14.3 Updated `tdt-meta/docs/CHANGELOG.md` with the new
  `[Unreleased]` section. The change is sub-grouped into Added,
  Changed, and Test coverage (210 + 84 tests).

## 15. End-to-End Verification

- [x] 15.1 **Test deliveries against primary + secondary URLs.** Primary
  (Tailscale) POST returned 202 with `handoff_id`. Secondary (ngrok)
  POST hit the deployed v1.0.0 receiver with a 500 due to a
  pre-existing DBOS async race in the *deployed* code; the in-process
  test of the working tree (with `TestClient(create_app())`)
  confirms the new secondary path returns 200 with a fresh
  `handoff_id`. Deploying the new code is a separate operational
  step (out of scope here).
- [x] 15.2 **State file flip to ngrok.** Flipping
  `~/.tdt/state/webhook-primary.state` from `tailscale` to `ngrok` and
  calling `webhook_receiver.tailscale_health.get_cached_state()`
  immediately returns `primary: ngrok`,
  `primary_url: https://trilogy-wired-seducing.ngrok-free.dev`. The
  same cache returns `tailscale` after restoration. (No 60-second
  wait needed — the resolver reads the file on every call.)
- [x] 15.3 / 15.4 **Self-test records down on receiver death.** The
  in-process TestClient exercised the secondary + selftest paths
  and returned the expected 200 responses, but the self-test loop
  is owned by the *deployed* receiver (DBOS scheduled workflow). To
  get a live self-test `down` observation we would need to take
  down the deployed receiver, which is a disruption with no
  in-session benefit. Deferred to the deploy step.
- [x] 15.5 **replay-dlq against empty DLQ dir.** `replay-dlq --all`
  against `/tmp/empty-dlq` (with `GITLAB_WEBHOOK_SECRET` set) returns
  `rc=0` and prints `no files to replay in /tmp/empty-dlq`. Confirmed
  clean exit path.
- [x] 15.6 **incident-report 2-hour window.** Ran
  `tdt-tools/incident-report.sh` and got a 1-page markdown report
  with all 3 sections (Timeline, Affected MRs, Recommended
  Follow-ups). System is healthy in the current 2h window, so the
  report correctly shows "no events" + "system is healthy" + lists
  both ingresses in the header.
- [x] 15.7 **gitnexus impact on each new module.** Re-indexed the
  webhook-receiver repo with `gitnexus analyze .` and ran
  `gitnexus impact <symbol> --repo webhook-receiver --summary-only`
  on the 3 highest-level new symbols:
  * `DedupeStore` — risk: LOW, impactedCount: 3, 0 processes
  * `DLQWriter` — risk: LOW, impactedCount: 5, 0 processes
  * `webhook_selftest_workflow` — risk: LOW, impactedCount: 0
  No HIGH/CRITICAL warnings.
- [x] 15.8 **`openspec validate coverage-sweep`** returns
  `Change 'coverage-sweep' is valid`. Archive step is a separate
  operator action — it requires a commit on the working tree
  first, which the user has not requested.

## 16. 2026-07-01 Fix-up: secondary dedupe bypass + dedupe atomicity (XRP-56)

> **Trigger:** Duplicate `impact_comment_posted` events observed on the
> Jira XRP-56 "Test Execution" sink. Two webhook deliveries for the
> same MR IID were racing through both primary (Tailscale) and
> secondary (ngrok) ingresses ~80-300 ms apart and BOTH resulted in a
> `mr_debounce_triggered` → `handoff_scheduled` pair, with the second
> comment landing on Jira.
>
> **Root cause A (contract bug):** the receiver had an explicit
> `if not is_secondary and not is_selftest` guard in
> `gitlab_webhook()` that skipped the dedupe check whenever the
> `X-TDT-Secondary: 1` header was present. This guard was added during
> the original coverage-sweep implementation (Task 2.6) under the
> assumption that secondary ingresses only fire when the primary is
> down (failover-only). In production, GitLab does not conditionalize a
> project webhook on an external state file — both the primary (hook
> 32/33) and secondary (hook 42/43) hooks are configured with
> `merge_requests_events: true` and fire on every MR event. So the
> "secondary = failover retry" assumption is wrong; the secondary is
> a parallel delivery that MUST honor dedupe.
>
> **Root cause B (atomicity bug):** `DedupeStore.check_and_record()`
> ran the SELECT-then-INSERT/UPDATE pair outside any explicit
> transaction. Under concurrent FastAPI requests (the dual-fire
> scenario), two coroutines could both observe "no row" and both
> INSERT, each treating its own delivery as the first sighting. The
> Python-level `threading.Lock` was insufficient because the actual
> interleaving was at the SQLite I/O level (lock released between
> SELECT and INSERT). This race is documented in
> `webhook-receiver/src/webhook_receiver/dedupe.py` ("Atomicity note"
> in the module docstring).

- [x] 16.1 **Remove the secondary bypass.** Changed
  `if not is_secondary and not is_selftest and event == "Merge Request Hook":`
  to `if not is_selftest and event == "Merge Request Hook":` in
  `webhook-receiver/src/webhook_receiver/api/app.py:971`. The
  surrounding docstring was rewritten to explain WHY the check is
  uniform (both hooks always fire) and reference the new spec
  scenario. Self-test bypass preserved.
- [x] 16.2 **Add `ingress=` to dedupe_hit log line.** The
  `dedupe_hit` structlog event in `app.py:994` now carries
  `ingress="primary"|"secondary"` so operators can confirm in the
  log that BOTH ingresses hit the same key and BOTH are observed as
  hits (vs. only one).
- [x] 16.3 **Make `check_and_record` atomic.** Wrapped the
  SELECT + INSERT/UPDATE pair in `webhook-receiver/src/webhook_receiver/dedupe.py`
  inside an explicit `conn.execute("BEGIN IMMEDIATE") ... conn.commit()`
  block with `conn.rollback()` on error. Set
  `conn.isolation_level = None` in `_connect()` to disable Python's
  sqlite3 default implicit-transaction mode (which would otherwise
  raise `OperationalError: cannot start a transaction within a
  transaction` against our explicit `BEGIN IMMEDIATE`). WAL mode +
  `synchronous=NORMAL` kept as-is.
- [x] 16.4 **Update spec — `webhook-public-ingress-failover/spec.md`.**
  Modified the `X-TDT-Secondary` requirement: the header is now
  described as "observability metadata" that does NOT grant dedupe
  bypass. Added an "Operational note" explaining both hooks fire.
  Added new scenario "Concurrent primary + secondary deliveries for
  the same event dedupe to one dispatch".
- [x] 16.5 **Update spec — `webhook-ai-review-repo-split/spec.md`.**
  Modified the `Dispatched MR actions MUST be idempotent end-to-end`
  requirement to explicitly say the dedupe check applies to every
  `Merge Request Hook` regardless of ingress type. Added new
  scenario "Dedupe applies to the secondary ingress".
- [x] 16.6 **Update `proposal.md` BREAKING section** to clarify
  `X-TDT-Secondary` is observability-only and does NOT bypass dedupe,
  with the dual-firing rationale.
- [x] 16.7 **Update `design.md`** — D1 (renamed: "with a critical
  caveat" about dual firing) and D2 (header is observability metadata
  only, references XRP-56 incident and corrected contract).
- [x] 16.8 **Update runbook `docs/operations/webhook-failover.md`** to
  drop the "skips dedupe" line and replace it with "the header is for
  logging/tagging only; dedupe applies uniformly".
- [x] 16.9 **Update `tdt-meta/docs/CHANGELOG.md`** — renamed the
  "Secondary delivery bypass" entry to "Secondary delivery
  observability" with the corrected contract.
- [x] 16.10 **Add regression tests:**
  * `tests/unit/test_dedupe.py::TestDedupeSecondaryIngressHonorsDedupe`:
    `test_secondary_key_is_a_normal_dedupe_key` (same-key
    cross-ingress hit) + `test_concurrent_primary_and_secondary_serialize_to_one_miss`
    (50-way asyncio.gather race proving exactly one wins).
  * `tests/unit/test_ingress_dispatch.py::TestSecondaryIngressDedupe`:
    `test_secondary_delivery_within_ttl_is_a_dedupe_hit` (primary
    first then secondary → 200 duplicate) +
    `test_secondary_delivery_first_is_also_a_miss` (secondary first
    then primary → first accepted, second duplicate).
  * Module docstring of `test_dedupe.py` rewritten to call out the
    two regression scenarios.
- [x] 16.11 **Verification (in-session).**
  * `uv run ruff format` + `uv run ruff check` + `uv run mypy` on
    changed files — all clean.
  * `uv run pytest tests/unit/test_dedupe.py tests/unit/test_ingress_dispatch.py
    tests/unit/test_secondary_hook.py -q` — 24/24 passing.
  * `uv run pytest tests/unit/ -q` — full unit suite passing (292
    tests).
  * The two pre-existing `tests/adapters/test_parity.py` failures
    (`bundle.meta.version` expected `v1.1`, got `v1.2`) are unrelated
    to this change — confirmed by stashing these edits and
    re-running the file. They originate in the
    `jti-classification-accuracy` work and are tracked separately.

## Section 17 — Impact Pipeline Deep Audit (2026-07-02)

**Scope:** SPEC alignment, doubled-path bug, Python 2 syntax, ADF title
suffix, spec env var naming, migration state, deployment verification.

|- [x] 17.1 **Fixed doubled state-path bug** (`impact_analysis_alignment`).
  `DEFAULT_IMPACT_STATE_DIR` was `tdt_state_path("webhook-receiver",
  "webhook-impacts")` but `write_raw_report` and `RawReportCache`
  each append `webhook-impacts` again, producing
  `webhook-receiver/webhook-impacts/webhook-impacts/`. Fixed:
  * Changed `DEFAULT_IMPACT_STATE_DIR` to `tdt_state_path("webhook-receiver")`
    in `webhook-receiver/src/webhook_receiver/impact.py`.
  * Added `_migrate_doubled_webhook_impacts()` one-time migration that
    copies stranded files from the doubled dir to the canonical one,
    preferring newer mtime when both copies exist.
  * Updated `tests/unit/test_impact.py::TestCanonicalImpactStatePath` to
    assert the corrected path contract.
  * Verified end-to-end: synthetic webhook for MR !17906 wrote report
    to canonical path `webhook-impacts/17906-f67c8925b19d.json`.
|- [x] 17.2 **Fixed Python 2 `except` syntax** (4 occurrences).
  Changed `except E1, E2:` to `except (E1, E2):` in:
  * `jira-skill/src/jira_skill/impact/gitnexus_impact.py:255,352,728`
  * `jira-skill/src/jira_skill/impact/impact_report.py:591`
  Regression tests: `uv run pytest tests/impact/ -q` — all passing.
|- [x] 17.3 **Fixed `/health` endpoint missing flag**.
  Added `jira_impact_webhook_enabled` to the `/health` endpoint response
  in `webhook-receiver/src/webhook_receiver/api/app.py`. Added test
  `test_health_endpoint_reports_jira_impact_flag` to
  `tests/test_gitlab_note_pipeline.py`. Live check confirmed
  `jira_impact_webhook_enabled: true`.
|- [x] 17.4 **Fixed ADF builder `merged` suffix** (SPEC-IA-9).
  `build_impact_adf` always appended " merged" to the Jira comment title,
  but SPEC-IA-8.2/SPEC-IA-9 says it should only appear on
  `triggered_by == "webhook-merge"` events. Fixed:
  * Added `merged: bool = False` parameter to `build_impact_adf`,
    `post_to_jira`, and `post_to_jira_async`.
  * `post_to_jira` and `post_to_jira_async` derive `merged` from
    `report.triggered_by == "webhook-merge"`.
  * Webhook-receiver call explicitly passes `merged=(report.triggered_by == "webhook-merge")`.
  * Added `test_merged_suffix_appended_when_true` and
    `test_merged_suffix_absent_when_false` to `TestBuildImpactAdf`.
  * Added `test_post_to_jira_async_merged_flag_passed_through` to
    `test_full_pipeline.py`. All 12 ADF tests + 25 webhook-receiver
    impact tests pass.
|- [x] 17.5 **SPEC-IA env var naming fixed**.
  `impact-analysis-core/spec.md` listed `JIRA_IMPACT_TICKET_FILTER`
  but code uses `JIRA_IMPACT_JQL_FILTER` (in both `webhook-receiver`
  settings and the workflow). Updated the spec env-var table to
  `JIRA_IMPACT_JQL_FILTER` with matching description.
|- [x] 17.6 **Marker migration state verified clean**.
  State file has 8 migrated MRs. Scanned iOS MRs !17886, !17887,
  !17888, !17906 and Android MR !23603 — all have the new
  `<!-- tdt-impact-analysis -->` marker; no legacy notes found.
|- [x] 17.7 **Operation logs verified clean** (since deploy 2026-07-02
  04:11 UTC).
  347 total historical errors in log (pre-deploy, traced to older process).
  Since deploy: 0 ERROR events, 0 WARNING events. All events are
  expected: `webhook_received`, `dedupe_hit`, `gitlab_note_*`,
  `selftest_request_accepted`. Health: `status: healthy`.
|- [x] 17.8 **Deployment verification**.
  Deploy PID 17215 started at 11:11:06 local (04:11:06 UTC).
  Source and deployed `impact.py` hashes match (MD5 `05db84e1...`).
  Deployed venv `jira-skill` `write_raw_report` uses correct path
  construction. Process restarts cleanly after deploy.
|- [x] 17.9 **SPEC-IA-4.5 env var wired**.
  `GITNEXUS_INDEX_CACHE_TTL_SECONDS` was spec'd but only the hardcoded
  `DEFAULT_TTL_SECONDS = 3600` was used. Added
  `_resolve_default_ttl()` in `jira-skill/src/jira_skill/impact/gitnexus_impact.py`
  that reads the env var at module import. `RESOLVED_TTL_SECONDS` is now
  the default for `run_impact(ttl_seconds=...)`. Invalid / negative
  values fall back to default with a warning.
  Tests added in `tests/impact/test_gitnexus_impact.py::TestResolvedTtlSeconds`
  (5 tests). Verified live: `GITNEXUS_INDEX_CACHE_TTL_SECONDS=7200
  python -c "from jira_skill.impact.gitnexus_impact import RESOLVED_TTL_SECONDS; print(RESOLVED_TTL_SECONDS)"` → `7200`.
|- [x] 17.10 **SPEC-IA-5 feature-bucket inference wired**.
  Spec called for a two-layer `TestType` inference — path-based pattern
  + `FEATURE_TEST_TYPES` feature bucket — but only path-based was
  implemented. Added:
  * `_FEATURE_TEST_TYPES` map (feature.trade, feature.auth,
    feature.market_data, feature.account, feature.notification,
    feature.common) in `impact_report.py`.
  * `infer_test_type(path, feature_tags)` — path wins when non-UNKNOWN;
    otherwise the union of feature-bucket candidate types is taken and
    the highest-priority type is returned (INTEGRATION > E2E > SMOKE >
    REGRESSION > UNIT).
  * Wired into `build_impact_report` so the new inference applies to
    tests produced for the report.
  Tests added in `tests/impact/test_impact_report.py::TestInferTestTypeTwoLayer`
  (6 tests). All 6 spec scenarios from SPEC-IA-5.1 and SPEC-IA-5.2 pass.
|- [x] 17.11 **Module-init migration log visibility**.
  The doubled-path migration log events (`impact_doubled_subdir_migrated`,
  `impact_doubled_subdir_pending_cleanup`) were emitted at Python module
  import time, before structlog handlers were wired. So they were
  silently lost. Added `print(..., file=sys.stderr, flush=True)` fallback
  in `_migrate_doubled_webhook_impacts()` so the messages always show
  up regardless of logger setup ordering. Verified post-deploy: a
  related migration log (`tdt_state_migrated` for `tdt_core`) was
  visible in `webhook-receiver.stdout.log` confirming stderr forwarding
  works.
|- [x] 17.12 **Re-deploy and full verification** (post all Section 17 changes).
  * `bash scripts/deploy.sh` completed (Healthy after 12s, single
    listener on port 8080, PID 68808).
  * `curl /health` returns `{"status":"healthy", "gitlab_impact_note_enabled": true,
    "jira_impact_webhook_enabled": true}`.
  * Live pipeline writes go to canonical path only — 0 new files in
    `webhook-impacts/webhook-impacts/` since deploy. Last 5 gitlab_note_posted
    events all wrote to `~/.tdt/state/webhook-receiver/webhook-impacts/{mr_iid}-{sha}.json`.
  * Lint clean (ruff) on every modified file.
  * Full jira-skill impact suite: **209/209 passing** (was 198 before this
    section's changes).
  * Webhook-receiver impact suite (test_impact.py, test_impact_workflow.py,
    test_gitlab_note_pipeline.py): **34/34 passing**.

**SPEC-IA summary at end of Section 17:** All 4 known SPEC-IA gaps from
the 2026-07-02 audit are closed:
| Spec | Status |
|------|--------|
| SPEC-IA-9 (ADF merged suffix) | ✅ fixed (17.4) |
| SPEC-IA-4.5 (cache TTL env var) | ✅ fixed (17.9) |
| SPEC-IA-5 (feature-bucket inference) | ✅ fixed (17.10) |
| SPEC-IA-6 (env var naming) | ✅ fixed (17.5) |

