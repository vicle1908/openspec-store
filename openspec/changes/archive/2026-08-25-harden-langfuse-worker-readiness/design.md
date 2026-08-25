## Context

See `proposal.md` for motivation. The stable Docker Desktop full profile uses Langfuse web/worker `4.16.0`, Redis `8.10.1-alpine`, and ClickHouse `26.7.5.10-alpine`. Langfuse `4.16.0` supports `REDIS_SOCKET_TIMEOUT_MS=0`, which disables the ioredis socket watchdog that produced the observed 30-second idle-queue errors. The setting must be represented as the fixed Compose literal `REDIS_SOCKET_TIMEOUT_MS: "0"` in both web and worker; it must not be promoted to an env-template, tools-config, or operator option.

The pinned worker's `/api/ready?failIfQueueConsumptionStuck=true` endpoint is still useful for process and queue registration, but its queue-stuck calculation uses a 3,600-second inactivity threshold and worker connection errors do not necessarily change that state. A live worker with recent activity can therefore continue returning HTTP 200 during a 60–120 second Redis interruption. Compose `depends_on` and the existing container-local Redis healthcheck provide startup and container signals, not an ongoing worker-network reachability guarantee.

## Goals / Non-Goals

**Goals:**

- Set the supported socket-timeout policy identically in the web and worker Compose models as a fixed non-secret literal.
- Preserve the real Redis 8 BullMQ compatibility gate, exact image versions, v4 OTLP route, and value-free evidence.
- Enforce external deployment composite readiness from the strict worker endpoint, a same-worker-network authenticated Redis probe, and existing container health.
- Prove exact Langfuse event receipt and independent Collector, Tempo, and MLflow fan-out.
- Verify clean convergence and bounded Redis interruption/recovery, requiring three consecutive composite passes before recovery is accepted.
- Bound the dominant local Docker consumers from measured evidence so health and verifier timers remain schedulable on the 8-vCPU Docker Desktop baseline.

**Non-Goals:**

- Do not promise or require the upstream worker endpoint itself to return HTTP 503 during a short Redis outage; endpoint-level 503 would require an upstream or custom worker change outside this contract.
- Do not add a PID-only healthcheck, use a bare Redis ping as worker readiness, or treat a fresh queue-activity timestamp as proof of Redis reachability.
- Do not expose `REDIS_SOCKET_TIMEOUT_MS` through env templates, tools configuration, or operator input, and do not invent `REDIS_COMMAND_TIMEOUT_MS`, `REDIS_BLOCKING_TIMEOUT_MS`, or other unsupported variables.
- Do not downgrade Redis, change ClickHouse 26, bypass the BullMQ version check, record credentials, perform routine database/volume migrations, or change base/MLflow-only behavior. A credential exposure is an incident exception: rotation is mandatory, and fresh reset is allowed only for the affected backend under explicit no-old-data authority when in-place rotation is unavailable.

## Decisions

### Use a fixed Compose literal for the supported socket policy

The web and worker Compose service definitions SHALL each contain the exact non-secret literal `REDIS_SOCKET_TIMEOUT_MS: "0"`. Static render and focused tests SHALL prove paired presence and SHALL prove that env templates, tools configuration, and operator input do not provide an alternate lane. The existing `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` policy remains exactly `false`; disabling the socket watchdog is not a version-check bypass.

### Keep the strict worker endpoint as one composite input

The worker healthcheck SHALL call `/api/ready?failIfQueueConsumptionStuck=true` with finite budgets and require the successful, queue-enabled, not-stuck response. This check covers process and queue registration, but it is not an outage detector for the selected short fault window. The verifier SHALL never infer an endpoint HTTP 503 promise from this endpoint.

### Add external composite readiness on the worker's network path

The external deployment verifier SHALL report ready only when all of these current signals pass together:

1. `langfuse-worker` is running and its strict endpoint returns HTTP 200 with queue consumption enabled and `stuck: false`.
2. A bounded authenticated Redis PING or equivalent command succeeds from the same private network path used by `langfuse-worker`.
3. `langfuse-redis` is running and its existing Docker healthcheck is `healthy`.
4. `langfuse-worker` has no unhealthy Docker health state.

A failed same-worker-network Redis probe makes the external composite non-ready immediately or within its declared finite probe budget, regardless of a recent worker activity timestamp or an upstream HTTP 200. The existing container health states and endpoint remain independent evidence fields; logs and Docker events are supplemental diagnostics, not the sole positive readiness signal.

### Preserve compatibility, routing, and fan-out as separate gates

The selected images remain Langfuse `4.16.0`, Redis `8.10.1-alpine`, and ClickHouse `26.7.5.10-alpine`, with `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` exactly `false`. Collector acceptance SHALL use `/api/public/otel/v1/traces` and `x-langfuse-ingestion-version: "4"`, then independently verify exactly one unique trace event in both `default.events_core` and `default.events_full`, Collector export/acceptance counters, Tempo HTTP success, and MLflow span receipt. No legacy ingestion route or credential value belongs in the artifacts or evidence.

### Separate clean-window and fault/recovery evidence

The clean window SHALL require at least ten minutes of zero Redis-version, command, BullMQ, socket-timeout, and unplanned-restart errors. The fault proof SHALL be disposable-first and then run against the retained stack. During the controlled 60–120 second Redis interruption, expected transient connection errors may be recorded and classified only within the fault interval; they SHALL not be conflated with the clean or post-recovery windows. Recovery SHALL use alias-preserving restoration or the normal Compose lifecycle, SHALL never remove volumes, SHALL complete within the declared 120-second bound, and SHALL require three consecutive successful composite evaluations plus representative post-recovery queue work.

### Keep local health budgets schedulable

Measured Docker Desktop evidence SHALL bound LGTM to 1.0 CPU and ClickHouse to 1.5 CPUs on the 8-vCPU local baseline. ClickHouse Docker health SHALL use its lightweight local HTTP `/ping` with a finite inner and outer budget rather than the loaded native client command. These constraints preserve capacity for worker timers, Redis lock renewal, healthchecks, and the external verifier; they do not change production image pins or memory reservations.

### Fail closed after a credential exposure

No diagnostic SHALL print a backend credential. If a local tool nevertheless exposes one, that value is compromised and MUST be rotated without being copied into artifacts. In-place rotation is preferred. When the application user cannot rotate itself and the user has explicitly authorized no old data, the affected backend alone MAY be recreated on a fresh versioned volume with a new unprinted credential. All migrations, composite readiness, event fan-out, and clean-window gates MUST then be rerun against the final cohort, and the exception MUST be disclosed value-free in durable evidence.

## Risks / Trade-offs

- [The upstream endpoint remains HTTP 200 while Redis is unreachable] → Make the same-worker-network authenticated Redis probe a required external composite input and state explicitly that endpoint 503 is not promised.
- [Disabling the socket watchdog removes one client-side idle protection] → Retain the real BullMQ version gate, current container health, strict endpoint, bounded authenticated probe, clean log window, and post-recovery queue job.
- [Web and worker drift in their socket policy] → Require identical fixed Compose literals and render/preflight assertions for both services.
- [Transient fault errors are mistaken for a clean failure] → Bound and label the fault interval separately, then require zero relevant errors in clean and post-recovery windows.
- [A recovery exercise damages retained state] → Prove the procedure on a disposable stack first, use alias-preserving recovery or Compose lifecycle for retained services, and forbid `down -v`, volume removal, and prune operations.
- [Heavy local backends starve health and Redis timers] → Apply the measured CPU limits, use lightweight health probes, and require final-cohort health plus composite evidence before promotion.
- [A diagnostic exposes a credential] → Stop using the value, rotate it without printing it, scope any no-old-data reset to the affected backend, and rerun final-cohort acceptance.

## Migration Plan

1. Run focused Compose, preflight, gateway, and evidence-contract tests against the committed source; render all four profiles without daemon mutation.
2. Confirm the fixed `REDIS_SOCKET_TIMEOUT_MS: "0"` literal appears in both web and worker Compose services, the exact Redis/ClickHouse images remain selected, the BullMQ bypass remains `false`, and no unsupported or legacy setting is present.
3. Recreate only `langfuse-web` and `langfuse-worker` for the primary readiness cohort; do not recreate Redis or the Collector for this task, and preserve stateful services and volumes.
4. Establish strict endpoint, same-worker-network authenticated Redis, existing-container-health, and external composite evidence.
5. Rerun the exact v4 event path and verify one event in each of `default.events_core` and `default.events_full`, plus Collector, Tempo, and MLflow fan-out.
6. Observe the ten-minute clean window, then run disposable-first and retained-stack fault/recovery proof with expected transient fault errors separated from zero-error clean/post-recovery windows and three consecutive composite passes.
7. If acceptance fails, use alias-preserving recovery or the normal Compose lifecycle against the same services without `down -v`, volume removal, or prune; no database or credential migration is part of rollback.
8. If a credential is exposed during diagnostics, follow the incident exception separately from rollback: rotate it, fresh-reset only the affected backend when explicitly authorized and necessary, rerun migrations and all final-cohort gates, and disclose the exception without the value.
