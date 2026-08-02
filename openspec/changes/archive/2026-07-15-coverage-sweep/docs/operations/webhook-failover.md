# Webhook Failover Runbook (coverage-sweep change)

This runbook describes how to fail over the webhook receiver between the
two public ingresses (Tailscale and ngrok) and how to verify the
failover is working end-to-end.

## Architecture

```
GitLab                                   webhook-receiver (127.0.0.1:8080)
  |                                                  ^
  |-- (Tailscale, primary hook) --------------------+  https://les-mac-mini.tailc6b508.ts.net
  |                                                  |
  +-- (ngrok, secondary hook) ----------------------+  https://<random>.ngrok-free.dev
                                                     |
                                          X-TDT-Secondary: 1
                                                     |
                                          X-TDT-Selftest: 1
                                                     |
                                            (synthetic probes run by
                                             tdt-scheduler serve in
                                             agent-core container)
```

The two ingresses are independent tunnels. The receiver runs locally
on `127.0.0.1:8080`; the public URLs are forwarders.

| Ingress | URL | LaunchAgent | State file |
|---------|-----|-------------|------------|
| Primary (Tailscale) | `https://les-mac-mini.tailc6b508.ts.net` | `com.tdt.tailscale-funnel` (or operator-managed) | `~/.tdt/state/webhook-primary.state` = `tailscale` |
| Secondary (ngrok)   | `https://<random>.ngrok-free.dev` | `com.tdt.ngrok-webhook-secondary` | `~/.tdt/state/webhook-secondary.url` |

The active primary is whichever URL the receiver is currently
publishing. The default is **Tailscale** because the
`webhook-primary.state` file is seeded with `tailscale`.

## Hook configuration

Each project has TWO webhooks installed in GitLab:

| Project | Primary hook | Secondary hook |
|---------|--------------|----------------|
| `pspl/poems-mobile3-ios`     (231) | id 32 → Tailscale URL | id 42 → ngrok URL |
| `pspl/poems-mobile3-android` (232) | id 33 → Tailscale URL | id 43 → ngrok URL |

The secondary hook has the `X-TDT-Secondary: 1` custom header set. The receiver
reads it and logs every delivery as `ingress=primary` or `ingress=secondary` for
dashboard and incident-report purposes. **The header does not bypass dedupe** —
both hooks are always installed with `merge_requests_events: true` and both fire
for every MR event, so the receiver applies the `(project_id, MR IID, event_type)`
dedupe check uniformly to both ingresses (see
`openspec/changes/coverage-sweep/specs/webhook-ai-review-repo-split/spec.md`).

To add a new project, run:

```bash
cd "$HOME/Developer/tdt"
uv run --project webhook-receiver --with python-gitlab --with tdt-core \
  python tdt-tools/secondary-hook.py install --project <pid>
```

To remove:

```bash
uv run --project webhook-receiver --with python-gitlab --with tdt-core \
  python tdt-tools/secondary-hook.py uninstall --project <pid>
```

To list current hooks:

```bash
uv run --project webhook-receiver --with python-gitlab --with tdt-core \
  python tdt-tools/secondary-hook.py list --project <pid>
```

## Failover procedure (Tailscale → ngrok)

1. **Confirm the failure.** Check the self-test status:
   ```bash
   curl -s http://127.0.0.1:8080/health/ingress | jq .
   ```
   If `selftest` is `null` or `primary_status != "ok"`, the primary is
   down.

2. **Check ngrok is up:**
   ```bash
   cat ~/.tdt/state/webhook-secondary.url
   launchctl list | grep ngrok-webhook-secondary
   ```
   If ngrok is not up, restart it: `launchctl kickstart -k
   gui/$UID/com.tdt.ngrok-webhook-secondary`.

3. **Flip the primary state file:**
   ```bash
   echo "ngrok" > ~/.tdt/state/webhook-primary.state
   ```

4. **Re-deploy the receiver (or just wait for the next 5-minute
   self-test cycle to report a new OK).**

5. **Verify the failover:**
   ```bash
   curl -s http://127.0.0.1:8080/health/ingress | jq .
   ```
   The `primary` field should be `ngrok` and `primary_url` should be
   the ngrok URL.

6. **Check the dashboard:**
   ```bash
   hook-dashboard --project 231 --hook-id 32
   ```
   New hook events should be returning 2xx.

## Failover procedure (ngrok → Tailscale)

1. Confirm Tailscale is reachable:
   ```bash
   tailscale status
   ```
2. Flip the state file:
   ```bash
   echo "tailscale" > ~/.tdt/state/webhook-primary.state
   ```
3. Re-deploy or wait for the next self-test cycle.
4. Verify with `curl -s http://127.0.0.1:8080/health/ingress | jq .`

## Replaying DLQ events

If the DLQ accumulated entries while the primary was down:

```bash
# 1. List DLQ files
ls ~/.tdt/state/webhook-deadletter/

# 2. Replay them all (delete on success moves them to replayed/<date>/)
tdt-tools/replay-dlq.py --all --delete-on-success
```

The replay script POSTs each original payload to the receiver with
`X-TDT-Replay: 1` so the receiver treats it as a fresh delivery.

## Generating an incident report

```bash
# Default: project 231, last 2 hours
tdt-tools/incident-report.sh

# Custom:
uv run --project webhook-receiver python -m webhook_receiver.incident_report \
  --project 231 --window-hours 4 --json
```

## State file reference

| File | Purpose |
|------|---------|
| `~/.tdt/state/webhook-primary.state` | "tailscale" or "ngrok" |
| `~/.tdt/state/webhook-secondary.url` | ngrok public URL (auto-captured by `tdt-tools/ngrok-webhook-secondary.sh`) |
| `~/.tdt/state/webhook-dedupe.sqlite` | SQLite DB of recent webhook deliveries (10-min TTL) |
| `~/.tdt/state/webhook-deadletter/*.json` | One file per failed `ai-review` dispatch |
| `~/.tdt/state/webhook-selftest-observations.jsonl` | Self-test history (capped at 720 lines = 60 hours) |
| `~/.tdt/state/webhook-replayed/<date>/*.json` | Archived DLQ files (replay succeeded) |

## Scheduled workflows (DBOS, owned by tdt-scheduler in agent-core)

* `webhook-selftest` — `*/5 * * * *` — probes primary + secondary
  ingress, writes an observation to the JSONL file, escalates after 3
  consecutive `down` results.
* `dlq-reaper` — `0 3 * * *` — deletes DLQ files older than
  `WEBHOOK_DLQ_FAILURE_TTL_SECONDS` (default 10 days) and enforces
  `WEBHOOK_DLQ_MAX_FILES` (default 10 000) by deleting the oldest.

Inspect with the DBOS Conductor or the
`tdt_core.scheduler.engine` API. See
`docs/tdt-python-reference.md` for details.

## Common pitfalls

1. **The ngrok LaunchAgent is not running** — the secondary URL file
   is empty or stale, the dashboard reports "secondary: not configured".
   Fix: `launchctl kickstart -k
   gui/$UID/com.tdt.ngrok-webhook-secondary`. The wrapper script
   captures the new URL into the state file.

2. **The receiver was redeployed with `DATABASE_URL` not set** — DBOS
   can't start, the scheduled workflows are not registered. Check
   `~/.tdt-webhook-receiver/logs/webhook-receiver.stderr.log` for
   `DBOS` errors.

3. **The state file contains a typo** — `tailcale` instead of
   `tailscale`. The receiver silently defaults to `tailscale`, so the
   failover never engages. Fix: `echo tailscale >
   ~/.tdt/state/webhook-primary.state`.

4. **The secret in the secondary hook does not match the receiver's
   `GITLAB_WEBHOOK_SECRET`** — the secondary deliveries are
   authenticated as 401. Reinstall with
   `tdt-tools/secondary-hook.py install --project <pid>` (the wrapper
   reads the env var).
