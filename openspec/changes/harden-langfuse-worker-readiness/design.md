## Context

See `proposal.md` for motivation. The stable Docker Desktop full profile uses Langfuse web/worker `4.16.0`, Redis `8.10.1-alpine`, and ClickHouse `26.7.5.10-alpine`. The worker previously had no Docker healthcheck, Redis dependencies used `service_started`, and the coordinator accepted empty Docker health metadata. The pinned worker image exposes a queue-aware readiness endpoint on port 3030. Redis 8 remains an explicit compatibility deviation from Langfuse's documented Redis 7 baseline.

## Goals / Non-Goals

**Goals:**

- Make worker readiness represent initialized, non-stuck queue consumption.
- Prevent ambient or file configuration from bypassing the Redis 8 BullMQ version gate.
- Preserve exact v4 Langfuse OTLP routing and behavioral event receipt.
- Keep acceptance value-free and scoped to the existing `tdt-local-full` owner project.

**Non-Goals:**

- Do not add a PID/process-exists healthcheck or treat Redis PING as worker readiness.
- Do not invent undocumented Langfuse/ioredis timeout environment variables.
- Do not downgrade Redis, retune memory/health budgets without measurements, rotate credentials, migrate data, or remove volumes.
- Do not change base or MLflow-only profile behavior.

## Decisions

### Use the image-supported queue-aware worker endpoint

The worker healthcheck calls the pinned image's `/api/ready?failIfQueueConsumptionStuck=true` endpoint with finite Docker health budgets. This is chosen over PID checks because the endpoint is initialized after worker startup and evaluates queue-consumption state. A future image upgrade must revalidate this endpoint before changing the pin.

### Require Redis health before Langfuse consumers start

Both web and worker depend on Redis with `service_healthy`, while PostgreSQL/ClickHouse health and the MinIO completion gate remain unchanged. This orders startup on authenticated Redis readiness without claiming that Redis health alone proves worker readiness.

### Fail closed on the BullMQ bypass

Preflight reads both the operator env file and the ambient process override and accepts only exact `false`. Other values fail before Docker mutation and diagnostics name only the field, not its surrounding environment. This deliberately removes an implicit local exception lane; any future bypass requires a separate OpenSpec change and explicit evidence contract.

### Keep v4 ingestion and receipt as separate evidence

Static configuration requires `/api/public/otel/v1/traces` and `x-langfuse-ingestion-version: "4"`. Runtime acceptance separately proves one exact event in Langfuse ClickHouse. A successful header/config validation does not replace event receipt, and event receipt does not replace worker readiness.

### Defer Redis resource tuning

The existing reservation, limit, health timing, and `noeviction` policy remain unchanged because no measured queue workload establishes a safe `maxmemory` or tighter budget. Measurement is tracked separately and MUST precede any tuning.

## Risks / Trade-offs

- [The pinned worker endpoint changes in a future Langfuse release] → Keep web/worker pins coupled and require daemon-free render, image inspection, endpoint probe, and focused tests before promotion.
- [A transient queue initialization delay holds the worker unhealthy] → Use finite start period, interval, timeout, and retry budgets; do not weaken the readiness predicate.
- [Ambient environment unexpectedly enables the bypass] → Validate ambient and file sources before any Docker command and reject non-false values.
- [A short clean log window misses recurring timeout cadence] → Retain the historical warning until a longer bounded observation proves otherwise; do not infer closure from one successful event.
- [Queue-aware health adds another dependency to Compose convergence] → Recreate only affected services and preserve stateful databases and volumes; rollback to the prior source commit and recreate the same services without deleting volumes.

## Migration Plan

1. Validate focused Compose, preflight, gateway, and evidence tests against the committed source.
2. Render all four profiles without daemon mutation and validate the pinned Collector configurations.
3. Recreate only `langfuse-redis`, `langfuse-worker`, and `otel-gateway` using the protected operator env file; preserve all databases and volumes.
4. Wait for Redis health, strict worker readiness, and external gateway readiness.
5. Emit one uniquely identified trace through the gateway and prove exactly one event in Langfuse ingestion tables, zero affected-service restarts, and a bounded clean compatibility-error window.
6. Roll back by selecting the prior source commit and recreating the same affected services without `down -v` or prune if the new readiness contract fails.
