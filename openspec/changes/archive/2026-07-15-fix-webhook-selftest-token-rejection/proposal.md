# Why

This change bundles two operational fixes that surfaced together during scheduler monitoring on 2026-07-15:

1. The `webhook-selftest` DBOS workflow was sending an empty `X-Gitlab-Token` while the receiver enforced `GITLAB_WEBHOOK_SECRET`, producing a ~46h storm of `WEBHOOK_SELFTEST_ESCALATION` events (361 events between 2026-07-13 16:10 and 2026-07-15 14:55 UTC).
2. The scheduler container's `entrypoint.sh` redirected PID 1's stdout/stderr entirely to a host-bind-mounted log file, so `docker logs` could not see what the scheduler was emitting — silently breaking the standard container-level logging path for an "Up / healthy" service.

## Fix 1 — `webhook-selftest` token forwarding

Root cause is in `webhook-receiver/src/webhook_receiver/dbos_scheduling.py:96-104`: the wrapper reads `GITLAB_WEBHOOK_SECRET` into `_secret`, then calls `webhook_selftest_workflow(webhook_secret="")` with a hardcoded empty string, ignoring the value it just read. The receiver enforces token equality *before* the `X-TDT-Selftest` bypass at `webhook-receiver/src/webhook_receiver/api/app.py:1002-1018`, so the empty token mismatches the configured 64-char secret and the probe always 401s.

The fix is a one-line change: forward `_secret` instead of `""`. The empty-secret deployment case (`"" == ""`) is preserved.

## Fix 2 — scheduler entrypoint dual-sink logging

`entrypoint.sh` redirected PID 1's stdout/stderr to a file inside the bind-mounted `$TDT_HOME` directory. The container's stdout — and therefore the Docker json-file log driver that backs `docker logs` — received nothing. Replace `exec >> "${LOG_FILE}" 2>&1` with `exec > >(tee -a "${LOG_FILE}") 2>&1`, which fans output to both the file and the container's stdout.

# What Changes

- `webhook_receiver/dbos_scheduling.py::_selftest_workflow` calls `webhook_selftest_workflow(webhook_secret=_secret)` instead of `webhook_secret=""`.
- The stale comment block above the registration (lines 89-95) is rewritten to describe the current behaviour: the probe always presents the configured token.
- `agent_core/deployments/scheduler/entrypoint.sh` replaces the file-only redirect with a tee-based dual-sink redirect.
- The canonical spec `webhook-delivery-self-test` (promoted by `coverage-sweep`) is **MODIFIED** to add the token-forwarding contract as an explicit numbered step in the main requirement, with two new scenarios covering the "secret set" and "secret unset" cases. The previously silent assumption (no auth configured) is made explicit so future readers don't fall into the same trap.
- The canonical spec `scheduler-entrypoint` (promoted by `scheduler-compose-self-bootstrap`) is **MODIFIED** to require that PID 1's stdout reaches the Docker log driver as well as the host-bind-mounted log file, with a new scenario validating `docker logs` round-trips scheduler output.

# Impact

- `webhook-selftest` workflow: no signature change (still takes `webhook_secret`).
- `webhook_receiver/selftest.py::webhook_selftest_workflow`: unchanged.
- DBOS scheduler registration / apply pipeline: unchanged.
- Deployment: receivers without `GITLAB_WEBHOOK_SECRET` set continue to work — `os.environ.get(..., "")` returns `""` and the receiver's auth check (`"" != ""`) is false, so the probe is accepted as before.
- Container: `docker logs` now returns scheduler output (DBOS banners, structlog lines, reload events). The host file continues to receive the same content.
- Specs: two existing capabilities (`webhook-delivery-self-test`, `scheduler-entrypoint`) are updated in place — no new capabilities introduced, so the docs surface stays singular.