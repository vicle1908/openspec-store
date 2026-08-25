## Why

The stable full observability stack could report success while `langfuse-worker` had no Docker readiness gate and its BullMQ consumers emitted recurring Redis socket-timeout errors. This change makes worker queue readiness and the Redis 8 compatibility boundary fail closed so container liveness cannot substitute for behavioral acceptance.

## What Changes

- Require Langfuse web and worker to wait for healthy Redis instead of merely a started Redis process.
- Add the pinned Langfuse 4.16 worker's bounded `/api/ready?failIfQueueConsumptionStuck=true` health contract.
- Reject file and ambient attempts to enable `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` for the selected Redis 8 deployment.
- Make the Langfuse v4 OTLP route and `x-langfuse-ingestion-version: "4"` header explicit in static and retained runtime evidence.
- Require behavioral evidence to distinguish worker queue readiness from Docker process liveness.
- Preserve the selected Redis `8.10.1-alpine` compatibility deviation and defer memory/timeout tuning until a measured workload supplies defensible values.
- Non-goals: no Redis downgrade, no speculative Redis or ioredis timeout variables, no PID-only worker healthcheck, no legacy ingestion route, no credential rotation, no database or volume migration, and no compatibility changes to base or MLflow-only profiles.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tdt-observability-docker-deployment`: Require a bounded queue-aware Langfuse worker readiness gate, healthy Redis dependency ordering, a fail-closed BullMQ version-check control, and the v4 OTLP ingestion header.
- `tdt-compose-operational-readiness`: Require full and Langfuse profile acceptance to retain worker queue-readiness, exact event receipt, compatibility-error classification, and affected-service restart evidence.

## Impact

- Owning repository: `/Users/androidteam/Developer/tdt-observability`.
- Planning/spec owner: `/Users/androidteam/Developer/openspec-store`.
- Runtime surfaces: `tdt-local-full` services `langfuse-redis`, `langfuse-worker`, and `otel-gateway`; Langfuse PostgreSQL, ClickHouse, MinIO, volumes, and credentials remain preserved.
- Code and configuration: Langfuse Compose overlay, deployment preflight, Collector route contract tests, Compose/readiness tests, runbook, and durable acceptance evidence.
- No agent-core, scheduler, canonical tdt-core, Omniroute, host-native service, or foreign Docker resource ownership changes.
