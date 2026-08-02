# Design: fix-webhook-selftest-token-rejection

This change bundles two operational fixes that surfaced together during
monitoring:

1. The `webhook-selftest` DBOS workflow was sending an empty `X-Gitlab-Token`
   while the receiver enforced `GITLAB_WEBHOOK_SECRET`, producing a 46h storm of
   `WEBHOOK_SELFTEST_ESCALATION` events.
2. The scheduler container's `entrypoint.sh` redirected PID 1's stdout/stderr
   entirely to a host-bind-mounted file, so `docker logs` could not see
   what the scheduler was emitting.

---

## Part 1 — `webhook-selftest` token forwarding

### Problem recap

`webhook-selftest` is a DBOS scheduled workflow registered by `webhook_receiver.dbos_scheduling:register_all_schedules`. Every 5 minutes it probes the configured primary webhook URL with a synthetic Merge Request Hook POST and writes a row to the observations JSONL file. Three consecutive `primary_status` values in `(down, timeout, error)` trigger an `escalation=true` row and a `WEBHOOK_SELFTEST_ESCALATION` structlog event.

In the running deployment the receiver enforces token equality before the self-test bypass:

```1002:1018:webhook-receiver/src/webhook_receiver/api/app.py
    token = request.headers.get("X-Gitlab-Token", "")
    if token != settings.webhook_secret:
        ...
        raise HTTPException(status_code=401, detail="Unauthorized")
    ...
    is_selftest = request.headers.get("X-TDT-Selftest", "").strip() == "1"
```

`settings.webhook_secret` is set in this deployment (64-char value, sourced from `GITLAB_WEBHOOK_SECRET` via `tdt_core.env.get_env`).

The DBOS registration wrapper reads the secret then drops it on the floor:

```96:102:webhook-receiver/src/webhook_receiver/dbos_scheduling.py
    _secret = os.environ.get("GITLAB_WEBHOOK_SECRET", "")

    async def _selftest_workflow(*args: Any, **kwargs: Any) -> None:
        from webhook_receiver.selftest import webhook_selftest_workflow

        await webhook_selftest_workflow(webhook_secret="")
```

Result: every probe sends `X-Gitlab-Token: ""`, the receiver responds `401 {"detail":"Unauthorized"}`, and the scheduler emits a `WEBHOOK_SELFTEST_ESCALATION` event every 5 minutes — 361 between 2026-07-13 16:10 and 2026-07-15 14:55.

### Why the comment lied

The pre-existing block comment above the registration asserted "the receiver does not enforce token auth when its own `GITLAB_WEBHOOK_SECRET` is unset (which is the case in this deployment)". That was true at the time of writing and remains a correct *reading* of the receiver code: an empty receiver secret accepts an empty probe token. But the deployment later added `GITLAB_WEBHOOK_SECRET` to harden the ingress, and the wrapper's hardcoded empty-string call was never revisited.

### Fix

Forward `_secret` instead of `""`:

```96:104:webhook-receiver/src/webhook_receiver/dbos_scheduling.py
    _secret = os.environ.get("GITLAB_WEBHOOK_SECRET", "")

    async def _selftest_workflow(*args: Any, **kwargs: Any) -> None:
        from webhook_receiver.selftest import webhook_selftest_workflow

        await webhook_selftest_workflow(webhook_secret=_secret)
```

The comment block is rewritten to describe the new behaviour: the probe always presents the configured token, and an empty secret is still safe because `"" == ""` is the receiver's accept path for unauthenticated deployments.

### Behaviour matrix

| `GITLAB_WEBHOOK_SECRET` | `X-Gitlab-Token` sent | Receiver check | Probe accepted? |
|-------------------------|-----------------------|----------------|-----------------|
| unset / empty           | `""`                  | `"" == ""`     | yes             |
| non-empty (current)     | `<the secret>`        | match          | yes             |
| non-empty, mismatched   | `<wrong value>`       | reject         | no (401)        |

### Testing

Two new tests in `tests/unit/test_dbos_scheduling.py`:

- `test_forwards_configured_secret` — sets `GITLAB_WEBHOOK_SECRET=test-token-abc123`, registers the schedules with a mock engine, captures the inner workflow invocation, asserts the inner was called with `webhook_secret="test-token-abc123"`.
- `test_forwards_empty_secret_when_unset` — removes the env var, asserts the wrapper passes `webhook_secret=""` (preserving the no-auth-deployment case).

The two tests use a small `monkeypatch` of `webhook_receiver.selftest.webhook_selftest_workflow` (the lazy import target) so no DBOS / Postgres fixture is needed.

### Live verification

After rebuild + recreate:

- Container restarted at `2026-07-15T07:52:11Z` (UTC), reached `healthy` in ~30 s.
- Observation at `2026-07-15T07:55:01Z`: `primary_status=ok`, code 200, latency 185 ms, `escalation=false` — first post-fix probe.
- Subsequent probes at 08:00 / 08:05 / 08:45 / 08:50 / 08:55 UTC: all `primary_status=ok`, all `escalation=false`.
- `WEBHOOK_SELFTEST_ESCALATION` count frozen at 361 since `2026-07-15T07:55Z` (was climbing every 5 min before).

---

## Part 2 — scheduler entrypoint dual-sink logging

### Problem recap

`entrypoint.sh` ran `exec >> "${LOG_FILE}" 2>&1` on PID 1 immediately after
creating the host-bind-mounted log directory. This redirected every
subsequent byte written to PID 1's stdout or stderr *exclusively* to the
host file. The container's stdout — and therefore the Docker json-file
log driver that backs `docker logs` — received nothing. The host file
filled correctly (5.2 MB observed) but every standard container-level
log inspection was empty:

```
$ docker logs agent-core-local-scheduler-1 --since 2h | wc -l
0
```

PID 1's `fd 1` and `fd 2` both pointed at the log file:

```
/proc/1/fd -> 1 -> /home/agent/.tdt/logs/scheduler-entrypoint.log
                2 -> /home/agent/.tdt/logs/scheduler-entrypoint.log
```

This contradicted the standard operational runbook in
`docs/operations/scheduler-healthcheck.md` and made log rotation /
shipping impossible to verify.

### Fix

Replace `exec >> "${LOG_FILE}" 2>&1` with `exec > >(tee -a "${LOG_FILE}") 2>&1`:

```16:24:agent-core/deployments/scheduler/entrypoint.sh
TDT_HOME="${TDT_HOME:-/home/agent/.tdt}"
mkdir -p "${TDT_HOME}/logs" "${TDT_HOME}/schedules"
LOG_FILE="${TDT_HOME}/logs/scheduler-entrypoint.log"
exec > >(tee -a "${LOG_FILE}") 2>&1
```

The redirect replaces PID 1's stdout with the read end of a named pipe.
`tee` reads from that pipe and writes to both the terminal (which becomes
the Docker json-file driver) and the host file. The final
`exec uv run tdt-scheduler serve` inherits the tee-writer's stdout, so
even post-fork scheduler output reaches both sinks.

### Functional test

The pattern was validated in a sandbox before redeploy:

```
--- captured console (docker-stdout analogue) ---
line-before-exec
line-after-exec-stdout
line-after-exec-stderr
--- file contents (host log analogue) ---
line-before-exec
line-after-exec-stdout
line-after-exec-stderr
```

Both sinks see every line, including the post-`exec` output.

### Live verification

After rebuild + recreate at `2026-07-15T07:28Z`:

- Container reached `healthy` in ~29 s.
- `docker logs --since 1m agent-core-local-scheduler-1` now returns DBOS
  startup banners, structlog lines, and `schedule.reload_completed
  manifests_count=4 schedules_applied=21` — previously empty.
- Host file continues to receive the same lines, preserving the
  cross-restart persistence contract.

---

## Out of scope

- Token rotation / TTL — not requested.
- Rotating the persisted observations JSONL past 720 lines — already enforced by the append path in `_append_observation`.
- Rotating the host bind-mounted log file (`scheduler-entrypoint.log`)
  beyond what `tee -a` provides — left for a future change.
- Refactoring `webhook_selftest_workflow` to read the secret from
  `settings` rather than accept it as a kwarg — larger change, not
  needed for this fix.