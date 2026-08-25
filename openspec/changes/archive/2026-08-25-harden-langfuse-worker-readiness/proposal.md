## Why

The stable full observability stack can report success while Langfuse web and worker processes emit recurring Redis socket-timeout errors, and the upstream worker readiness endpoint can remain HTTP 200 during a short Redis outage because its queue-activity threshold is much longer than the outage window. This change makes the supported Redis socket policy explicit in Compose and makes deployment readiness fail closed through an external composite check rather than treating process liveness or the upstream endpoint alone as proof of Redis reachability.

## What Changes

- Set the supported `REDIS_SOCKET_TIMEOUT_MS: "0"` as a fixed literal in the Compose environment for both `langfuse-web` and `langfuse-worker`; it is not an env-template, tools-config, or operator input option.
- Keep Langfuse web and worker startup ordered on healthy Redis and retain the pinned queue-aware `/api/ready?failIfQueueConsumptionStuck=true` worker check.
- Add external composite deployment readiness that requires the strict worker endpoint, a bounded authenticated Redis probe from the same network path used by the worker, and the existing Redis and worker container health states.
- Treat a failed composite probe as deployment non-ready even if the upstream endpoint remains HTTP 200; this change does not promise or require an upstream endpoint HTTP 503 response.
- Preserve the pinned Langfuse `4.16.0` web/worker pair, Redis `8.10.1-alpine`, ClickHouse `26.7.5.10-alpine`, and `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` exactly `false`.
- Keep the Langfuse v4 OTLP route `/api/public/otel/v1/traces` and `x-langfuse-ingestion-version: "4"` explicit in static and runtime evidence.
- Require exact event receipt in both `default.events_core` and `default.events_full`, with Collector, Tempo, and MLflow fan-out evidence kept as separate acceptance signals.
- Require a clean compatibility window and a disposable-first then retained-stack Redis fault/recovery proof with transient fault errors classified separately from clean and post-recovery zero-error windows, three consecutive composite passes before recovery is accepted, and no volume removal.
- Bound the two dominant Docker Desktop consumers, LGTM and ClickHouse, from measured live evidence so their background work cannot starve worker/Redis timers; use a lightweight bounded ClickHouse HTTP healthcheck instead of the loaded native client probe.
- Keep unsupported timeout variables, the legacy ingestion route, credential values, Redis downgrade, routine database/volume migration, and unrelated profile changes out of scope. If a diagnostic exposes a backend credential, fail closed: rotate it without recording the value and, only under explicit no-old-data authority when in-place rotation is unavailable, fresh-reset that affected backend and rerun its complete acceptance.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdt-observability-docker-deployment`: Require fixed paired Redis socket configuration, healthy Redis ordering, the strict worker endpoint, the false BullMQ bypass, v4 OTLP routing, and external composite readiness.
- `tdt-compose-operational-readiness`: Require exact Redis 8 and ClickHouse 26 behavioral evidence, event fan-out, clean error windows, and bounded fault/recovery evidence.

## Impact

- Owning implementation repository: `/Users/androidteam/Developer/tdt-observability`.
- Planning/spec owner: `/Users/androidteam/Developer/openspec-store`.
- Runtime surfaces: the existing `tdt-local-full` Langfuse web, worker, Redis, Collector, ClickHouse, and LGTM services. Stateful databases, credentials, and volumes remain preserved for the ordinary correction/fault path; a security-incident reset is limited to the exposed backend under explicit no-old-data authority.
- Code and configuration: Langfuse Compose models, deployment preflight/verifier, Collector route contract tests, Compose/readiness tests, runbook, and durable acceptance evidence.
- Runtime verification: the external composite result must record the strict endpoint, same-worker-network authenticated Redis probe, existing container health, exact event-table receipt, fan-out, clean windows, fault interval, recovery passes, and restart classification without recording credential values.
- No agent-core, scheduler, canonical tdt-core, Omniroute, host-native service, foreign Docker resource, or legacy-route ownership changes.
